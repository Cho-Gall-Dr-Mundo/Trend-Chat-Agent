# researcher.py

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
# serper_image_search는 이제 사용하지 않으므로 import에서 제거
from tools import scrape_web_page, serper_news_search

def create_researcher_agent(llm):
    # 이 부분은 변경 없습니다.
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 주어진 URL 목록을 보고 scrape_web_page 도구를 호출하는 역할만 수행합니다. 만약 URL 목록이 없다면 아무것도 하지 않습니다."),
        ("placeholder", "{messages}")
    ])
    return prompt | llm.bind_tools([scrape_web_page])

def researcher_node(state, agent):
    """
    1. trend_data에 유효한 뉴스 URL이 있는지 확인합니다.
    2. URL이 충분하면, 해당 URL과 썸네일을 사용합니다.
    3. URL이 없거나 부족하면, trend_data의 키워드를 사용하여 serper_news_search로 정보를 보강합니다.
    4. 확보된 URL 목록으로 스크레이핑을 진행하고, 수집된 정보는 state에 저장합니다.
    """
    trend_data = state.get('trend_data', {})
    keyword = trend_data.get('keyword')
    news_from_trend = trend_data.get('news', [])

    # 반환할 최종 검색 결과 초기화
    final_news_results = []
    final_image_url = ""

    # 스크레이핑할 URL 목록과 이미지 URL 확보
    urls_to_scrape = [item.get('url') for item in news_from_trend if item.get('url')]
    if news_from_trend and news_from_trend[0].get('thumbnail'):
        final_image_url = news_from_trend[0].get('thumbnail')

    # 초기 URL 목록이 부실한 경우, Serper로 보강
    if not urls_to_scrape and keyword:
        print(f"  -> 초기 데이터 부족. 키워드 '{keyword}'로 Serper 뉴스 검색 실행...")
        news_results_from_serper = serper_news_search.run(keyword)
        
        print("--- Serper API Raw Response ---")
        import json
        print(json.dumps(news_results_from_serper, indent=2, ensure_ascii=False))
        print("-----------------------------")

        if news_results_from_serper:
            final_news_results = news_results_from_serper[:3]
            urls_to_scrape = [item.get('link') for item in final_news_results if item.get('link')]
            print(f"  -> Serper에서 {len(urls_to_scrape)}개의 뉴스 URL 확보.")
            # Serper 결과의 첫 번째 뉴스에 썸네일이 있다면 이미지 URL로 사용
            if final_news_results and final_news_results[0].get('thumbnail'):
                final_image_url = final_news_results[0].get('thumbnail')
    else:
        # 초기 데이터가 정상이었던 경우, 그 데이터를 최종 결과로 사용
        final_news_results = news_from_trend

    # 최종적으로 스크레이핑할 URL이 없는 경우
    if not urls_to_scrape:
        print("  -> 수집할 유효한 URL이 없어 스크레이핑을 건너뜁니다.")
        pass

    # 확보된 URL들로 스크레이핑 도구 호출 메시지 생성
    tool_calls = []
    for url in urls_to_scrape:
        tool_calls.append({
            "name": "scrape_web_page",
            "args": {"url": url},
            "id": f"tool_call_{url.replace('://', '_').replace('/', '_')}"
        })

    ai_msg = AIMessage(content="", tool_calls=tool_calls)

    return {
        "messages": [state['messages'][0], ai_msg],
        "research_results": {
            "news": final_news_results,
            "image_url": final_image_url
        }
    }