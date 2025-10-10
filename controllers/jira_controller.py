from services import jira_service

PROJECT_KEY = "MA"
PROJECT_ID = "10002"

async def create_and_assign_issue(issue):
    issue_data = {
        "project_key": PROJECT_KEY,
        "project_id": PROJECT_ID,
        "summary": issue.summary,
        "description": issue.description
    }
    return await jira_service.create_and_assign_random_developer(issue_data)
