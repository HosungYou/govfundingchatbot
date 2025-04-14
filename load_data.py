import os
import json
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

# 환경 변수 로드
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY", "")
qdrant_url = os.getenv("QDRANT_URL", "")
qdrant_api_key = os.getenv("QDRANT_API_KEY", "")

# Extract URLs from HTML content
def extract_urls_from_html(html_content):
    """Extracts all URLs from HTML content, both from href attributes and plain text."""
    urls = []
    
    # Extract URLs from href attributes if HTML tags are present
    if '<a href=' in html_content:
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            for a_tag in soup.find_all('a', href=True):
                urls.append(a_tag['href'])
        except Exception as e:
            print(f"Error parsing HTML: {e}")
    
    # Also look for URLs in the text using regex
    url_pattern = re.compile(r'https?://(?:www\.)?(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^"\s<>]*)?')
    text_urls = url_pattern.findall(html_content)
    
    # Combine both lists and remove duplicates
    all_urls = list(set(urls + text_urls))
    
    # Filter to only include NSF URLs
    nsf_urls = [url for url in all_urls if 'nsf.gov' in url]
    
    return nsf_urls

# Find best URL for a funding opportunity
def find_best_url(opp_num, description, xml_detail=None):
    """Determines the best URL for a funding opportunity based on multiple sources."""
    urls = extract_urls_from_html(description)
    
    # If URLs found in description, prioritize them
    if urls:
        # If multiple URLs, try to find the most relevant one
        if len(urls) > 1:
            # First try: URL containing the opportunity number
            for url in urls:
                if opp_num in url:
                    return url
            
            # Second try: URL with pubs pattern which is common for NSF solicitations
            for url in urls:
                if '/pubs/' in url:
                    return url
        
        # If only one URL or no better match found, return the first one
        return urls[0]
    
    # If no URLs in description, try to construct one based on patterns
    
    # Pattern 1: Check if opportunity number follows NSF publication pattern (YY-NNN)
    if opp_num and re.match(r'\d{2}-\d{3}', opp_num):
        year_part = opp_num.split('-')[0]
        full_year = f"20{year_part}"  # Assuming 20xx year
        num_part = opp_num.split('-')[1]
        
        # Common NSF publication URL pattern
        pub_url = f"https://www.nsf.gov/pubs/{full_year}/nsf{year_part}{num_part}/nsf{year_part}{num_part}.htm"
        return pub_url
    
    # Pattern 2: Check XML data for links
    if xml_detail and isinstance(xml_detail, dict):
        # Look for any URLs in XML data
        xml_description = xml_detail.get("description_xml", "")
        if xml_description:
            xml_urls = extract_urls_from_html(xml_description)
            if xml_urls:
                return xml_urls[0]
        
        # Look for detected links from XML
        detected_links = xml_detail.get("detected_links_xml", [])
        if detected_links and len(detected_links) > 0:
            return detected_links[0]
    
    # Pattern 3: Use the opportunity ID if available (sometimes different from number)
    opportunity_id = None
    if xml_detail and isinstance(xml_detail, dict):
        opportunity_id = xml_detail.get("opportunityId_xml")
    
    if opportunity_id:
        return f"https://www.nsf.gov/funding/pgm_summ.jsp?pims_id={opportunity_id}"
    
    # Fallback to basic pattern with opportunity number
    return f"https://www.nsf.gov/funding/pgm_summ.jsp?pims_id={opp_num}" if opp_num else ""

# 데이터 로드
def load_json_data(file_path="merged_data.json"):
    """merged_data.json 파일에서 데이터를 로드합니다."""
    print(f"Loading data from {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Successfully loaded {len(data)} records")
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return []

# 문서 생성
def create_documents(data):
    """Creates searchable Document objects from JSON data."""
    documents = []
    
    for record in data:
        # Extract core data from fetch_detail
        fetch_detail = record.get("fetch_detail", {})
        opp_num = fetch_detail.get("opportunityNumber", "")
        title = fetch_detail.get("title", "")
        agency = fetch_detail.get("agencyName", "")
        
        # Extract detailed description
        synopsis = fetch_detail.get("synopsis", {})
        synopsis_desc = synopsis.get("synopsisDesc", "")
        
        # Extract additional data from xml_detail
        xml_detail = record.get("xml_detail", {})
        award_ceiling = xml_detail.get("award_ceiling_xml", "") if xml_detail else ""
        close_date = xml_detail.get("close_date_xml", "") if xml_detail else ""
        
        # Find the best URL for this opportunity - pass XML detail too
        best_url = find_best_url(opp_num, synopsis_desc, xml_detail)
        
        # Construct document text (in searchable format)
        text_content = f"""
        Funding Opportunity: {title}
        Opportunity Number: {opp_num}
        Agency: {agency}
        Award Ceiling: {award_ceiling}
        Close Date: {close_date}
        
        Description:
        {synopsis_desc}
        """
        
        # Set metadata (fields to use for search)
        metadata = {
            "title": title,
            "opportunity_number": opp_num,
            "agency": agency,
            "award_ceiling": award_ceiling,
            "close_date": close_date,
            "source": "NSF Funding",
            "url": best_url
        }
        
        # Create Document object
        doc = Document(
            page_content=text_content,
            metadata=metadata
        )
        documents.append(doc)
    
    print(f"Created {len(documents)} searchable documents")
    return documents

# 벡터 DB에 데이터 저장
def store_in_vectordb(documents, collection_name="my-grants-collection"):
    """문서들을 Qdrant 벡터 DB에 저장합니다."""
    print(f"Storing {len(documents)} documents in Qdrant collection: {collection_name}")
    
    # OpenAI 임베딩 모델 초기화
    embeddings = OpenAIEmbeddings(
        openai_api_key=openai_key,
        model="text-embedding-ada-002"
    )
    
    # 벡터 저장소에 문서 저장
    # from_documents는 새 컬렉션을 생성하거나 기존 컬렉션을 대체합니다
    vectorstore = QdrantVectorStore.from_documents(
        documents=documents,
        embedding=embeddings,
        url=qdrant_url,
        api_key=qdrant_api_key,
        collection_name=collection_name,
        force_recreate=True  # 기존 컬렉션이 있다면 다시 생성
    )
    
    print(f"Successfully stored data in Qdrant collection: {collection_name}")
    return vectorstore

def main():
    """메인 실행 함수"""
    print("Starting data loading process...")
    
    # 1. JSON 데이터 로드
    data = load_json_data()
    if not data:
        print("No data to process. Exiting.")
        return
    
    # 2. 문서 생성
    documents = create_documents(data)
    if not documents:
        print("No documents created. Exiting.")
        return
    
    # 3. 벡터 DB에 저장
    vectorstore = store_in_vectordb(documents)
    print("Data loading process complete!")

if __name__ == "__main__":
    main()