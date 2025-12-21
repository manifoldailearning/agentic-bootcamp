"""
Teaching Example 02: Database Models with SQLAlchemy

This example demonstrates:
- SQLAlchemy model definition
- Column types and constraints
- Relationships (Foreign Keys)
- Enums for type safety
- Timestamps


RUN: python src/db/init_db_runner.py

docker exec -it delivery-center-postgres psql -U postgres -d delivery_center
\dn
\dt chat_store.*
\d chat_store.conversations
\d chat_store.messages

\dt vector_store.*
\d vector_store.documents
\d vector_store.embeddings
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
import uuid

# ============================================================================
# STEP 1: Create Base Class
# ============================================================================
# This is the base for all our models
# It provides common functionality

Base = declarative_base()


# ============================================================================
# STEP 2: Define Enums
# ============================================================================
# Enums provide type safety - only valid values allowed

class ConversationStatus(PyEnum):
    """Conversation status enum."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class MessageRole(PyEnum):
    """Message role enum."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# ============================================================================
# STEP 3: Define Models
# ============================================================================

class Conversation(Base):
    """
    Conversation model.
    
    Represents a user conversation/workflow session.
    Notice the design decisions:
    - id is String (not auto-increment) for flexibility
    - user_id is required (nullable=False)
    - status uses Enum for type safety
    - meta_data is JSON for flexibility
    - Timestamps are timezone-aware
    """
    
    __tablename__ = "conversations"
    __table_args__ = {"schema": "chat_store"}  # Separate schema
    
    # Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Required fields
    user_id = Column(String, nullable=False)  # Cannot be NULL
    user_role = Column(String, nullable=False)
    
    # Optional fields
    title = Column(String)  # Can be NULL
    
    # Enum field - only allows ACTIVE, ARCHIVED, DELETED
    status = Column(
        Enum(ConversationStatus),
        default=ConversationStatus.ACTIVE,
        nullable=False
    )
    
    # JSON field for flexible metadata
    # Note: We use meta_data, not metadata (SQLAlchemy reserves 'metadata')
    meta_data = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # Set by database
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()  # Updated automatically
    )


class Message(Base):
    """
    Message model.
    
    Represents individual messages in a conversation.
    Notice the foreign key relationship to Conversation.
    """
    
    __tablename__ = "messages"
    __table_args__ = {"schema": "chat_store"}
    
    # Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Key - links to Conversation
    # This creates a relationship: one Conversation has many Messages
    conversation_id = Column(
        String,
        ForeignKey("chat_store.conversations.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Enum for role
    role = Column(Enum(MessageRole), nullable=False)
    
    # Content
    content = Column(Text, nullable=False)  # Text can be very long
    
    # Timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )


# ============================================================================
# STEP 4: Demonstrate Usage
# ============================================================================

def demonstrate_models():
    """Show how models work."""
    print("=" * 70)
    print("Database Models Example")
    print("=" * 70)
    
    print("\n📋 Conversation Model:")
    print(f"   Table: {Conversation.__tablename__}")
    print(f"   Schema: {Conversation.__table_args__['schema']}")
    print(f"   Columns: {[col.name for col in Conversation.__table__.columns]}")
    
    print("\n📋 Message Model:")
    print(f"   Table: {Message.__tablename__}")
    print(f"   Foreign Key: conversation_id → conversations.id")
    
    print("\n🔑 Key Design Decisions:")
    print("   1. String IDs (not auto-increment) for flexibility")
    print("   2. Enums for type safety (only valid values)")
    print("   3. JSON columns for flexible metadata")
    print("   4. Timezone-aware timestamps (important for audit)")
    print("   5. Foreign keys with CASCADE delete")
    
    print("\n💡 Why These Choices?")
    print("   - String IDs: Can use UUIDs, custom formats, etc.")
    print("   - Enums: Prevents invalid data at database level")
    print("   - JSON: Allows schema evolution without migrations")
    print("   - TZ timestamps: Critical for distributed systems")
    print("   - CASCADE: Automatic cleanup (delete conversation → delete messages)")


if __name__ == "__main__":
    demonstrate_models()
    
    print("\n" + "=" * 70)
    print("Next: See how to use these models with database sessions")
    print("=" * 70)


