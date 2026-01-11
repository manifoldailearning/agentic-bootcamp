"""Streamlit frontend application."""
import streamlit as st
import requests
import json
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# For demo purposes, you can also use the test workflow directly
USE_DIRECT_WORKFLOW = False  # Set to True to bypass API

# Page config
st.set_page_config(
    page_title="Delivery Command Center",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "workflow_result" not in st.session_state:
    st.session_state.workflow_result = None
if "pending_approvals" not in st.session_state:
    st.session_state.pending_approvals = []
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None


def authenticate():
    """Simple authentication (replace with real auth)."""
    # For demo: auto-login as demo user
    if "user_id" not in st.session_state:
        st.session_state.user_id = "demo_user"
        st.session_state.user_role = "PM"
        st.session_state.auth_token = None  # Will be created on first API call
    
    return True  # Always allow access for demo


def make_api_request(endpoint: str, method: str = "GET", data: Dict = None, headers: Dict = None):
    """Make API request."""
    url = f"{API_BASE_URL}{endpoint}"
    
    # For demo: API accepts requests without auth (uses demo user)
    default_headers = {"Content-Type": "application/json"}
    
    # Optional: Add auth token if available (not required for demo)
    if st.session_state.get("auth_token"):
        default_headers["Authorization"] = f"Bearer {st.session_state.auth_token}"
    
    if headers:
        default_headers.update(headers)
    
    try:
        if method == "GET":
            response = requests.get(url, headers=default_headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=default_headers)
        else:
            return None
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            st.error("Authentication failed. Please login again.")
        else:
            st.error(f"API Error: {str(e)}")
            # Show response details for debugging
            try:
                error_detail = e.response.json()
                st.json(error_detail)
            except:
                st.text(e.response.text)
        return None
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None


def main():
    """Main application."""
    if not authenticate():
        return
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select Page",
            ["Ask Copilot", "Daily Status", "Risk Dashboard", "Approvals", "Audit Trail"],
        )
    
    # Main content
    if page == "Ask Copilot":
        show_copilot_page()
    elif page == "Daily Status":
        show_daily_status_page()
    elif page == "Risk Dashboard":
        show_risk_dashboard_page()
    elif page == "Approvals":
        show_approvals_page()
    elif page == "Audit Trail":
        show_audit_trail_page()


