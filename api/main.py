from fastapi import FastAPI
from api.routes.webhook import router as webhook_router
from api.routes.approval import router as approval_router
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