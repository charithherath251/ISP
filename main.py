# main.py
import csv
import os
from fastapi import Request
from datetime import datetime
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
import motor.motor_asyncio
import bcrypt
from typing import Dict, Any
from models import UserActivity
from validators import average_mouse_speed, movement_variance, is_constant_scroll_speed, analyze_keystroke_timings
from thresholds import HUMAN_THRESHOLDS
from fastapi.middleware.cors import CORSMiddleware
from db import pre_login_collection, post_login_collection

app = FastAPI()

PRE_LOGIN_CSV_FILE = "Prelogin_user_behavior_log.csv"
POST_LOGIN_CSV_FILE = "Postlogin_user_behavior_log.csv"

#mongoDB connection
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
db = client["dashboard"]
users = db["users"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500","http://localhost:5501","http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#get data from mongoDB
@app.get("/get-pre-logs")
async def get_pre_logs():
    logs = await pre_login_collection.find().to_list(length=1000)
    for log in logs:
        log["_id"] = str(log["_id"])  
    return logs

@app.get("/get-post-logs")
async def get_post_logs():
    logs = await post_login_collection.find().to_list(length=1000)
    for log in logs:
        log["_id"] = str(log["_id"])
    return logs

#pre-login user validation
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
    doc = {
        "timestamp": datetime.utcnow(),
        "mouseMoves": activity.mouseMoves,
        "keypresses": activity.keypresses,
        "scrolls": activity.scrolls,
        "clicks": activity.clicks,
        "interactionTime": activity.timing[0] if activity.timing else 0,
        "avgSpeed": round(avg_speed, 2),
        "movementVariance": round(variance, 2),
        "keystrokeMean": round(keystroke_result["mean"], 2),
        "keystrokeStdDev": round(keystroke_result["std_dev"], 2),
        "success": success,
        "reasons": reasons
    }

    await pre_login_collection.insert_one(doc)

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

#post-login user validation
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

    doc = {
        "timestamp": datetime.utcnow(),
        "mouseMoves": activity.mouseMoves,
        "keypresses": activity.keypresses,
        "scrolls": activity.scrolls,
        "clicks": activity.clicks,
        "interactionTime": activity.timing[0] if activity.timing else 0,
        "avgSpeed": round(avg_speed, 2),
        "movementVariance": round(variance, 2),
        "success": success,
        "reasons": reasons
    }

    await post_login_collection.insert_one(doc)
    
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

    return {"success": success, "reasons": reasons}

#user dashboard authentication
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    user = await users.find_one({"username": username})
    if not user or not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    response = JSONResponse(content={"success": True})
    response.set_cookie(
        key="authenticated",
        value="true",
        httponly=False,
        samesite="Lax",
        secure=False,
        domain="localhost"
    )
    response.set_cookie(
        key="username",
        value=username,
        httponly=False,
        samesite="Lax",
        secure=False,
        domain="localhost"
    )
    return response

#user dashboard logout
@app.get("/logout")
async def logout():
    response = RedirectResponse(url="http://localhost:5500/login.html")
    response.delete_cookie("authenticated")
    response.delete_cookie("username")  # if you're using it
    return response

#user dashboard session handling  
@app.get("/profile")
async def get_profile(request: Request):
    auth_cookie = request.cookies.get("authenticated")
    if auth_cookie != "true":
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"success": True, "username": request.cookies.get("username", "Unknown")}
