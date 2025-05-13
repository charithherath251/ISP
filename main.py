# from fastapi import FastAPI, Request
# from pydantic import BaseModel
# from typing import List
# from fastapi.middleware.cors import CORSMiddleware
# from datetime import datetime, timedelta
# from fastapi.responses import HTMLResponse
# from statistics import mean
# from fastapi.templating import Jinja2Templates
# from collections import defaultdict, Counter

# app = FastAPI()

# all_sessions = []  # Stores all behavior validation attempts for analytics
# templates = Jinja2Templates(directory="templates")


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Or ["http://localhost:5500"] if you want to restrict
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# class MouseMovement(BaseModel):
#     x: float
#     y: float
#     timestamp: int

# class BehaviorData(BaseModel):
#     mouseMoves: int
#     keypresses: int
#     scrolls: int
#     clicks: int
#     mouseMovements: List[MouseMovement]
#     timing: List[int]
#     startTime: int

# @app.post("/validate-user")
# async def validate_user(data: BehaviorData):
#     suspicious = False
#     reasons = []

#     if data.mouseMoves < 1000 and data.keypresses < 1000 and data.scrolls < 1000:
#         suspicious = True
#         reasons.append("Minimal activity")

#     if data.timing and data.timing[0] < 500:
#         suspicious = True
#         reasons.append("Interaction too fast")

#     if suspicious:
#         return {"success": False, "message": "Suspicious behavior detected", "reasons": reasons}

#     return {"success": True, "message": "User is legitimate"}


# @app.post("/validate-session")
# async def validate_session(data: BehaviorData):
#     suspicious = False
#     reasons = []

#     if data.mouseMoves < 1000 and data.keypresses < 1000 and data.scrolls < 1:
#         suspicious = True
#         reasons.append("No interaction during session interval")

#     if data.timing and data.timing[0] < 500:
#         suspicious = True
#         reasons.append("Interaction too short")

#     all_sessions.append({
#         # "sessionId": data.sessionId,
#         "mouseMoves": data.mouseMoves,
#         "keypresses": data.keypresses,
#         "scrolls": data.scrolls,
#         "clicks": data.clicks,
#         "timing": data.timing,
#         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "status": "Suspicious" if suspicious else "Legit",
#         "reason": ", ".join(reasons) if suspicious else "-"
#     })

#     return {
#         "success": not suspicious,
#         "message": "Session behavior evaluated",
#         "reasons": reasons
#     }


# @app.get("/dashboard", response_class=HTMLResponse)
# def dashboard(request: Request):
#     legit = [s for s in all_sessions if s["status"] == "Legit"]
#     suspicious = [s for s in all_sessions if s["status"] == "Suspicious"]

#     # avg_clicks = round(mean([s["clicks"] for s in all_sessions]), 2) if all_sessions else 0
#     # avg_keys = round(mean([s["keypresses"] for s in all_sessions]), 2) if all_sessions else 0

#     # Safely parse timestamp if it's a string
#     for s in all_sessions:
#         if isinstance(s["timestamp"], str):
#             s["timestamp"] = datetime.strptime(s["timestamp"], "%Y-%m-%d %H:%M:%S")


#     # daily_counts = Counter(s["timestamp"].strftime("%Y-%m-%d") for s in all_sessions)
#     # status_counts = Counter(s["status"] for s in all_sessions)
#     # hour_counts = Counter(s["timestamp"].strftime("%H") for s in all_sessions)

#     # from collections import defaultdict
#     # trend_data = defaultdict(lambda: {"Legit": 0, "Suspicious": 0})

#     # for s in all_sessions:
#     #     day = s["timestamp"].strftime("%Y-%m-%d")
#     #     trend_data[day][s["status"]] += 1




#     # return templates.TemplateResponse("dashboard.html", {
#     #     "request": request,
#     #     "total": len(all_sessions),
#     #     "legit": len(legit),
#     #     "suspicious": len(suspicious),
#     #     "avg_clicks": avg_clicks,
#     #     "avg_keys": avg_keys,
#     #     "suspicious_rows": suspicious[-10:]
#     # })
#     now = datetime.now()
#     total_today = sum(1 for s in all_sessions if s['timestamp'].date() == now.date())
#     total_week = sum(1 for s in all_sessions if now - timedelta(days=7) <= s['timestamp'] <= now)
#     total_month = sum(1 for s in all_sessions if now.month == s['timestamp'].month)

#     status_counts = [
#         sum(1 for s in all_sessions if s['status'] == 'Legit'),
#         sum(1 for s in all_sessions if s['status'] == 'Suspicious')
#     ]

#     login_by_hour = Counter(s['timestamp'].strftime('%H') for s in all_sessions)
#     login_hours = list(range(24))
#     login_counts = [login_by_hour.get(f"{h:02}", 0) for h in login_hours]

#     trend_data = defaultdict(lambda: {"Legit": 0, "Suspicious": 0})
#     for s in all_sessions:
#         day = s['timestamp'].strftime('%Y-%m-%d')
#         trend_data[day][s['status']] += 1

#     trend_labels = list(sorted(trend_data.keys()))
#     trend_legit = [trend_data[d]['Legit'] for d in trend_labels]
#     trend_suspicious = [trend_data[d]['Suspicious'] for d in trend_labels]

