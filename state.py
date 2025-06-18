# state.py
from typing import TypedDict, List

class TrendAgentState(TypedDict):
    keyword: str
    search_results: List[dict]
    summary: str
    categories: List[str]
    blog_post: str