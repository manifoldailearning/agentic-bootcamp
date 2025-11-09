from langchain_community.document_loaders import PyPDFLoader
loader = PyPDFLoader("example.pdf")
docs = loader.load()

for doc in docs:
    print(f"data type of doc: {type(doc)}")
    print(doc.page_content)