def show_copilot_page():
    """Ask Copilot chat interface."""
    st.title("🚀 Delivery Command Center - PM Copilot")
    
    st.markdown("""
    **Example Request:**
    > "Give me a delivery risk report for next 14 days across my program. 
    > Identify blockers, owners, and propose mitigation. Then draft stakeholder 
    > email + JIRA updates. Escalate high-risk items for my approval before posting."
    """)
    
    # Input
    user_request = st.text_area(
        "Enter your request:",
        height=100,
        placeholder="Describe what you need...",
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        project_key = st.text_input("Project Key (optional)", placeholder="PROJ")
    with col2:
        sprint_id = st.text_input("Sprint ID (optional)", placeholder="123")
    
    days_ahead = st.slider("Days Ahead", 7, 30, 14)
    
    if st.button("Run Workflow", type="primary"):
        with st.spinner("Running workflow... This may take a minute."):
            result = make_api_request(
                "/workflow/run",
                method="POST",
                data={
                    "user_request": user_request,
                    "project_key": project_key if project_key else None,
                    "sprint_id": sprint_id if sprint_id else None,
                    "days_ahead": days_ahead,
                },
            )
            
            if result:
                st.session_state.conversation_id = result.get("conversation_id")
                st.session_state.workflow_result = result.get("result", {})
                st.success("Workflow completed!")
                st.rerun()
    
    # Display results
    if st.session_state.workflow_result:
        st.divider()
        st.header("Results")
        
        result = st.session_state.workflow_result
        
        # Risk Report
        if result.get("risk_report"):
            with st.expander("📊 Risk Report", expanded=True):
                try:
                    # Try to display as markdown
                    st.markdown(result["risk_report"])
                except Exception as e:
                    # If markdown fails, display as code
                    st.error(f"Error displaying risk report: {str(e)}")
                    st.code(result["risk_report"], language="text")
        
        # Stakeholder Email
        if result.get("stakeholder_email"):
            with st.expander("📧 Stakeholder Email", expanded=True):
                st.markdown(result["stakeholder_email"])
                if st.button("Copy Email"):
                    st.code(result["stakeholder_email"], language=None)
        
        # Status Report
        if result.get("status_report"):
            with st.expander("📋 Status Report"):
                st.markdown(result["status_report"])
        
        # Proposed Actions
        if result.get("proposed_actions"):
            st.divider()
            st.header("⚠️ Proposed Actions (Require Approval)")
            actions = result["proposed_actions"]
            
            for i, action in enumerate(actions):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{action.get('type', 'unknown').upper()}** on {action.get('issue_key', 'N/A')}")
                        st.markdown(f"**Reason:** {action.get('reason', 'N/A')}")
                        st.json(action.get('payload', {}))
                    with col2:
                        st.button("Approve", key=f"approve_{i}", type="primary")
                        st.button("Reject", key=f"reject_{i}")
                        st.button("Edit", key=f"edit_{i}")
        
        # Evaluation Scores
        if result.get("evaluation_scores"):
            with st.expander("✅ Quality Evaluation"):
                eval_scores = result["evaluation_scores"]
                for metric, data in eval_scores.items():
                    if isinstance(data, dict) and "score" in data:
                        score = data["score"]
                        threshold = data.get("threshold", 0.8)
                        passed = data.get("passed", False)
                        
                        st.progress(score, text=f"{metric}: {score:.2%} (Threshold: {threshold:.2%})")
                        if passed:
                            st.success(f"✓ {metric} passed")
                        else:
                            st.warning(f"⚠ {metric} below threshold")


def show_daily_status_page():
    """Daily status auto-generated report."""
    st.title("📅 Daily Status")
    
    if st.button("Generate Today's Status"):
        with st.spinner("Generating status report..."):
            # This would call the workflow with a daily status request
            result = make_api_request(
                "/workflow/run",
                method="POST",
                data={
                    "user_request": "Generate today's delivery status report with key metrics and blockers",
                    "days_ahead": 7,
                },
            )
            
            if result:
                st.session_state.workflow_result = result.get("result", {})
                st.rerun()
    
    if st.session_state.workflow_result:
        result = st.session_state.workflow_result
        if result.get("status_report"):
            st.markdown(result["status_report"])


def show_risk_dashboard_page():
    """Risk dashboard with visualizations."""
    st.title("📊 Delivery Risk Dashboard")
    
    # Mock data for visualization (replace with real API call)
    risk_data = {
        "High Risk": 5,
        "Medium Risk": 12,
        "Low Risk": 23,
    }
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("High Risk Items", risk_data["High Risk"], delta=-2)
    with col2:
        st.metric("Medium Risk Items", risk_data["Medium Risk"], delta=3)
    with col3:
        st.metric("Low Risk Items", risk_data["Low Risk"], delta=1)
    
    # Risk heatmap
    st.subheader("Risk Heatmap")
    fig = px.bar(
        x=list(risk_data.keys()),
        y=list(risk_data.values()),
        color=list(risk_data.values()),
        color_continuous_scale="Reds",
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Top Blockers
    st.subheader("Top Blockers")
    blockers_data = pd.DataFrame({
        "Issue": ["JIRA-1234", "JIRA-5678", "JIRA-9012"],
        "Risk Score": [95, 87, 82],
        "Days Blocked": [5, 3, 7],
        "Owner": ["Team A", "Team B", "Team C"],
    })
    st.dataframe(blockers_data, use_container_width=True)
    
    # Risk Trends
    st.subheader("Risk Trends (Last 7 Days)")
    dates = pd.date_range(end=datetime.now(), periods=7, freq="D")
    trend_data = pd.DataFrame({
        "Date": dates,
        "High Risk": [6, 7, 5, 6, 5, 5, 5],
        "Medium Risk": [10, 11, 12, 11, 12, 12, 12],
    })
    fig = px.line(trend_data, x="Date", y=["High Risk", "Medium Risk"], title="Risk Trend")
    st.plotly_chart(fig, use_container_width=True)


def show_approvals_page():
    """Approval queue."""
    st.title("✅ Approval Queue")
    
    if st.button("Refresh Approvals"):
        approvals = make_api_request("/approvals/pending")
        if approvals:
            st.session_state.pending_approvals = approvals
    
    if st.session_state.pending_approvals:
        for approval in st.session_state.pending_approvals:
            with st.container():
                st.markdown(f"### {approval['action_type'].upper()} - {approval.get('action_payload', {}).get('issue_key', 'N/A')}")
                st.json(approval["action_payload"])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Approve", key=f"approve_{approval['id']}", type="primary"):
                        make_api_request(
                            f"/approvals/{approval['id']}/approve",
                            method="POST",
                            data={"approval_id": approval["id"], "action": "approve"},
                        )
                        st.success("Approved!")
                        st.rerun()
                with col2:
                    if st.button("Reject", key=f"reject_{approval['id']}"):
                        reason = st.text_input("Rejection reason", key=f"reason_{approval['id']}")
                        if reason:
                            make_api_request(
                                f"/approvals/{approval['id']}/approve",
                                method="POST",
                                data={"approval_id": approval["id"], "action": "reject", "rejection_reason": reason},
                            )
                            st.rerun()
                with col3:
                    st.caption(f"Created: {approval.get('created_at', 'N/A')}")
    else:
        st.info("No pending approvals")


def show_audit_trail_page():
    """Audit trail."""
    st.title("📜 Audit Trail")
    
    st.markdown("""
    View all tool calls and actions taken by the system for audit purposes.
    """)
    
    conversation_id = st.text_input("Conversation ID (optional)", placeholder="Enter conversation ID to filter")
    
    if st.button("Load Audit Trail", type="primary"):
        endpoint = "/audit/tool-calls"
        if conversation_id:
            endpoint += f"?conversation_id={conversation_id}"
        
        tool_calls = make_api_request(endpoint, method="GET")
        
        if tool_calls is not None:
            if len(tool_calls) > 0:
                df = pd.DataFrame(tool_calls)
                st.dataframe(df, use_container_width=True)
                
                # Filter by status
                if "status" in df.columns:
                    st.subheader("Status Distribution")
                    status_counts = df["status"].value_counts()
                    st.bar_chart(status_counts)
                
                # Summary stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Tool Calls", len(tool_calls))
                with col2:
                    if "status" in df.columns:
                        success_count = len(df[df["status"] == "success"]) if "success" in df["status"].values else 0
                        st.metric("Successful", success_count)
                with col3:
                    if "tool_name" in df.columns:
                        unique_tools = df["tool_name"].nunique()
                        st.metric("Unique Tools", unique_tools)
            else:
                st.info("No audit trail entries found. Tool calls will appear here once workflows are executed.")
        else:
            st.warning("Could not load audit trail. Database may not be configured.")


if __name__ == "__main__":
    main()

