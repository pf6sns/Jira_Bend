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
