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

# URL regular expression
url_pattern = re.compile(r'(https?://[^\s]+)')

# Logging configuration (set to output up to DEBUG level)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def extract_links(text):
    """Extract http/https links from text and return as a list"""
    if not text:
        return []
    return url_pattern.findall(text)


########################################
# 1) search2 pagination
########################################
def fetch_all_grants_from_search2():
    """Get all grant listings using search2 API pagination."""
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

    logging.info("[Step 1] Starting search2 API pagination...")

    while True:
        try:
            resp = requests.post(SEARCH_API_URL, headers=HEADERS, json=search_payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            if not data or "data" not in data:
                logging.warning("[WARN] No 'data' in search2 response. Terminating.")
                break

            data_section = data["data"]
            if total_hits == 0:
                total_hits = data_section.get("hitCount", 0)
                logging.info(f"Total grant count (hitCount): {total_hits}")

            opp_hits = data_section.get("oppHits", [])
            if not opp_hits:
                logging.info("[INFO] No more oppHits found. Terminating.")
                break

            for grant_obj in opp_hits:
                unique_id = grant_obj.get('id')
                if unique_id and unique_id not in fetched_ids:
                    fetched_ids.add(unique_id)
                    all_grants_search.append(grant_obj)

            current_start = data_section.get("startRecord", 0)
            hits_returned = len(opp_hits)
            logging.info(f"This page: {hits_returned} grants → Cumulative: {len(all_grants_search)}/{total_hits}")

            if current_start + hits_returned >= total_hits:
                logging.info("All pages collected.")
                break
            else:
                search_payload["startRecordNum"] = current_start + hits_returned

        except requests.HTTPError as e:
            logging.error(f"[ERROR] search2 HTTP error: {e}")
            break
        except requests.RequestException as e:
            logging.error(f"[ERROR] search2 request exception: {e}")
            break
        except json.JSONDecodeError as e:
            logging.error(f"[ERROR] search2 JSON parsing error: {e}")
            break

    logging.info(f"[Result] search2 total collected grants: {len(all_grants_search)}")
    return all_grants_search


########################################
# 2) fetchOpportunity parallel detail lookup
########################################
def _fetch_opportunity_detail(opp_id):
    """Individual fetchOpportunity API call (used in ThreadPoolExecutor)"""
    payload = {"opportunityId": opp_id}
    try:
        r = requests.post(FETCH_API_URL, headers=HEADERS, json=payload, timeout=30)
        r.raise_for_status()
        fetched_data = r.json()
        return fetched_data.get("data")
    except requests.HTTPError as e:
        logging.error(f"[ERROR] fetchOpportunity HTTP error [{opp_id}]: {e}")
    except requests.RequestException as e:
        logging.error(f"[ERROR] fetchOpportunity request exception [{opp_id}]: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"[ERROR] fetchOpportunity JSON parsing error [{opp_id}]: {e}")
    return None

def fetch_details_for_grants(all_grants_search, max_workers=10):
    """
    Parallel fetchOpportunity detail lookup based on IDs from search2
    Find http/https links in synopsisDesc -> add to 'detected_links_api'
    """
    logging.info("\n[Step 2] Starting fetchOpportunity detail lookup (parallel)...")
    all_grants_details = []

    # List of opp_ids to extract
    opp_ids = [item["id"] for item in all_grants_search if "id" in item]

    # Parallel processing with ThreadPoolExecutor
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
                    "search_summary": {"id": oid},  # Minimal structure
                    "fetch_detail": detail_inner
                }
                all_grants_details.append(combined)
            if i % 50 == 0:
                logging.info(f"{i}/{len(opp_ids)} processed")

    logging.info(f"[Result] fetchOpportunity detail lookup: total {len(all_grants_details)} grants")
    return all_grants_details


########################################
# 3) grants.gov/xml-extract page parsing → ZIP
########################################
def get_latest_zip_url():
    """Simple static parsing. Find .zip candidates and return the first one."""
    logging.debug(f"[DEBUG] XML listing page request: {XML_LISTING_PAGE}")
    try:
        resp = requests.get(XML_LISTING_PAGE, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"[ERROR] xml-extract page request failed: {e}")
        return None

    logging.debug(f"[DEBUG] Response status={resp.status_code}, length={len(resp.content)} bytes")
    soup = BeautifulSoup(resp.text, "html.parser")
    # Collect .zip candidates
    all_a = soup.select("a[href]")
    candidates = []
    for link_tag in all_a:
        href = link_tag.get("href", "").strip()
        if (".zip" in href.lower()) or ("GrantsDBExtract" in href):
            candidates.append(href)

    logging.debug(f"[DEBUG] .zip link candidates {len(candidates)}:")
    for c in candidates:
        logging.debug("  - %s", c)

    if not candidates:
        logging.info("[INFO] No zip link found.")
        return None

    first = candidates[0]
    if not first.startswith("http"):
        # Assuming grants.gov/extract/...
        base_url = "https://www.grants.gov/extract/"
        first = base_url + first.lstrip("/")
    logging.debug(f"[DEBUG] First zip link: {first}")
    return first

def download_and_parse_xml_dump():
    """
    grants.gov/xml-extract -> first zip URL -> download -> extract -> XML parsing
    Assumes 'OpportunitySynopsisDetail_1_0' items exist
    Key is <OpportunityNumber> to match with fetchOpp oppNum
    """
    xml_data_map = {}

    logging.info("\n[Step 3] grants.gov/xml-extract -> ZIP download...")

    zip_url = get_latest_zip_url()
    if not zip_url:
        logging.warning("[WARN] zip_url= None -> Skipping XML parsing.")
        return xml_data_map

    zip_filename = "temp_latest.zip"
    try:
        r2 = requests.get(zip_url, stream=True, timeout=60)
        r2.raise_for_status()
        with open(zip_filename, 'wb') as f:
            for chunk in r2.iter_content(chunk_size=8192):
                f.write(chunk)
        logging.debug(f"[DEBUG] ZIP file download OK: {zip_filename}")

    except requests.RequestException as e:
        logging.error(f"[ERROR] ZIP download failed: {e}")
        return xml_data_map

    # Extract ZIP
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
            logging.info("[INFO] No .xml file found in ZIP")
            return xml_data_map
        logging.debug(f"[DEBUG] Extracted XML file: {extracted_xml}")
    except zipfile.BadZipFile as e:
        logging.error(f"[ERROR] BadZipFile: {e}")
        return xml_data_map
    except Exception as e:
        logging.error(f"[ERROR] Exception during zip extraction: {e}")
        return xml_data_map

    # XML parsing
    if extracted_xml and os.path.exists(extracted_xml):
        logging.debug("[DEBUG] XML parsing...")
        try:
            tree = ET.parse(extracted_xml)
            root = tree.getroot()
            opps = root.findall(".//OpportunitySynopsisDetail_1_0", root.nsmap if hasattr(root, 'nsmap') else {})
            if not opps:
                opps = root.findall(".//{http://apply.grants.gov/system/OpportunityDetail-V1.0}OpportunitySynopsisDetail_1_0")

            logging.debug(f"[DEBUG] <OpportunitySynopsisDetail_1_0> {len(opps)} found")

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

            logging.debug(f"[DEBUG] XML parsing complete. dict size = {len(xml_data_map)}")
        except ET.ParseError as e:
            logging.error(f"[ERROR] XML syntax error: {e}")
    else:
        logging.info("[INFO] XML file does not exist, skipping parsing.")

    return xml_data_map


########################################
# 4) Merge
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

    logging.info(f"[Result] Final merged_data count: {len(merged_list)}")
    return merged_list


########################################
# MAIN
########################################
def main():
    # 1) search2
    all_grants_search = fetch_all_grants_from_search2()

    # 2) fetchOpportunity (parallel)
    all_grants_details = fetch_details_for_grants(all_grants_search, max_workers=10)

    # 3) xml-extract -> zip -> xml parse
    xml_data_map = download_and_parse_xml_dump()

    # 4) Merge
    merged_data = merge_data(all_grants_details, xml_data_map)

    # 5) JSON
    try:
        with open(OUTPUT_JSON_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)
        logging.info(f"\n--- '{OUTPUT_JSON_FILENAME}' file saved successfully ---")
    except IOError as e:
        logging.error(f"[ERROR] JSON save error: {e}")

    logging.info("\n--- Full process completed ---")


if __name__ == "__main__":
    main()

# (Example cron for automatic execution daily at 2 AM - Linux environment)
# $ crontab -e
# 0 2 * * * /usr/bin/python /path/to/this_script.py >> /path/to/logfile.log 2>&1
#
# This will automatically run the script every day at 2 AM.

