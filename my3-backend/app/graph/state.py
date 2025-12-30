from typing import TypedDict, List, Optional, Literal, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """Agent state for My3 LangGraph workflow."""
    # Conversation
    messages: Annotated[List[BaseMessage], add_messages]
    user_id: str
    conversation_id: Optional[str]
    
    # Context (loaded from DB)
    user_recipients: List[dict]
    user_occasions: List[dict]
    
    # Current processing
    current_intent: Optional[Literal["gift_search", "add_recipient", "update_info", "casual_chat", "unclear"]]
    detected_person: Optional[dict]  # {name, relationship, interests, age_band}
    recipient_exists: Optional[bool]
    matched_recipient_id: Optional[str]
    ambiguous_recipients: Optional[List[dict]]  # List of recipients when relationship is ambiguous
    
    # Actions to execute
    pending_actions: List[dict]
    requires_confirmation: bool
    confirmation_prompt: Optional[str]
    
    # Response
    ai_response: Optional[str]
    gift_ideas: Optional[List[dict]]
    error: Optional[str]

