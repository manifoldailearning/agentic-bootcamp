import logging
from prometheus_client import Counter, Histogram, start_http_server

# Metrics
REQUEST_COUNTER = Counter("genai_requests_total", "Total requests received")
LLM_LATENCY = Histogram("genai_llm_latency_ms", "LLM call latency in milliseconds")
RETRIEVAL_LATENCY = Histogram("genai_retrieval_latency_ms", "Retrieval step latency in milliseconds")

#  Use this as a central logging function for the entire pipeline
# def log(question, model_input, model_output, guardrail_output=None, model="unknown", latency_ms=None, user_id=None, retrieved_context=None):
#     REQUEST_COUNTER.inc()
#     logging.info("----------- AUDIT LOG -----------")
#     logging.info(f"User ID: {user_id}")
#     logging.info(f"Question: {question}")

def log(question, model_input, model_output, user_id=None):
    REQUEST_COUNTER.inc()
    logging.info("Number of requests: {REQUEST_COUNTER}")
    logging.info(f"Question: {question}")
    logging.info(f"Model input: {model_input}") #  question + context
    logging.info(f"Model output: {model_output}")
    logging.info(f"User ID: {user_id if user_id else 'N/A'}")
    logging.info("---------------------------------")

def record_metric(metric_name, value):
    if metric_name == "genai_llm_latency_ms":
        LLM_LATENCY.observe(value)
    elif metric_name == "genai_retrieval_latency_ms":
        RETRIEVAL_LATENCY.observe(value)

def start_metrics_server(port=8002):
    start_http_server(port)
    logging.info(f"Prometheus metrics server running at http://localhost:{port}/metrics")