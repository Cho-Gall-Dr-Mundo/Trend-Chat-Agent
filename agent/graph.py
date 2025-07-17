from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from .state import AgentState
from tools import scrape_web_page, serper_news_search
from config import LLM_GROQ_70B, LLM_GEMINI_FLASH_1, LLM_GEMINI_FLASH_2, LLM_GEMINI_PRO
from agent.researcher import create_researcher_agent, researcher_node
from agent.summarizer import create_summarizer_agent, summarizer_node
from agent.categorizer import create_categorizer_agent, categorizer_node
from agent.creator import create_creator_agent, creator_node

# --- 실행 단위(Runnable) 생성 ---
# 역할에 맞는 최적의 모델을 할당
researcher_agent = create_researcher_agent(LLM_GROQ_70B) 
summarizer_agent = create_summarizer_agent(LLM_GEMINI_FLASH_2)
categorizer_agent = create_categorizer_agent(LLM_GEMINI_FLASH_1) 
creator_agent = create_creator_agent(LLM_GEMINI_PRO)     
tool_node = ToolNode([scrape_web_page, serper_news_search])

# --- 워크플로우 정의 ---
workflow = StateGraph(AgentState)

workflow.add_node("Researcher", lambda state: researcher_node(state, researcher_agent))
workflow.add_node("tool_node", tool_node)
workflow.add_node("Summarizer", lambda state: summarizer_node(state, summarizer_agent))
workflow.add_node("Categorizer", lambda state: categorizer_node(state, categorizer_agent))
workflow.add_node("Creator", lambda state: creator_node(state, creator_agent))

# --- 엣지(흐름) 정의 ---
workflow.set_entry_point("Researcher")

# Researcher가 도구를 호출하면 tool_node로 감
workflow.add_edge("Researcher", "tool_node")

# ToolNode는 기본적으로 입력 메시지에 자신의 결과를 '추가'
# 따라서 Summarizer는 이전 메시지(Human, AI)와 ToolMessage를 모두 받게 됨
workflow.add_edge("tool_node", "Summarizer")

# Summarizer 다음에는 Categorizer로 감
workflow.add_edge("Summarizer", "Categorizer")

# Categorizer 다음에는 트래픽을 확인하여 분기
def check_traffic(state):
    traffic = state.get("trend_data", {}).get("approxTraffic", 0)
    if traffic >= 2000:
        print("  -> 트래픽 2000 이상, Creator 실행")
        return "Creator"
    else:
        print("  -> 트래픽 2000 미만, 워크플로우 종료")
        return END

workflow.add_conditional_edges("Categorizer", check_traffic)

# Creator 다음에는 종료
workflow.add_edge("Creator", END)

app = workflow.compile()