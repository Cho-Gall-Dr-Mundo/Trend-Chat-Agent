from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage
from dummy_data import dummy_trend_data
from agent import app # agent 패키지에서 최종 컴파일된 그래프를 가져옴

def main(): 
    # dummy_trend_data 활용해서 명확하게 메시지 만듦
    keyword = dummy_trend_data["keyword"]
    news_articles = dummy_trend_data["news"]
    approx_traffic = dummy_trend_data["approxTraffic"]

    # 초기 state (trend_data까지 명시)
    initial_state = {
        "messages": [
            HumanMessage(
                content=(
                    f"# 분석 요청\n"
                    f"- 키워드: {keyword}\n"
                    f"- 검색량: {approx_traffic}\n"
                    f"- 관련 뉴스: {[news['title'] for news in news_articles]}\n"
                    f"- 관련 뉴스 URL: {[news['url'] for news in news_articles]}\n"
                )
            )
        ],
        "next": None,
        "trend_data": dummy_trend_data,
    }
    
    print("--- MCP 워크플로우 실행 시작 ---")
    final_state = None

    # stream()을 사용하여 각 단계의 결과를 실시간으로 확인
    for event in app.stream(initial_state, {"recursion_limit": 15}):
        final_state = event
        for key, value in event.items():
            print(f"--- [이벤트] 노드 '{key}' 실행 결과 ---")
            print("-" * 60)
    
    # 최종 결과물 출력
    print("\n\n" + "="*60)
    print("--- ✨ 최종 결과물 (Supervisor 아키텍처) ---")
    print("="*60)
    
    messages = final_state['supervisor']['messages']

    def get_response_by_agent_name(agent_name):
        for msg in reversed(messages):
            if hasattr(msg, "additional_kwargs") and msg.additional_kwargs.get('agent_name') == agent_name:
                return msg.content
        return "결과 없음"

    summary = get_response_by_agent_name("Summarizer")
    categories = get_response_by_agent_name("Categorizer")
    blog_post = get_response_by_agent_name("Creator")

    print(f"키워드: {keyword}")
    print(f"\n[생성된 요약문]\n{summary}")
    print(f"\n[분류된 카테고리]\n{categories}")
    print(f"\n[생성된 블로그 포스트]\n{blog_post}")

if __name__ == "__main__":
    main()
