"""
Pattern 3: Parallel Pattern

Multiple agents work simultaneously on independent tasks.
Results are aggregated after all agents complete.

Architecture:
         Input
          │
    ┌─────┼─────┐
    ▼     ▼     ▼
  Agent Agent Agent
    A     B     C
    │     │     │
    └─────┼─────┘
          ▼
      Aggregator
          │
          ▼
       Output
"""

import os
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv()


# ============================================================================
# STATE DEFINITION
# ============================================================================

class State(BaseModel):
    """State with parallel results"""
    user_request: str
    perspective_1: Optional[str] = None  # From Agent 1
    perspective_2: Optional[str] = None  # From Agent 2
    perspective_3: Optional[str] = None  # From Agent 3
    final_result: Optional[str] = None   # Aggregated result


# ============================================================================
# PARALLEL AGENTS
# ============================================================================

class PerspectiveAgent:
    """Agent that provides a specific perspective"""
    
    def __init__(self, perspective: str):
        self.perspective = perspective # technical, business, user experience
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    def analyze(self, user_request: str) -> str:
        """Analyze from this agent's perspective"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"You are an expert providing a {self.perspective} perspective."),
            ("human", """Analyze this request from a {perspective} perspective:

{user_request}

Provide your analysis:""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "user_request": user_request,
            "perspective": self.perspective
        })
        return response.content


class AggregatorAgent:
    """Combines parallel results"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    def aggregate(self, user_request: str, perspectives: List[str]) -> str:
        """Combine all perspectives"""
        perspectives_text = "\n\n".join([
            f"Perspective {i+1}:\n{p}"
            for i, p in enumerate(perspectives) if p
        ])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an Aggregator. Combine multiple perspectives into a comprehensive response."),
            ("human", """Original Request: {user_request}

Multiple Perspectives:
{perspectives}

Combine these perspectives into a balanced, comprehensive response:""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "user_request": user_request,
            "perspectives": perspectives_text
        })
        return response.content


# ============================================================================
# WORKFLOW
# ============================================================================

def create_workflow():
    """Create parallel workflow"""
    
    # Create agents with different perspectives
    agent1 = PerspectiveAgent(perspective="technical")
    agent2 = PerspectiveAgent(perspective="business")
    agent3 = PerspectiveAgent(perspective="user experience")
    aggregator = AggregatorAgent()
    
    # Parallel nodes - all execute simultaneously
    def parallel_1_node(state: State) -> dict:
        print("\n" + "="*60)
        print("PARALLEL 1: Technical Perspective...")
        print("="*60)
        
        result = agent1.analyze(state.user_request)
        print("✓ Technical analysis completed")
        
        return {"perspective_1": result}
    
    def parallel_2_node(state: State) -> dict:
        print("\n" + "="*60)
        print("PARALLEL 2: Business Perspective...")
        print("="*60)
    
        result = agent2.analyze(state.user_request)
        print("✓ Business analysis completed")
        
        return {"perspective_2": result}
    
    def parallel_3_node(state: State) -> dict:
        print("\n" + "="*60)
        print("PARALLEL 3: UX Perspective...")
        print("="*60)
        result = agent3.analyze(state.user_request)
        print("✓ UX analysis completed")
        
        return {"perspective_3": result}
    
    # Aggregation node
    def aggregate_node(state: State) -> dict:
        print("\n" + "="*60)
        print("AGGREGATOR: Combining perspectives...")
        print("="*60)
        perspectives = [
            state.perspective_1,
            state.perspective_2,
            state.perspective_3
        ]
        
        final = aggregator.aggregate(state.user_request, perspectives)
        print("✓ Aggregation completed")
        
        return {"final_result": final}
    
    # Build graph
    workflow = StateGraph(State)
    
    # Add parallel nodes
    workflow.add_node("parallel_1", parallel_1_node)
    workflow.add_node("parallel_2", parallel_2_node)
    workflow.add_node("parallel_3", parallel_3_node)
    workflow.add_node("aggregate", aggregate_node)
    
    # All parallel nodes start from entry point
    workflow.set_entry_point("parallel_1")
    workflow.add_edge("parallel_1", "parallel_2")
    workflow.add_edge("parallel_2", "parallel_3")
    workflow.add_edge("parallel_3", "aggregate")
    workflow.add_edge("aggregate", END)
    
    # Note: In a true parallel system, all three would run simultaneously
    # LangGraph processes them sequentially, but they're independent
    # For true parallelism, you'd use async/threading
    
    return workflow.compile()


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "="*60)
    print("PARALLEL PATTERN DEMO")
    print("="*60)
    
    user_request = "Should we implement a new feature for our app?"
    print(f"\nRequest: {user_request}\n")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY not found\n")
    
    app = create_workflow()
    app.get_graph().draw_mermaid_png(output_file_path="parallel.png")
    initial_state = State(user_request=user_request)
    
    print("🚀 Starting parallel workflow...\n")
    print("(Note: Agents work on independent tasks)\n")
    
    try:
        final_state_dict = app.invoke(initial_state.model_dump())
        final_state = State(**final_state_dict)
        
        print("\n" + "="*60)
        print("FINAL RESULT (Combined Perspectives)")
        print("="*60)
        print(f"\n{final_state.final_result}\n")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        raise


if __name__ == "__main__":
    main()
