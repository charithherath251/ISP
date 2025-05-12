# thresholds.py

HUMAN_THRESHOLDS = {
    "min_mouse_moves": 5,
    "min_clicks": 1,
    "avg_speed_range": (5, 100),  # pixel/sec
    "variance_range": (10, 1500),
    "min_interaction_time": 1000,  # milliseconds
    "scroll_speed_tolerance": 0.01 
}

KEYSTROKE_THRESHOLDS = {
    "min_mean_ms": 100,   # Too fast = bot
    "min_stddev_ms": 30   # Too uniform = bot
}
