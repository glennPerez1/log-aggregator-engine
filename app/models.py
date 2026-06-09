from pydantic import BaseModel, Field
from datetime import datetime

class LogEntry(BaseModel):
    # Ensures the client passes a valid ISO timestamp, or defaults to the current UTC time string
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    service_name: str = Field(..., min_length=1, max_length=100, description="The name of the service generating the log")
    log_level: str = Field(..., description="Must be INFO, WARN, ERROR, or DEBUG")
    message: str = Field(..., min_length=1, description="The main descriptive message of the event")

    # This enforces clean structure during parsing
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2026-06-09T16:42:00Z",
                "service_name": "payment-gateway",
                "log_level": "ERROR",
                "message": "Connection timed out while contacting upstream banking APIs."
            }
        }