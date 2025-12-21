"""Dependency Agent."""
from typing import Dict, Any, List
from .base import BaseAgent
from src.integrations import JiraClient

DEPENDENCY_AGENT_SYSTEM_PROMPT = """You are a Dependency Agent. Your role is to:
1. Find cross-team dependencies
2. Identify missing owners
3. Detect stalled handoffs
4. Map dependency chains

Output format:
{
    "dependencies": [
        {
            "from": "JIRA-123",
            "to": "JIRA-456",
            "type": "blocks|depends on",
            "status": "blocked|at_risk|ok",
            "owner": "team_name",
            "stalled_days": 3
        }
    ],
    "missing_owners": ["JIRA-789"],
    "critical_path": ["JIRA-123", "JIRA-456", "JIRA-789"]
}
"""


class DependencyAgent(BaseAgent):
    """Dependency analysis agent."""
    
    def __init__(self):
        super().__init__("dependency_agent", DEPENDENCY_AGENT_SYSTEM_PROMPT)
        self.jira_client = JiraClient()
    
    def analyze_dependencies(
        self,
        stories: List[Dict[str, Any]],
        jira_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze dependencies."""
        # Get dependencies for each story
        all_dependencies = []
        for story in stories[:50]:  # Limit for performance
            deps = self.jira_client.get_dependencies(story['key'])
            all_dependencies.extend(deps)
        
        input_data = {
            "input": f"""
            Analyze dependencies:
            
            Stories: {len(stories)}
            Dependencies found: {len(all_dependencies)}
            
            JIRA Analysis:
            {jira_analysis.get('output', '')}
            
            Dependency data:
            {all_dependencies[:20]}
            
            Identify:
            1. Blocked items
            2. Missing owners
            3. Stalled handoffs
            4. Critical path
            """
        }
        
        return self.invoke(input_data)

