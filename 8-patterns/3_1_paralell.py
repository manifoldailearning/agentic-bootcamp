"""
Pattern 3: Parallel Pattern (TRUE parallel via asyncio.gather)

- Three perspective agents run concurrently (async LLM calls)
- Then an aggregator combines outputs
"""

import os
import asyncio
from typing import List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

load_dotenv()


# ============================================================================
# STATE
# ============================================================================

class State(BaseModel):
    user_request: str
    perspective_1: Optional[str] = None  # technical
    perspective_2: Optional[str] = None  # business
    perspective_3: Optional[str] = None  # UX
    final_result: Optional[str] = None


# ============================================================================
# AGENTS
# ============================================================================

class PerspectiveAgent:
    def __init__(self, perspective: str):
        self.perspective = perspective
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert providing a {perspective} perspective."),
            ("human", """Analyze this request from a {perspective} perspective:

{user_request}

Provide your analysis:""")
        ])

        self.chain = self.prompt | self.llm
# invoke - blocks the thread until the response is ready - SequentilIO
# ainvoke - non-blocking, returns a coroutine - ParallelIO
    async def analyze(self, user_request: str) -> str:
        resp = await self.chain.ainvoke({
            "user_request": user_request,
            "perspective": self.perspective
        })
        return resp.content


class AggregatorAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an Aggregator. Combine multiple perspectives into a comprehensive response."),
            ("human", """Original Request: {user_request}

Multiple Perspectives:
{perspectives}

Combine these perspectives into a balanced, comprehensive response:""")
        ])
        self.chain = self.prompt | self.llm

    async def aggregate(self, user_request: str, perspectives: List[str]) -> str:
        perspectives_text = "\n\n".join(
            [f"Perspective {i+1}:\n{p}" for i, p in enumerate(perspectives) if p]
        )

        resp = await self.chain.ainvoke({
            "user_request": user_request,
            "perspectives": perspectives_text
        })
        return resp.content


# ============================================================================
# WORKFLOW
# ============================================================================

def create_workflow():
    agent1 = PerspectiveAgent("technical")
    agent2 = PerspectiveAgent("business")
    agent3 = PerspectiveAgent("user experience")
    aggregator = AggregatorAgent()

    # TRUE PARALLEL: one node runs 3 async calls concurrently
    async def run_parallel_node(state: State) -> dict:
        print("\n" + "="*60)
        print("PARALLEL: Running 3 perspective agents concurrently...")
        print("="*60)

        t1 = agent1.analyze(state.user_request)
        t2 = agent2.analyze(state.user_request)
        t3 = agent3.analyze(state.user_request)

        p1, p2, p3 = await asyncio.gather(t1, t2, t3)

        print("✓ Technical done")
        print("✓ Business done")
        print("✓ UX done")

        return {
            "perspective_1": p1,
            "perspective_2": p2,
            "perspective_3": p3
        }

    async def aggregate_node(state: State) -> dict:
        print("\n" + "="*60)
        print("AGGREGATOR: Combining perspectives...")
        print("="*60)

        final = await aggregator.aggregate(
            state.user_request,
            [state.perspective_1, state.perspective_2, state.perspective_3]
        )
        print("✓ Aggregation done")
        return {"final_result": final}

    workflow = StateGraph(State)
    workflow.add_node("parallel", run_parallel_node)
    workflow.add_node("aggregate", aggregate_node)

    workflow.set_entry_point("parallel")
    workflow.add_edge("parallel", "aggregate")
    workflow.add_edge("aggregate", END)

    return workflow.compile()


# ============================================================================
# MAIN
# ============================================================================

async def main():
    print("\n" + "="*60)
    print("TRUE PARALLEL PATTERN DEMO")
    print("="*60)

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY not found\n")

    user_request = "Should we implement a new feature for our app?"
    print(f"\nRequest: {user_request}\n")

    app = create_workflow()
    app.get_graph().draw_mermaid_png(output_file_path="parallel_v2.png")
    initial_state = State(user_request=user_request)

    print("🚀 Starting workflow...\n")
    final_out = await app.ainvoke(initial_state)         # <-- async invoke
    final_state = State.model_validate(final_out)

    print("\n" + "="*60)
    print("FINAL RESULT (Combined Perspectives)")
    print("="*60)
    print(f"\n{final_state.final_result}\n")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
