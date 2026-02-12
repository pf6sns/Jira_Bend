"""
API routes for exposing Jira issue data to frontend
"""
from fastapi import APIRouter, HTTPException
from services import jira_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jira", tags=["Jira"])

@router.get("/issues")
async def get_all_issues(limit: int = 50, offset: int = 0):
    """
    Fetch Jira issues with pagination
    """
    try:
        # Fetch issues from Jira
        issues = await jira_service.fetch_issues(limit=limit, offset=offset)
        
        if issues is None:
            raise HTTPException(status_code=500, detail="Failed to fetch issues from Jira")
        
        # Transform issues to frontend format
        formatted_issues = []
        for issue in issues:
            key = issue.get("key")
            fields = issue.get("fields", {})
            
            formatted_issues.append({
                "key": key,
                "id": issue.get("id"),
                "fields": {
                    "summary": fields.get("summary", ""),
                    "description": fields.get("description", ""),
                    "status": {
                        "name": fields.get("status", {}).get("name", "")
                    },
                    "priority": {
                        "name": fields.get("priority", {}).get("name", "")
                    } if fields.get("priority") else None,
                    "assignee": {
                        "displayName": fields.get("assignee", {}).get("displayName", ""),
                        "emailAddress": fields.get("assignee", {}).get("emailAddress", "")
                    } if fields.get("assignee") else None,
                    "created": fields.get("created", ""),
                    "updated": fields.get("updated", ""),
                    "issuetype": {
                        "name": fields.get("issuetype", {}).get("name", "")
                    } if fields.get("issuetype") else None
                }
            })
        
        return {"success": True, "issues": formatted_issues}
        
    except Exception as e:
        logger.error(f"Error fetching Jira issues: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/issues/{issue_key}")
async def get_issue_by_key(issue_key: str):
    """
    Fetch a single Jira issue by its key (e.g., PROJ-123)
    """
    try:
        # Fetch specific issue from Jira
        issue = await jira_service.get_issue_by_key(issue_key)
        
        if not issue:
            raise HTTPException(status_code=404, detail=f"Issue {issue_key} not found")
        
        key = issue.get("key")
        fields = issue.get("fields", {})
        
        formatted_issue = {
            "key": key,
            "id": issue.get("id"),
            "fields": {
                "summary": fields.get("summary", ""),
                "description": fields.get("description", ""),
                "status": {
                    "name": fields.get("status", {}).get("name", "")
                },
                "priority": {
                    "name": fields.get("priority", {}).get("name", "")
                } if fields.get("priority") else None,
                "assignee": {
                    "displayName": fields.get("assignee", {}).get("displayName", ""),
                    "emailAddress": fields.get("assignee", {}).get("emailAddress", "")
                } if fields.get("assignee") else None,
                "created": fields.get("created", ""),
                "updated": fields.get("updated", ""),
                "issuetype": {
                    "name": fields.get("issuetype", {}).get("name", "")
                } if fields.get("issuetype") else None
            }
        }
        
        return {"success": True, "issue": formatted_issue}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching issue {issue_key}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
