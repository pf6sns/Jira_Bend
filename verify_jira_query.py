import httpx
import os
import asyncio
from dotenv import load_dotenv
import base64

load_dotenv()

JIRA_EMAIL = os.getenv("JIRA_EMAIL", "").strip()
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "").strip()
BASE_URL = "https://abithan.atlassian.net"

async def check_jira_updates():
    if not JIRA_EMAIL or not JIRA_API_TOKEN:
        print("Missing Jira credentials")
        return

    auth_str = f"{JIRA_EMAIL}:{JIRA_API_TOKEN}"
    auth_bytes = auth_str.encode('ascii')
    base64_auth = base64.b64encode(auth_bytes).decode('ascii')

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Basic {base64_auth}"
    }
    
    # JQL to find all issues in project 'MA'
    jql = "project = 'MA' ORDER BY updated DESC"
    
    url = f"{BASE_URL}/rest/api/3/search/jql"
    payload = {
        "jql": jql,
        "fields": ["summary", "status", "updated", "created"],
        "maxResults": 100
    }
    
    print(f"Querying Jira (POST): {url}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Response Data: {data}")
                # Try to parse based on inspection
                if 'issues' in data:
                    print(f"Found {len(data['issues'])} issues.")
                    for issue in data['issues'][:5]:
                        status = issue['fields']['status']['name']
                        created = issue['fields']['created']
                        print(f"- {issue['key']} Created: {created} Status: {status}")
            else:
                print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(check_jira_updates())
