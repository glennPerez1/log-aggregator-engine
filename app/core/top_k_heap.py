import heapq
import threading

class TopKErrorAnalyzer:
    def __init__(self, k: int = 5):
        self.k = k
        # Hash Map to keep running frequencies of unique error strings
        self.frequency_map = {}
        # Thread lock to maintain consistency across asynchronous routines
        self.lock = threading.Lock()

    def record_error(self, message: str):
        """Increments the count of an error message in the frequency map."""
        with self.lock:
            if message in self.frequency_map:
                self.frequency_map[message] += 1
            else:
                self.frequency_map[message] = 1

    def get_top_errors(self) -> list:
        """
        Uses a Min-Heap mechanism to extract the Top-K error messages 
        efficiently in O(N log K) time complexity boundaries.
        """
        with self.lock:
            # If the map is empty, return an empty list immediately
            if not self.frequency_map:
                return []
            
            # heapq.nlargest extracts the highest counts from our frequency pool
            # It creates a min-heap under the hood of size K
            top_k = heapq.nlargest(
                self.k, 
                self.frequency_map.items(), 
                key=lambda item: item[1]
            )
            
            # Format the output clearly for API exposure
            return [{"message": msg, "count": cnt} for msg, cnt in top_k]

# Singleton analyzer instance across our backend application
error_analyzer = TopKErrorAnalyzer(k=5)