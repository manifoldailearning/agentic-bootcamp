"""Delivery Risk Agent."""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .base import BaseAgent

RISK_AGENT_SYSTEM_PROMPT = """You are a Delivery Risk Agent. Your role is to:
1. Compute risk scores (0-100) for delivery items
2. Identify root causes of risks
3. Forecast delay probability
4. Prioritize risks by severity and impact

Risk factors to consider:
- Overdue items
- Blockers and dependencies
- Aging tickets
- Missing assignees
- Status stagnation
- Reopened bugs
- Sprint completion rate

Output format:
{
    "risk_score": 0-100,
    "risk_level": "low|medium|high|critical",
    "root_causes": ["cause1", "cause2"],
    "delay_probability": 0.0-1.0,
    "mitigation_recommendations": ["rec1", "rec2"],
    "high_risk_items": [
        {
            "issue_key": "JIRA-123",
            "risk_score": 85,
            "reason": "Blocked for 5 days"
        }
    ]
}
"""


class DeliveryRiskAgent(BaseAgent):
    """Delivery risk analysis agent."""
    
    def __init__(self):
        super().__init__("risk_agent", RISK_AGENT_SYSTEM_PROMPT)
    
    def compute_risk(
        self,
        jira_data: Dict[str, Any],
        days_ahead: int = 14
    ) -> Dict[str, Any]:
        """Compute delivery risk."""
        input_data = {
            "input": f"""
            Analyze delivery risk for the next {days_ahead} days based on:
            
            JIRA Analysis:
            {jira_data.get('output', '')}
            
            Data Summary:
            - Stories: {jira_data.get('data', {}).get('stories_count', 0)}
            - Bugs: {jira_data.get('data', {}).get('bugs_count', 0)}
            - Sprint Health: {jira_data.get('data', {}).get('sprint_health', {})}
            
            Compute comprehensive risk assessment.
            """
        }
        
        return self.invoke(input_data)
    
    def calculate_risk_score(self, item: Dict[str, Any]) -> float:
        """Calculate risk score for a single item."""
        score = 0.0
        
        # Overdue items
        if item.get('due_date'):
            due_date = datetime.fromisoformat(item['due_date'].replace('Z', '+00:00'))
            if due_date < datetime.now(due_date.tzinfo):
                days_overdue = (datetime.now(due_date.tzinfo) - due_date).days
                score += min(days_overdue * 10, 40)
        
        # Blockers
        if item.get('blockers'):
            score += len(item['blockers']) * 15
        
        # Missing assignee
        if not item.get('assignee'):
            score += 20
        
        # Status stagnation (in same status > 7 days)
        if item.get('updated'):
            updated = datetime.fromisoformat(item['updated'].replace('Z', '+00:00'))
            days_stale = (datetime.now(updated.tzinfo) - updated).days
            if days_stale > 7:
                score += min((days_stale - 7) * 2, 25)
        
        return min(score, 100.0)

