from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://learn.manifoldailearning.com/services/nvidiancpaai")

docs = loader.load()
print(docs[0].page_content)