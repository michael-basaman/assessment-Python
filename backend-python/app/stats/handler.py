"""GET /api/stats."""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException


class Handler:
    """Serves the GET /api/stats route.

    BUG: Stats are recomputed from disk on every single request — no
    caching. For a large dataset this is unnecessarily expensive.

    Fix: Cache the computed stats in memory. Invalidate the cache only
    when items.json is modified (hint: compare `os.path.getmtime(...)`
    across calls).
    """

    def __init__(self, data_path: str) -> None:
        self.data_path = data_path
        # TODO: add cache fields here


def compute(items: list[dict]) -> dict:
    if not items:
        return {"total": 0, "averagePrice": 0.0}
    total = len(items)
    total_price = sum(item["price"] for item in items)
    return {"total": total, "averagePrice": total_price / total}


def build_router(handler: Handler) -> APIRouter:
    router = APIRouter()

    @router.get("/api/stats")
    def get_stats():
        # BUG: reads and parses the entire file on every request.
        try:
            with open(handler.data_path, "r", encoding="utf-8") as f:
                raw = f.read()
        except OSError:
            raise HTTPException(status_code=500, detail="failed to read data")

        try:
            items = json.loads(raw)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="failed to parse data")

        return compute(items)

    return router
