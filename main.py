from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from fastapi.responses import HTMLResponse
from statistics import mean
from fastapi.templating import Jinja2Templates


app = FastAPI()

all_sessions = []  # Stores all behavior validation attempts for analytics
templates = Jinja2Templates(directory="templates")


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

    if data.mouseMoves < 1000 and data.keypresses < 1000 and data.scrolls < 1:
        suspicious = True
        reasons.append("No interaction during session interval")

    if data.timing and data.timing[0] < 500:
        suspicious = True
        reasons.append("Interaction too short")

    all_sessions.append({
        # "sessionId": data.sessionId,
        "mouseMoves": data.mouseMoves,
        "keypresses": data.keypresses,
        "scrolls": data.scrolls,
        "clicks": data.clicks,
        "timing": data.timing,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Suspicious" if suspicious else "Legit",
        "reason": ", ".join(reasons) if suspicious else "-"
    })

    return {
        "success": not suspicious,
        "message": "Session behavior evaluated",
        "reasons": reasons
    }


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    legit = [s for s in all_sessions if s["status"] == "Legit"]
    suspicious = [s for s in all_sessions if s["status"] == "Suspicious"]

    avg_clicks = round(mean([s["clicks"] for s in all_sessions]), 2) if all_sessions else 0
    avg_keys = round(mean([s["keypresses"] for s in all_sessions]), 2) if all_sessions else 0

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "total": len(all_sessions),
        "legit": len(legit),
        "suspicious": len(suspicious),
        "avg_clicks": avg_clicks,
        "avg_keys": avg_keys,
        "suspicious_rows": suspicious[-10:]
    })
