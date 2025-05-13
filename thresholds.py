# thresholds.py

HUMAN_THRESHOLDS = {
    "min_mouse_moves": 60,
    "min_clicks": 3,
    "avg_speed_range": (7, 110),  # pixel/sec
    "variance_range": (29, 10900),
    "min_interaction_time": 10000,  # milliseconds
    "scroll_speed_tolerance": 0.01 
}

KEYSTROKE_THRESHOLDS = {
    "min_mean_ms": 210,   # Too fast = bot
    "min_stddev_ms": 285   # Too uniform = bot
}
