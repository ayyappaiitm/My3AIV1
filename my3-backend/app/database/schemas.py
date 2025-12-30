from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
import re
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


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Recipient Schemas
class RecipientBase(BaseModel):
    name: str
    relationship: Optional[str] = None
    age_band: Optional[str] = None
    interests: List[str] = []
    constraints: List[str] = []
    notes: Optional[str] = None
    is_core_contact: Optional[bool] = True
    network_level: Optional[int] = 1
    # Address fields
    street_address: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    address_validation_status: Optional[str] = None
    
    @field_validator('postal_code')
    @classmethod
    def validate_postal_code(cls, v: Optional[str]) -> Optional[str]:
        """Basic validation for postal code format (allows US ZIP, international formats)."""
        if v is None or v == "":
            return None
        # Remove spaces and hyphens for validation
        cleaned = re.sub(r'[\s-]', '', v)
        # Allow US ZIP (5 digits or 5+4 format), Canadian postal code (A1A1A1), and international formats (alphanumeric, 3-10 chars)
        if re.match(r'^\d{5}(?:\d{4})?$', cleaned):  # US ZIP
            return v
        if re.match(r'^[A-Za-z]\d[A-Za-z]\d[A-Za-z]\d$', cleaned):  # Canadian postal code
            return v
        if re.match(r'^[A-Za-z0-9]{3,10}$', cleaned):  # International format (basic)
            return v
        # If doesn't match common formats, still allow it (validation will catch issues)
        return v


class RecipientCreate(RecipientBase):
    pass


class RecipientUpdate(BaseModel):
    name: Optional[str] = None
    relationship: Optional[str] = None
    age_band: Optional[str] = None
    interests: Optional[List[str]] = None
    constraints: Optional[List[str]] = None
    notes: Optional[str] = None
    is_core_contact: Optional[bool] = None
    network_level: Optional[int] = None
    # Address fields
    street_address: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    address_validation_status: Optional[str] = None


class RecipientResponse(RecipientBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    upcoming_occasions_count: Optional[int] = 0  # Count of upcoming occasions
    relationships: Optional[List[Dict[str, Any]]] = []  # Relationships to other recipients
    
    class Config:
        from_attributes = True


# Occasion Schemas
class OccasionBase(BaseModel):
    name: str
    occasion_type: Optional[str] = None
    date: Optional[date] = None
    budget_range: Optional[str] = None
    status: OccasionStatus = OccasionStatus.IDEA_NEEDED
    
    @field_validator('date')
    @classmethod
    def validate_future_date(cls, v: Optional[date]) -> Optional[date]:
        """Validate that occasion date is in the future (if provided)."""
        if v is not None:
            from datetime import date as date_class
            today = date_class.today()
            if v < today:
                raise ValueError(f"Occasion date must be in the future. Provided date: {v}")
        return v


class OccasionCreate(OccasionBase):
    recipient_id: UUID


class OccasionUpdate(BaseModel):
    name: Optional[str] = None
    occasion_type: Optional[str] = None
    date: Optional[date] = None
    budget_range: Optional[str] = None
    status: Optional[OccasionStatus] = None
    
    @field_validator('date')
    @classmethod
    def validate_future_date(cls, v: Optional[date]) -> Optional[date]:
        """Validate that occasion date is in the future (if provided)."""
        if v is not None:
            from datetime import date as date_class
            today = date_class.today()
            if v < today:
                raise ValueError(f"Occasion date must be in the future. Provided date: {v}")
        return v


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
    url: Optional[HttpUrl] = None
    is_shortlisted: str = "false"
    
    @field_validator('url', mode='before')
    @classmethod
    def validate_url_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate URL format for gift links."""
        if v is None or v == "":
            return None
        # HttpUrl will validate the format automatically
        # This validator allows empty strings to be converted to None
        return v if v else None


class GiftIdeaCreate(GiftIdeaBase):
    occasion_id: UUID


class GiftIdeaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[str] = None
    category: Optional[str] = None
    url: Optional[HttpUrl] = None
    is_shortlisted: Optional[str] = None
    
    @field_validator('url', mode='before')
    @classmethod
    def validate_url_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate URL format for gift links."""
        if v is None or v == "":
            return None
        # HttpUrl will validate the format automatically
        return v if v else None


class GiftIdeaResponse(GiftIdeaBase):
    id: UUID
    occasion_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class RecipientDetailResponse(RecipientResponse):
    """Recipient with full details including occasions and gifts."""
    occasions: Optional[List[OccasionResponse]] = []
    past_gifts: Optional[List[GiftIdeaResponse]] = []


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
    response: str
    gift_ideas: Optional[List[dict]] = None
    requires_confirmation: Optional[bool] = False
    confirmation_prompt: Optional[str] = None
    conversation_id: UUID
    metadata: Optional[dict] = None


class ChatConfirmRequest(BaseModel):
    conversation_id: UUID
    confirmed: bool


class ChatConfirmResponse(BaseModel):
    message: str
    recipient: Optional[dict] = None
    occasion: Optional[dict] = None
    relationship: Optional[dict] = None


# Recipient Relationship Schemas
class RecipientRelationshipBase(BaseModel):
    from_recipient_id: UUID
    to_recipient_id: UUID
    relationship_type: str
    is_bidirectional: Optional[bool] = False


class RecipientRelationshipCreate(RecipientRelationshipBase):
    pass


class RecipientRelationshipResponse(RecipientRelationshipBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

