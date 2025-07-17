from langchain_core.prompts import ChatPromptTemplate
from prompts import CREATOR_AGENT_PROMPT

def create_creator_agent(llm):
    prompt = ChatPromptTemplate.from_template(CREATOR_AGENT_PROMPT)
    return prompt | llm

def creator_node(state, agent):
    # 상태(state)에서 모든 재료를 가져옴
    summary = state.get('summary')
    categories = state.get('categories')
    trend_data = state.get('trend_data')
    research_results = state.get('research_results', {}) # Researcher가 저장한 정보

    # 데이터 유효성 검사
    if not all([summary, categories, trend_data]):
        raise ValueError("Creator 노드 실행에 필요한 데이터가 부족합니다.")

    keyword = trend_data.get('keyword', '')
    
    # Researcher가 찾아준 정보를 바탕으로 뉴스 리스트와 이미지 URL 구성
    news_list = research_results.get('news', [])
    image_url = research_results.get('image_url', "")

    formatted_news_list = ""
    if news_list and isinstance(news_list, list):
        for item in news_list:
            title = item.get("title", "제목 없음")
            # 일반 검색 결과와 뉴스 검색 결과의 URL 키('link', 'url')를 모두 고려
            url = item.get("link") or item.get("url", "#")
            formatted_news_list += f"- {title} ({url})\n"
            
    # AI 에이전트에게 최종 정보 전달
    final_payload = {
        "keyword": keyword,
        "summary": summary,
        "categories": str(categories),
        "news": formatted_news_list,
        "image_url": image_url
    }
    
    result = agent.invoke(final_payload)
    
    # AI가 생성한 콘텐츠를 최종 가공
    raw_content = getattr(result, "content", "") or ""
    
    # 만약 결과가 예상치 못하게 리스트로 왔을 경우를 대비하여 join 처리
    if isinstance(raw_content, list):
        # 이미지 태그가 깨지지 않도록 단순 join
        blog_post_content = "".join(str(item) for item in raw_content)
    else:
        blog_post_content = str(raw_content)
    
    # 후처리: 불필요한 앞뒤 공백 및 줄바꿈 제거
    blog_post_content = blog_post_content.strip()

    # 최종 결과 반환
    return {"blog_post": blog_post_content}