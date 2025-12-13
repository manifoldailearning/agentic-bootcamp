"""
Pattern 1: Supervisor-Worker Pattern

A central Supervisor agent receives tasks and delegates them to specialized Worker agents.
The Supervisor coordinates the workflow and aggregates results.

Architecture:
    User Request
         │
         ▼
    Supervisor (coordinates)
         │
    ┌────┴────┐
    ▼         ▼
  Worker1  Worker2
    │         │
    └────┬────┘
         ▼
    Supervisor (aggregates)
         │
         ▼
    Final Result
"""

import os
import json
from typing import List, Optional, Dict, Any
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
    """A task assigned to a worker"""
    task_id: int
    description: str
    assigned_to: Optional[str] = None  # Which worker handles it
    result: Optional[str] = None


class State(BaseModel):
    """Shared state"""
    user_request: str
    tasks: List[Task] = Field(default_factory=list)
    final_result: Optional[str] = None


# ============================================================================
# SUPERVISOR AGENT
# ============================================================================

class SupervisorAgent:
    """Central coordinator that delegates tasks to workers"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    def plan(self, user_request: str) -> List[Task]:
        """Break down request and assign to workers"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Supervisor Agent. Break down requests into tasks 
and assign them to specialized workers (Writer, Researcher, Analyst)."""),
            ("human", """Request: {user_request}

Create 2-3 tasks and assign each to a worker:
- Writer: for content creation
- Researcher: for information gathering
- Analyst: for data analysis

Return JSON:
{{
  "tasks": [
    {{"task_id": 1, "description": "task", "assigned_to": "Writer"}},
    {{"task_id": 2, "description": "task", "assigned_to": "Researcher"}}
  ]
}}""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"user_request": user_request})
        content = response.content
        
        # Extract JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        try:
            data = json.loads(content)
            return [Task(**task) for task in data["tasks"]]
        except:
            return [
                Task(task_id=1, description="Research the topic", assigned_to="Researcher"),
                Task(task_id=2, description="Create content", assigned_to="Writer")
            ]
    
    def aggregate(self, user_request: str, tasks: List[Task]) -> str:
        """Combine worker results into final output"""
        results_text = "\n\n".join([
            f"Task {t.task_id} ({t.assigned_to}): {t.result}"
            for t in tasks if t.result
        ])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a Supervisor. Combine worker results into a final response."),
            ("human", """Original Request: {user_request}

Worker Results:
{results}

Combine these into a complete, coherent response:""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "user_request": user_request,
            "results": results_text
        })
        return response.content


# ============================================================================
# WORKER AGENTS
# ============================================================================

class WorkerAgent:
    """Specialized worker that executes assigned tasks"""
    
    def __init__(self, worker_type: str):
        self.worker_type = worker_type
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    def execute(self, user_request: str, task: Task) -> str:
        """Execute a task based on worker specialization"""
        prompts = {
            "Writer": "You are a Writer. Create clear, engaging content.",
            "Researcher": "You are a Researcher. Gather and summarize information.",
            "Analyst": "You are an Analyst. Analyze data and provide insights."
        }
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", prompts.get(self.worker_type, "You are a Worker. Complete the task.")),
            ("human", """Original Request: {user_request}

Your Task: {task_description}

Complete this task as a {worker_type}:""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "user_request": user_request,
            "task_description": task.description,
            "worker_type": self.worker_type
        })
        return response.content


# ============================================================================
# WORKFLOW
# ============================================================================

def create_workflow():
    """Create Supervisor-Worker workflow"""
    
    supervisor = SupervisorAgent()
    workers = {
        "Writer": WorkerAgent("Writer"),
        "Researcher": WorkerAgent("Researcher"),
        "Analyst": WorkerAgent("Analyst")
    }
    
    # Supervisor: Plan and delegate
    def supervisor_plan_node(state: State) -> dict:
        print("\n" + "="*60)
        print("SUPERVISOR: Planning and delegating tasks...")
        print("="*60)
        
        tasks = supervisor.plan(state.user_request)
        
        print(f"✓ Created {len(tasks)} tasks:")
        for task in tasks:
            print(f"  - Task {task.task_id} → {task.assigned_to}: {task.description}")
        
        return {"tasks": [task.model_dump() for task in tasks]}
    
    # Workers: Execute tasks
    def workers_execute_node(state: State) -> dict:
        print("\n" + "="*60)
        print("WORKERS: Executing assigned tasks...")
        print("="*60)
    
        tasks = [Task(**t) if isinstance(t, dict) else t for t in state.tasks]
        
        # Execute each task with appropriate worker
        for task in tasks:
            if task.assigned_to in workers:
                print(f"  → {task.assigned_to} working on Task {task.task_id}...")
                worker = workers[task.assigned_to]
                task.result = worker.execute(state.user_request, task)
                print(f"    ✓ Task {task.task_id} completed")
        
        return {"tasks": [task.model_dump() for task in tasks]}
    
    # Supervisor: Aggregate results
    def supervisor_aggregate_node(state: State) -> dict:
        print("\n" + "="*60)
        print("SUPERVISOR: Aggregating results...")
        print("="*60)
        
        tasks = [Task(**t) if isinstance(t, dict) else t for t in state.tasks]
        
        final_result = supervisor.aggregate(state.user_request, tasks)
        print("✓ Final result generated")
        
        return {"final_result": final_result}
    
    # Build graph
    workflow = StateGraph(State)
    workflow.add_node("supervisor_plan", supervisor_plan_node)
    workflow.add_node("workers_execute", workers_execute_node)
    workflow.add_node("supervisor_aggregate", supervisor_aggregate_node)
    
    workflow.set_entry_point("supervisor_plan")
    workflow.add_edge("supervisor_plan", "workers_execute")
    workflow.add_edge("workers_execute", "supervisor_aggregate")
    workflow.add_edge("supervisor_aggregate", END)
    return workflow.compile()


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "="*60)
    print("SUPERVISOR-WORKER PATTERN DEMO")
    print("="*60)
    
    user_request = "Create a blog post about Agentic AI"
    print(f"\nRequest: {user_request}\n")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY not found\n")
    
    app = create_workflow()
    app.get_graph().draw_mermaid_png(output_file_path="supervisor_worker.png")
    initial_state = State(user_request=user_request)
    
    print("🚀 Starting workflow...\n")
    
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
