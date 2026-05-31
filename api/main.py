from fastapi import FastAPI
from api.routes import webhook, approval, auth
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from agent.graph import init_graph, close_graph
        await init_graph()
    except Exception as e:
        print("Failed to initialize graph:", e)
    yield
    try:
        from agent.graph import close_graph
        await close_graph()
    except Exception as e:
        pass

app = FastAPI(title="PR Review Agent Webhook API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook.router)
app.include_router(approval.router)
app.include_router(auth.router, prefix="/auth")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)