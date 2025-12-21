"""Type definitions for workflow state."""
from typing import Dict, Any, TypedDict


class WorkflowState(TypedDict):
    """Workflow state."""
    user_request: str
    user_id: str
    user_role: str
    conversation_id: str
    plan: Dict[str, Any]
    jira_analysis: Dict[str, Any]
    risk_report: Dict[str, Any]
    dependency_analysis: Dict[str, Any]
    comms_output: Dict[str, Any]
    proposed_actions: Dict[str, Any]
    governance_check: Dict[str, Any]
    evaluation_results: Dict[str, Any]
    final_output: Dict[str, Any]
    errors: list

