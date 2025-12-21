"""Action Agent - Tool Executor."""
from typing import Dict, Any, List
from .base import BaseAgent

ACTION_AGENT_SYSTEM_PROMPT = """You are an Action Agent. Your role is to:
1. Prepare JIRA actions (comments, transitions, assignments, subtasks)
2. Format actions for approval workflow
3. Ensure actions are valid and safe

Output format:
{
    "proposed_actions": [
        {
            "type": "comment|transition|assign|create_subtask",
            "issue_key": "JIRA-123",
            "payload": {
                "comment": "text" OR
                "transition": "Blocked" OR
                "assignee": "email@example.com" OR
                "summary": "Subtask title",
                "description": "Subtask description"
            },
            "reason": "Why this action is needed"
        }
    ]
}

NEVER execute actions directly. Only prepare them for approval.
"""


class ActionAgent(BaseAgent):
    """Action preparation agent."""
    
    def __init__(self):
        super().__init__("action_agent", ACTION_AGENT_SYSTEM_PROMPT)
    
    def prepare_actions(
        self,
        risk_report: Dict[str, Any],
        dependency_analysis: Dict[str, Any],
        comms_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare JIRA actions."""
        input_data = {
            "input": f"""
            Based on the analysis, prepare JIRA actions:
            
            Risk Report:
            {risk_report.get('output', '')}
            
            Dependency Analysis:
            {dependency_analysis.get('output', '')}
            
            Communications:
            {comms_output.get('output', '')}
            
            Propose specific, actionable JIRA updates:
            - Comments on blocked items
            - Status transitions
            - Assignments for unassigned items
            - Subtasks for follow-ups
            
            Output as JSON with proposed_actions array.
            """
        }
        return self.invoke(input_data)

