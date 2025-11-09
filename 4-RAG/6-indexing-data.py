from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()
connection = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"


# embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

loader = PyPDFLoader("example.pdf")
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=30,
    chunk_overlap=10,
    length_function=len)

splitted_docs = splitter.split_documents(docs)
print(splitted_docs)
for s,n in zip(splitted_docs,range(len(splitted_docs))):
    print(f"Chunk {n} --> {s.page_content} --> Len is {len(s.page_content)}")
    print("---")

# Separate Generation of Embeddings is not required as PGVector will handle it
# embeddings = embedding_model.embed_documents([chunk.page_content for chunk in splitted_docs])
# for e,n in zip(embeddings,range(len(embeddings))):
#     print(f"Embedding {n+1} --> {e[:10]} --> Len is {len(e)}")
#     print("---")    

#create vector store
vector_store = PGVector.from_documents(
    documents =splitted_docs, # chunks of documents
    embedding = embedding_model,
    connection = connection
)

#query the vector store
query = "Software Engineer"
results = vector_store.similarity_search(query, k=4)
for result in results:
    print(result.page_content)
    print("---")

query = "Software Engineer"
results = vector_store.similarity_search_with_score(query, k=4)
for result, score in results:
    print(result.page_content)
    print(f"Score: {score}")
    print("---")