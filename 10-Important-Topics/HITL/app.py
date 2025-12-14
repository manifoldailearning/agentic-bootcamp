# app.py
import os
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from my_agent import agent

app = FastAPI(title="LangGraph Deployment Demo", version="1.0.0")


class InvokeRequest(BaseModel):
    user_input: str = Field(..., min_length=1)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/invoke")
def invoke(req: InvokeRequest):
    try:
        trace_id = str(uuid.uuid4())

        # This is the key call for your class:
        result = agent.invoke({"user_input": req.user_input, "trace_id": trace_id})

        return {
            "trace_id": trace_id,
            "plan": result.get("plan"),
            "answer": result.get("answer"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph execution failed: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8002")),
        reload=True,
    )
