"""
Vector Store Module for RAG (Retrieval-Augmented Generation) System

This module provides functionality for storing and retrieving documents using Redis
as a vector database. It uses OpenAI embeddings to convert text into vector
representations, enabling semantic search capabilities.

Key Components:
- RedisVectorStore: Persistent vector storage using Redis
- OpenAIEmbeddings: Converts text to high-dimensional vectors
- Document: LangChain document structure for storing text content
"""

import config
from langchain_openai import OpenAIEmbeddings
from langchain_redis import RedisVectorStore
from langchain_core.documents import Document
from dotenv import load_dotenv
import time
load_dotenv()
# Redis connection URL from configuration
# Format: redis://[username]:[password]@[host]:[port] or redis://[host]:[port]
REDIS_URL = config.REDIS_URL

# Initialize the embedding model that converts text to vectors
# This model is used both for indexing documents and querying
# The embedding model is shared across all operations for consistency
embedding_model = OpenAIEmbeddings(model=config.EMBEDDING_MODEL)


def add_documents(documents: list[str]):
    """
    Add documents to the Redis vector store.
    
    This function takes a list of text strings, converts them to Document objects,
    generates embeddings for each document, and stores them in Redis with the
    specified index name. The documents become searchable after this operation.
    
    Args:
        documents (list[str]): A list of text strings to be stored in the vector database.
                              Each string will be converted to a Document object and embedded.
    
    Returns:
        None: This function performs a side effect (storing documents) and doesn't return a value.
    
    Note:
        - Documents are automatically embedded using the configured embedding model
        - All documents are stored in the same Redis index (specified in config.INDEX_NAME)
        - If documents with the same content already exist, they may be duplicated
    """
    # Convert each string to a LangChain Document object
    # Document objects have a page_content field that stores the actual text
    docs = [Document(page_content=doc) for doc in documents]
    
    # Create or update the Redis vector store with the new documents
    # This operation:
    # 1. Generates embeddings for each document using the embedding_model
    # 2. Stores the embeddings and metadata in Redis
    # 3. Creates the index if it doesn't exist
    RedisVectorStore.from_documents(
        documents=docs,
        embedding=embedding_model,
        redis_url=REDIS_URL,
        index_name=config.INDEX_NAME,
    )


def get_vectorstore():
    """
    Get an instance of the Redis vector store.
    
    This function creates and returns a RedisVectorStore instance connected to
    the configured Redis database and index. This instance can be used to perform
    similarity searches and other vector operations.
    
    Returns:
        RedisVectorStore: A configured instance of the Redis vector store that can be
                         used for querying and retrieving documents.
    
    Note:
        - This doesn't create a new index, it connects to an existing one
        - The index must have been created previously using add_documents()
        - Multiple calls return independent instances (stateless)
    """
    # try except to handle the error if the index name is not found
    try:
        return RedisVectorStore(
            embeddings=embedding_model,
            redis_url=REDIS_URL,
            index_name=config.INDEX_NAME,
        )
    except Exception as e:
        print(f"Error: {e}")
        return None



def retrieve_documents(query: str, k: int = 3):
    """
    Retrieve the most similar documents to a query using semantic search.
    
    This function performs a similarity search in the vector store. It converts
    the query text to an embedding, compares it with all stored document embeddings,
    and returns the k most similar documents based on cosine similarity.
    
    Args:
        query (str): The search query text. This will be embedded and compared
                     against all stored document embeddings.
        k (int, optional): The number of most similar documents (chunks) to retrieve.
                          Defaults to 3. Higher values return more results but
                          may include less relevant chunks.
    
    Returns:
        list[str]: A list of the page_content (text) from the k most similar documents.
                   Results are ordered by similarity (most similar first).
    
    Example:
        >>> results = retrieve_documents("machine learning algorithms", k=5)
        >>> print(results[0])  # Most similar document text
    """
    # Fetch the instance of the vector store connected to Redis
    # Retry logic to handle the error in redis
    for i in range(3):
        try:
            vectorstore = get_vectorstore()
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)
    # vectorstore = get_vectorstore()
    
    # Perform similarity search: converts query to embedding and finds k nearest neighbors
    # Returns Document objects sorted by similarity (highest similarity first)
    results = vectorstore.similarity_search(query, k=k)
    
    # Extract just the text content from each Document object
    return [d.page_content for d in results]


def retrieve_documents_with_score(query: str, k: int = 3):
    """
    Retrieve the most similar documents with their similarity scores.
    
    Similar to retrieve_documents(), but also returns the similarity scores for each
    result. The score indicates how similar the document is to the query (lower scores
    typically mean higher similarity, depending on the distance metric used).
    
    Args:
        query (str): The search query text to search for in the vector store.
        k (int, optional): The number of most similar documents to retrieve.
                          Defaults to 3.
    
    Returns:
        list[tuple[str, float]]: A list of tuples, where each tuple contains:
            - str: The page_content (text) of a similar document
            - float: The similarity/distance score for that document
          Results are ordered by similarity (most similar first).
    
    Note:
        - Lower scores typically indicate higher similarity (distance-based)
        - Scores can be used to filter results by a threshold
        - Useful for understanding retrieval quality and relevance
    
    Example:
        >>> results = retrieve_documents_with_score("neural networks", k=3)
        >>> for text, score in results:
        ...     print(f"Score: {score:.4f} - {text[:50]}...")
    """
    # Fetch the instance of the vector store connected to Redis
    vectorstore = get_vectorstore()
    
    # Perform similarity search with scores included
    # Returns tuples of (Document, score) sorted by similarity
    results = vectorstore.similarity_search_with_score(query, k=k)
    
    # Extract text content and scores, returning as list of (text, score) tuples
    return [(d.page_content, score) for d, score in results]