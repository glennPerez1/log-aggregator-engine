import sqlite3
import asyncio
from concurrent.futures import ThreadPoolExecutor

DB_PATH = "logs.db"

class AsyncDatabase:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        # Thread pool to run blocking SQLite operations asynchronously
        self.executor = ThreadPoolExecutor(max_workers=1)

    def _execute_write(self, query: str, params: tuple = ()):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
        finally:
            conn.close()

    async def execute_write(self, query: str, params: tuple = ()):
        """Runs database write operations inside a separate thread pool to prevent blocking."""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(self.executor, self._execute_write, query, params)

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Create our core log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS application_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                service_name TEXT NOT NULL,
                log_level TEXT NOT NULL,
                message TEXT NOT NULL
            );
        """)
        # Create a composite B-Tree index for lightning fast time-series analytics lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_logs_service_level_time 
            ON application_logs (service_name, log_level, timestamp DESC);
        """)
        conn.commit()
        conn.close()

    async def initialize(self):
        """Initializes tables and indexes asynchronously on app startup."""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(self.executor, self._init_db)

# Create a singleton instance to use across our application
db = AsyncDatabase()