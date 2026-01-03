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

async def process_issue_update(issue_key, status, summary):
    """
    Process an issue update: Check status and update ServiceNow if needed.
    """
    print(f"Processing issue {issue_key}: Status='{status}', Summary='{summary}'")
    
    # Check if status is Resolved, Done, or Closed
    if status in ["Resolved", "Done", "Closed"]:
        # Extract ServiceNow Ticket ID from summary
        # Look for INC followed by digits, anywhere in the string
        import re
        match = re.search(r"(INC\d+)", summary)
        
        if match:
            servicenow_id = match.group(1)
            print(f"Found ServiceNow ID: {servicenow_id}")
            
            # Update ServiceNow
            from services import servicenow_service
            result = await servicenow_service.update_incident_status(servicenow_id, "6")
            
            return {"status": "processed", "servicenow_update": result}
        else:
            print("No ServiceNow ID found in summary")
            return {"status": "ignored", "reason": "No ServiceNow ID in summary"}
            
    return {"status": "ignored", "reason": f"Status {status} not tracked"}

async def handle_webhook_event(payload: dict):
    """
    Handle incoming Jira webhook events.
    """
    try:
        # Log the entire payload for debugging
        import json
        print(f"DEBUG: Received Webhook Payload:\n{json.dumps(payload, indent=2)}")
        
        event_type = payload.get("webhookEvent")
        print(f"DEBUG: Event Type: {event_type}")
        
        # We only care about issue updates
        if event_type != "jira:issue_updated":
            print(f"DEBUG: Ignoring event type {event_type}")
            return {"status": "ignored", "reason": f"Event type {event_type} not handled"}
            
        issue = payload.get("issue", {})
        fields = issue.get("fields", {})
        status = fields.get("status", {}).get("name")
        summary = fields.get("summary", "")
        
        return await process_issue_update(issue.get("key"), status, summary)
        
    except Exception as e:
        print(f"Error handling webhook: {e}")
        return {"status": "error", "message": str(e)}
