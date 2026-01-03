import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

SERVICENOW_INSTANCE_URL = os.getenv("SERVICENOW_INSTANCE_URL", "").strip()
SERVICENOW_USER = os.getenv("SERVICENOW_USERNAME", "").strip()
SERVICENOW_PASSWORD = os.getenv("SERVICENOW_PASSWORD", "").strip()

if SERVICENOW_INSTANCE_URL.endswith("/"):
    SERVICENOW_INSTANCE_URL = SERVICENOW_INSTANCE_URL[:-1]

BASE_URL = f"{SERVICENOW_INSTANCE_URL}/api/now/table/incident"

async def debug_specific_incident():
    # The failing sys_id from the user's logs
    sys_id = "e0522a7383863e90830b1f65eeaad3be" 
    
    print(f"Debugging INC0010038 (sys_id: {sys_id})")
    
    auth = (SERVICENOW_USER, SERVICENOW_PASSWORD)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    
    async with httpx.AsyncClient() as client:
        # 1. GET current state
        print("\n--- Current State ---")
        try:
            res = await client.get(f"{BASE_URL}/{sys_id}", auth=auth, headers=headers)
            if res.status_code == 200:
                data = res.json()
                result = data['result']
                print(f"Number: {result.get('number')}")
                print(f"State: {result.get('state')}")
                print(f"Incident State: {result.get('incident_state')}")
                print(f"Close Code: {result.get('close_code')}")
                print(f"Close Notes: {result.get('close_notes')}")
                print(f"Category: {result.get('category')}")
            else:
                print(f"Read failed: {res.status_code} - {res.text}")
                return
        except Exception as e:
            print(f"Read Exception: {e}")
            return

        # 2. Brute Force for this incident
        print("\n--- Brute Forcing Close Code ---")
        codes = [
            "solved_permanently", "Solved (Permanently)",
            "solved_workaround", "Solved (Work Around)",
            "closed_resolved", "Closed/Resolved",
            "solution_provided", "Solution Provided",
            "fixed", "Fixed",
            "done", "Done",
            "resolved", "Resolved"
        ]
        
        for code in codes:
            print(f"Trying: {code}")
            payload = {
                "state": "6", 
                "incident_state": "6",
                "close_code": code,
                "close_notes": "Resolved via Specific Debug Script"
            }
            try:
                res = await client.patch(f"{BASE_URL}/{sys_id}", auth=auth, headers=headers, json=payload)
                if res.status_code == 200:
                    print(f"SUCCESS! Valid code: {code}")
                    return
                else:
                    print(f"Failed ({res.status_code}): {res.text}")
            except Exception as e:
                print(f"Update Exception: {e}")

if __name__ == "__main__":
    asyncio.run(debug_specific_incident())
