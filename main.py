from fastapi import FastAPI
from routes import jira_route

app = FastAPI(title="Jira Auto Task Assigner")

app.include_router(jira_route.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
