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

async def verify_state_update():
    sys_id = "090b3fff83027e90830b1f65eeaad333" 
    
    print(f"Verifying State Update for sys_id: {sys_id}")
    
    auth = (SERVICENOW_USER, SERVICENOW_PASSWORD)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    
    async with httpx.AsyncClient() as client:
        # 1. Update to Resolved (6)
        print("\n--- Attempting Update to '6' (Resolved) ---")
        payload = {
            "state": "6", 
            "incident_state": "6",
            "close_code": "solved_permanently",
            "close_notes": "Resolved via Verification Script"
        }
        try:
            res = await client.patch(f"{BASE_URL}/{sys_id}", auth=auth, headers=headers, json=payload)
            print(f"Update Status: {res.status_code}")
            if res.status_code != 200:
                print(f"Update Failed: {res.text}")
                return
            else:
                print("Update Successful (API returned 200)")
        except Exception as e:
            print(f"Update Exception: {e}")
            return

        # 2. Read back to verify
        print("\n--- Reading back Incident State ---")
        try:
            res = await client.get(f"{BASE_URL}/{sys_id}", auth=auth, headers=headers)
            if res.status_code == 200:
                data = res.json()
                current_state = data['result'].get('state')
                current_incident_state = data['result'].get('incident_state')
                print(f"Current State: {current_state}")
                print(f"Current Incident State: {current_incident_state}")
                
                if str(current_state) == "6":
                    print("SUCCESS: State is '6'")
                else:
                    print(f"FAILURE: State is '{current_state}', expected '6'")
            else:
                print(f"Read failed: {res.status_code}")
        except Exception as e:
            print(f"Read Exception: {e}")

        # 3. Check Valid State Choices
        print("\n--- Checking Valid State Choices ---")
        try:
            choice_url = f"{SERVICENOW_INSTANCE_URL}/api/now/table/sys_choice?sysparm_query=name=incident^element=state"
            res = await client.get(choice_url, auth=auth, headers=headers)
            if res.status_code == 200:
                choices = res.json().get("result", [])
                print("Valid States:")
                for choice in choices:
                    print(f"- Label: {choice.get('label')}, Value: {choice.get('value')}")
            else:
                print(f"Failed to get choices: {res.status_code}")
        except Exception as e:
            print(f"Get Choices Exception: {e}")

if __name__ == "__main__":
    asyncio.run(verify_state_update())
