from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from agent import app

load_dotenv()

async def process_trend_data(trend_data: dict) -> dict:
    """하나의 트렌드 데이터를 받아 AI 에이전트 워크플로우를 실행하고 최종 상태를 반환합니다."""
    
    keyword = trend_data.get("keyword", "N/A")
    news_articles = trend_data.get("news", [])

    # Researcher에게 전달할 초기 메시지 구성
    initial_content = (
        f"'{keyword}' 트렌드 분석을 위해 다음 URL들의 내용을 수집해줘:\n"
        + "\n".join([f"- {news.get('url', '')}" for news in news_articles])
    )
    
    initial_state = {
        "messages": [
            HumanMessage(content=initial_content)
        ],
        "trend_data": trend_data,
        "summary": None,
        "categories": None,
        "blog_post": None
    }

    print("--- AI 에이전트 워크플로우 실행 시작 ---")
    final_state = initial_state.copy()
    
    # app.astream()을 사용하여 비동기적으로 워크플로우 실행
    async for event in app.astream(initial_state, {"recursion_limit": 15}):
        for node_name, event_data in event.items():
            print(f"--- [이벤트] 노드 '{node_name}' 실행 결과 ---")
            if event_data:
                final_state.update(event_data)
    
    summary_content = final_state.get('summary')
    blog_post_content = final_state.get('blog_post')
    
    # Kafka Producer로 보낼 최종 결과 객체를 구성하여 반환
    return {
        "keyword": keyword,
        "summary": summary_content or '', 
        "categories": final_state.get('categories',{}),
        "blog_post": blog_post_content or '', 
    }

if __name__ == "__main__":
    print()