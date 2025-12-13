"""
Pattern 4: Hierarchical Pattern

Multi-level organization with managers and workers.
Top-level manager delegates to middle managers,
who coordinate their own workers.

Architecture:
        Manager (Top Level)
            │
    ┌──────┴──────┐
    ▼             ▼
  Manager A    Manager B
    │             │
  ┌─┴─┐         ┌─┴─┐
  ▼   ▼         ▼   ▼
Worker Worker Worker Worker
  A1   A2      B1   B2
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

class Task(BaseModel):
    """Task in the hierarchy"""
    task_id: int
    description: str
    department: str  # Which department handles it
    result: Optional[str] = None


class State(BaseModel):
    """Hierarchical state"""
    user_request: str
    department_a_tasks: List[Task] = Field(default_factory=list)
    department_b_tasks: List[Task] = Field(default_factory=list)
    department_a_results: List[str] = Field(default_factory=list)
    department_b_results: List[str] = Field(default_factory=list)
    final_result: Optional[str] = None


# ============================================================================
# HIERARCHICAL AGENTS
# ============================================================================

class TopManagerAgent:
    """Top-level manager that coordinates departments"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    def delegate(self, user_request: str) -> dict:
        """Delegate tasks to departments"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Top Manager. Delegate tasks to departments:
- Department A: Technical tasks
- Department B: Business tasks"""),
            ("human", """Request: {user_request}

Create tasks for each department. Return JSON:
{{
  "department_a": [
    {{"task_id": 1, "description": "technical task"}}
  ],
  "department_b": [
    {{"task_id": 1, "description": "business task"}}
  ]
}}""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"user_request": user_request})
        content = response.content
        
        import json
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        try:
            data = json.loads(content)
            dept_a = [Task(**t, department="A") for t in data.get("department_a", [])]
            dept_b = [Task(**t, department="B") for t in data.get("department_b", [])]
            return {"department_a_tasks": dept_a, "department_b_tasks": dept_b}
        except:
            return {
                "department_a_tasks": [Task(task_id=1, description="Technical analysis", department="A")],
                "department_b_tasks": [Task(task_id=1, description="Business analysis", department="B")]
            }


class DepartmentManagerAgent:
    """Middle manager that coordinates workers in their department"""
    
    def __init__(self, department: str):
        self.department = department
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    def coordinate(self, user_request: str, tasks: List[Task]) -> List[str]:
        """Coordinate workers to complete department tasks"""
        tasks_text = "\n".join([f"Task {t.task_id}: {t.description}" for t in tasks])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"You are a {self.department} Department Manager. Coordinate your team to complete tasks."),
            ("human", """Original Request: {user_request}

Department Tasks:
{tasks}

Provide results for each task:""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "user_request": user_request,
            "tasks": tasks_text
        })
        
        # Split response into results (simplified)
        results = [response.content]  # In real system, would parse properly
        return results


class TopManagerAggregator:
    """Top manager aggregates department results"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    def aggregate(self, user_request: str, dept_a_results: List[str], dept_b_results: List[str]) -> str:
        """Combine department results"""
        results_text = f"""
Department A Results:
{chr(10).join(dept_a_results)}

Department B Results:
{chr(10).join(dept_b_results)}
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a Top Manager. Combine department results into final output."),
            ("human", """Original Request: {user_request}

{results}

Create final comprehensive response:""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "user_request": user_request,
            "results": results_text
        })
        return response.content


# ============================================================================
# WORKFLOW
# ============================================================================

def create_workflow():
    """Create hierarchical workflow"""
    
    top_manager = TopManagerAgent()
    dept_a_manager = DepartmentManagerAgent("Technical")
    dept_b_manager = DepartmentManagerAgent("Business")
    aggregator = TopManagerAggregator()
    
    # Level 1: Top Manager delegates
    def top_manager_node(state: State) -> dict:
        print("\n" + "="*60)
        print("TOP MANAGER: Delegating to departments...")
        print("="*60)
        
        delegation = top_manager.delegate(state.user_request)
        
        print(f"✓ Delegated {len(delegation['department_a_tasks'])} tasks to Department A")
        print(f"✓ Delegated {len(delegation['department_b_tasks'])} tasks to Department B")
        
        return {
            "department_a_tasks": [t.model_dump() for t in delegation["department_a_tasks"]],
            "department_b_tasks": [t.model_dump() for t in delegation["department_b_tasks"]]
        }
    
    # Level 2: Department A Manager coordinates
    def dept_a_manager_node(state: State) -> dict:
        print("\n" + "="*60)
        print("DEPARTMENT A MANAGER: Coordinating technical tasks...")
        print("="*60)
        
        tasks = [Task(**t) if isinstance(t, dict) else t for t in state.department_a_tasks]
        results = dept_a_manager.coordinate(state.user_request, tasks)
        
        print(f"✓ Department A completed {len(results)} tasks")
        
        return {"department_a_results": results}
    
    # Level 2: Department B Manager coordinates
    def dept_b_manager_node(state: State) -> dict:
        print("\n" + "="*60)
        print("DEPARTMENT B MANAGER: Coordinating business tasks...")
        print("="*60)
        
        tasks = [Task(**t) if isinstance(t, dict) else t for t in state.department_b_tasks]
        results = dept_b_manager.coordinate(state.user_request, tasks)
        
        print(f"✓ Department B completed {len(results)} tasks")
        
        return {"department_b_results": results}
    
    # Level 1: Top Manager aggregates
    def top_aggregator_node(state: State) -> dict:
        print("\n" + "="*60)
        print("TOP MANAGER: Aggregating department results...")
        print("="*60)
        
        final = aggregator.aggregate(
            state.user_request,
            state.department_a_results,
            state.department_b_results
        )
        
        print("✓ Final result generated")
        
        return {"final_result": final}
    
    # Build hierarchical graph
    workflow = StateGraph(State)
    workflow.add_node("top_manager", top_manager_node)
    workflow.add_node("dept_a_manager", dept_a_manager_node)
    workflow.add_node("dept_b_manager", dept_b_manager_node)
    workflow.add_node("top_aggregator", top_aggregator_node)
    
    workflow.set_entry_point("top_manager")
    workflow.add_edge("top_manager", "dept_a_manager")
    workflow.add_edge("dept_a_manager", "dept_b_manager")
    workflow.add_edge("dept_b_manager", "top_aggregator")
    workflow.add_edge("top_aggregator", END)
    
    return workflow.compile()


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "="*60)
    print("HIERARCHICAL PATTERN DEMO")
    print("="*60)
    
    user_request = "Develop a new product feature"
    print(f"\nRequest: {user_request}\n")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY not found\n")
    
    app = create_workflow()
    initial_state = State(user_request=user_request)
    
    print("🚀 Starting hierarchical workflow...\n")
    
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
