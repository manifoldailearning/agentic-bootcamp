"""Chat and workflow state models."""
from sqlalchemy import Column, String, Text, JSON, ForeignKey, Enum, Boolean, DateTime
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel
from datetime import datetime
# https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html
# id = Column(String, primary_key=True) # String Primary Key, UUID is a good choice for this
# id = Column(UUID, primary_key=True, default=uuid.uuid4) # UUID Primary Key, UUID is a good choice for this


class MessageRole(str, enum.Enum):
    """Message role types."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    AGENT = "agent"


class ApprovalStatus(str, enum.Enum):
    """Approval status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EDITED = "edited"


class ToolCallStatus(str, enum.Enum):
    """Tool call status."""
    PENDING = "pending"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Conversation(BaseModel):
    """Conversation/workflow session."""
    
    __tablename__ = "conversations"
    __table_args__ = {"schema": "chat_store"}
    id = Column(String, primary_key=True) # String Primary Key, UUID is a good choice for this
    user_id = Column(String, nullable=False, index=True) # who created the conversation - not recommended to have orphaned conversations
    user_role = Column(String, nullable=False)  # PM, Program Manager, Engineer, Admin
    title = Column(String)
    status = Column(String, default="active")  # active, completed, archived
    meta_data = Column(JSON, default=dict)  # Renamed from 'metadata' (reserved in SQLAlchemy)
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="conversation", cascade="all, delete-orphan")
    tool_calls = relationship("ToolCall", back_populates="conversation", cascade="all, delete-orphan")
    created_at = Column(DateTime(timezone=True), server_default=datetime.now)
    updated_at = Column(DateTime(timezone=True), server_default=datetime.now)

class Message(BaseModel):
    """Chat message."""
    
    __tablename__ = "messages"
    __table_args__ = {"schema": "chat_store"}
    
    conversation_id = Column(String, ForeignKey("chat_store.conversations.id"), nullable=False, index=True)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    agent_name = Column(String)  # Which agent generated this
    meta_data = Column(JSON, default=dict)  # Renamed from 'metadata' (reserved in SQLAlchemy)
    
    conversation = relationship("Conversation", back_populates="messages")


class Approval(BaseModel):
    """Human approval for proposed actions."""
    
    __tablename__ = "approvals"
    __table_args__ = {"schema": "chat_store"}
    id = Column(String, primary_key=True) # String Primary Key, UUID is a good choice for this
    conversation_id = Column(String, ForeignKey("chat_store.conversations.id"), nullable=False, index=True)
    action_type = Column(String, nullable=False)  # jira_comment, jira_transition, jira_assign, etc.
    action_payload = Column(JSON, nullable=False)
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    approved_by = Column(String)
    approved_at = Column(DateTime(timezone=True))
    rejection_reason = Column(Text)
    edited_payload = Column(JSON)  # If user edited before approving
    
    conversation = relationship("Conversation", back_populates="approvals")


class ToolCall(BaseModel):
    """Tool call audit log."""
    
    __tablename__ = "tool_calls"
    __table_args__ = {"schema": "chat_store"}
    
    conversation_id = Column(String, ForeignKey("chat_store.conversations.id"), nullable=False, index=True)
    tool_name = Column(String, nullable=False)
    tool_input = Column(JSON, nullable=False)
    tool_output = Column(JSON)
    status = Column(Enum(ToolCallStatus), default=ToolCallStatus.PENDING)
    error_message = Column(Text)
    execution_time_ms = Column(String)
    approval_id = Column(String, ForeignKey("chat_store.approvals.id"))
    trace_id = Column(String, index=True)  # OpenTelemetry trace ID
    
    conversation = relationship("Conversation", back_populates="tool_calls")

