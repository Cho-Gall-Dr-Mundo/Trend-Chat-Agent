from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from tools import scrape_web_page

# Researcher는 간단한 작업만 하므로 LLM이 굳이 필요 없을 수도 있지만,
# 여러 도구를 쓰거나 실패 시 재시도하는 등 복잡한 로직을 위해 LLM 기반으로 만듬
def create_researcher_agent(llm):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 주어진 URL 목록을 보고 scrape_web_page 도구를 호출하는 역할만 수행합니다."),
        ("placeholder", "{messages}")
    ])
    return prompt | llm.bind_tools([scrape_web_page])

def researcher_node(state, agent):
    # Researcher는 이전 대화가 필요 없으므로, state의 초기 메시지만 사용
    initial_message = state['messages'][0]
    
    result = agent.invoke({"messages": [initial_message]})
    
    ai_msg = AIMessage(
        content=result.content or "",
        tool_calls=getattr(result, 'tool_calls', []),
        response_metadata=getattr(result, 'response_metadata', {})
    )
    
    # tool_calls만 상태에 추가하여 tool_node로 전달
    return {"messages": [initial_message, ai_msg]}