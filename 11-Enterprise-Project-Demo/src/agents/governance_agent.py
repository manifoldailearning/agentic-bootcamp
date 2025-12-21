"""Governance & Compliance Agent."""
from typing import Dict, Any
from .base import BaseAgent

GOVERNANCE_AGENT_SYSTEM_PROMPT = """You are a Governance & Compliance Agent. Your role is to:
1. Ensure actions align with company policies
2. Check for PII leakage
3. Validate change control requirements
4. Verify action safety (no destructive actions)

Policy checks:
- No PII in comments (emails, phone numbers, customer names)
- No unauthorized status transitions
- No assignments to invalid users
- No deletion or destructive actions
- Compliance with SLA and definition of done

Output format:
{
    "compliant": true|false,
    "violations": [
        {
            "action": "action_description",
            "violation": "policy_violation_description",
            "severity": "high|medium|low"
        }
    ],
    "approved_actions": ["action1", "action2"],
    "rejected_actions": ["action3"]
}
"""


class GovernanceAgent(BaseAgent):
    """Governance and compliance agent."""
    
    def __init__(self):
        super().__init__("governance_agent", GOVERNANCE_AGENT_SYSTEM_PROMPT)
    
    def validate_actions(
        self,
        proposed_actions: Dict[str, Any],
        policies: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Validate actions against policies."""
        input_data = {
            "input": f"""
            Validate proposed actions for compliance:
            
            Proposed Actions:
            {proposed_actions.get('output', '')}
            
            Policies:
            {policies or 'Default enterprise policies'}
            
            Check for:
            1. PII leakage
            2. Policy violations
            3. Unsafe actions
            4. Change control requirements
            
            Output validation results.
            """
        }
        return self.invoke(input_data)

