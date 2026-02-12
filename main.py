from fastapi import FastAPI
from routes import jira_route, jira_data_routes
from contextlib import asynccontextmanager
import asyncio
from services import jira_service
from controllers import jira_controller

async def poll_jira_updates():
    """
    Background task to poll Jira for updates every 10 seconds.
    """
    while True:
        try:
            print("Polling Jira for updates...")
            issues = await jira_service.check_recent_updates()
            if issues:
                print(f"Found {len(issues)} updated issues.")
                for issue in issues:
                    key = issue.get("key")
                    fields = issue.get("fields", {})
                    status = fields.get("status", {}).get("name")
                    summary = fields.get("summary", "")
                    
                    await jira_controller.process_issue_update(key, status, summary)
            # Silence log when no updates found to reduce clutter
                
        except Exception as e:
            print(f"Error in polling loop: {e}")
            
        await asyncio.sleep(10)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    task = asyncio.create_task(poll_jira_updates())
    yield
    # Shutdown
    task.cancel()

app = FastAPI(title="Jira Auto Task Assigner", lifespan=lifespan)

# Add CORS middleware to allow frontend requests
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jira_route.router)
app.include_router(jira_data_routes.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
