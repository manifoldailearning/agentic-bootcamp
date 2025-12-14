# my_agent/graph.py
import os
from typing import TypedDict, Optional

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

class State(TypedDict, total=False):
    user_input: str
    plan: str
    answer: str
    trace_id: Optional[str]


def build_graph():
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-nano"),
        temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.2")),
    )

    def planner(state: State) -> State:
        prompt = (
            "You are a planner. Create a short step-by-step plan (3-6 bullets).\n"
            f"User: {state['user_input']}\n"
            "Return only the bullets."
        )
        plan = llm.invoke(prompt).content
        return {"plan": plan}

    def executor(state: State) -> State:
        prompt = (
            "You are an executor. Use the plan to produce the final answer.\n\n"
            f"Plan:\n{state.get('plan','')}\n\n"
            f"User: {state['user_input']}\n"
            "Return a clear final answer."
        )
        answer = llm.invoke(prompt).content
        return {"answer": answer}

    g = StateGraph(State)
    g.add_node("planner", planner)
    g.add_node("executor", executor)

    g.set_entry_point("planner")
    g.add_edge("planner", "executor")
    g.add_edge("executor", END)

    return g.compile()



agent = build_graph()
agent.get_graph().draw_mermaid_png(output_file_path="graph.png")