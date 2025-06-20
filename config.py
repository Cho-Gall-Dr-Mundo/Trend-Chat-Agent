from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI 

# --- 모델 설정 ---
LLM_GROQ_8B = ChatGroq(model_name="llama3-8b-8192", temperature=0)

LLM_GROQ_70B = ChatGroq(model_name="llama3-70b-8192", temperature=0)

LLM_GEMINI_FLASH = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1)

# --- 도구 설정 ---