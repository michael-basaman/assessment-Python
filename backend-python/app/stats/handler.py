"""GET /api/stats."""

from __future__ import annotations

import json
import threading
import os
from typing import Optional

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
        self._lock = threading.RLock()
        self._cached: Optional[list[dict]] = None
        self._cached_mtime: Optional[float] = None
        # TODO: add cache fields here

    def get_stats(self):
        # returns cached version of stats
        #  if the data_path has not been modified since cache compute
        #  otherwise, compute stats and return
        #
        # handles concurrent access with lock

        with self._lock:
            try:
                last_modified_time = os.path.getmtime(self.data_path)
            except OSError:
                raise HTTPException(status_code=500, detail="failed to stat data")

            if self._cached_mtime is not None and last_modified_time <= self._cached_mtime:
                return self._cached

            try:
                with open(self.data_path, "r", encoding="utf-8") as f:
                    raw = f.read()
            except OSError:
                raise HTTPException(status_code=500, detail="failed to read data")

            try:
                items = json.loads(raw)
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail="failed to parse data")

            computed = self.compute(items)

            self._cached = computed
            self._cached_mtime = last_modified_time

        return computed

    def compute(self, items: list[dict]) -> dict:
        if not items:
            return {"total": 0, "averagePrice": 0.0}
        total = len(items)
        total_price = sum(item["price"] for item in items)
        return {"total": total, "averagePrice": total_price / total}


def build_router(handler: Handler) -> APIRouter:
    router = APIRouter()

    @router.get("/api/stats")
    def get_stats():
        return handler.get_stats()

    return router
