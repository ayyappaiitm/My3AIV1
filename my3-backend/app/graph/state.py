from typing import TypedDict, List, Optional, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class My3State(TypedDict):
    """State for My3 LangGraph workflow."""
    messages: Annotated[List[BaseMessage], add_messages]
    user_id: Optional[str]
    recipient_id: Optional[str]
    occasion_id: Optional[str]
    recipient_name: Optional[str]
    occasion_type: Optional[str]
    budget_range: Optional[str]
    gift_ideas: List[dict]
    current_step: str  # "greeting", "profiling", "recommending", "confirming", "done"
    needs_confirmation: bool
    confirmation_data: Optional[dict]

