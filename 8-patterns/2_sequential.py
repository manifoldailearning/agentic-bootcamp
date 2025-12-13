"""
Pattern 2: Sequential/Chain Pattern

Agents work one after another in a linear sequence.
Each agent's output becomes the next agent's input.

Architecture:
    Input
     │
     ▼
    Agent A
     │
     ▼
    Agent B
     │
     ▼
    Agent C
     │
     ▼
    Output
"""

import os
from typing import Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv()


# ============================================================================
# STATE DEFINITION
# ============================================================================
# dictionary based state / pydantic based state
class State(BaseModel):
    """State flows sequentially through agents"""
    user_request: str
    research_result: Optional[str] = None   # Output from Researcher
    analysis_result: Optional[str] = None   # Output from Analyst
    final_result: Optional[str] = None      # Output from Writer


# ============================================================================
# SEQUENTIAL AGENTS
# ============================================================================

class ResearcherAgent:
    """First agent: Gathers information"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    def research(self, user_request: str) -> str:
        """Research the topic"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a Researcher. Gather key information about the topic."),
            ("human", "Research this topic: {user_request}\n\nProvide key facts and information:")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"user_request": user_request})
        return response.content


class AnalystAgent:
    """Second agent: Analyzes research"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    def analyze(self, user_request: str, research: str) -> str:
        """Analyze the research findings"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an Analyst. Analyze information and identify key insights."),
            ("human", """Original Request: {user_request}

Research Findings:
{research}

Analyze this information and provide key insights:""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "user_request": user_request,
            "research": research
        })
        return response.content


class WriterAgent:
    """Third agent: Creates final output"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    def write(self, user_request: str, research: str, analysis: str) -> str:
        """Write final result using research and analysis"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a Writer. Create a clear, comprehensive response."),
            ("human", """Original Request: {user_request}

Research:
{research}

Analysis:
{analysis}

Create a complete response combining the research and analysis:""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "user_request": user_request,
            "research": research,
            "analysis": analysis
        })
        return response.content


# ============================================================================
# WORKFLOW
# ============================================================================

def create_workflow():
    """Create sequential workflow"""
    
    researcher = ResearcherAgent()
    analyst = AnalystAgent()
    writer = WriterAgent()
    
    # Step 1: Research
    def research_node(state: State) -> dict:
        print("\n" + "="*60)
        print("STEP 1: RESEARCHER - Gathering information...")
        print("="*60)

        research = researcher.research(state.user_request)
        print("✓ Research completed")
        
        return {"research_result": research}
    
    # Step 2: Analysis
    def analysis_node(state: State) -> dict:
        print("\n" + "="*60)
        print("STEP 2: ANALYST - Analyzing research...")
        print("="*60)
        analysis = analyst.analyze(state.user_request, state.research_result)
        print("✓ Analysis completed")
        
        return {"analysis_result": analysis}
    
    # Step 3: Writing
    def writing_node(state: State) -> dict:
        print("\n" + "="*60)
        print("STEP 3: WRITER - Creating final output...")
        print("="*60)
        final = writer.write(
            state.user_request,
            state.research_result,
            state.analysis_result
        )
        print("✓ Writing completed")
        
        return {"final_result": final}
    
    # Build sequential graph
    workflow = StateGraph(State)
    workflow.add_node("research", research_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("writing", writing_node)
    
    # Sequential flow
    workflow.set_entry_point("research")
    workflow.add_edge("research", "analysis")
    workflow.add_edge("analysis", "writing")
    workflow.add_edge("writing", END)
    
    return workflow.compile()


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "="*60)
    print("SEQUENTIAL/CHAIN PATTERN DEMO")
    print("="*60)
    
    user_request = "Explain how machine learning works"
    print(f"\nRequest: {user_request}\n")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY not found\n")
    
    app = create_workflow()
    app.get_graph().draw_mermaid_png(output_file_path="sequential.png")
    initial_state = State(user_request=user_request)
    
    print("🚀 Starting sequential workflow...\n")
    
    try:
        final_state_dict = app.invoke(initial_state.model_dump())
        final_state = State(**final_state_dict)
        
        print("\n" + "="*60)
        print("FINAL RESULT")
        print("="*60)
        print(f"\n{final_state.final_result}\n")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        raise


if __name__ == "__main__":
    main()
