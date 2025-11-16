from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
load_dotenv()
connection = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"


# embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

loader = PyPDFLoader("book_manuscript.pdf")
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=100 ,
    chunk_overlap=20,
    length_function=len)

splitted_docs = splitter.split_documents(docs)

#create vector store
vector_store = PGVector.from_documents(
    documents =splitted_docs, # chunks of documents
    embedding = embedding_model,
    connection = connection
)

# create retriever
retriever = vector_store.as_retriever(search_kwargs={"k": 5}) # k is the number of chunks to return

llm = ChatOpenAI(model="gpt-4.1-nano")



prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that summarizes books."),
    ("user", "Summarize the following book on the mentioned query: {input}")
])
output = prompt.invoke({"input": "Summarize the book on the query: What is the main idea of the book? Summarize it in 200 words."})
# chain = prompt | retriever | llm | StrOutputParser()

# response = chain.invoke({"input": "Summarize the book on the query: What is the main idea of the book? Summarize it in 200 words."})
retrieve = retriever.invoke("What does it mean by monitoring in the book?")
print(retrieve)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that summarizes books."),
    ("user", "Summarize the following book on the mentioned query: {input} and the following context: {context}")
])

response = prompt.invoke({"input":"What does it mean by monitoring in the book?", "context": retrieve})
print("Prompt Output:")
print(response)

# invoke the llm
llm_output = llm.invoke(response)
print("LLM Output:")
print(llm_output.content)