import asyncio
from fastapi import APIRouter, status
from app.models import LogEntry

router = APIRouter(prefix="/api/v1", tags=["Ingestion"])

# Memory-bound FIFO queue to buffer incoming logs
INGESTION_QUEUE = asyncio.Queue(maxsize=10000)

@router.post("/logs", status_code=status.HTTP_202_ACCEPTED)
async def ingest_log(log: LogEntry):
    """
    Receives incoming JSON logs, validates them using the Pydantic schema, 
    and drops them into an in-memory queue for asynchronous background processing.
    """
    try:
        # Non-blocking insertion into the queue
        INGESTION_QUEUE.put_nowait(log)
        return {"status": "accepted", "message": "Log buffered successfully"}
    except asyncio.QueueFull:
        # Failsafe if background worker falls too far behind under intense stress
        return {
            "status": "rejected", 
            "message": "Ingestion queue capacity reached. Dropping payload."
        }