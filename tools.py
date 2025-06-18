import trafilatura
from langchain.tools import tool

@tool
def scrape_web_page(url: str) -> str:
    """
    주어진 URL의 웹 페이지에 접속하여, 뉴스 기사의 핵심 본문 텍스트를 추출합니다.
    이 도구는 URL을 분석하여 광고나 댓글 등 불필요한 부분을 최대한 제거하고
    본문 내용만 반환하는 데 특화되어 있습니다.
    분석할 뉴스 기사의 내용을 확인하려면 반드시 이 도구를 사용해야 합니다.
    """
    print(f"  [도구 실행] 스크레이핑 시작: {url}")
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            return f"오류: URL에 접속할 수 없거나 내용이 없습니다."
            
        # 댓글, 광고 등을 제외하고 순수 본문만 추출
        content = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
        
        if content is None:
            return f"오류: 해당 URL에서 유의미한 본문을 추출하지 못했습니다."

        print(f"  -> 스크레이핑 성공, 텍스트 길이: {len(content)}")
        # LLM 토큰 제한을 고려하여 최대 4000자로 제한
        return content[:4000]
    except Exception as e:
        return f"오류: 스크레이핑 중 예외 발생 - {str(e)}"