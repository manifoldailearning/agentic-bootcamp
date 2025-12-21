"""JIRA Analyst Agent."""
from typing import Dict, Any, List
from .base import BaseAgent
from src.integrations import JiraClient

JIRA_ANALYST_SYSTEM_PROMPT = """You are a JIRA Analyst Agent. Your role is to:
1. Analyze JIRA data (epics, stories, bugs, sprints)
2. Summarize sprint health metrics
3. Identify blockers and aging tickets
4. Extract key insights from ticket status, transitions, and comments

Always cite specific JIRA issue keys (e.g., JIRA-1234) in your analysis.
Be concise and data-driven.
"""


class JiraAnalystAgent(BaseAgent):
    """JIRA analysis agent."""
    
    def __init__(self):
        super().__init__("jira_analyst", JIRA_ANALYST_SYSTEM_PROMPT)
        self.jira_client = JiraClient()
    
    def analyze_sprint_health(
        self,
        project_key: str = None,
        sprint_id: str = None,
        days_ahead: int = 14
    ) -> Dict[str, Any]:
        """Analyze sprint health."""
        # Get data
        stories = self.jira_client.get_stories(project_key=project_key, sprint=sprint_id, days_ahead=days_ahead)
        bugs = self.jira_client.get_bugs(project_key=project_key, days_ahead=days_ahead)
        sprint_health = self.jira_client.get_sprint_health(sprint_id) if sprint_id else None
        
        # Analyze
        input_data = {
            "input": f"""
            Analyze the following JIRA data:
            
            Stories ({len(stories)}):
            {self._format_stories(stories[:20])}  # Limit for token efficiency
            
            Bugs ({len(bugs)}):
            {self._format_bugs(bugs[:10])}
            
            Sprint Health:
            {sprint_health}
            
            Provide:
            1. Sprint health summary
            2. Top blockers
            3. Aging tickets (overdue or at risk)
            4. Status distribution
            5. Key insights
            """
        }
        
        analysis = self.invoke(input_data)
        analysis["data"] = {
            "stories_count": len(stories),
            "bugs_count": len(bugs),
            "sprint_health": sprint_health,
        }
        return analysis
    
    def _format_stories(self, stories: List[Dict[str, Any]]) -> str:
        """Format stories for analysis."""
        return "\n".join([
            f"- {s['key']}: {s['summary']} | Status: {s['status']} | Assignee: {s['assignee']} | Due: {s['due_date']} | Blockers: {s['blockers']}"
            for s in stories
        ])
    
    def _format_bugs(self, bugs: List[Dict[str, Any]]) -> str:
        """Format bugs for analysis."""
        return "\n".join([
            f"- {b['key']}: {b['summary']} | Status: {b['status']} | Priority: {b['priority']} | Reopened: {b.get('reopened_count', 0)}x"
            for b in bugs
        ])

