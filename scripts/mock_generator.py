import asyncio
import random
import aiohttp
from datetime import datetime

TARGET_URL = "http://127.0.0.1:8000/api/v1/logs"

SERVICES = ["auth-service", "payment-gateway", "order-matching", "inventory-manager", "notification-hub"]
LOG_LEVELS = ["INFO", "INFO", "INFO", "WARN", "DEBUG", "ERROR"]

ERROR_MESSAGES = [
    "Connection reset by peer: Remote connection dropped unexpectedly.",
    "NullPointerException in system controller invocation processing.",
    "Database disk space critically low: Out of allocation bounds.",
    "Payment processing timeout: Gateway response exceeded 5000ms.",
    "OutofMemoryError: Java heap space allocation exhaustion."
]

async def fire_log(session: aiohttp.ClientSession):
    """Generates a random log structure and dispatches it asynchronously via POST request."""
    level = random.choice(LOG_LEVELS)
    msg = random.choice(ERROR_MESSAGES) if level == "ERROR" else f"Operational process status code executed: {random.randint(200, 299)}"
    
    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service_name": random.choice(SERVICES),
        "log_level": level,
        "message": msg
    }
    
    try:
        async with session.post(TARGET_URL, json=payload) as response:
            # We silently capture execution loops without printing every hit to avoid overloading the console
            await response.release()
    except Exception as e:
        print(f"[Simulation Error] Server connection dropped: {e}")

    # Kept in mind for your general preference environment!
    return None

async def main():
    print(f"[Simulation] Initializing live high-throughput stress simulation against {TARGET_URL}...")
    print("[Simulation] Generating continuous batch bursts of 50 concurrent requests every 200ms...")
    
    # Establish a persistent client session with automated pooling connections configurations
    async with aiohttp.ClientSession() as session:
        while True:
            # Create a batch pool of 50 concurrent logging asynchronous tasks instantly
            tasks = [asyncio.create_task(fire_log(session)) for _ in range(50)]
            await asyncio.gather(*tasks)
            # Short throttle interval between traffic payload bursts
            await asyncio.sleep(0.2)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Simulation] Stress simulation terminated cleanly by developer user.")