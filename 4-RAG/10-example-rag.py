from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders.parsers.pdf import PyPDFParser
from langchain_core.documents.base import Blob, Document
# Load environment variables

load_dotenv()

connection = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0.5)

blob = Blob.from_path("./book_manuscript.pdf")

parser = PyPDFParser()

documents = parser.lazy_parse(blob)
docs = []
for doc in documents:
    docs.append(doc)
# print(docs[0].page_content)
# print(docs[0].metadata)
# print(docs)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # Adjust chunk size as needed
    chunk_overlap=50  # Adjust overlap as needed
)

chunks = splitter.split_documents(docs)
# print(f"Number of chunks created: {len(chunks)}")
# for i, chunk in enumerate(chunks):
#     print(f"Chunk {i+1}:")
#     print(chunk.page_content)  # Print the content of each chunk
#     print("--------------------------------")

# create vector store
vector_store = PGVector.from_documents(
    documents=chunks,
    embedding=embeddings,
    connection=connection,
    use_jsonb=True,  # Use JSONB for metadata storage
)

# create retriever

retriever = vector_store.as_retriever(search_kwargs= {"k":2})

query = "NVIDIA exam"

docs = retriever.invoke(query)

#print docs
print("Retrieved Context is as follows: ")
print(docs)
print("---------------")
for i,d in enumerate[Document](docs):
    print(f"{i+1} context is:")
    print(d.page_content)
    print("***************")
prompt = ChatPromptTemplate.from_template(
    """"Answer the question based only on the provided context.
    context: {context}
    question: {question}"""
)

llm_chain = prompt | llm

user_input = {"context": docs,
              "question":query }

result = llm_chain.invoke(user_input)
print("Output from RAG:")
print(result.content)
# for r in enumerate(result):
#     print(f"output : {r.page_content}")
#     print("---------------")