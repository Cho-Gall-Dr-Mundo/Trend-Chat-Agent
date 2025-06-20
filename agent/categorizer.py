import ast
import re
from langchain_core.prompts import ChatPromptTemplate
from prompts import CATEGORIZER_AGENT_PROMPT

def create_categorizer_agent(llm):
    prompt = ChatPromptTemplate.from_template(CATEGORIZER_AGENT_PROMPT)
    return prompt | llm

def categorizer_node(state, agent):
    summary = state.get("summary")

    if not summary or not summary.strip():
        return {"categories": []}

    result = agent.invoke({"summary": summary})
    ai_msg_content = result.content or ""

    categories_list = []
    try:
        # 정규식으로 LLM의 응답에서 리스트 부분만 안전하게 추출
        match = re.search(r"\[.*?\]", ai_msg_content, re.DOTALL)
        if match:
            list_str = match.group(0)
            categories_list = ast.literal_eval(list_str)
            if not isinstance(categories_list, list):
                categories_list = []
    except (ValueError, SyntaxError) as e:
        categories_list = []

    if not categories_list:
        return {"categories": []}

    # messages 상태를 건드리지 않고, 생성된 categories만 반환하여 효율성 증대
    return {"categories": categories_list}