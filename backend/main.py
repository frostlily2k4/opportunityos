import json
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agent.pipeline import run_pipeline_stream

app = FastAPI(title="OpportunityOS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class DiscoverRequest(BaseModel):
    query: str
    profile: dict = {}


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/discover")
async def discover(req: DiscoverRequest):
    async def event_stream():
        async for update in run_pipeline_stream(req.query, req.profile):
            yield f"data: {json.dumps(update)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
