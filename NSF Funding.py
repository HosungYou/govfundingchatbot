import requests
import json
import os
import time
import zipfile
import re
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import concurrent.futures
import logging

########################################
# CONFIG
########################################
SEARCH_API_URL = "https://api.grants.gov/v1/api/search2"
FETCH_API_URL = "https://api.grants.gov/v1/api/fetchOpportunity"
XML_LISTING_PAGE = "https://www.grants.gov/xml-extract"

OUTPUT_JSON_FILENAME = "merged_data.json"

HEADERS = {
    'Content-Type': 'application/json',
}

# URL 정규식
url_pattern = re.compile(r'(https?://[^\s]+)')

# 로깅 설정 (DEBUG 레벨까지 출력하도록 설정)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def extract_links(text):
    """텍스트 내 http/https 형태의 링크를 리스트로 반환"""
    if not text:
        return []
    return url_pattern.findall(text)


########################################
# 1) search2 페이징
########################################
def fetch_all_grants_from_search2():
    """search2 API 페이징으로 모든 공고 목록."""
    search_payload = {
        "keyword": "",
        "agencies": "",
        "oppStatuses": "forecasted|posted",
        "startRecordNum": 0,
        "rows": 100
    }

    all_grants_search = []
    fetched_ids = set()
    total_hits = 0

    logging.info("[1단계] search2 API 페이징 시작...")

    while True:
        try:
            resp = requests.post(SEARCH_API_URL, headers=HEADERS, json=search_payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            if not data or "data" not in data:
                logging.warning("[WARN] search2 응답에 'data'가 없습니다. 종료.")
                break

            data_section = data["data"]
            if total_hits == 0:
                total_hits = data_section.get("hitCount", 0)
                logging.info(f"총 공고 수(hitCount): {total_hits}")

            opp_hits = data_section.get("oppHits", [])
            if not opp_hits:
                logging.info("[INFO] 더 이상 oppHits가 없어 종료.")
                break

            for grant_obj in opp_hits:
                unique_id = grant_obj.get('id')
                if unique_id and unique_id not in fetched_ids:
                    fetched_ids.add(unique_id)
                    all_grants_search.append(grant_obj)

            current_start = data_section.get("startRecord", 0)
            hits_returned = len(opp_hits)
            logging.info(f"이번 페이지 {hits_returned}개 → 누적 {len(all_grants_search)}/{total_hits}")

            if current_start + hits_returned >= total_hits:
                logging.info("모든 페이지를 수집했습니다.")
                break
            else:
                search_payload["startRecordNum"] = current_start + hits_returned

        except requests.HTTPError as e:
            logging.error(f"[ERROR] search2 HTTP 에러: {e}")
            break
        except requests.RequestException as e:
            logging.error(f"[ERROR] search2 요청 예외: {e}")
            break
        except json.JSONDecodeError as e:
            logging.error(f"[ERROR] search2 JSON 파싱오류: {e}")
            break

    logging.info(f"[결과] search2 총 수집 공고: {len(all_grants_search)}개")
    return all_grants_search


########################################
# 2) fetchOpportunity 병렬 상세 조회
########################################
def _fetch_opportunity_detail(opp_id):
    """fetchOpportunity API 개별 호출 (ThreadPoolExecutor에서 사용)"""
    payload = {"opportunityId": opp_id}
    try:
        r = requests.post(FETCH_API_URL, headers=HEADERS, json=payload, timeout=30)
        r.raise_for_status()
        fetched_data = r.json()
        return fetched_data.get("data")
    except requests.HTTPError as e:
        logging.error(f"[ERROR] fetchOpportunity HTTP 에러 [{opp_id}]: {e}")
    except requests.RequestException as e:
        logging.error(f"[ERROR] fetchOpportunity 요청 예외 [{opp_id}]: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"[ERROR] fetchOpportunity JSON 파싱오류 [{opp_id}]: {e}")
    return None

def fetch_details_for_grants(all_grants_search, max_workers=10):
    """
    search2로 얻은 ID 목록을 기반으로 fetchOpp 상세 조회 병렬화
    synopsisDesc에서 http/https 링크를 파악 -> 'detected_links_api' 추가
    """
    logging.info("\n[2단계] fetchOpportunity 상세 조회(병렬) 시작...")
    all_grants_details = []

    # 추출할 opp_id 목록
    opp_ids = [item["id"] for item in all_grants_search if "id" in item]

    # ThreadPoolExecutor로 병렬 처리
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_id = {executor.submit(_fetch_opportunity_detail, oid): oid for oid in opp_ids}

        for i, future in enumerate(concurrent.futures.as_completed(future_to_id), start=1):
            oid = future_to_id[future]
            detail_inner = future.result()
            if detail_inner:
                syn_text = detail_inner.get("synopsis", {}).get("synopsisDesc", "")
                found_urls = extract_links(syn_text)
                detail_inner["detected_links_api"] = found_urls

                combined = {
                    "search_summary": {"id": oid},  # 최소 구조
                    "fetch_detail": detail_inner
                }
                all_grants_details.append(combined)
            if i % 50 == 0:
                logging.info(f"{i}/{len(opp_ids)}개 처리됨")

    logging.info(f"[결과] fetchOpportunity 상세 조회: 총 {len(all_grants_details)}개")
    return all_grants_details


########################################
# 3) grants.gov/xml-extract 페이지 파싱 → ZIP
########################################
def get_latest_zip_url():
    """단순 정적 파싱. .zip 후보를 찾아 첫 번째 반환."""
    logging.debug(f"[DEBUG] XML listing 페이지 요청: {XML_LISTING_PAGE}")
    try:
        resp = requests.get(XML_LISTING_PAGE, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"[ERROR] xml-extract 페이지 요청 실패: {e}")
        return None

    logging.debug(f"[DEBUG] 응답 status={resp.status_code}, 길이={len(resp.content)} bytes")
    soup = BeautifulSoup(resp.text, "html.parser")
    # .zip candidate 수집
    all_a = soup.select("a[href]")
    candidates = []
    for link_tag in all_a:
        href = link_tag.get("href", "").strip()
        if (".zip" in href.lower()) or ("GrantsDBExtract" in href):
            candidates.append(href)

    logging.debug(f"[DEBUG] .zip 링크 후보 {len(candidates)}개:")
    for c in candidates:
        logging.debug("  - %s", c)

    if not candidates:
        logging.info("[INFO] zip 링크를 찾지 못함.")
        return None

    first = candidates[0]
    if not first.startswith("http"):
        # grants.gov/extract/... 가정
        base_url = "https://www.grants.gov/extract/"
        first = base_url + first.lstrip("/")
    logging.debug(f"[DEBUG] 첫 zip 링크: {first}")
    return first

def download_and_parse_xml_dump():
    """
    grants.gov/xml-extract -> 첫 zip URL -> 다운로드 -> 해제 -> XML 파싱
    'OpportunitySynopsisDetail_1_0' 항목들이 있음을 전제
    키는 <OpportunityNumber>로 fetchOpp oppNum과 매칭
    """
    xml_data_map = {}

    logging.info("\n[3단계] grants.gov/xml-extract -> ZIP 다운로드...")

    zip_url = get_latest_zip_url()
    if not zip_url:
        logging.warning("[WARN] zip_url= None -> XML 파싱 스킵.")
        return xml_data_map

    zip_filename = "temp_latest.zip"
    try:
        r2 = requests.get(zip_url, stream=True, timeout=60)
        r2.raise_for_status()
        with open(zip_filename, 'wb') as f:
            for chunk in r2.iter_content(chunk_size=8192):
                f.write(chunk)
        logging.debug(f"[DEBUG] ZIP 파일 다운로드 OK: {zip_filename}")

    except requests.RequestException as e:
        logging.error(f"[ERROR] ZIP 다운로드 실패: {e}")
        return xml_data_map

    # 압축 해제
    extracted_xml = None
    try:
        with zipfile.ZipFile(zip_filename, 'r') as zf:
            zf.extractall(".")
            file_list = zf.namelist()
            for fn in file_list:
                if fn.lower().endswith(".xml"):
                    extracted_xml = fn
                    break
        if not extracted_xml:
            logging.info("[INFO] ZIP 내 .xml 파일을 못 찾았음")
            return xml_data_map
        logging.debug(f"[DEBUG] 추출된 XML 파일: {extracted_xml}")
    except zipfile.BadZipFile as e:
        logging.error(f"[ERROR] BadZipFile: {e}")
        return xml_data_map
    except Exception as e:
        logging.error(f"[ERROR] zip 해제 중 예외: {e}")
        return xml_data_map

    # XML 파싱
    if extracted_xml and os.path.exists(extracted_xml):
        logging.debug("[DEBUG] XML 파싱...")
        try:
            tree = ET.parse(extracted_xml)
            root = tree.getroot()
            opps = root.findall(".//OpportunitySynopsisDetail_1_0", root.nsmap if hasattr(root, 'nsmap') else {})
            if not opps:
                opps = root.findall(".//{http://apply.grants.gov/system/OpportunityDetail-V1.0}OpportunitySynopsisDetail_1_0")

            logging.debug(f"[DEBUG] <OpportunitySynopsisDetail_1_0> {len(opps)}개 발견")

            for opp_elem in opps:
                opp_number = opp_elem.findtext("{http://apply.grants.gov/system/OpportunityDetail-V1.0}OpportunityNumber")
                if not opp_number:
                    opp_number = opp_elem.findtext("OpportunityNumber")

                opp_id = opp_elem.findtext("{http://apply.grants.gov/system/OpportunityDetail-V1.0}OpportunityID") \
                         or opp_elem.findtext("OpportunityID")
                title = opp_elem.findtext("{http://apply.grants.gov/system/OpportunityDetail-V1.0}OpportunityTitle") \
                        or opp_elem.findtext("OpportunityTitle")
                desc = opp_elem.findtext("{http://apply.grants.gov/system/OpportunityDetail-V1.0}Description") \
                       or opp_elem.findtext("Description")
                agency_name = opp_elem.findtext("{http://apply.grants.gov/system/OpportunityDetail-V1.0}AgencyName") \
                              or opp_elem.findtext("AgencyName")

                found_links = extract_links(desc)

                if opp_number:
                    xml_data_map[opp_number] = {
                        "opportunityId_xml": opp_id,
                        "opportunityNumber_xml": opp_number,
                        "title_xml": title,
                        "agencyName_xml": agency_name,
                        "description_xml": desc,
                        "detected_links_xml": found_links,
                        "close_date_xml": opp_elem.findtext("{http://apply.grants.gov/system/OpportunityDetail-V1.0}CloseDate") \
                                           or opp_elem.findtext("CloseDate"),
                        "award_ceiling_xml": opp_elem.findtext("{http://apply.grants.gov/system/OpportunityDetail-V1.0}AwardCeiling") \
                                            or opp_elem.findtext("AwardCeiling"),
                    }

            logging.debug(f"[DEBUG] XML 파싱 완료. dict size = {len(xml_data_map)}")
        except ET.ParseError as e:
            logging.error(f"[ERROR] XML 구문 오류: {e}")
    else:
        logging.info("[INFO] XML 파일이 존재하지 않음, 파싱 스킵.")

    return xml_data_map


########################################
# 4) 병합
########################################
def merge_data(all_grants_details, xml_data_map):
    """
    fetchOpp -> fetch_detail["opportunityNumber"]
    XML -> 'OpportunityNumber_xml'
    => key match
    """
    merged_list = []
    for record in all_grants_details:
        fetch_part = record["fetch_detail"]
        opp_num = fetch_part.get("opportunityNumber")
        if opp_num and opp_num in xml_data_map:
            record["xml_detail"] = xml_data_map[opp_num]
        else:
            record["xml_detail"] = None
        merged_list.append(record)

    logging.info(f"[결과] 최종 merged_data 개수: {len(merged_list)}")
    return merged_list


########################################
# MAIN
########################################
def main():
    # 1) search2
    all_grants_search = fetch_all_grants_from_search2()

    # 2) fetchOpportunity (병렬)
    all_grants_details = fetch_details_for_grants(all_grants_search, max_workers=10)

    # 3) xml-extract -> zip -> xml parse
    xml_data_map = download_and_parse_xml_dump()

    # 4) 병합
    merged_data = merge_data(all_grants_details, xml_data_map)

    # 5) JSON
    try:
        with open(OUTPUT_JSON_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)
        logging.info(f"\n--- '{OUTPUT_JSON_FILENAME}' 파일 저장 완료 ---")
    except IOError as e:
        logging.error(f"[ERROR] JSON 저장 오류: {e}")

    logging.info("\n--- 전체 프로세스 종료 ---")


if __name__ == "__main__":
    main()

# (매일 새벽 2시에 자동 실행하기 위한 cron 예시 - 리눅스 환경)
# $ crontab -e
# 0 2 * * * /usr/bin/python /path/to/this_script.py >> /path/to/logfile.log 2>&1
#
# 이렇게 설정해두면 매일 새벽 2시에 자동으로 이 스크립트가 실행된다.

