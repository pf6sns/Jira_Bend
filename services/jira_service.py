import random
import httpx
import logging

logger = logging.getLogger(__name__)
from utils.jira_helper import (
    get_project_users,
    create_jira_issue,
    assign_task_by_account,
    BASE_URL,
    HEADERS,
    AUTH
)

async def create_and_assign_random_developer(issue_data):
    # issue_data now contains 'summary' and 'description' directly
    developers = await get_project_users(issue_data["project_key"])
    if not developers:
        raise Exception("No developers found in the project")

    selected_dev = random.choice(developers)

    task_data = {
        "task_title": issue_data.get("summary", "Untitled Task"),
        "task_description": issue_data.get("description", "")
    }

    issue_response = await create_jira_issue(
        issue_data["project_key"],
        task_data
    )

    issue_id = issue_response.get("key")
    if not issue_id:
        raise Exception("Failed to create Jira issue")

    await assign_task_by_account(issue_id, selected_dev["accountId"])

    return {"issue": issue_id, "assigned_to": selected_dev["displayName"]}

async def fetch_issues(limit: int = 50, offset: int = 0):
    """
    Fetch Jira issues with pagination using the NEW Jira Search JQL API
    """
    jql = "project = 'MA' ORDER BY created DESC"
    # Using the exact endpoint recommended by the 410 error message
    url = f"{BASE_URL}/rest/api/3/search/jql"
    payload = {
        "jql": jql,
        "fields": ["summary", "description", "status", "priority", "assignee", "created", "updated", "issuetype"],
        "maxResults": limit
        # startAt is deprecated in the new token-based search/jql API
    }
    
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(url, headers=HEADERS, auth=AUTH, json=payload)
            if res.status_code == 200:
                data = res.json()
                # The new API might return results in 'issues' or 'results'
                return data.get("issues", []) or data.get("results", [])
            else:
                logger.error(f"Error fetching Jira issues from {url}: {res.status_code} - {res.text}")
                return []
    except Exception as e:
        logger.error(f"Exception fetching Jira issues: {e}")
        return []

async def check_recent_updates():
    """
    Check for Jira issues updated in the last 1 hour using NEW search API
    """
    jql = "project = 'MA' AND updated >= -1h ORDER BY updated DESC"
    url = f"{BASE_URL}/rest/api/3/search/jql"
    payload = {
        "jql": jql,
        "fields": ["summary", "status", "updated"],
        "maxResults": 10
    }
    
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(url, headers=HEADERS, auth=AUTH, json=payload)
            if res.status_code == 200:
                data = res.json()
                return data.get("issues", []) or data.get("results", [])
            else:
                logger.error(f"Error checking recent Jira updates from {url}: {res.status_code} - {res.text}")
                return []
    except Exception as e:
        logger.error(f"Exception checking recent Jira updates: {e}")
        return []

async def update_issue_status_by_servicenow_id(servicenow_id: str, new_status: str):
    """
    Find a Jira issue by its ServiceNow ID in the summary and transition it.
    new_status should be 'Done', 'In Progress', etc.
    """
    # 1. Search for the issue
    jql = f"project = 'MA' AND summary ~ '{servicenow_id}'"
    issues = await fetch_issues_with_jql(jql)
    
    if not issues:
        logger.warning(f"No Jira issue found for ServiceNow ID: {servicenow_id}")
        return {"success": False, "message": "Issue not found"}
    
    issue = issues[0]
    issue_key = issue["key"]
    
    # 2. Get available transitions
    try:
        from utils.jira_helper import get_issue_transitions, do_issue_transition
        transitions_data = await get_issue_transitions(issue_key)
        transitions = transitions_data.get("transitions", [])
        
        # 3. Find target transition
        # We'll be flexible with status names
        target_transition_id = None
        for t in transitions:
            if t["to"]["name"].lower() == new_status.lower():
                target_transition_id = t["id"]
                break
        
        if not target_transition_id:
            # Fallback: if looking for 'Done', try 'Resolved' or 'Closed'
            if new_status.lower() in ["done", "resolved", "closed"]:
                for t in transitions:
                    if t["to"]["name"].lower() in ["done", "resolved", "closed", "complete"]:
                        target_transition_id = t["id"]
                        break
        
        if not target_transition_id:
            logger.error(f"Could not find transition to '{new_status}' for {issue_key}")
            return {"success": False, "available_statuses": [t["to"]["name"] for t in transitions]}
        
        # 4. Perform transition
        await do_issue_transition(issue_key, target_transition_id)
        logger.info(f"Successfully transitioned Jira issue {issue_key} to {new_status}")
        return {"success": True, "issue_key": issue_key, "new_status": new_status}
        
    except Exception as e:
        logger.error(f"Error transitioning Jira issue: {e}")
        return {"success": False, "error": str(e)}

async def fetch_issues_with_jql(jql: str, limit: int = 50):
    url = f"{BASE_URL}/rest/api/3/search/jql"
    payload = {
        "jql": jql,
        "fields": ["summary", "status"],
        "maxResults": limit
    }
    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=HEADERS, auth=AUTH, json=payload)
        if res.status_code == 200:
            return res.json().get("issues", [])
        return []
