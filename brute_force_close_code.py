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

# List of potential close codes to try
POTENTIAL_CODES = [
    "solved_permanently",
    "Solved (Permanently)",
    "solved_workaround",
    "Solved (Work Around)",
    "closed_resolved",
    "Closed/Resolved",
    "solution_provided",
    "Solution Provided",
    "fixed",
    "Fixed",
    "done",
    "Done",
    "resolved",
    "Resolved"
]

async def brute_force_close_code():
    # The sys_id from the user's logs
    sys_id = "090b3fff83027e90830b1f65eeaad333" 
    
    print(f"Brute-forcing close_code for sys_id: {sys_id}")
    
    auth = (SERVICENOW_USER, SERVICENOW_PASSWORD)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    
    async with httpx.AsyncClient() as client:
        for code in POTENTIAL_CODES:
            print(f"\nTrying close_code: '{code}'")
            try:
                payload = {
                    "state": "6", 
                    "incident_state": "6",
                    "close_code": code,
                    "close_notes": "Resolved via Brute Force Script"
                }
                res = await client.patch(f"{BASE_URL}/{sys_id}", auth=auth, headers=headers, json=payload)
                
                if res.status_code == 200:
                    print(f"SUCCESS! Valid close_code found: '{code}'")
                    print(f"Response: {res.json()}")
                    return code
                else:
                    print(f"Failed with {res.status_code}")
                    # print(f"Response: {res.text}")
            except Exception as e:
                print(f"Exception: {e}")
                
    print("\nAll codes failed.")
    return None

if __name__ == "__main__":
    asyncio.run(brute_force_close_code())
