from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from app.database.models import OccasionStatus


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# Recipient Schemas
class RecipientBase(BaseModel):
    name: str
    relationship: Optional[str] = None
    age_band: Optional[str] = None
    interests: List[str] = []
    constraints: List[str] = []
    notes: Optional[str] = None


class RecipientCreate(RecipientBase):
    pass


class RecipientUpdate(BaseModel):
    name: Optional[str] = None
    relationship: Optional[str] = None
    age_band: Optional[str] = None
    interests: Optional[List[str]] = None
    constraints: Optional[List[str]] = None
    notes: Optional[str] = None


class RecipientResponse(RecipientBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Occasion Schemas
class OccasionBase(BaseModel):
    name: str
    occasion_type: Optional[str] = None
    date: Optional[date] = None
    budget_range: Optional[str] = None
    status: OccasionStatus = OccasionStatus.IDEA_NEEDED


class OccasionCreate(OccasionBase):
    recipient_id: UUID


class OccasionUpdate(BaseModel):
    name: Optional[str] = None
    occasion_type: Optional[str] = None
    date: Optional[date] = None
    budget_range: Optional[str] = None
    status: Optional[OccasionStatus] = None


class OccasionResponse(OccasionBase):
    id: UUID
    user_id: UUID
    recipient_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Gift Idea Schemas
class GiftIdeaBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: Optional[str] = None
    category: Optional[str] = None
    url: Optional[str] = None
    is_shortlisted: str = "false"


class GiftIdeaCreate(GiftIdeaBase):
    occasion_id: UUID


class GiftIdeaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[str] = None
    category: Optional[str] = None
    url: Optional[str] = None
    is_shortlisted: Optional[str] = None


class GiftIdeaResponse(GiftIdeaBase):
    id: UUID
    occasion_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# Conversation Schemas
class ConversationResponse(BaseModel):
    id: UUID
    user_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# Message Schemas
class MessageBase(BaseModel):
    role: str
    content: str
    metadata: Optional[str] = None


class MessageCreate(MessageBase):
    conversation_id: UUID


class MessageResponse(MessageBase):
    id: UUID
    conversation_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# Chat Schemas
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    metadata: Optional[dict] = None


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[UUID] = None


class ChatResponse(BaseModel):
    conversation_id: UUID
    message: ChatMessage
    state: Optional[dict] = None  # LangGraph state snapshot

