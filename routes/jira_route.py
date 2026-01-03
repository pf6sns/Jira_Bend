from fastapi import APIRouter, HTTPException
from controllers import jira_controller
from pydantic import BaseModel

router = APIRouter(prefix="/jira", tags=["Jira"])

class IssueCreateRequest(BaseModel):
    summary: str
    description: str

@router.post("/auto-assign")
async def auto_assign_task(issue: IssueCreateRequest):
    try:
        result = await jira_controller.create_and_assign_issue(issue)
        return {"message": "Task created and assigned successfully", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def jira_webhook(payload: dict):
    """
    Endpoint to receive Jira webhooks
    """
    try:
        result = await jira_controller.handle_webhook_event(payload)
        return result
    except Exception as e:
        # Log error but return 200 to Jira so it doesn't retry indefinitely
        print(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}
