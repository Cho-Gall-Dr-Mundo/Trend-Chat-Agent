from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import ToolMessage
from prompts import SUMMARIZER_PROMPT_TEMPLATE

def create_summarizer_agent(llm):
    prompt = ChatPromptTemplate.from_template(SUMMARIZER_PROMPT_TEMPLATE)
    return prompt | llm

def summarizer_node(state, agent):
    # tool_node의 실행 결과인 ToolMessage들만 필터링
    tool_messages = [m for m in state['messages'] if isinstance(m, ToolMessage)]
    
    # 각 ToolMessage의 내용을 번호를 매겨 하나의 문자열로 합침
    # 이렇게 하면 LLM이 각 기사를 구분하기 용이해짐
    contents_str = "\n\n---\n\n".join(
        f"뉴스 {i+1}:\n{msg.content}" for i, msg in enumerate(tool_messages)
    )
    
    result = agent.invoke({"contents": contents_str})
    summary = result.content
    
    return {"summary": summary}