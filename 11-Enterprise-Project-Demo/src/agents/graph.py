"""LangGraph workflow orchestrator."""
from typing import Dict, Any, Annotated
from langgraph.graph import StateGraph, END
import structlog
import json

from .types import WorkflowState
from .planner import PlannerAgent
from .jira_analyst import JiraAnalystAgent
from .risk_agent import DeliveryRiskAgent
from .dependency_agent import DependencyAgent
from .comms_agent import CommsAgent
from .action_agent import ActionAgent
from .governance_agent import GovernanceAgent
from src.evaluation.evaluator import Evaluator

logger = structlog.get_logger()


class DeliveryCommandCenterGraph:
    """Main LangGraph workflow."""
    
    def __init__(self):
        self.planner = PlannerAgent()
        self.jira_analyst = JiraAnalystAgent()
        self.risk_agent = DeliveryRiskAgent()
        self.dependency_agent = DependencyAgent()
        self.comms_agent = CommsAgent()
        self.action_agent = ActionAgent()
        self.governance_agent = GovernanceAgent()
        self.evaluator = Evaluator()
        
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow."""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("jira_analyst", self._jira_analyst_node)
        workflow.add_node("risk_agent", self._risk_agent_node)
        workflow.add_node("dependency_agent", self._dependency_agent_node)
        workflow.add_node("comms_agent", self._comms_agent_node)
        workflow.add_node("action_agent", self._action_agent_node)
        workflow.add_node("governance_agent", self._governance_agent_node)
        workflow.add_node("evaluator", self._evaluator_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Set entry point
        workflow.set_entry_point("planner")
        
        # Add edges
        workflow.add_edge("planner", "jira_analyst")
        workflow.add_edge("jira_analyst", "risk_agent")
        workflow.add_edge("jira_analyst", "dependency_agent")
        workflow.add_edge("risk_agent", "comms_agent")
        workflow.add_edge("dependency_agent", "comms_agent")
        workflow.add_edge("comms_agent", "action_agent")
        workflow.add_edge("action_agent", "governance_agent")
        workflow.add_edge("governance_agent", "evaluator")
        workflow.add_edge("evaluator", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def _planner_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Planner node."""
        try:
            plan = self.planner.create_plan(state["user_request"])
            logger.info("Planner completed", conversation_id=state.get("conversation_id"))
            return {"plan": plan}
        except Exception as e:
            logger.error("Planner failed", error=str(e))
            return {"errors": state.get("errors", []) + [f"Planner error: {str(e)}"]}
    
    def _jira_analyst_node(self, state: WorkflowState) -> Dict[str, Any]:
        """JIRA analyst node."""
        try:
            # Extract project/sprint from request or use defaults
            analysis = self.jira_analyst.analyze_sprint_health(days_ahead=14)
            logger.info("JIRA analysis completed", conversation_id=state.get("conversation_id"))
            return {"jira_analysis": analysis}
        except Exception as e:
            logger.error("JIRA analysis failed", error=str(e))
            return {"errors": state.get("errors", []) + [f"JIRA analysis error: {str(e)}"]}
    
    def _risk_agent_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Risk agent node."""
        try:
            risk_report = self.risk_agent.compute_risk(
                state.get("jira_analysis", {}),
                days_ahead=14
            )
            logger.info("Risk analysis completed", conversation_id=state.get("conversation_id"))
            return {"risk_report": risk_report}
        except Exception as e:
            logger.error("Risk analysis failed", error=str(e))
            return {"errors": state.get("errors", []) + [f"Risk analysis error: {str(e)}"]}
    
    def _dependency_agent_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Dependency agent node."""
        try:
            stories = state.get("jira_analysis", {}).get("data", {}).get("stories", [])
            dep_analysis = self.dependency_agent.analyze_dependencies(
                stories,
                state.get("jira_analysis", {})
            )
            logger.info("Dependency analysis completed", conversation_id=state.get("conversation_id"))
            return {"dependency_analysis": dep_analysis}
        except Exception as e:
            logger.error("Dependency analysis failed", error=str(e))
            return {"errors": state.get("errors", []) + [f"Dependency analysis error: {str(e)}"]}
    
    def _comms_agent_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Comms agent node."""
        try:
            # Draft stakeholder email
            email = self.comms_agent.draft_stakeholder_email(
                state.get("risk_report", {}),
                state.get("jira_analysis", {}),
                days_ahead=14
            )
            
            # Draft status report
            status_report = self.comms_agent.draft_status_report(
                state.get("jira_analysis", {}),
                state.get("risk_report", {})
            )
            
            logger.info("Comms generation completed", conversation_id=state.get("conversation_id"))
            return {
                "comms_output": {
                    "email": email,
                    "status_report": status_report,
                }
            }
        except Exception as e:
            logger.error("Comms generation failed", error=str(e))
            return {"errors": state.get("errors", []) + [f"Comms error: {str(e)}"]}
    
    def _action_agent_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Action agent node."""
        try:
            actions = self.action_agent.prepare_actions(
                state.get("risk_report", {}),
                state.get("dependency_analysis", {}),
                state.get("comms_output", {})
            )
            logger.info("Actions prepared", conversation_id=state.get("conversation_id"))
            return {"proposed_actions": actions}
        except Exception as e:
            logger.error("Action preparation failed", error=str(e))
            return {"errors": state.get("errors", []) + [f"Action error: {str(e)}"]}
    
    def _governance_agent_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Governance agent node."""
        try:
            validation = self.governance_agent.validate_actions(
                state.get("proposed_actions", {})
            )
            logger.info("Governance check completed", conversation_id=state.get("conversation_id"))
            return {"governance_check": validation}
        except Exception as e:
            logger.error("Governance check failed", error=str(e))
            return {"errors": state.get("errors", []) + [f"Governance error: {str(e)}"]}
    
    def _evaluator_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Evaluator node."""
        try:
            eval_results = self.evaluator.evaluate_workflow(state)
            logger.info("Evaluation completed", conversation_id=state.get("conversation_id"))
            return {"evaluation_results": eval_results}
        except Exception as e:
            logger.error("Evaluation failed", error=str(e))
            return {"errors": state.get("errors", []) + [f"Evaluation error: {str(e)}"]}
    
    def _finalize_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Finalize output."""
        try:
            logger.info("Workflow finalized", conversation_id=state.get("conversation_id"))
            return {
                "final_output": {
                    "risk_report": self._format_risk_report(state.get("risk_report", {})),
                    "stakeholder_email": state.get("comms_output", {}).get("email", {}).get("output", ""),
                    "status_report": state.get("comms_output", {}).get("status_report", {}).get("output", ""),
                    "proposed_actions": self._extract_actions(state.get("proposed_actions", {})),
                    "governance_status": state.get("governance_check", {}).get("output", ""),
                    "evaluation_scores": state.get("evaluation_results", {}),
                    "errors": state.get("errors", []),
                }
            }
        except Exception as e:
            logger.error("Finalization failed", error=str(e))
            return {"errors": state.get("errors", []) + [f"Finalization error: {str(e)}"]}
    
    def _extract_actions(self, actions_output: Dict[str, Any]) -> list:
        """Extract actions from agent output."""
        try:
            output_text = actions_output.get("output", "")
            # Try to parse JSON from output
            if "proposed_actions" in output_text:
                # Extract JSON block
                start = output_text.find("{")
                end = output_text.rfind("}") + 1
                if start >= 0 and end > start:
                    parsed = json.loads(output_text[start:end])
                    return parsed.get("proposed_actions", [])
        except Exception:
            pass
        return []
    
    def _format_risk_report(self, risk_report: Dict[str, Any]) -> str:
        """Format risk report for display."""
        try:
            output_text = risk_report.get("output", "")
            if not output_text:
                return "Risk report not available."
            
            # Try to parse JSON from output
            try:
                # Clean up the text - remove leading/trailing whitespace
                output_text = output_text.strip()
                
                # Extract JSON block if present
                start = output_text.find("{")
                end = output_text.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = output_text[start:end]
                    parsed = json.loads(json_str)
                    
                    # Format as markdown
                    formatted = f"""## Risk Score: {parsed.get('risk_score', 'N/A')}/100\n\n"""
                    
                    risk_level = parsed.get('risk_level', 'N/A')
                    if isinstance(risk_level, str):
                        formatted += f"**Risk Level:** {risk_level.upper()}\n\n"
                    else:
                        formatted += f"**Risk Level:** {risk_level}\n\n"
                    
                    delay_prob = parsed.get('delay_probability', 0)
                    if isinstance(delay_prob, (int, float)):
                        formatted += f"**Delay Probability:** {delay_prob * 100:.1f}%\n\n"
                    else:
                        formatted += f"**Delay Probability:** {delay_prob}\n\n"
                    
                    root_causes = parsed.get('root_causes', [])
                    if root_causes and isinstance(root_causes, list):
                        formatted += "### Root Causes\n\n"
                        for cause in root_causes:
                            formatted += f"- {cause}\n"
                        formatted += "\n"
                    
                    mitigation = parsed.get('mitigation_recommendations', [])
                    if mitigation and isinstance(mitigation, list):
                        formatted += "### Mitigation Recommendations\n\n"
                        for rec in mitigation:
                            formatted += f"- {rec}\n"
                        formatted += "\n"
                    
                    high_risk = parsed.get('high_risk_items', [])
                    if high_risk and isinstance(high_risk, list):
                        formatted += "### High-Risk Items\n\n"
                        for item in high_risk:
                            if isinstance(item, dict):
                                issue_key = item.get('issue_key', 'N/A')
                                reason = item.get('reason', 'N/A')
                                risk_score = item.get('risk_score', 'N/A')
                                formatted += f"- **{issue_key}**: {reason} (Risk: {risk_score})\n"
                        formatted += "\n"
                    
                    return formatted
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning("Could not parse risk report as JSON, returning as text", error=str(e))
                # If not JSON, return as-is (might be formatted text)
                return output_text
            
            # Return as-is if not JSON
            return output_text
        except Exception as e:
            logger.error("Error formatting risk report", error=str(e))
            return f"Error displaying risk report: {str(e)}"
    
    def run(self, user_request: str, user_id: str, user_role: str, conversation_id: str) -> Dict[str, Any]:
        """Run workflow."""
        initial_state: WorkflowState = {
            "user_request": user_request,
            "user_id": user_id,
            "user_role": user_role,
            "conversation_id": conversation_id,
            "plan": {},
            "jira_analysis": {},
            "risk_report": {},
            "dependency_analysis": {},
            "comms_output": {},
            "proposed_actions": {},
            "governance_check": {},
            "evaluation_results": {},
            "final_output": {},
            "errors": [],
        }
        
        result = self.graph.invoke(initial_state)
        return result.get("final_output", {})

