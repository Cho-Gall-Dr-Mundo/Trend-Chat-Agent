import os
import trafilatura
from langchain.tools import tool
import requests

@tool
def scrape_web_page(url: str) -> str:
    """
    주어진 URL의 웹 페이지에 접속하여, 뉴스 기사의 핵심 본문 텍스트를 추출합니다.
    광고나 댓글 등 불필요한 부분은 최대한 제거하고, 본문만 반환합니다.
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            return f"오류: {url} 페이지 다운로드에 실패했습니다."

        content = trafilatura.extract(downloaded) 
        
        # content가 None일 경우, 빈 문자열 대신 명시적인 메시지를 반환
        if content is None:
            return f"오류: {url} 페이지에서 본문을 추출하지 못했습니다."

        # 너무 짧은 경우도 실패로 간주
        if len(content.strip()) < 30:
            return f"오류: {url} 페이지의 본문이 너무 짧아 유의미한 내용을 찾지 못했습니다."

        # 텍스트 길이 제한
        limited_content = content[:1500]
        return limited_content

    except Exception as e:
        return f"오류: {url} 스크레이핑 중 예외가 발생했습니다 - {e}"
    
@tool
def serper_news_search(keyword: str) -> list:
    """
    주어진 키워드로 Serper.dev API를 통해 '일반 웹 검색'을 수행합니다.
    (기존 이름은 유지하지만, 실제로는 일반 웹 검색을 수행하여 더 포괄적인 결과를 가져옵니다.)
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return [{"error": "SERPER_API_KEY 환경변수가 설정되어 있지 않습니다."}]
    
    url = "https://google.serper.dev/search"
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}

    # 'tbm' 파라미터를 제거하여 일반 웹 검색을 수행
    payload = {
        "q": keyword,
        "gl": "kr",  
        "hl": "ko"   
    }
    
    try:
        print(f"  -> Serper: '{keyword}' 일반 웹 검색 실행...")
        response = requests.post(url, headers=headers, json=payload, timeout=8)
        response.raise_for_status()
        data = response.json()
        
        results = data.get("organic", [])
        
        if results:
            print(f"  -> Serper: 일반 웹 검색 성공. {len(results)}개 결과 반환.")
        else:
            print("  -> Serper: 일반 웹 검색 결과 없음.")
            
        return results

    except Exception as e:
        print(f"[serper_news_search Error] Serper 검색 실패: {e}")
        return [{"error": f"Serper 검색 실패: {str(e)}"}]