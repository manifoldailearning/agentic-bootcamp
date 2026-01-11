"""Vector store operations."""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
import structlog
from langchain_openai import OpenAIEmbeddings

logger = structlog.get_logger()

# Try different import paths for PGVector (version compatibility)
# Make vector store optional for demo - API can work without it
PGVector = None
LangchainDocument = None

try:
    from langchain_community.vectorstores.pgvector import PGVector
    logger.info("Using langchain_community.vectorstores.pgvector")
except ImportError:
    try:
        from langchain.vectorstores.pgvector import PGVector
        logger.info("Using langchain.vectorstores.pgvector")
    except ImportError:
        logger.warning("PGVector not available - vector search will be disabled")

try:
    from langchain_core.documents import Document as LangchainDocument
except ImportError:
    try:
        from langchain.schema import Document as LangchainDocument
    except ImportError:
        try:
            from langchain_core.documents.base import Document as LangchainDocument
        except ImportError:
            pass

from src.config import settings
from src.models.vector_models import Document, Embedding


class VectorStore:
    """Vector store for semantic search."""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,
        )
        self.connection_string = settings.postgres_url
        self.collection_name = "delivery_documents"
    
    def get_langchain_store(self):
        """Get LangChain PGVector store."""
        if PGVector is None:
            logger.warning("PGVector not available - vector store disabled")
            return None
        return PGVector(
            connection_string=self.connection_string,
            embedding_function=self.embeddings,
            collection_name=self.collection_name,
        )
    
    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        session: Optional[Session] = None
    ) -> List[str]:
        """Add documents to vector store."""
        doc_ids = []
        
        for doc_data in documents:
            # Store metadata in Postgres
            doc = Document(
                title=doc_data.get("title", ""),
                content=doc_data.get("content", ""),
                doc_type=doc_data.get("doc_type", "unknown"),
                source=doc_data.get("source"),
                source_id=doc_data.get("source_id"),
                meta_data=doc_data.get("metadata", {}),
                created_by=doc_data.get("created_by"),
                tags=doc_data.get("tags", []),
            )
            
            if session:
                session.add(doc)
                session.flush()
                doc_id = doc.id
            else:
                from src.db.session import get_vector_db
                with get_vector_db() as db:
                    db.add(doc)
                    db.commit()
                    doc_id = doc.id
            
            # Create embeddings and store in PGVector
            if LangchainDocument is not None and PGVector is not None:
                langchain_docs = [
                    LangchainDocument(
                        page_content=doc_data["content"],
                        metadata={
                            "doc_id": doc_id,
                            "title": doc_data.get("title", ""),
                            "doc_type": doc_data.get("doc_type", ""),
                            "source": doc_data.get("source", ""),
                            "source_id": doc_data.get("source_id", ""),
                        }
                    )
                ]
                
                store = self.get_langchain_store()
                if store is not None:
                    store.add_documents(langchain_docs)
            
            doc_ids.append(doc_id)
        
        logger.info("Added documents to vector store", count=len(doc_ids))
        return doc_ids
    
    def search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List:
        """Search for similar documents."""
        store = self.get_langchain_store()
        if store is None:
            logger.warning("Vector store not available - returning empty results")
            return []
        results = store.similarity_search_with_score(query, k=k, filter=filter)
        
        # Return just the documents (without scores for now)
        return [doc for doc, score in results]
    
    def search_with_scores(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[tuple]:
        """Search with similarity scores."""
        store = self.get_langchain_store()
        if store is None:
            logger.warning("Vector store not available - returning empty results")
            return []
        return store.similarity_search_with_score(query, k=k, filter=filter)

