from langchain_core.prompts import ChatPromptTemplate
from prompts import CREATOR_AGENT_PROMPT

def create_creator_agent(llm):
    prompt = ChatPromptTemplate.from_template(CREATOR_AGENT_PROMPT)
    return prompt | llm

def creator_node(state, agent):
    summary = state.get('summary')
    categories = state.get('categories')
    trend_data = state.get('trend_data')

    if not (summary and categories and trend_data):
        raise Exception("블로그 포스트 생성을 위한 데이터가 부족합니다.")

    # 만약 뉴스나 썸네일이 없을 경우를 대비하여 기본값을 설정
    image_url = ""
    if trend_data.get('news') and len(trend_data['news']) > 0:
        image_url = trend_data['news'][0].get('thumbnail', "")

    # agent.invoke에 image_url을 추가로 전달
    result = agent.invoke({
        "keyword": trend_data['keyword'],
        "summary": summary,
        "categories": str(categories),
        "image_url": image_url
    })
    
    blog_post_content = result.content or ""
    
    return {"blog_post": blog_post_content}