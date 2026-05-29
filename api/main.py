from fastapi import FastAPI
from api.routes.webhook import router as webhook_router
from api.routes.approval import router as approval_router

# ─── YOUR TURN (PHASE 5) ──────────────────────────────────────
# Goal: Initialize the FastAPI app and register our routers.
# Hint:
# 1. Create a FastAPI app instance: `app = FastAPI(title="PR Review Agent")`
# 2. Include the webhook router: `app.include_router(webhook_router)`
# 3. Include the approval router: `app.include_router(approval_router)`
# Expected result: A functional FastAPI app that routes traffic correctly.
# ────────────────────────────────────────────────────────────
# TODO: Initialize your app here!
app=FastAPI(title="PR Review Agent")
app.include_router(webhook_router)
app.include_router(approval_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)