import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

print("Checking Environment Variables:")
print(f"SERVICENOW_INSTANCE_URL: {os.getenv('SERVICENOW_INSTANCE_URL')}")
print(f"SERVICENOW_USERNAME: {os.getenv('SERVICENOW_USERNAME')}")
print(f"SERVICENOW_PASSWORD: {'*' * 8 if os.getenv('SERVICENOW_PASSWORD') else 'None'}")

async def test_webhook():
    url = "http://127.0.0.1:8000/jira/webhook"
    
    # Payload with "Closed" status and INC number without brackets
    payload = {
        "webhookEvent": "jira:issue_updated",
        "issue": {
            "key": "TEST-456",
            "fields": {
                "summary": "INC0012345 - Critical Issue (No Brackets)",
                "status": {
                    "name": "Closed"
                }
            }
        }
    }
    
    print(f"\nSending webhook to {url}...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {response.json()}")
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    asyncio.run(test_webhook())
