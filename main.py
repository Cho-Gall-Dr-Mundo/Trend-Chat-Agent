from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage
from dummy_data import dummy_trend_data
from agent import app

def main():
    keyword = dummy_trend_data["keyword"]
    news_articles = dummy_trend_data["news"]
    
    # Summarizer에게 필요한 모든 정보를 담은 초기 메시지를 생성
    initial_content = (
        f"키워드 '{keyword}'에 대한 트렌드 분석을 시작합니다.\n\n"
        f"분석할 뉴스 URL 목록: {[news['url'] for news in news_articles]}"
    )
    
    initial_state = {
        "messages": [
            HumanMessage(content=initial_content)
        ],
        "trend_data": dummy_trend_data,
        "scraped_contents": {},
        "summary": None,
        "categories": None,
        "blog_post": None
    }

    final_state =  initial_state.copy()
    
    # 전체 토큰 사용량을 추적할 딕셔너리를 생성
    total_token_usage = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
    }

    for event in app.stream(initial_state, {"recursion_limit": 15}):
        for node_name, event_data in event.items():
            # 각 이벤트 데이터에서 토큰 사용량 정보를 찾음
            token_usage = None
            # Summarizer 노드의 경우, 'messages' 리스트의 마지막 AIMessage에서 정보를 찾음
            if event_data and (messages := event_data.get("messages")):
                last_message = messages[-1]
                if hasattr(last_message, "response_metadata"):
                    token_usage = last_message.response_metadata.get("token_usage")
            
            # Creator/Categorizer 노드의 경우, 반환값 자체에 포함될 수 있음
            elif event_data and (metadata := event_data.get("response_metadata")):
                token_usage = metadata.get("token_usage")


            # 토큰 정보를 찾았다면 로그를 출력하고 누적
            if token_usage:
                total_token_usage["prompt_tokens"] += token_usage.get("prompt_tokens", 0)
                total_token_usage["completion_tokens"] += token_usage.get("completion_tokens", 0)
                total_token_usage["total_tokens"] += token_usage.get("total_tokens", 0)
            
            if event_data:
                final_state.update(event_data)

    # 최종 결과물 출력
    print("\n\n" + "="*60)
    print("--- 최종 결과물 ---")
    print("="*60)
    print(f"키워드: {final_state.get('trend_data', {}).get('keyword', '')}")
    print(f"\n[생성된 요약문]\n{final_state.get('summary','')}")
    print(f"\n[분류된 카테고리]\n{final_state.get('categories','')}")
    print(f"\n[생성된 블로그 포스트]\n{final_state.get('blog_post','')}")
    
    # 최종 누적된 토큰 사용량을 출력
    print("\n" + "="*60)
    print("--- 총 토큰 사용량 ---")
    print(f"- 입력(Prompt) 토큰: {total_token_usage['prompt_tokens']}")
    print(f"- 출력(Completion) 토큰: {total_token_usage['completion_tokens']}")
    print(f"- 전체 토큰: {total_token_usage['total_tokens']}")
    print("="*60)

if __name__ == "__main__":
    main()