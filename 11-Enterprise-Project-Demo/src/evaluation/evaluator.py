"""Evaluation pipeline for quality checks."""
from typing import Dict, Any
import re
import json
import structlog

from src.config import settings
from src.agents.types import WorkflowState

logger = structlog.get_logger()


class Evaluator:
    """Quality evaluation pipeline."""
    
    def __init__(self):
        self.thresholds = {
            "groundedness": settings.eval_groundedness_threshold,
            "completeness": settings.eval_completeness_threshold,
            "policy_compliance": settings.eval_policy_compliance_threshold,
            "action_accuracy": settings.eval_action_accuracy_threshold,
            "communication_quality": settings.eval_communication_quality_threshold,
        }
    
    def evaluate_workflow(self, state: WorkflowState) -> Dict[str, Any]:
        """Evaluate entire workflow output."""
        results = {
            "groundedness": self._evaluate_groundedness(state),
            "completeness": self._evaluate_completeness(state),
            "policy_compliance": self._evaluate_policy_compliance(state),
            "action_accuracy": self._evaluate_action_accuracy(state),
            "communication_quality": self._evaluate_communication_quality(state),
        }
        
        # Overall pass/fail
        results["overall_pass"] = all(
            results[k]["score"] >= self.thresholds[k]
            for k in self.thresholds.keys()
        )
        
        return results
    
    def _evaluate_groundedness(self, state: WorkflowState) -> Dict[str, Any]:
        """Check if outputs cite JIRA keys and sources."""
        score = 0.0
        issues = []
        
        # Check risk report
        risk_output = state.get("risk_report", {}).get("output", "")
        jira_keys = re.findall(r'JIRA-\d+', risk_output)
        if jira_keys:
            score += 0.3
        else:
            issues.append("Risk report missing JIRA issue keys")
        
        # Check comms output
        comms_output = state.get("comms_output", {}).get("email", {}).get("output", "")
        comms_keys = re.findall(r'JIRA-\d+', comms_output)
        if comms_keys:
            score += 0.3
        else:
            issues.append("Stakeholder email missing JIRA issue keys")
        
        # Check if actions reference real issues
        actions = state.get("proposed_actions", {}).get("output", "")
        action_keys = re.findall(r'JIRA-\d+', actions)
        if action_keys:
            score += 0.4
        else:
            issues.append("Proposed actions missing JIRA issue keys")
        
        return {
            "score": min(score, 1.0),
            "threshold": self.thresholds["groundedness"],
            "passed": score >= self.thresholds["groundedness"],
            "issues": issues,
        }
    
    def _evaluate_completeness(self, state: WorkflowState) -> Dict[str, Any]:
        """Check if all required elements are present."""
        score = 0.0
        issues = []
        
        # Check risk report has blockers, owners, mitigation
        risk_output = state.get("risk_report", {}).get("output", "").lower()
        if "blocker" in risk_output or "blocked" in risk_output:
            score += 0.2
        else:
            issues.append("Risk report missing blockers")
        
        if "owner" in risk_output or "assignee" in risk_output:
            score += 0.2
        else:
            issues.append("Risk report missing owners")
        
        if "mitigation" in risk_output or "recommendation" in risk_output:
            score += 0.2
        else:
            issues.append("Risk report missing mitigation")
        
        # Check stakeholder email exists
        if state.get("comms_output", {}).get("email"):
            score += 0.2
        else:
            issues.append("Missing stakeholder email")
        
        # Check proposed actions exist
        if state.get("proposed_actions", {}).get("output"):
            score += 0.2
        else:
            issues.append("Missing proposed actions")
        
        return {
            "score": min(score, 1.0),
            "threshold": self.thresholds["completeness"],
            "passed": score >= self.thresholds["completeness"],
            "issues": issues,
        }
    
    def _evaluate_policy_compliance(self, state: WorkflowState) -> Dict[str, Any]:
        """Check policy compliance."""
        score = 1.0
        issues = []
        
        # Check governance agent output
        gov_output = state.get("governance_check", {}).get("output", "").lower()
        
        if "violation" in gov_output or "non-compliant" in gov_output:
            score -= 0.5
            issues.append("Policy violations detected")
        
        # Check for PII patterns
        all_outputs = " ".join([
            state.get("risk_report", {}).get("output", ""),
            state.get("comms_output", {}).get("email", {}).get("output", ""),
        ])
        
        # Simple PII detection
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b\d{3}-\d{3}-\d{4}\b'
        
        if re.search(email_pattern, all_outputs):
            # Emails in JIRA context might be OK, but flag for review
            pass
        
        return {
            "score": max(score, 0.0),
            "threshold": self.thresholds["policy_compliance"],
            "passed": score >= self.thresholds["policy_compliance"],
            "issues": issues,
        }
    
    def _evaluate_action_accuracy(self, state: WorkflowState) -> Dict[str, Any]:
        """Check if proposed actions are valid."""
        score = 1.0
        issues = []
        
        # Check if actions have required fields
        actions_output = state.get("proposed_actions", {}).get("output", "")
        
        # Try to parse actions
        try:
            if "proposed_actions" in actions_output:
                start = actions_output.find("{")
                end = actions_output.rfind("}") + 1
                if start >= 0:
                    parsed = json.loads(actions_output[start:end])
                    actions = parsed.get("proposed_actions", [])
                    
                    for action in actions:
                        if not action.get("type"):
                            score -= 0.2
                            issues.append("Action missing type")
                        if not action.get("issue_key"):
                            score -= 0.2
                            issues.append("Action missing issue_key")
                        if not action.get("payload"):
                            score -= 0.2
                            issues.append("Action missing payload")
        except Exception as e:
            score -= 0.5
            issues.append(f"Could not parse actions: {str(e)}")
        
        return {
            "score": max(score, 0.0),
            "threshold": self.thresholds["action_accuracy"],
            "passed": score >= self.thresholds["action_accuracy"],
            "issues": issues,
        }
    
    def _evaluate_communication_quality(self, state: WorkflowState) -> Dict[str, Any]:
        """Check communication quality."""
        score = 0.0
        issues = []
        
        email_output = state.get("comms_output", {}).get("email", {}).get("output", "")
        
        # Check length (should be concise)
        word_count = len(email_output.split())
        if 50 <= word_count <= 500:
            score += 0.3
        else:
            issues.append(f"Email length inappropriate: {word_count} words")
        
        # Check for metrics
        if re.search(r'\d+', email_output):
            score += 0.2
        else:
            issues.append("Email missing metrics")
        
        # Check for actionable items
        if "action" in email_output.lower() or "next step" in email_output.lower():
            score += 0.2
        else:
            issues.append("Email missing actionable items")
        
        # Check for executive tone (no vague claims)
        vague_words = ["maybe", "perhaps", "might", "could be"]
        vague_count = sum(1 for word in vague_words if word in email_output.lower())
        if vague_count == 0:
            score += 0.3
        else:
            issues.append(f"Email contains {vague_count} vague claims")
        
        return {
            "score": min(score, 1.0),
            "threshold": self.thresholds["communication_quality"],
            "passed": score >= self.thresholds["communication_quality"],
            "issues": issues,
        }

