import httpx
import os
from dotenv import load_dotenv

load_dotenv()

SERVICENOW_INSTANCE_URL = os.getenv("SERVICENOW_INSTANCE_URL", "").strip()
SERVICENOW_USER = os.getenv("SERVICENOW_USERNAME", "").strip()
SERVICENOW_PASSWORD = os.getenv("SERVICENOW_PASSWORD", "").strip()

# Ensure URL doesn't have a trailing slash for consistency
if SERVICENOW_INSTANCE_URL.endswith("/"):
    SERVICENOW_INSTANCE_URL = SERVICENOW_INSTANCE_URL[:-1]

BASE_URL = f"{SERVICENOW_INSTANCE_URL}/api/now/table/incident"

async def update_incident_status(incident_number: str, state: str):
    """
    Update the status of a ServiceNow incident.
    
    Args:
        incident_number (str): The incident number (e.g., INC0010001).
        state (str): The new state code (e.g., '6' for Resolved).
    """
    if not all([SERVICENOW_INSTANCE_URL, SERVICENOW_USER, SERVICENOW_PASSWORD]):
        print("ServiceNow credentials missing in .env")
        return None

    # First, get the sys_id of the incident
    async with httpx.AsyncClient() as client:
        auth = (SERVICENOW_USER, SERVICENOW_PASSWORD)
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        
        # Query to find sys_id
        query_url = f"{BASE_URL}?sysparm_query=number={incident_number}&sysparm_limit=1"
        try:
            res = await client.get(query_url, auth=auth, headers=headers)
            res.raise_for_status()
            data = res.json()
            
            if not data.get("result"):
                print(f"Incident {incident_number} not found in ServiceNow")
                return None
                
            sys_id = data["result"][0]["sys_id"]
            
            # Now update the incident
            update_url = f"{BASE_URL}/{sys_id}"
            
            payload = {"state": state, "incident_state": state}
            
            # If resolving (6) or closing (7), add mandatory fields
            if state in ["6", "7"]:
                # Try multiple close codes as different incidents/categories might require different values
                close_codes = ["solved_permanently", "Solution Provided", "Closed/Resolved", "Resolved"]
                
                for code in close_codes:
                    payload["close_code"] = code
                    payload["close_notes"] = "Resolved via Jira Automation."
                    
                    try:
                        print(f"Attempting update with close_code='{code}'...")
                        update_res = await client.patch(update_url, auth=auth, headers=headers, json=payload)
                        if update_res.status_code == 200:
                            print(f"Successfully updated ServiceNow incident {incident_number} to state {state} using code '{code}'")
                            return update_res.json()
                        elif update_res.status_code == 403:
                            print(f"Failed with code '{code}' (403), trying next...")
                            continue
                        else:
                            update_res.raise_for_status()
                    except Exception as e:
                        print(f"Error with code '{code}': {e}")
                        continue
                
                print(f"All close codes failed for {incident_number}")
                return None
            else:
                # For non-resolving states, just update
                update_res = await client.patch(update_url, auth=auth, headers=headers, json=payload)
                update_res.raise_for_status()
                print(f"Successfully updated ServiceNow incident {incident_number} to state {state}")
                return update_res.json()
            
        except Exception as e:
            print(f"Error updating ServiceNow incident: {str(e)}")
            return None
