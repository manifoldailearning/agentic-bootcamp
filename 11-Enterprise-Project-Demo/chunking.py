from langchain.text_splitter import SemanticChunker

chunker = SemanticChunker(
    embedding_function=embeddings,
    breakpoint_threshold_amount=95  # percentile
)

chunks = chunker.split_text(document)


# Hybrid search
# Retrieve candidates
candidates = vector_db.query(query, top_k=10)

# Rerank (fast, local model)
reranked = reranker.rerank(query, candidates, top_k=3)

# Send only top 3 to LLM
llm_response = llm.generate(context=reranked)


# Cache layer
cached_embed = cache.get(query)
if not cached_embed:
    cached_embed = embed_model.embed(query)
    cache.set(query, cached_embed, ttl=3600)

results = vector_db.query(cached_embed, top_k=5)



class ProductionRAG:
    def __init__(self):
        self.embedder = OpenAIEmbeddings()
        self.vector_db = PineconeVectorStore()
        self.reranker = CohereRerank()
        self.llm = ChatOpenAI(model="gpt-4-turbo")
        self.permission_service = PermissionService()
    
    def query(self, user_query, user_id):
        # 1. Embed query
        query_embed = self.embedder.embed(user_query)
        
        # 2. Hybrid search
        candidates = self.vector_db.hybrid_search(
            query_embed, 
            query_text=user_query,
            top_k=10
        )
        
        # 3. Permission filter
        accessible = [
            doc for doc in candidates 
            if self.permission_service.can_access(user_id, doc)
        ]
        
        # 4. Rerank
        reranked = self.reranker.rerank(
            user_query, 
            accessible, 
            top_k=3
        )
        
        # 5. Generate
        context = "\n\n".join([doc.content for doc in reranked])
        response = self.llm.generate(
            query=user_query,
            context=context
        )
        
        return response, reranked  # response + sources