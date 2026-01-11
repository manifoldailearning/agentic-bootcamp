"""JIRA integration client."""
from typing import List, Dict, Any, Optional
from jira import JIRA
from datetime import datetime, timedelta
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings

logger = structlog.get_logger()


class JiraClient:
    """JIRA API client."""
    
    def __init__(self):
        self.client = JIRA(
            server=settings.jira_server,
            basic_auth=(settings.jira_email, settings.jira_api_token),
        )
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_epics(self, project_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get epics from JIRA."""
        jql = "issuetype = Epic"
        if project_key:
            jql += f" AND project = {project_key}"
        
        issues = self.client.search_issues(jql, maxResults=100)
        
        epics = []
        for issue in issues:
            epics.append({
                "key": issue.key,
                "summary": issue.fields.summary,
                "status": issue.fields.status.name,
                "assignee": issue.fields.assignee.displayName if issue.fields.assignee else None,
                "due_date": issue.fields.duedate,
                "created": issue.fields.created,
                "updated": issue.fields.updated,
                "description": issue.fields.description,
            })
        
        return epics
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_stories(
        self,
        project_key: Optional[str] = None,
        sprint: Optional[str] = None,
        days_ahead: int = 14
    ) -> List[Dict[str, Any]]:
        """Get stories for risk analysis."""
        jql = "issuetype = Story"
        if project_key:
            jql += f" AND project = {project_key}"
        if sprint:
            jql += f" AND sprint = {sprint}"
        
        # Focus on items due in next N days or overdue
        cutoff_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        jql += f" AND (duedate <= {cutoff_date} OR duedate IS EMPTY)"
        
        issues = self.client.search_issues(jql, maxResults=500, expand="changelog")
        
        stories = []
        for issue in issues:
            # Get status transitions
            transitions = []
            if hasattr(issue, 'changelog') and issue.changelog:
                for history in issue.changelog.histories:
                    for item in history.items:
                        if item.field == "status":
                            transitions.append({
                                "from": item.fromString,
                                "to": item.toString,
                                "date": history.created,
                            })
            
            stories.append({
                "key": issue.key,
                "summary": issue.fields.summary,
                "status": issue.fields.status.name,
                "assignee": issue.fields.assignee.displayName if issue.fields.assignee else None,
                "assignee_email": issue.fields.assignee.emailAddress if issue.fields.assignee else None,
                "due_date": issue.fields.duedate,
                "created": issue.fields.created,
                "updated": issue.fields.updated,
                "description": issue.fields.description,
                "priority": issue.fields.priority.name if issue.fields.priority else None,
                "labels": issue.fields.labels,
                "blockers": [label for label in issue.fields.labels if "blocker" in label.lower()],
                "transitions": transitions,
                "comments": self._get_comments(issue),
                "subtasks": [st.key for st in issue.fields.subtasks] if issue.fields.subtasks else [],
            })
        
        return stories
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_bugs(
        self,
        project_key: Optional[str] = None,
        days_ahead: int = 14
    ) -> List[Dict[str, Any]]:
        """Get bugs."""
        jql = "issuetype = Bug"
        if project_key:
            jql += f" AND project = {project_key}"
        
        cutoff_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        jql += f" AND (duedate <= {cutoff_date} OR duedate IS EMPTY)"
        
        issues = self.client.search_issues(jql, maxResults=200)
        
        bugs = []
        for issue in issues:
            bugs.append({
                "key": issue.key,
                "summary": issue.fields.summary,
                "status": issue.fields.status.name,
                "assignee": issue.fields.assignee.displayName if issue.fields.assignee else None,
                "due_date": issue.fields.duedate,
                "priority": issue.fields.priority.name if issue.fields.priority else None,
                "labels": issue.fields.labels,
                "reopened_count": len([h for h in issue.changelog.histories if any(
                    item.field == "status" and item.toString == "Reopened"
                    for item in h.items
                )]) if hasattr(issue, 'changelog') else 0,
            })
        
        return bugs
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_dependencies(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get issue dependencies."""
        issue = self.client.issue(issue_key, expand="links")
        
        dependencies = []
        if hasattr(issue.fields, 'issuelinks'):
            for link in issue.fields.issuelinks:
                if hasattr(link, 'outwardIssue'):
                    dependencies.append({
                        "type": link.type.outward,
                        "key": link.outwardIssue.key,
                        "status": link.outwardIssue.fields.status.name,
                    })
                elif hasattr(link, 'inwardIssue'):
                    dependencies.append({
                        "type": link.type.inward,
                        "key": link.inwardIssue.key,
                        "status": link.inwardIssue.fields.status.name,
                    })
        
        return dependencies
    
    def _get_comments(self, issue) -> List[Dict[str, Any]]:
        """Get issue comments."""
        comments = []
        if hasattr(issue.fields, 'comment') and issue.fields.comment.comments:
            for comment in issue.fields.comment.comments:
                comments.append({
                    "author": comment.author.displayName,
                    "body": comment.body,
                    "created": comment.created,
                })
        return comments
    
    def add_comment(self, issue_key: str, comment: str) -> Dict[str, Any]:
        """Add comment to issue."""
        comment_obj = self.client.add_comment(issue_key, comment)
        return {
            "id": comment_obj.id,
            "body": comment_obj.body,
            "created": comment_obj.created,
        }
    
    def transition_issue(self, issue_key: str, transition_name: str) -> bool:
        """Transition issue status."""
        issue = self.client.issue(issue_key)
        transitions = self.client.transitions(issue)
        
        for transition in transitions:
            if transition['name'].lower() == transition_name.lower():
                self.client.transition_issue(issue, transition['id'])
                return True
        
        return False
    
    def assign_issue(self, issue_key: str, assignee_email: str) -> bool:
        """Assign issue to user."""
        try:
            self.client.assign_issue(issue_key, assignee_email)
            return True
        except Exception as e:
            logger.error("Failed to assign issue", issue_key=issue_key, error=str(e))
            return False
    
    def create_subtask(self, parent_key: str, summary: str, description: str) -> Dict[str, Any]:
        """Create subtask."""
        issue_dict = {
            'project': {'key': parent_key.split('-')[0]},
            'summary': summary,
            'description': description,
            'issuetype': {'name': 'Sub-task'},
            'parent': {'key': parent_key},
        }
        
        new_issue = self.client.create_issue(fields=issue_dict)
        return {
            "key": new_issue.key,
            "summary": new_issue.fields.summary,
        }
    
    def get_sprint_health(self, sprint_id: str) -> Dict[str, Any]:
        """Get sprint health metrics."""
        sprint = self.client.sprint(sprint_id)
        board_id = sprint.originBoardId
        
        # Get sprint issues
        jql = f"sprint = {sprint_id}"
        issues = self.client.search_issues(jql, maxResults=500)
        
        total_story_points = sum(
            issue.fields.customfield_10016 or 0
            for issue in issues
            if hasattr(issue.fields, 'customfield_10016')
        )
        
        completed_story_points = sum(
            issue.fields.customfield_10016 or 0
            for issue in issues
            if issue.fields.status.name in ["Done", "Closed"]
            and hasattr(issue.fields, 'customfield_10016')
        )
        
        return {
            "sprint_id": sprint_id,
            "sprint_name": sprint.name,
            "state": sprint.state,
            "start_date": sprint.startDate,
            "end_date": sprint.endDate,
            "total_issues": len(issues),
            "total_story_points": total_story_points,
            "completed_story_points": completed_story_points,
            "completion_rate": completed_story_points / total_story_points if total_story_points > 0 else 0,
            "issues_by_status": self._count_by_status(issues),
        }
    
    def _count_by_status(self, issues) -> Dict[str, int]:
        """Count issues by status."""
        status_counts = {}
        for issue in issues:
            status = issue.fields.status.name
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts

