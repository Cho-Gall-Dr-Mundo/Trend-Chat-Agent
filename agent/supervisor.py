from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from pydantic.v1 import BaseModel, Field
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from .state import AgentState
from config import LLM
from tools import scrape_web_page
from prompts import SUPERVISOR_PROMPT, SUMMARIZER_AGENT_PROMPT, CATEGORIZER_AGENT_PROMPT, CREATOR_AGENT_PROMPT

class SupervisorOutput(BaseModel):
    next: str = Field(description="다음으로 호출할 전문가의 이름. 사용 가능한 전문가 목록 또는 'FINISH' 중 하나여야 합니다.")

def create_worker_agent(role: str, tools: list = None):
    prompt = ChatPromptTemplate.from_messages([("system", role), ("placeholder", "{messages}")])
    if tools:
        return prompt | LLM.bind_tools(tools)
    # tools=None인 경우 function-calling 끄고 일반 LLM 대화로
    return prompt | LLM

members = ["Summarizer", "Categorizer", "Creator"]
supervisor_agent = (
    ChatPromptTemplate.from_messages([
        ("system", SUPERVISOR_PROMPT.format(members=", ".join(members))),
        ("placeholder", "{messages}")
    ])
    | LLM
)

summarizer_agent = create_worker_agent(SUMMARIZER_AGENT_PROMPT, [scrape_web_page])
categorizer_agent = create_worker_agent(CATEGORIZER_AGENT_PROMPT, [])
creator_agent = create_worker_agent(CREATOR_AGENT_PROMPT, [])

def agent_node(state: AgentState, agent, name: str):
    print(f"\n--- 전문가 호출: {name} ---")
    result = agent.invoke(state)
    if not hasattr(result, 'additional_kwargs'):
        result.additional_kwargs = {}
    result.additional_kwargs['agent_name'] = name
    print(result)
    # 항상 누적할 필요 없음, 최근 메시지만
    return {"messages": [result]}

def supervisor_node(state: AgentState):
    print("\n--- 감독자(Supervisor) 판단 중... ---")
    system_message = SystemMessage(
        content=SUPERVISOR_PROMPT.format(members=", ".join(["Summarizer", "Categorizer", "Creator"]))
    )

    trend_data = state.get("trend_data", {})
    trend_context = (
        f"키워드: {trend_data.get('keyword', '')}\n"
        f"검색량(approxTraffic): {trend_data.get('approxTraffic', 0)}\n"
        f"상태: {trend_data.get('status', '')}\n"
        f"시간: {trend_data.get('time', '')}\n"
        f"관련 뉴스: {[news['title'] for news in trend_data.get('news',[])]}\n"
    )
    context_message = HumanMessage(content=trend_context)

    # 마지막 에이전트와 결과를 추출
    last_agent_name = None
    last_agent_content = ""
    for msg in reversed(state['messages']):
        if hasattr(msg, "additional_kwargs") and msg.additional_kwargs.get("agent_name"):
            last_agent_name = msg.additional_kwargs.get("agent_name")
            last_agent_content = getattr(msg, "content", "")
            break

    # 프롬프트에 명시적으로 이전 단계/결과 전달
    if last_agent_name:
        last_agent_summary = (
            f"[직전 실행 전문가] {last_agent_name}\n"
            f"[직전 결과]\n{last_agent_content}\n"
        )
        last_agent_message = HumanMessage(content=last_agent_summary)
        messages = [system_message, context_message, last_agent_message]
    else:
        messages = [system_message, context_message]

    for m in messages:
        print("== supervisor 전달 메시지 (최종)==", m)

    response = LLM.invoke(messages)
    result = (response.content or "").strip()
    print("-> 감독자 결정:", repr(result))
    if result not in {"Summarizer", "Categorizer", "Creator", "FINISH"}:
        print("LLM이 예상값을 반환하지 않음. fallback: Summarizer")
        result = "Summarizer"
    return {"next": result}
tool_node = ToolNode([scrape_web_page])

workflow = StateGraph(AgentState)
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("Summarizer", lambda state: agent_node(state, summarizer_agent, "Summarizer"))
workflow.add_node("Categorizer", lambda state: agent_node(state, categorizer_agent, "Categorizer"))
workflow.add_node("Creator", lambda state: agent_node(state, creator_agent, "Creator"))
workflow.add_node("tool_node", tool_node)

workflow.set_entry_point("supervisor")
workflow.add_conditional_edges(
    "supervisor",
    lambda state: state["next"],
    {name: name for name in members} | {"FINISH": END}
)

def after_worker(state: AgentState):
    last_message = state['messages'][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tool_node"
    else:
        return "supervisor"

workflow.add_conditional_edges("Summarizer", after_worker)
workflow.add_edge("tool_node", "Summarizer")
workflow.add_edge("Categorizer", "supervisor")
workflow.add_edge("Creator", "supervisor")

app = workflow.compile()