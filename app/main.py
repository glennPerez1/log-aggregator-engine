import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import db
from app.api.ingestion import INGESTION_QUEUE, router as ingestion_router
from app.api.analytics import router as analytics_router
from app.core.sliding_window import error_tracker
from app.core.top_k_heap import error_analyzer

async def log_writer_worker():
    """
    A persistent background worker loop that runs for the lifetime of the application.
    It flushes logs to SQLite and routes ERROR logs to our in-memory DSA engines.
    """
    print("[Worker] Persistent Log Writer Worker started successfully.")
    while True:
        try:
            log_item = await INGESTION_QUEUE.get()
            
            # --- DSA Layer Hook ---
            # If an incoming log entry is an ERROR, track it in memory instantly
            if log_item.log_level.upper() == "ERROR":
                error_tracker.add_error(log_item.timestamp)
                error_analyzer.record_error(log_item.message)
            
            # --- Persistent Storage Layer ---
            query = """
                INSERT INTO application_logs (timestamp, service_name, log_level, message)
                VALUES (?, ?, ?, ?);
            """
            params = (log_item.timestamp, log_item.service_name, log_item.log_level, log_item.message)
            await db.execute_write(query, params)
            
            INGESTION_QUEUE.task_done()
        except asyncio.CancelledError:
            print("[Worker] Shutting down worker loop gracefully...")
            break
        except Exception as e:
            print(f"[Worker Error] Failed to process log entry: {e}")
            await asyncio.sleep(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages system startup and shutdown events cleanly."""
    print("[Initialization] Connecting and establishing indexed database tables...")
    await db.initialize()
    
    worker_task = asyncio.create_task(log_writer_worker())
    yield
    
    print("[Shutdown] Cleaning up pending background operations...")
    worker_task.cancel()
    await asyncio.gather(worker_task, return_exceptions=True)

app = FastAPI(
    title="High-Throughput Real-Time Log Aggregator Engine",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(ingestion_router)
app.include_router(analytics_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "log-aggregator-engine"}