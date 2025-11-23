from vector_store import retrieve_documents

def retrieve_context(query:str, k:int = 3) -> str:
    context = retrieve_documents(query, k)
    ## context --> list[str] (each element is a chunk from vector database)
    return "\n\n".join(context) # join the context into a single string