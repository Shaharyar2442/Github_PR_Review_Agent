from fastapi import FastAPI
from api.routes.webhook import router as webhook_router
from api.routes.approval import router as approval_router
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Open the database connection pool on startup
    try:
        from agent.graph import pool
        if pool is not None:
            await pool.open()
    except ImportError:
        pass
    yield
    # Close the pool on shutdown
    try:
        from agent.graph import pool
        if pool is not None:
            await pool.close()
    except ImportError:
        pass

# TODO: Initialize your app here!
app=FastAPI(title="PR Review Agent", lifespan=lifespan)



app.include_router(webhook_router)
app.include_router(approval_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)