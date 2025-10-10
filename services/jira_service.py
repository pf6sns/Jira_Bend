import random
from utils.jira_helper import (
    get_project_users,
    create_jira_issue,
    assign_task_by_account
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
