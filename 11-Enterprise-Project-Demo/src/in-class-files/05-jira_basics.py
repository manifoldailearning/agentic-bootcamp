# pip install 'jira[cli]'
from jira import JIRA
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

jira_server = os.getenv("JIRA_SERVER")
jira_email = os.getenv("JIRA_EMAIL")
jira_api_token = os.getenv("JIRA_API_TOKEN")

jira = JIRA(server=jira_server, basic_auth=(jira_email, jira_api_token))
print(f"Connected to JIRA {jira_server}")
print(jira.projects())

# get the issues for a project
# example JQL
examples = [
        ("All issues in project", 'project = SCRUM'),
        ("Issues in progress", 'project = SCRUM AND status = "In Progress"'),
        ("High priority bugs", 'project = SCRM AND priority = High AND type = Bug'),
        ("My assigned issues", 'assignee = currentUser()'),
        ("Updated recently", 'updated >= -14d'),
        ("Overdue issues", 'dueDate < now() AND status != Done'),
        ("Blocked issues", 'labels = blocker'),
    ]

for example in examples:
    print(f"Example: {example[0]}")
    print(f"JQL: {example[1]}")
    issues = jira.search_issues(jql_str=example[1], maxResults=10)
    print(f"Issues: {issues}")
    print("---")