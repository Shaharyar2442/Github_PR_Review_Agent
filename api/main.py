from fastapi import FastAPI
from api.routes import webhook, approval, auth
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from config import ALLOWED_ORIGINS


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from agent.graph import init_graph, close_graph
        await init_graph()
        logger.info("Agent graph initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize graph: {e}")
    yield
    try:
        from agent.graph import close_graph
        await close_graph()
    except Exception:
        pass

app = FastAPI(title="PR Review Agent Webhook API", lifespan=lifespan)

# Security: Use explicit origin allow-list instead of wildcard.
# Set ALLOWED_ORIGINS env var as comma-separated list in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(webhook.router)
app.include_router(approval.router)
app.include_router(auth.router, prefix="/auth")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)