#     return templates.TemplateResponse("dashboard.html", {
#         "request": request,
#         "total_today": total_today,
#         "total_week": total_week,
#         "total_month": total_month,
#         "status_counts": status_counts,
#         "login_hours": login_hours,
#         "login_counts": login_counts,
#         "trend_labels": trend_labels,
#         "trend_legit": trend_legit,
#         "trend_suspicious": trend_suspicious,
#         "suspicious_rows": suspicious[-10:]
#     })

# main.py
import csv
import os
from datetime import datetime
from fastapi import FastAPI
from typing import Dict, Any
from models import UserActivity
from validators import average_mouse_speed, movement_variance, is_constant_scroll_speed, analyze_keystroke_timings
# from validators import analyze_keystroke_stats
from thresholds import HUMAN_THRESHOLDS
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

PRE_LOGIN_CSV_FILE = "Prelogin_user_behavior_log.csv"
POST_LOGIN_CSV_FILE = "Postlogin_user_behavior_log.csv"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:5500"] if you want to restrict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/validate-user")
async def validate_user(activity: UserActivity) -> Dict[str, Any]:
    reasons = []
    
    if activity.mouseMoves < HUMAN_THRESHOLDS["min_mouse_moves"]:
        reasons.append("Too few mouse movements.")
    
    if activity.clicks < HUMAN_THRESHOLDS["min_clicks"]:
        reasons.append("Not enough clicks.")
    
    if activity.timing[0] < HUMAN_THRESHOLDS["min_interaction_time"]:
        reasons.append("Interaction was suspiciously quick.")
    
    avg_speed = average_mouse_speed(activity.mouseMovements)
    if not (HUMAN_THRESHOLDS["avg_speed_range"][0] <= avg_speed <= HUMAN_THRESHOLDS["avg_speed_range"][1]):
        reasons.append(f"Unnatural mouse speed detected: {avg_speed:.2f}px/s.")
    
    variance = movement_variance(activity.mouseMovements, avg_speed)
    if not (HUMAN_THRESHOLDS["variance_range"][0] <= variance <= HUMAN_THRESHOLDS["variance_range"][1]):
        reasons.append(f"Unnatural mouse movement patterns detected (variance: {variance:.2f}).")

    if is_constant_scroll_speed(activity.scrollEvents, HUMAN_THRESHOLDS["scroll_speed_tolerance"]):
        reasons.append("Constant scrolling speed detected.")

    keystroke_result = analyze_keystroke_timings(activity.keystrokeTimings)
    if keystroke_result["suspicious"]:
        reasons.append(f"Suspicious typing pattern (mean: {keystroke_result['mean']:.2f} ms, stddev: {keystroke_result['std_dev']:.2f} ms)")
    
    success = len(reasons) == 0

      # Ensure CSV file exists with header
    file_exists = os.path.isfile(PRE_LOGIN_CSV_FILE)
    
    with open(PRE_LOGIN_CSV_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
    
        keystroke_resul = analyze_keystroke_timings(activity.keystrokeTimings)
        keystroke_result["mean"]
        keystroke_result["std_dev"]

    
        triggerTime = datetime.fromtimestamp(activity.startTime / 1000)

        writer.writerow([
            triggerTime,
            activity.mouseMoves,
            activity.keypresses,
            activity.scrolls,
            activity.clicks,
            activity.timing,
            activity.timing[0],
            round(avg_speed, 2),
            round(variance, 2),
            round(keystroke_result["mean"], 2),
            round(keystroke_result["std_dev"], 2)
        ])
    
    return {"success": success, "reasons": reasons}

@app.post("/validate-session")
async def validate_session(activity: UserActivity) -> Dict[str, Any]:
    reasons = []
    
    if activity.mouseMoves < HUMAN_THRESHOLDS["min_mouse_moves"]:
        reasons.append("Too few mouse movements.")
    
    if activity.clicks < HUMAN_THRESHOLDS["min_clicks"]:
        reasons.append("Not enough clicks.")

    avg_speed = average_mouse_speed(activity.mouseMovements)
    if not (HUMAN_THRESHOLDS["avg_speed_range"][0] <= avg_speed <= HUMAN_THRESHOLDS["avg_speed_range"][1]):
        reasons.append(f"Unnatural mouse speed detected: {avg_speed:.2f}px/s.")
    
    variance = movement_variance(activity.mouseMovements, avg_speed)
    if not (HUMAN_THRESHOLDS["variance_range"][0] <= variance <= HUMAN_THRESHOLDS["variance_range"][1]):
        reasons.append(f"Unnatural mouse movement patterns detected (variance: {variance:.2f}).")

    if is_constant_scroll_speed(activity.scrollEvents, HUMAN_THRESHOLDS["scroll_speed_tolerance"]):
        reasons.append("Constant scrolling speed detected.")
 
    success = len(reasons) == 0
    
    # Ensure CSV file exists with header
    file_exists = os.path.isfile(POST_LOGIN_CSV_FILE)
    
    with open(POST_LOGIN_CSV_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
    
        # ks_mean, ks_stddev = analyze_keystroke_timings(activity.keystrokeTimings)
    
        triggerTime = datetime.fromtimestamp(activity.startTime / 1000)

        writer.writerow([
            triggerTime,
            activity.mouseMoves,
            activity.scrolls,
            activity.clicks,
            round(avg_speed, 2),
            round(variance, 2),
            # round(ks_mean, 2),
            # round(ks_stddev, 2)
        ])

    # return {"success": True}

    return {"success": success, "reasons": reasons}