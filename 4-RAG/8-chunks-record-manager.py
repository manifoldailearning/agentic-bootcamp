from langchain_core.indexing.base import InMemoryRecordManager
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_core.indexing import index
# from langchain.docstore.document import Document
from langchain_community.document_loaders import TextLoader
from langchain_classic.indexes import SQLRecordManager
from langchain_text_splitters.character import RecursiveCharacterTextSplitter


load_dotenv()
connection = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"
collection_name = "my_docs"
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
namespace = "langchain_rag"

vector_store = PGVector(
    embeddings=embedding_model,
    connection=connection,
    collection_name=collection_name,
    use_jsonb=True
)

record_manager = InMemoryRecordManager(namespace=namespace)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=10,
    chunk_overlap=5,
    length_function=len)
record_manager.create_schema()

cats_loader = TextLoader("cats.txt")
dogs_loader = TextLoader("dogs.txt")
new_source = TextLoader("new_source.txt")
cats_docs = cats_loader.load()
dogs_docs = dogs_loader.load()
new_source_docs = new_source.load()
cats_docs = splitter.split_documents(cats_docs) # chunking the documents
dogs_docs = splitter.split_documents(dogs_docs) # chunking the documents
new_source_docs = splitter.split_documents(new_source_docs) # chunking the documents
# display output of documents   
print(cats_docs)
print(dogs_docs)
print(new_source_docs)
# index the documents
index_1 = index(cats_docs, record_manager, vector_store, cleanup="incremental",source_id_key="source") 
# 1st iteration will add new documents to the vector store
print("Indexing cats documents:",index_1)
index_2 = index(dogs_docs, record_manager, vector_store,source_id_key="source" ) 
# 2nd iteration will update the existing documents in the vector store
print("Indexing dogs documents:",index_2)
index_3 = index(cats_docs, record_manager, vector_store,source_id_key="source" ) 
# 3rd iteration will add new documents to the vector store
print("Repeated Indexing cats documents:",index_3)

index_4 = index(new_source_docs, record_manager, vector_store,source_id_key="source" ) 
# 4th iteration will add new documents to the vector store
print("Indexing new source (having same content as dogs) documents:",index_4)

# modify the content of cats.txt
with open("cats.txt", "at") as f:
    f.write("I have a cat named Fluffy.\n")

cats_loader = TextLoader("cats.txt")
cats_docs = cats_loader.load()
cats_docs = splitter.split_documents(cats_docs) # chunking the documents
index_5 = index(cats_docs, record_manager, vector_store,source_id_key="source" ) 
# 5th iteration will update the existing documents in the vector store
print("Updating cats documents:",index_5)
