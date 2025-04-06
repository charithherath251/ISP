from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:5500"] if you want to restrict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BehaviorData(BaseModel):
    mouseMoves: int
    keypresses: int
    scrolls: int
    clicks: int
    timing: List[int]

@app.post("/validate-user")
async def validate_user(data: BehaviorData):
    suspicious = False
    reasons = []

    if data.mouseMoves < 1000 and data.keypresses < 1000 and data.scrolls < 1000:
        suspicious = True
        reasons.append("Minimal activity")

    if data.timing and data.timing[0] < 500:
        suspicious = True
        reasons.append("Interaction too fast")

    if suspicious:
        return {"success": False, "message": "Suspicious behavior detected", "reasons": reasons}

    return {"success": True, "message": "User is legitimate"}


@app.post("/validate-session")
async def validate_session(data: BehaviorData):
    suspicious = False
    reasons = []

    if data.mouseMoves < 1000 and data.keypresses < 1000 and data.scrolls < 1000:
        suspicious = True
        reasons.append("No interaction during session interval")

    if data.timing and data.timing[0] < 500:
        suspicious = True
        reasons.append("Interaction too short")

    return {
        "success": not suspicious,
        "message": "Session behavior evaluated",
        "reasons": reasons
    }
