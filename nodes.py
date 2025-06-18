from langchain_core.messages import HumanMessage
from state import TrendAgentState
import prompts
from config import LLM, TAVILY_CLIENT

# 노드 1: 트렌드 리서처
def execute_researcher(state: TrendAgentState):
    print("--- 🔍 트렌드 리서처 실행 ---")
    keyword = state['keyword']
    response = TAVILY_CLIENT.search(query=f"'{keyword}'가 왜 트렌드인가?", search_depth="advanced", max_results=5)
    state['search_results'] = response['results']
    return state

# 노드 2: 트렌드 분석가
def execute_analyst(state: TrendAgentState):
    print("--- 📊 트렌드 분석가 실행 ---")
    search_results_text = "\n\n".join([f"URL: {res['url']}\nContent: {res['content']}" for res in state['search_results']])
    
    prompt = prompts.ANALYST_PROMPT_TEMPLATE.format(
        keyword=state['keyword'],
        search_results_text=search_results_text
    )
    
    response = LLM.invoke([HumanMessage(content=prompt)])
    state['summary'] = response.content
    return state

# 노드 3: 카테고리 분류기
def execute_classifier(state: TrendAgentState):
    print("--- 🏷️ 카테고리 분류기 실행 ---")
    prompt = prompts.CLASSIFIER_PROMPT_TEMPLATE.format(summary=state['summary'])
    
    response = LLM.invoke([HumanMessage(content=prompt)])
    try:
        # LLM이 생성한 문자열 리스트를 실제 Python 리스트로 안전하게 변환
        state['categories'] = eval(response.content)
    except:
        state['categories'] = ["기타"] # 변환 실패 시 기본값
    return state

# 노드 4: 콘텐츠 생성가
def execute_creator(state: TrendAgentState):
    print("--- ✍️ 콘텐츠 생성가 실행 ---")
    categories_str = ", ".join(state['categories'])
    
    # [추가] 리서처가 수집한 원본 데이터를 프롬프트에 넣기 좋게 가공합니다.
    search_results_str = "\n\n".join(
        [f"출처 URL: {res['url']}\n내용: {res['content']}" for res in state['search_results']]
    )

    # [수정] format에 search_results_str를 추가합니다.
    prompt = prompts.CREATOR_PROMPT_TEMPLATE.format(
        keyword=state['keyword'],
        summary=state['summary'],
        categories_str=categories_str,
        search_results_str=search_results_str # 새로 추가된 변수
    )
    
    response = LLM.invoke([HumanMessage(content=prompt)])
    state['blog_post'] = response.content
    return state