# this is a place where you can have guardrails (pre processing steps) and other things like that
# you can also have a place where you can have the prompt engineering

from config import DEFAULT_MODEL
TEMPLATE = """ You are a helpful assistant, answer the questions as best as you can.
{context_block}


Question: {question}

Answer:
"""

def build_prompt(question: str, context:str) -> tuple[str,str]:
    context_block =f"Context: {context}" if context.strip() else "" # if context is not empty, add it to the context block
    return DEFAULT_MODEL, TEMPLATE.format(context_block=context_block, question=question)