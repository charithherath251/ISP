# models.py
from typing import List
from pydantic import BaseModel

class MouseMovement(BaseModel):
    x: float
    y: float
    timestamp: int

class ScrollEvent(BaseModel):
    timestamp: int
    scrollY: float

class UserActivity(BaseModel):
    mouseMoves: int
    keypresses: int
    scrolls: int
    clicks: int
    mouseMovements: List[MouseMovement]
    scrollEvents: List[ScrollEvent]
    keystrokeTimings: List[int]
    timing: List[int]
    startTime: int
    
