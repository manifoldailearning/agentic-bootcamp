"""Database session management."""
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
from typing import Generator
import structlog

from src.config import settings
from src.models.base import Base
from src.models.chat_models import Conversation, Message, Approval, ToolCall
from src.models.vector_models import Document, Embedding

logger = structlog.get_logger()

# Chat/Workflow DB
engine = create_engine(
    settings.postgres_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.environment == "development",
)

# Vector DB (same Postgres, different schema)
vector_engine = create_engine(
    settings.postgres_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
VectorSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=vector_engine)


def init_db():
    """Initialize database schemas and tables."""
    try:
        # Create schemas
        with engine.connect() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS chat_store"))
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS vector_store"))
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            except Exception:
                logger.warning("pgvector extension not available - vector search disabled")
            conn.commit()
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        Base.metadata.create_all(bind=vector_engine)
        
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database initialization failed (may not be needed for demo): {e}")
        # Continue without database for demo purposes


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_vector_db() -> Generator[Session, None, None]:
    """Get vector database session."""
    db = VectorSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

