# High-Throughput Real-Time Log Aggregator Engine

A high-performance backend utility built to ingest distributed microservice logs asynchronously, tracking error frequencies and computing Top-K operational failures using optimized in-memory data structures.

## Core Features
- Async Log Ingestion Engine
- Sliding Window Error Tracking
- Heap-based Analytics

## Setup Instructions
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload