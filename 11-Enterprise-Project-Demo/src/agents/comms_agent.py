"""Comms Agent."""
from typing import Dict, Any, List
from .base import BaseAgent

COMMS_AGENT_SYSTEM_PROMPT = """You are a Communications Agent. Your role is to:
1. Draft executive-ready stakeholder updates
2. Create status reports
3. Generate meeting agendas
4. Write JIRA update comments

Tone: Professional, concise, data-driven
Format: Use bullet points, include metrics, cite issue keys
Audience: Executives, stakeholders, team members
"""


class CommsAgent(BaseAgent):
    """Communications agent."""
    
    def __init__(self):
        super().__init__("comms_agent", COMMS_AGENT_SYSTEM_PROMPT)
    
    def draft_stakeholder_email(
        self,
        risk_report: Dict[str, Any],
        jira_analysis: Dict[str, Any],
        days_ahead: int = 14
    ) -> Dict[str, Any]:
        """Draft stakeholder email."""
        input_data = {
            "input": f"""
            Draft an executive-ready stakeholder email for delivery risk report (next {days_ahead} days).
            
            Risk Analysis:
            {risk_report.get('output', '')}
            
            JIRA Analysis:
            {jira_analysis.get('output', '')}
            
            Requirements:
            - Subject line
            - Executive summary (2-3 sentences)
            - Key risks and blockers
            - Mitigation plan
            - Action items
            - Keep under 300 words
            """
        }
        return self.invoke(input_data)
    
    def draft_jira_comments(
        self,
        risk_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Draft JIRA comments for high-risk items."""
        input_data = {
            "input": f"""
            Draft JIRA comments for high-risk items:
            
            {risk_items}
            
            Each comment should:
            - Explain the risk
            - Propose mitigation
            - Tag relevant stakeholders
            - Be professional and actionable
            """
        }
        return self.invoke(input_data)
    
    def draft_status_report(
        self,
        jira_analysis: Dict[str, Any],
        risk_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Draft status report."""
        input_data = {
            "input": f"""
            Draft a status report combining:
            
            JIRA Analysis:
            {jira_analysis.get('output', '')}
            
            Risk Report:
            {risk_report.get('output', '')}
            
            Include: Summary, Metrics, Risks, Next Steps
            """
        }
        return self.invoke(input_data)

