"""Server bootstrap, routing, and middleware.

Run with:
    uvicorn app.main:app --host 0.0.0.0 --port 4001
or just:
    make run
"""

from __future__ import annotations

import os
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.items.handler import Handler as ItemsHandler, build_router as build_items_router
from app.stats.handler import Handler as StatsHandler, build_router as build_stats_router

DATA_PATH = os.environ.get("DATA_PATH", "../data/items.json")

app = FastAPI(title="backend-python")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:4001"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Logs method, path, and duration for every request, mirroring the
    Go `loggingMiddleware`."""
    start = time.monotonic()
    response = await call_next(request)
    elapsed_ms = (time.monotonic() - start) * 1000
    print(f"{request.method} {request.url.path} {elapsed_ms:.2f}ms")
    return response


items_handler = ItemsHandler(DATA_PATH)
stats_handler = StatsHandler(DATA_PATH)

app.include_router(build_items_router(items_handler))
app.include_router(build_stats_router(stats_handler))


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "4001"))
    print(f"Backend running on http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
