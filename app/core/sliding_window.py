from collections import deque
from datetime import datetime, timedelta

class SlidingWindowErrorTracker:
    def __init__(self, window_minutes: int = 5):
        self.window_size = timedelta(minutes=window_minutes)
        # Using a deque (Double-Ended Queue) for efficient O(1) pops from the front
        self.error_timestamps = deque()

    def add_error(self, timestamp_str: str):
        """Adds a new error timestamp to our tracker window."""
        try:
            # Parse incoming ISO format string to a python datetime object
            # Handles 'Z' suffix variation by replacing it if necessary
            clean_ts = timestamp_str.replace('Z', '+00:00')
            dt = datetime.fromisoformat(clean_ts)
            self.error_timestamps.append(dt)
        except Exception as e:
            print(f"[Tracker Error] Could not parse timestamp {timestamp_str}: {e}")

    def get_error_count(self) -> int:
        """
        Cleans up expired entries outside the time frame window 
        and returns the active error count in O(1) space inspection.
        """
        now = datetime.utcnow()
        cutoff_time = now - self.window_size

        # Evict all timestamps older than our sliding window threshold boundary
        while self.error_timestamps and self.error_timestamps[0] < cutoff_time:
            self.error_timestamps.popleft()

        return len(self.error_timestamps)

# Singleton tracker instance across our backend application app environment context
error_tracker = SlidingWindowErrorTracker(window_minutes=5)