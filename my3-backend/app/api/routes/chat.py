from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from langchain_core.messages import HumanMessage
from app.database.connection import get_db
from app.database.models import User, Conversation, Message
from app.database.schemas import ChatRequest, ChatResponse, ChatMessage
from app.api.dependencies import get_current_user
from app.graph.workflow import workflow_app
from app.graph.state import My3State

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Handle chat message and return AI response."""
    # Get or create conversation
    if request.conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user.id
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        conversation = Conversation(user_id=current_user.id)
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
    
    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    await db.commit()
    
    # Prepare state for LangGraph
    state: My3State = {
        "messages": [HumanMessage(content=request.message)],
        "user_id": str(current_user.id),
        "recipient_id": None,
        "occasion_id": None,
        "recipient_name": None,
        "occasion_type": None,
        "budget_range": None,
        "gift_ideas": [],
        "current_step": "greeting",
        "needs_confirmation": False,
        "confirmation_data": None
    }
    
    # Run workflow
    result = await workflow_app.ainvoke(state)
    
    # Get AI response
    ai_response = result["messages"][-1].content if result.get("messages") else "I'm here to help!"
    
    # Save AI message
    ai_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=ai_response
    )
    db.add(ai_message)
    await db.commit()
    
    return ChatResponse(
        conversation_id=conversation.id,
        message=ChatMessage(role="assistant", content=ai_response),
        state=result
    )


@router.post("/confirm")
async def confirm_action(
    conversation_id: UUID,
    action: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Confirm an action (e.g., add recipient, select gift)."""
    # This will be implemented to handle confirmations
    return {"status": "confirmed", "action": action}

