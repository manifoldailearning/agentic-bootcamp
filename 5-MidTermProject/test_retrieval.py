from vector_store import retrieve_documents_with_score

query = "What is Agentic AI?"
print("Query: ", query)
results = retrieve_documents_with_score(query, k=2, )
print("Results: ", results)
for result, score in results:
    print("Result: ", result)
    print("Score: ", score)
    print("---")

# Result Filtering - To avoid duplicate results
# if similarity difference is < 0.001, then consider it as the same document
# MMR - Maximal Marginal Relevance
# Reduce chunk overlap