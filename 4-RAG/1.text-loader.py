from langchain_community.document_loaders import TextLoader

loader = TextLoader("my_text.txt")
docs = loader.load()
print(docs[0].page_content)