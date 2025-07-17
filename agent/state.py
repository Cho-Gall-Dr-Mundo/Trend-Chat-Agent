from typing import TypedDict, Dict, List, Optional
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: List[BaseMessage]
    trend_data: dict
    scraped_contents: Dict[str, str]
    summary: Optional[str]
    categories: Optional[List[str]]
    research_results: Optional[Dict]
    blog_post: Optional[str]