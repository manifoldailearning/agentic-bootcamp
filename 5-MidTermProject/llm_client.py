from langchain_openai import ChatOpenAI
from config import TEMPERATURE,MAX_TOKENS
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
import os
import logging
from functools import lru_cache
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY is not set")

@lru_cache(maxsize=10) # cache the results of the function to avoid reinitializing the chat model for the same model name
def _get_chat(model_name:str) -> ChatOpenAI:
    logging.info(f"Initializing the chat model for {model_name}")
    return ChatOpenAI(model=model_name, 
            temperature=TEMPERATURE, 
            max_tokens=MAX_TOKENS, 
            api_key=OPENAI_API_KEY
            )

def call(model_name:str, prompt: str) -> str:
    chat = _get_chat(model_name)
    logging.info(f"Calling the chat model for {model_name}")
    response:AIMessage = chat.invoke(prompt) 
    return response.content
