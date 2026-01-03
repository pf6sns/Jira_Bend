import asyncio
from services import jira_service
from controllers import jira_controller

async def test_polling_logic():
    print("Testing Polling Logic (One Iteration)...")
    try:
        # 1. Fetch updates
        print("Fetching updates from Jira...")
        issues = await jira_service.check_recent_updates()
        
        if issues:
            print(f"Found {len(issues)} updated issues.")
            for issue in issues:
                key = issue.get("key")
                fields = issue.get("fields", {})
                status = fields.get("status", {}).get("name")
                summary = fields.get("summary", "")
                
                print(f"Processing {key}...")
                # 2. Process update
                result = await jira_controller.process_issue_update(key, status, summary)
                print(f"Result for {key}: {result}")
        else:
            print("No recent updates found (this is expected if no tickets were updated in the last 2 mins).")
            
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    asyncio.run(test_polling_logic())
