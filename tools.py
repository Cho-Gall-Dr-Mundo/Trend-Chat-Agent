import trafilatura
from langchain.tools import tool

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

        # include_comments=False 등은 기본값이므로 생략 가능
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