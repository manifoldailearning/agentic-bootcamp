"""Vector database models."""
from sqlalchemy import Column, String, Text, JSON, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    # Fallback if pgvector not available
    from sqlalchemy import TypeDecorator
    class Vector(TypeDecorator):
        impl = None
from .base import BaseModel


class Document(BaseModel):
    """Document stored in vector DB."""
    
    __tablename__ = "documents"
    __table_args__ = {"schema": "vector_store"}
    
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    doc_type = Column(String, nullable=False)  # PRD, architecture, SOW, runbook, postmortem, SOP, policy
    source = Column(String)  # JIRA, ServiceNow, Confluence, etc.
    source_id = Column(String, index=True)  # JIRA issue key, doc ID, etc.
    meta_data = Column(JSON, default=dict)  # Renamed from 'metadata' (reserved in SQLAlchemy)
    created_by = Column(String)
    tags = Column(JSON, default=list)


class Embedding(BaseModel):
    """Document embedding."""
    
    __tablename__ = "embeddings"
    __table_args__ = (
        Index("ix_embeddings_vector", "embedding", postgresql_using="ivfflat", postgresql_with={"lists": 100}),
        {"schema": "vector_store"}
    )
    
    document_id = Column(String, nullable=False, index=True)
    embedding = Column(Vector(1536))  # 1536 is the dimension of the embedding
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(String, default="0")
    meta_data = Column(JSON, default=dict)  # Renamed from 'metadata' (reserved in SQLAlchemy)

