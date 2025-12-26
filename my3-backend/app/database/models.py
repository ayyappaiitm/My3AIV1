from sqlalchemy import Column, String, Text, Date, DateTime, ForeignKey, Enum as SQLEnum, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database.connection import Base


class OccasionStatus(str, enum.Enum):
    IDEA_NEEDED = "idea_needed"
    SHORTLISTED = "shortlisted"
    DECIDED = "decided"
    DONE = "done"


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    recipients = relationship("Recipient", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


class Recipient(Base):
    __tablename__ = "recipients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    relationship_type = Column(String(100))  # mom, dad, wife, friend, etc.
    age_band = Column(String(50))  # optional
    interests = Column(ARRAY(String), default=[])
    constraints = Column(ARRAY(String), default=[])  # allergies, preferences, etc.
    notes = Column(Text)  # optional
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="recipients")
    occasions = relationship("Occasion", back_populates="recipient", cascade="all, delete-orphan")


class Occasion(Base):
    __tablename__ = "occasions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recipient_id = Column(UUID(as_uuid=True), ForeignKey("recipients.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)  # "Birthday", "Anniversary", etc.
    occasion_type = Column(String(100))  # birthday, anniversary, holiday, etc.
    date = Column(Date)  # optional
    budget_range = Column(String(50))  # "$50-100", etc.
    status = Column(SQLEnum(OccasionStatus), default=OccasionStatus.IDEA_NEEDED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    recipient = relationship("Recipient", back_populates="occasions")
    gift_ideas = relationship("GiftIdea", back_populates="occasion", cascade="all, delete-orphan")


class GiftIdea(Base):
    __tablename__ = "gift_ideas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    occasion_id = Column(UUID(as_uuid=True), ForeignKey("occasions.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(String(50))  # "$49.99" or price range
    category = Column(String(100))  # electronics, books, experiences, etc.
    url = Column(String(500))  # link to product/experience
    is_shortlisted = Column(String(10), default="false")  # "true" or "false" as string for LangGraph compatibility
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    occasion = relationship("Occasion", back_populates="gift_ideas")


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # "user", "assistant", "system"
    content = Column(Text, nullable=False)
    message_metadata = Column(Text)  # JSON string for additional data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

