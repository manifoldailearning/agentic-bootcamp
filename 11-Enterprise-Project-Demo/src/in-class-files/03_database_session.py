"""
 Database Session Management

This example demonstrates:
- Database connection patterns
- Context managers for sessions
- Transaction management
- Error handling

"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator


# ============================================================================
# STEP 1: Create Database Engine
# ============================================================================
# Engine manages connection pool

def create_database_engine(connection_string: str):
    """
    Create database engine.
    
    Args:
        connection_string: Database URL (e.g., postgresql://user:pass@host/db)
        
    Returns:
        SQLAlchemy engine
    """
    engine = create_engine(
        connection_string,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,        # Connection pool size
        max_overflow=20,     # Additional connections if needed
    )
    return engine


# ============================================================================
# STEP 2: Create Session Factory
# ============================================================================
# Session factory creates individual sessions

def create_session_factory(engine):
    """Create session factory."""
    return sessionmaker(
        autocommit=False,  # Manual commit control
        autoflush=False,   # Manual flush control
        bind=engine,
    )


# ============================================================================
# STEP 3: Context Manager Pattern
# ============================================================================
# Context managers ensure proper cleanup (commit/rollback/close)

@contextmanager
def get_db_session(session_factory) -> Generator[Session, None, None]:
    """
    Get database session with automatic cleanup.
    
    This is a context manager - use with 'with' statement.
    It automatically:
    - Commits on success
    - Rolls back on error
    - Closes the session
    
    Usage:
        with get_db_session(session_factory) as db:
            # Use db here
            db.add(object)
            # Auto-commits when exiting 'with' block
    """
    db = session_factory()
    try:
        yield db  # Give session to caller
        db.commit()  # Commit if no errors
    except Exception:
        db.rollback()  # Rollback on error
        raise  # Re-raise exception
    finally:
        db.close()  # Always close session


# ============================================================================
# STEP 4: Demonstrate Usage
# ============================================================================

def demonstrate_session_management():
    """Show how to use database sessions."""
    print("=" * 70)
    print("Database Session Management Example")
    print("=" * 70)
    
    # Example connection string (for demo - use environment variable in production)
    connection_string = "postgresql://user:pass@localhost/mydb"
    
    print("\n📋 Step 1: Create Engine and Session Factory")
    print("   engine = create_engine(connection_string)")
    print("   SessionLocal = sessionmaker(bind=engine)")
    
    # In real usage:
    engine = create_database_engine(connection_string)
    SessionLocal = create_session_factory(engine)
    
    print("\n📋 Step 2: Use Context Manager")
    print("   with get_db_session(SessionLocal) as db:")
    print("       # Use db here")
    print("       db.add(object)")
    print("       # Auto-commits on exit")
    
    print("\n🔑 Key Benefits:")
    print("   1. Automatic cleanup (always closes session)")
    print("   2. Transaction safety (auto-commit/rollback)")
    print("   3. Error handling (rollback on exception)")
    print("   4. Resource management (no leaks)")
    
    print("\n💡 Why Context Manager?")
    print("   - Ensures session is always closed")
    print("   - Handles errors gracefully")
    print("   - Prevents connection leaks")
    print("   - Cleaner code (no try/finally needed)")
    
    print("\n⚠️  Common Mistakes:")
    print("   ❌ db = SessionLocal()  # Never closed")
    print("   ❌ db.commit() without try/except")
    print("   ❌ Forgetting to close session")
    print("   ✅ Use context manager (with statement)")


# ============================================================================
# STEP 5: Schema Creation Example
# ============================================================================

def demonstrate_schema_creation():
    """Show how to create schemas."""
    print("\n" + "=" * 70)
    print("Schema Creation Example")
    print("=" * 70)
    
    print("\n📋 Creating Schemas:")
    print("   with engine.connect() as conn:")
    print("       conn.execute(text('CREATE SCHEMA IF NOT EXISTS chat_store'))")
    print("       conn.execute(text('CREATE SCHEMA IF NOT EXISTS vector_store'))")
    print("       conn.commit()")
    
    print("\n💡 Why Separate Schemas?")
    print("   - Namespace separation")
    print("   - Different access patterns")
    print("   - Easier to manage")
    print("   - Can have different permissions")


if __name__ == "__main__":
    demonstrate_session_management()
    demonstrate_schema_creation()
    
    print("\n" + "=" * 70)
    print("Key Takeaway: Always use context managers for database sessions!")
    print("=" * 70)


