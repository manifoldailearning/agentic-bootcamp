"""ServiceNow integration client."""
from typing import List, Dict, Any, Optional
import requests
from requests.auth import HTTPBasicAuth
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings

logger = structlog.get_logger()


class ServiceNowClient:
    """ServiceNow API client."""
    
    def __init__(self):
        if not settings.servicenow_instance:
            logger.warning("ServiceNow not configured")
            self.enabled = False
            return
        
        self.enabled = True
        self.base_url = f"https://{settings.servicenow_instance}.service-now.com/api/now"
        self.auth = HTTPBasicAuth(settings.servicenow_username, settings.servicenow_password)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_change_requests(
        self,
        days_ahead: int = 14
    ) -> List[Dict[str, Any]]:
        """Get change requests."""
        if not self.enabled:
            return []
        
        # Query for upcoming change requests
        url = f"{self.base_url}/table/change_request"
        params = {
            "sysparm_query": "active=true",
            "sysparm_limit": 100,
        }
        
        try:
            response = requests.get(url, auth=self.auth, headers=self.headers, params=params)
            response.raise_for_status()
            
            results = response.json().get("result", [])
            return [
                {
                    "number": cr.get("number"),
                    "short_description": cr.get("short_description"),
                    "state": cr.get("state"),
                    "priority": cr.get("priority"),
                    "assigned_to": cr.get("assigned_to", {}).get("display_value") if isinstance(cr.get("assigned_to"), dict) else None,
                    "start_date": cr.get("start_date"),
                    "end_date": cr.get("end_date"),
                }
                for cr in results
            ]
        except Exception as e:
            logger.error("Failed to fetch change requests", error=str(e))
            return []
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_incidents(
        self,
        days_ahead: int = 14
    ) -> List[Dict[str, Any]]:
        """Get incidents."""
        if not self.enabled:
            return []
        
        url = f"{self.base_url}/table/incident"
        params = {
            "sysparm_query": "active=true",
            "sysparm_limit": 100,
        }
        
        try:
            response = requests.get(url, auth=self.auth, headers=self.headers, params=params)
            response.raise_for_status()
            
            results = response.json().get("result", [])
            return [
                {
                    "number": inc.get("number"),
                    "short_description": inc.get("short_description"),
                    "state": inc.get("state"),
                    "priority": inc.get("priority"),
                    "severity": inc.get("severity"),
                    "assigned_to": inc.get("assigned_to", {}).get("display_value") if isinstance(inc.get("assigned_to"), dict) else None,
                    "opened_at": inc.get("opened_at"),
                }
                for inc in results
            ]
        except Exception as e:
            logger.error("Failed to fetch incidents", error=str(e))
            return []

