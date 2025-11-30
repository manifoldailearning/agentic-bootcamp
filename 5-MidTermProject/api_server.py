import uvicorn
import time
import uuid 
import logging
from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
#setup logging
logging.basicConfig(level=logging.INFO, 
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
handlers=[logging.FileHandler("rag_pipeline.log", mode="at"),
logging.StreamHandler()
])

from cache_store import get as get_cache, set as set_cache
from retrieval import retrieve_context
from router import build_prompt
from llm_client import call as llm_call
from postprocess import secured_output
from guardrails import apply_guardrails
from observability import log, record_metric, start_metrics_server
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="RAG Pipeline API",
    version="1.0.0",
    description="API for the RAG pipeline",
)

# Enable CORS for front end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000/page.html"], # In production, you should specify the allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    question: str
    user_id: str | None = None

class AskResponse(BaseModel):
    answer : str
    request_id: str | None = None

# core pipeline function
def run_pipeline(question:str, user_id:str | None = None):
    logging.info(f"Running the RAG pipeline for question: {question}")

    # step 1: check the cache
    cached_response = get_cache(question)
    if cached_response: # if not None
        logging.info(f"Cache HIT for question: {question}")
        print(f"Cache HIT for question: {question}")
        return cached_response
    print(f"Cache MISS for question: {question}")
    logging.info(f"Cache MISS for question: {question}")
    # step 2: retrieve the context
    start_retrieval_time = time.time()
    context = retrieve_context(question)
    end_retrieval_time = time.time()
    retrieval_time = end_retrieval_time - start_retrieval_time
    retieval_latency = int(retrieval_time * 1000) # convert to milliseconds
    logging.info(f"Retrieval time: {retieval_latency} milliseconds")
    record_metric("genai_retrieval_latency_ms", retieval_latency)
    # step 3: build the prompt
    model_name, prompt = build_prompt(question, context)
    logging.info(f"Built prompt for model: {model_name}")
    logging.info(f"Prompt: {prompt}")

    # step 4: call the LLM
    start_llm_time = time.time()
    response = llm_call(model_name, prompt)
    end_llm_time = time.time()
    llm_time = end_llm_time - start_llm_time
    llm_latency = int(llm_time * 1000) # convert to milliseconds
    logging.info(f"LLM time: {llm_latency} milliseconds")
    record_metric("genai_llm_latency_ms", llm_latency)
    logging.info(f"Response: {response}")
    response = secured_output(response)
    logging.info(f"Secured response: {response}")
    response = apply_guardrails(response)
    logging.info(f"Guardrails applied response: {response}")
    # step 5: cache the response
    set_cache(question, response)
    logging.info(f"Cached response for question: {question}")
    log(question, prompt, response, user_id) # question + prompt + response
    return response
    
# FAST API ROUTES

@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    request_id = str(uuid.uuid4())
    response = run_pipeline(request.question, request.user_id)
    print(f"Response: {response}")
    print(type(response))
    print(f"Request ID: {request_id}")
    print(type(request_id))
    return AskResponse(answer=response, request_id=request_id)

@app.get("/metrics") # Promethrus metrics endpoint - integrated into FASTAPI server
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
def welcome_message():
    return { "status": "ok", "message": "Welcome to the RAG pipeline API!",
    "metrics_url": f"http://localhost:8002/metrics", "health": f"/health"}

@app.get("/health")
def health_check():
    return { "status": "ok", "message": "RAG pipeline API is running!"}

if __name__ == "__main__":
    start_metrics_server()
    uvicorn.run(app, host="0.0.0.0", port=8001)