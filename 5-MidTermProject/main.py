import time
import argparse
import logging


#setup logging
logging.basicConfig(level=logging.INFO, 
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
handlers=[logging.FileHandler("rag_pipeline.log", mode="a"),
logging.StreamHandler()
])

from retrieval import retrieve_context
from router import build_prompt
from llm_client import call as llm_call

def run_pipeline(question:str):
    logging.info(f"Running the RAG pipeline for question: {question}")

    # step 2: retrieve the context
    start_retrieval_time = time.time()
    context = retrieve_context(question)
    end_retrieval_time = time.time()
    retrieval_time = end_retrieval_time - start_retrieval_time
    retieval_latency = int(retrieval_time * 1000) # convert to milliseconds
    logging.info(f"Retrieval time: {retieval_latency} milliseconds")

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
    logging.info(f"Response: {response}")
    return response
    



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RAG Pipeline")
    parser.add_argument("--question", type=str, required=True, help="Your question to the RAG pipeline")
    args = parser.parse_args()
    question = args.question
    output = run_pipeline(question)
