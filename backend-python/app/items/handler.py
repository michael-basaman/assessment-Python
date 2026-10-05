"""CRUD handlers for /api/items.

Mirrors the Go reference implementation's structure and intentional bugs.
"""

from __future__ import annotations

import json
import os
import threading
import time
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


class Item(BaseModel):
    """Item mirrors the JSON structure in data/items.json."""

    id: int
    name: str
    category: str
    price: float


class ItemInput(BaseModel):
    """Payload shape accepted by POST/PUT — deliberately untyped/loose,
    same as the Go version's bare `Item` decode target, so validation has
    to be added explicitly rather than falling out of the type system.
    """

    name: str = ""
    category: str = ""
    price: float = 0.0


class Handler:
    """Holds shared state for the items routes."""

    def __init__(self, data_path: str) -> None:
        self.data_path = data_path
        self._lock = threading.RLock()
        self._cached: Optional[list[dict]] = None
        self._cached_mtime: Optional[float] = None

    def read_data(self) -> list[dict]:
        """Reads items.json, using an in-memory cache keyed on file mtime.

        BUG: There is a race condition in this function.
        Identify it and fix it.
        """
        mtime = os.path.getmtime(self.data_path)

        with self._lock:
            if self._cached is not None and mtime <= self._cached_mtime:
                return self._cached
        # ↑ Lock is released here. Another thread can now enter and also
        #   proceed past this point before either one writes the cache.

        with open(self.data_path, "r", encoding="utf-8") as f:
            items = json.load(f)

        # BUG: We update the cache without holding the lock across the
        # whole check-then-act sequence above, so two concurrent threads
        # can both decide to re-read the file and race to overwrite each
        # other's cache entry.
        self._cached = items
        self._cached_mtime = mtime

        return items

    def write_data(self, items: list[dict]) -> None:
        """Persists items to disk and invalidates the cache."""
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2)

        with self._lock:
            self._cached = None


def build_router(handler: Handler) -> APIRouter:
    router = APIRouter()

    @router.get("/api/items")
    def list_items(q: str = "", page: int = 1, pageSize: int = 50):
        """GET /api/items?q=&page=1&pageSize=50"""
        try:
            data = handler.read_data()
        except OSError:
            raise HTTPException(status_code=500, detail="failed to read data")

        query = q.strip().lower()

        if page < 1:
            page = 1

        max_page_size = 200
        page_size = pageSize
        if page_size < 1 or page_size > max_page_size:
            page_size = 50

        results = data
        if query:
            results = [item for item in data if query in item["name"].lower()]

        total = len(results)
        offset = (page - 1) * page_size
        if offset > total:
            offset = total
        end = offset + page_size
        if end > total:
            end = total

        return {
            "items": results[offset:end],
            "total": total,
            "page": page,
            "pageSize": page_size,
            "q": query,
        }

    @router.get("/api/items/{item_id}")
    def get_item(item_id: str):
        """GET /api/items/{id}"""
        try:
            parsed_id = int(item_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="invalid id")

        try:
            data = handler.read_data()
        except OSError:
            raise HTTPException(status_code=500, detail="failed to read data")

        for item in data:
            if item["id"] == parsed_id:
                return item
        raise HTTPException(status_code=404, detail="item not found")

    @router.post("/api/items", status_code=201)
    def create_item(payload: ItemInput):
        """POST /api/items

        BUG: This handler is missing input validation entirely.
        A request with an empty name or a negative price is accepted
        without error.
        Add validation and return 400 Bad Request with a descriptive
        message when:
          - name is missing or blank
          - price is negative
        """
        # TODO: validate `payload` fields before saving

        try:
            data = handler.read_data()
        except OSError:
            raise HTTPException(status_code=500, detail="failed to read data")

        new_item = {
            "id": int(time.time() * 1000),
            "name": payload.name,
            "category": payload.category,
            "price": payload.price,
        }
        data.append(new_item)

        try:
            handler.write_data(data)
        except OSError:
            raise HTTPException(status_code=500, detail="failed to save data")

        return new_item

    @router.put("/api/items/{item_id}")
    def update_item(item_id: str, payload: ItemInput):
        """PUT /api/items/{id}

        TODO: Implement this handler.

        Requirements:
          - Decode the JSON request body into an item payload (done above).
          - Validate the fields (same rules as POST).
          - Find the item with the matching ID in the data file.
          - If not found, return 404.
          - Update name, category, and price fields (do NOT allow changing
            the id).
          - Persist the updated list and return the updated item with
            200 OK.
        """
        raise HTTPException(status_code=501, detail="not implemented")

    @router.delete("/api/items/{item_id}", status_code=204)
    def delete_item(item_id: str):
        """DELETE /api/items/{id}

        TODO: Implement this handler.

        Requirements:
          - Parse the {id} path parameter.
          - Find the item with the matching ID.
          - If not found, return 404.
          - Remove it from the list and persist the file.
          - Return 204 No Content (no body).
        """
        raise HTTPException(status_code=501, detail="not implemented")

    return router
