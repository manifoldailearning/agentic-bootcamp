from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/") # root endpoint/homepage
def welcome_message():
    return {"message": "Welcome to the RAG pipeline!"}

@app.get("/metrics")    
def metrics():
    return {"message": "Metrics are available here"}

@app.get("/rag")
def rag_pipeline():
    return {"message": "RAG pipeline is running!"}

@app.post("/generate")
def generate_response(question: str):
    output = question[::-1]
    return {"output": f"the generated response is {output}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)