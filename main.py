from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, END
from state import TrendAgentState
from nodes import (
    execute_researcher,
    execute_analyst,
    execute_classifier,
    execute_creator
)

def main():
    # 그래프 워크플로우 정의
    workflow = StateGraph(TrendAgentState)

    # 노드 추가: 각 노드 이름과 실행할 함수를 연결
    workflow.add_node("researcher", execute_researcher)
    workflow.add_node("analyst", execute_analyst)
    workflow.add_node("classifier", execute_classifier)
    workflow.add_node("creator", execute_creator)

    # 엣지(연결) 설정: 노드 간의 실행 순서를 정의
    workflow.set_entry_point("researcher")
    workflow.add_edge("researcher", "analyst")
    workflow.add_edge("analyst", "classifier")
    workflow.add_edge("classifier", "creator")
    workflow.add_edge("creator", END) # 'creator' 노드 이후 워크플로우 종료

    # 그래프 컴파일
    app = workflow.compile()

    # --- 실행 ---
    # 분석하고 싶은 트렌드 키워드 입력
    inputs = {"keyword": "jdb엔터테인먼트 대표"}
    final_state = app.invoke(inputs)

    # --- 최종 결과물 출력 ---
    print("\n\n" + "="*50)
    print("--- 최종 결과물 ---")
    print("="*50)
    print(f"키워드: {final_state['keyword']}")
    print(f"카테고리: {final_state['categories']}")
    print(f"\n[요약]\n{final_state['summary']}")
    print("\n" + "-"*50)
    print(f"--- 생성된 블로그 포스트 ---")
    print("-"*50)
    print(final_state['blog_post'])

if __name__ == "__main__":
    main()