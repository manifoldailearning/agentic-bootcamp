from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters.character import RecursiveCharacterTextSplitter

loader = PyPDFLoader("example.pdf")
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=20,
    chunk_overlap=10,
    length_function=len)

splitted_docs = splitter.split_documents(docs)
print(splitted_docs)
for s,n in zip(splitted_docs,range(len(splitted_docs))):
    print(f"Chunk {n+1} --> {s.page_content}")
    print("---")
