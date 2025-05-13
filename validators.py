# validators.py
from typing import List
from models import MouseMovement
from models import ScrollEvent


def average_mouse_speed(mouse_movements: List[MouseMovement]):
    if len(mouse_movements) < 2:
        return 0
    
    total_distance = sum((m.x**2 + m.y**2)**0.5 for m in mouse_movements)
    total_time = (mouse_movements[-1].timestamp - mouse_movements[0].timestamp) / 1000  # seconds
    
    if total_time == 0:
        return 0
    
    return total_distance / total_time

def movement_variance(mouse_movements: List[MouseMovement], avg_speed: float):
    speeds = [(m.x**2 + m.y**2)**0.5 for m in mouse_movements]
    if not speeds:
        return 0 
    variance = sum((speed - avg_speed)**2 for speed in speeds) / len(speeds)
    return variance

def is_constant_scroll_speed(scroll_events: List[ScrollEvent], tolerance=0.01) -> bool:
    if len(scroll_events) < 3:
        return False  # Too few events to analyze meaningfully

    speeds = []
    for i in range(1, len(scroll_events)):
        deltaY = scroll_events[i].scrollY - scroll_events[i - 1].scrollY
        deltaTime = scroll_events[i].timestamp - scroll_events[i - 1].timestamp
        if deltaTime == 0:
            continue
        speeds.append(deltaY / deltaTime)

    for i in range(1, len(speeds)):
        if abs(speeds[i] - speeds[i - 1]) > tolerance:
            return False  # Speed changes detected, likely human behavior
    return True  # Constant speed detected, potential bot

def analyze_keystroke_timings(timings: List[int]) -> dict:
    if not timings:
        return {"mean": 0, "std_dev": 0, "suspicious": True}

    mean = sum(timings) / len(timings)
    variance = sum((t - mean) ** 2 for t in timings) / len(timings)
    std_dev = variance ** 0.5

    # Flags bot-like behavior: very fast or uniform typing
    suspicious = mean < 100 or std_dev < 30

    return {
        "mean": mean,
        "std_dev": std_dev,
        "suspicious": suspicious
    }


#csv file

# def calculate_average_mouse_speed(movements):
#     if len(movements) < 2:
#         return 0
#     total_dist = sum((m.x**2 + m.y**2) ** 0.5 for m in movements)
#     total_time = (movements[-1].timestamp - movements[0].timestamp) / 1000
#     return total_dist / total_time if total_time else 0

# def calculate_movement_variance(movements, avg_speed):
#     speeds = [(m.x**2 + m.y**2)**0.5 for m in movements]
#     return sum((s - avg_speed) ** 2 for s in speeds) / len(speeds) if speeds else 0

def analyze_keystroke_stats(timings):
    if not timings:
        return 0, 0
    mean = sum(timings) / len(timings)
    variance = sum((t - mean) ** 2 for t in timings) / len(timings)
    return mean, variance ** 0.5
