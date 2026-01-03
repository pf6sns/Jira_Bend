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

async def debug_servicenow_update():
    # The sys_id from the user's logs
    sys_id = "090b3fff83027e90830b1f65eeaad333" 
    
    print(f"Debugging ServiceNow Update for sys_id: {sys_id}")
    print(f"URL: {BASE_URL}/{sys_id}")
    print(f"User: {SERVICENOW_USER}")
    
    auth = (SERVICENOW_USER, SERVICENOW_PASSWORD)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    
    async with httpx.AsyncClient() as client:
        # Test 1: GET (Confirm Read Access)
        print("\n--- Test 1: GET Request ---")
        try:
            res = await client.get(f"{BASE_URL}/{sys_id}", auth=auth, headers=headers)
            print(f"Status: {res.status_code}")
            if res.status_code == 200:
                print("Read access confirmed.")
                data = res.json()
                print(f"Current State: {data['result'].get('state')}")
                print(f"Current Short Description: {data['result'].get('short_description')}")
                print(f"Available Fields: {list(data['result'].keys())}")
                print(f"Close Code: {data['result'].get('close_code')}")
                print(f"Resolution Code: {data['result'].get('resolution_code')}")
            else:
                print(f"Read failed: {res.text}")
        except Exception as e:
            print(f"GET Exception: {e}")

        # Test 1.5: Get Valid Close Codes
        print("\n--- Test 1.5: Get Valid Close Codes ---")
        try:
            choice_url = f"{SERVICENOW_INSTANCE_URL}/api/now/table/sys_choice?sysparm_query=name=incident^element=close_code"
            res = await client.get(choice_url, auth=auth, headers=headers)
            if res.status_code == 200:
                choices = res.json().get("result", [])
                print("Valid Close Codes:")
                for choice in choices:
                    print(f"- Label: {choice.get('label')}, Value: {choice.get('value')}")
            else:
                print(f"Failed to get choices: {res.status_code}")
        except Exception as e:
            print(f"Get Choices Exception: {e}")

        # Test 2: PATCH Short Description (Confirm Write Access to simple field)
        print("\n--- Test 2: PATCH Short Description ---")
        try:
            payload = {"short_description": "Updated via Debug Script"}
            res = await client.patch(f"{BASE_URL}/{sys_id}", auth=auth, headers=headers, json=payload)
            print(f"Status: {res.status_code}")
            print(f"Response: {res.text}")
        except Exception as e:
            print(f"PATCH Description Exception: {e}")

        # Test 3: PATCH State (The failing request)
        print("\n--- Test 3: PATCH State to '6' (Resolved) ---")
        try:
            payload = {
                "state": "6", 
                "incident_state": "6",
                "close_code": "Closed/Resolved",
                "close_notes": "Resolved via Debug Script"
            }
            res = await client.patch(f"{BASE_URL}/{sys_id}", auth=auth, headers=headers, json=payload)
            print(f"Status: {res.status_code}")
            print(f"Response: {res.text}")
        except Exception as e:
            print(f"PATCH State Exception: {e}")

if __name__ == "__main__":
    asyncio.run(debug_servicenow_update())
