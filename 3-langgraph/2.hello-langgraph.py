from typing import TypedDict
from langgraph.graph import  START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
  # take environment variables from .env

load_dotenv()


llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                                temperature=0.5,
                                max_output_tokens=2048)

def llm_node(state: dict) -> dict:
    user_input = state.get("input", "How are you?")
    # user_input = state["input"]
    response = llm_gemini.invoke(user_input)
    return {"output": response.content}

class GraphState(TypedDict):
    input: str
    output: str

graph = StateGraph(GraphState)
graph.add_node("llm", llm_node)
graph.add_edge(START, "llm")
graph.add_edge("llm", END)

input_state = {"input": "Explain Langraph in one Sentence."}
app = graph.compile()


result = app.invoke(input_state)
app.get_graph().draw_mermaid_png()
print("Final Output:", result["output"])

