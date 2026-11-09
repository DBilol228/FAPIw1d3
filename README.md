# MedBook API

Learning project for an appointment booking API using FastAPI and Pydantic v2.
Requirements are described in [MedBook_API_TZ.md](MedBook_API_TZ.md).

## Setup and run

Install Python 3.11 or newer, then run from this directory:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs for Swagger UI.
Run a single worker because data is stored in memory and lost on restart.

## Project status

The folder structure, empty storage collections, and routers are prepared.
Schemas, endpoints, ID generation, and business rules still need implementation.
All application routes will use the `/api/v1` prefix.
# FAPIw1d3
