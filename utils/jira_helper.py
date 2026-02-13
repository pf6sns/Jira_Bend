import httpx
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://flowstream.atlassian.net"
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "").strip()
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "").strip()

AUTH = (JIRA_EMAIL, JIRA_API_TOKEN)

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

async def get_project_users(project_key: str):
    async with httpx.AsyncClient() as client:
        url = f"{BASE_URL}/rest/api/3/user/assignable/search?project={project_key}"
        res = await client.get(url, headers=HEADERS, auth=AUTH)
        res.raise_for_status()
        return res.json()

async def create_jira_issue(project_key, task_data):
    issue_data = {
        "fields": {
            "project": {
                "key": project_key
            },
            "summary": task_data.get("task_title", "Untitled Task"),
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": task_data.get("task_description", "")
                            }
                        ]
                    }
                ]
            },
            "issuetype": {
                "name": "Task"
            }
        }
    }

    async with httpx.AsyncClient() as client:
        url = f"{BASE_URL}/rest/api/3/issue"
        res = await client.post(url, headers=HEADERS, auth=AUTH, json=issue_data)
        res.raise_for_status()
        return res.json()


async def assign_task_by_account(issue_id, account_id):
    async with httpx.AsyncClient() as client:
        url = f"{BASE_URL}/rest/api/3/issue/{issue_id}/assignee"
        payload = {"accountId": account_id}
        res = await client.put(url, headers=HEADERS, auth=AUTH, json=payload)
        res.raise_for_status()
        return res.json() if res.text else {}

async def get_issue_transitions(issue_key):
    async with httpx.AsyncClient() as client:
        url = f"{BASE_URL}/rest/api/3/issue/{issue_key}/transitions"
        res = await client.get(url, headers=HEADERS, auth=AUTH)
        res.raise_for_status()
        return res.json()

async def do_issue_transition(issue_key, transition_id):
    async with httpx.AsyncClient() as client:
        url = f"{BASE_URL}/rest/api/3/issue/{issue_key}/transitions"
        payload = {"transition": {"id": transition_id}}
        res = await client.post(url, headers=HEADERS, auth=AUTH, json=payload)
        res.raise_for_status()
        return res.json() if res.text else {"success": True}
