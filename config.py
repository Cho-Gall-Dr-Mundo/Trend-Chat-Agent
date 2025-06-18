import os
from langchain_groq import ChatGroq
from tavily import TavilyClient

# --- 모델 및 도구 설정 ---
LLM = ChatGroq(model_name="llama3-70b-8192", temperature=0)
TAVILY_CLIENT = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))