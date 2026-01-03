import random
import httpx
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

async def check_recent_updates():
    """
    Check for Jira issues updated in the last 2 minutes.
    """
    jql = "updated >= -2m ORDER BY updated DESC"
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
                return data.get("issues", [])
            else:
                print(f"Error checking Jira updates: {res.status_code} - {res.text}")
                return []
    except Exception as e:
        print(f"Exception checking Jira updates: {e}")
        return []
