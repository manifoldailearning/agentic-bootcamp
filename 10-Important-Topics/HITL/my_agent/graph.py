import os
from typing import Literal, Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.types import interrupt
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# STATE
# -----------------------------
class State(TypedDict, total=False):
    user_input: str

    # Multi-agent artifacts
    route: Literal["research", "write"]
    research_notes: str
    draft: str

    # HITL artifacts
    approval_required: bool
    human_decision: Literal["approve", "edit", "reject"]
    human_edit: Optional[str]

    final_answer: str


def build_graph():
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-nano"),
        temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.2")),
    )

    # -----------------------------
    # SUPERVISOR (router / coordinator)
    # -----------------------------
    def supervisor_router(state: State) -> State:
        """
        Decide the next step. In this simple demo:
        - Always research first, then write.
        """
        # If we don't have research yet, route to research
        if not state.get("research_notes"):
            return {"route": "research"}

        # If we have research but no draft, route to write
        if not state.get("draft"):
            return {"route": "write"}

        # Otherwise, proceed to approval gate
        return {"route": "write"}  # route value won't matter after this; we'll transition via edges

    # -----------------------------
    # WORKER 1: Research Agent
    # -----------------------------
    def research_worker(state: State) -> State:
        prompt = (
            "You are a Research Agent. Create concise bullet notes for the user request.\n"
            "Rules:\n"
            "- Use 6-10 bullets\n"
            "- No final answer, only notes\n\n"
            f"User request: {state['user_input']}"
        )
        notes = llm.invoke(prompt).content
        return {"research_notes": notes}

    # -----------------------------
    # WORKER 2: Writer Agent
    # -----------------------------
    def writer_worker(state: State) -> State:
        prompt = (
            "You are a Writer Agent. Write a clear final answer using the research notes.\n"
            "Rules:\n"
            "- Keep it structured\n"
            "- Keep it practical\n\n"
            f"User request: {state['user_input']}\n\n"
            f"Research notes:\n{state.get('research_notes','')}"
        )
        draft = llm.invoke(prompt).content
        return {"draft": draft}

    # -----------------------------
    # RISK POLICY (decide if HITL is required)
    # -----------------------------
    def risk_gate(state: State) -> State:
        """
        Enterprise-style rule: require approval for anything that looks like:
        - sending messages/emails
        - taking actions
        - financial/medical/legal advice
        For demo: we'll require approval always (simple and consistent).
        """
        return {"approval_required": True}

    # -----------------------------
    # HUMAN APPROVAL NODE (HITL)
    # -----------------------------
    def human_approval(state: State) -> State:
        """
        Pause execution and ask human to approve/edit/reject.
        In Studio, this appears as a paused node with the draft.
        """
        payload = {
            "message": "Human approval required. Choose: approve | edit | reject",
            "draft": state["draft"],
            "instructions": "If edit: return an edited version of the draft. If reject: explain why."
        }

        response = interrupt(payload)

        # Expected response formats (keep it simple for learners):
        # 1) {"decision": "approve"}
        # 2) {"decision": "edit", "edited_text": "..."}
        # 3) {"decision": "reject", "reason": "..."}
        decision = (response or {}).get("decision", "approve")

        out: State = {"human_decision": decision}

        if decision == "edit":
            out["human_edit"] = (response or {}).get("edited_text", state["draft"])
        return out

    # -----------------------------
    # FINALIZER (Supervisor final)
    # -----------------------------
    def finalizer(state: State) -> State:
        decision = state.get("human_decision", "approve")

        if decision == "reject":
            return {
                "final_answer": (
                    "Rejected by human reviewer.\n\n"
                    "Reason: " + (state.get("human_edit") or "No reason provided.")
                )
            }

        if decision == "edit" and state.get("human_edit"):
            return {"final_answer": state["human_edit"]}

        # approve fallback
        return {"final_answer": state["draft"]}

    # -----------------------------
    # GRAPH
    # -----------------------------
    g = StateGraph(State)

    g.add_node("supervisor_router", supervisor_router)
    g.add_node("research_worker", research_worker)
    g.add_node("writer_worker", writer_worker)
    g.add_node("risk_gate", risk_gate)
    g.add_node("human_approval", human_approval)
    g.add_node("finalizer", finalizer)

    g.set_entry_point("supervisor_router")

    # Conditional routing: supervisor -> research or write
    def route_selector(state: State) -> str:
        return state["route"]

    g.add_conditional_edges(
        "supervisor_router",
        route_selector,
        {
            "research": "research_worker",
            "write": "writer_worker",
        },
    )

    # After research, go back to supervisor
    g.add_edge("research_worker", "supervisor_router")

    # After writer, go to risk gate
    g.add_edge("writer_worker", "risk_gate")

    # After risk gate, if approval required -> human_approval else -> finalizer
    def approval_selector(state: State) -> str:
        return "human" if state.get("approval_required") else "final"

    g.add_conditional_edges(
        "risk_gate",
        approval_selector,
        {"human": "human_approval", "final": "finalizer"},
    )

    g.add_edge("human_approval", "finalizer")
    g.add_edge("finalizer", END)

    return g.compile()


# Export for Platform discovery
agent = build_graph()
