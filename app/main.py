import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import db
from app.api.ingestion import INGESTION_QUEUE, router as ingestion_router

async def log_writer_worker():
    """
    A persistent background worker loop that runs for the lifetime of the application.
    It continuously monitors the INGESTION_QUEUE and flushes logs to the SQLite database.
    """
    print("[Worker] Persistent Log Writer Worker started successfully.")
    while True:
        try:
            # Blocks cleanly until an item is available in the memory queue
            log_item = await INGESTION_QUEUE.get()
            
            # Execute the query asynchronously using our database thread-pool executor
            query = """
                INSERT INTO application_logs (timestamp, service_name, log_level, message)
                VALUES (?, ?, ?, ?);
            """
            params = (log_item.timestamp, log_item.service_name, log_item.log_level, log_item.message)
            await db.execute_write(query, params)
            
            # Signal the queue that the processing task is complete
            INGESTION_QUEUE.task_done()
        except asyncio.CancelledError:
            print("[Worker] Shutting down worker loop gracefully...")
            break
        except Exception as e:
            print(f"[Worker Error] Failed to process log entry: {e}")
            # Prevents tight CPU spinning in case of unexpected errors
            await asyncio.sleep(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages system startup and shutdown events cleanly."""
    # --- Startup Logic ---
    print("[Initialization] Connecting and establishing indexed database tables...")
    await db.initialize()
    
    # Spin up our log writer loop as a background task
    worker_task = asyncio.create_task(log_writer_worker())
    
    yield  # The server stays open and accepts traffic here
    
    # --- Shutdown Logic ---
    print("[Shutdown] Cleaning up pending background operations...")
    worker_task.cancel()
    await asyncio.gather(worker_task, return_exceptions=True)

# Instantiate the main app utilizing our custom lifespan loop
app = FastAPI(
    title="High-Throughput Real-Time Log Aggregator Engine",
    version="1.0.0",
    lifespan=lifespan
)

# Attach our API endpoints to the router tree
app.include_router(ingestion_router)

@app.get("/health")
async def health_check():
    """A quick verification route to confirm the server engine is up and running."""
    return {"status": "healthy", "service": "log-aggregator-engine"}