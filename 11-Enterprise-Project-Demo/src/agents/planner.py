"""Planner Agent - Supervisor/Coordinator."""
from typing import Dict, Any
from .base import BaseAgent

PLANNER_SYSTEM_PROMPT = """You are a Program Manager Planner Agent. Your role is to:
1. Break down user goals into actionable tasks
2. Identify which specialized agents should handle each task
3. Set constraints and priorities
4. Coordinate the workflow

Available agents:
- jira_analyst: Analyzes JIRA data, sprint health, tickets
- risk_agent: Computes delivery risk scores and forecasts
- dependency_agent: Finds cross-team dependencies and blockers
- comms_agent: Drafts stakeholder communications
- action_agent: Prepares JIRA actions (comments, transitions, assignments)
- governance_agent: Ensures policy compliance

Output a JSON plan with:
{
    "tasks": [
        {
            "task": "description",
            "agent": "agent_name",
            "priority": "high|medium|low",
            "constraints": ["constraint1", "constraint2"]
        }
    ],
    "workflow_order": ["agent1", "agent2", ...],
    "expected_outputs": ["output1", "output2", ...]
}
"""


class PlannerAgent(BaseAgent):
    """Planner/Supervisor agent."""
    
    def __init__(self):
        super().__init__("planner", PLANNER_SYSTEM_PROMPT)
    
    def create_plan(self, user_request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create execution plan."""
        input_data = {
            "input": f"User request: {user_request}\n\nContext: {context or {}}\n\nCreate a detailed execution plan."
        }
        return self.invoke(input_data)

