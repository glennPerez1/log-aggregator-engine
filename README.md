#  High-Throughput Real-Time Log Aggregator Engine

A high-performance, asynchronous log ingestion and analytics pipeline built with **Python**, **FastAPI**, and **SQLite**.

The system is designed to handle high-volume log streams efficiently by decoupling API ingestion from disk persistence using an in-memory queue. Real-time analytics are computed entirely in memory using optimized Data Structures and Algorithms (DSA), enabling fast response times under heavy load.

---

## 📌 Features

###  Asynchronous Log Ingestion

Incoming log requests are immediately placed into an in-memory FIFO queue (`asyncio.Queue`) and acknowledged with a `202 Accepted` response.

This prevents slow disk I/O operations from blocking API requests and allows the system to sustain higher throughput.

**Complexity:** `O(1)` enqueue operation

---

###  Real-Time Error Rate Tracking

Tracks active `ERROR` logs within a rolling **5-minute sliding window**.

Implemented using a **Double-Ended Queue (****`collections.deque`****)**, enabling constant-time insertion and eviction of expired entries.

**Complexity:** `O(1)` per update

---

###  Top-K Error Analytics

Maintains the **Top 5 Most Frequent Error Messages** across all incoming log streams.

Uses:

* Hash Map (`dict`) for frequency counting
* Min-Heap (`heapq`) for efficient Top-K extraction

**Complexity:** `O(N log K)`

Where:

* `N` = Number of unique error messages
* `K` = Number of top results required (5)

---

###  Non-Blocking Database Persistence

A dedicated background worker continuously consumes logs from the queue and writes them into SQLite.

Database writes are executed in a thread pool to prevent blocking the FastAPI event loop.

---
## 🛠 Tech Stack

- Python 3.11+
- FastAPI
- AsyncIO
- SQLite
- Pydantic
- Uvicorn
- Heapq
- Collections (Deque)

---

##  System Architecture

```text
                   ┌─────────────────────┐
                   │     FastAPI API     │
                   └──────────┬──────────┘
                              │
                              ▼
                  ┌──────────────────────┐
                  │   asyncio.Queue      │
                  │  (Memory Buffer)     │
                  └──────────┬───────────┘
                             │
          ┌──────────────────┴──────────────────┐
          ▼                                     ▼

┌──────────────────┐               ┌──────────────────┐
│ Analytics Engine │               │ Background Worker│
│                  │               │                  │
│ • Sliding Window │               │ Queue Consumer   │
│ • Top-K Heap     │               │ SQLite Writer    │
└──────────────────┘               └────────┬─────────┘
                                             │
                                             ▼
                                   ┌────────────────┐
                                   │   SQLite DB    │
                                   └────────────────┘
```

---

## 📂 Project Structure

```text
log-aggregator-engine/
│
├── app/
│   ├── api/
│   │   └── routes.py
│   │
│   ├── core/
│   │   ├── sliding_window.py
│   │   └── topk_errors.py
│   │
│   ├── models/
│   │   └── schemas.py
│   │
│   ├── database.py
│   └── main.py
│
├── scripts/
│   └── mock_generator.py
│
├── logs.db
├── requirements.txt
└── README.md
```

---

## 🛠️ Installation

### 1. Clone Repository

```bash
git clone git@github.com:glennPerez1/log-aggregator-engine.git
git clone https://github.com/glennPerez1/log-aggregator-engine.git
cd log-aggregator-engine
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

#### Windows (Git Bash)

```bash
source venv/Scripts/activate
```

#### Windows (CMD)

```cmd
venv\Scripts\activate
```

#### Linux / macOS

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

##  Running the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Expected output:

```text
[Initialization] Database initialized successfully.
[Worker] Persistent Log Writer Worker started.
INFO: Uvicorn running on http://127.0.0.1:8000
```

---

##  Load Testing

Open a second terminal and run the traffic simulator:

```bash
source venv/Scripts/activate
python scripts/mock_generator.py
```

The simulator continuously generates concurrent log requests to stress-test the system.

---

##  Analytics Endpoints

### Swagger Documentation

```text
http://127.0.0.1:8000/docs
```

### Top-5 Error Dashboard

```text
http://127.0.0.1:8000/api/v1/analytics/top-errors
```

### Rolling 5-Minute Error Count

```text
http://127.0.0.1:8000/api/v1/analytics/error-rate
```

---

##  Example Log Request

```json
POST /api/v1/logs

{
  "service": "auth-service",
  "level": "ERROR",
  "message": "Database connection timeout",
  "timestamp": "2026-06-09T12:30:00Z"
}
```

Response:

```json
{
  "status": "accepted"
}
```

---

## ⚙️ Algorithm Complexity

| Component              | Data Structure       | Time Complexity | Space Complexity |
| ---------------------- | -------------------- | --------------- | ---------------- |
| Log Ingestion          | asyncio.Queue        | O(1)            | O(M)             |
| Sliding Window Tracker | collections.deque    | O(1)            | O(W)             |
| Frequency Counter      | Hash Map             | O(1) average    | O(U)             |
| Top-K Analytics        | Min-Heap             | O(N log K)      | O(K)             |
| Database Write         | SQLite + Thread Pool | O(1) per write  | O(1)             |

Where:

* **M** = Queue size
* **W** = Active logs inside 5-minute window
* **U** = Unique error messages
* **N** = Number of unique error messages
* **K** = Number of top results requested

---

##  Learning Objectives Demonstrated

This project demonstrates:

* FastAPI backend development
* Asynchronous programming with asyncio
* Producer–Consumer architecture
* Sliding Window algorithms
* Heap-based Top-K optimization
* Thread pool execution
* SQLite persistence
* High-throughput system design fundamentals
* Real-time analytics pipelines

---
