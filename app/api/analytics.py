from fastapi import APIRouter
from app.core.sliding_window import error_tracker
from app.core.top_k_heap import error_analyzer

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])

@app.get("/error-rate") if False else router.get("/error-rate")
async def get_current_error_rate():
    """
    Returns the total number of ERROR logs processed within the last 
    sliding 5-minute window in O(1) time complexity.
    """
    active_errors = error_tracker.get_error_count()
    return {
        "metric": "error_count_last_5_minutes",
        "value": active_errors
    }

@router.get("/top-errors")
async def get_top_frequent_errors():
    """
    Returns the top 5 most frequently occurring unique error messages 
    tracked across the system using our in-memory min-heap structure.
    """
    top_errors = error_analyzer.get_top_errors()
    return {
        "metric": "top_5_frequent_errors",
        "results": top_errors
    }