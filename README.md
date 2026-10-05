# Engineering Assessment (Python)

Welcome! This is a small full-stack project that shows a catalog of items stored in a JSON file.

The frontend is fully built and functional, and does not require any changes. Your task is to complete the Python backend so that it works seamlessly with the frontend.

The backend codebase has **intentional bugs** and **missing features** for you to work through.
You have **~1 hour**. Aim for clean, idiomatic Python - correctness and clarity matter more than covering everything.

---

## Project Structure

```
backend-python/
├── app/
│   ├── main.py              # App bootstrap, routing, middleware
│   ├── items/
│   │   └── handler.py       # CRUD handlers for /api/items
│   └── stats/
│       └── handler.py       # GET /api/stats
├── requirements.txt
└── Makefile
frontend/
├── ...                      # Fully functional, unchanged
```

The shared data file lives at `./data/items.json` (relative to this directory).

---

## Quick Start

### Python backend

```bash
# Requires Python 3.10+
cd backend-python
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 4001

# or
make run
```

### Frontend (unchanged dev workflow)

```bash
cd frontend
npm install
npm start            # starts on :3000, proxies /api → :4001
```

---

## API Reference

| Method | Path            | Description                                                   |
| ------ | --------------- | ------------------------------------------------------------- |
| GET    | /api/items      | Paginated list. Supports `q`, `page`, `pageSize` query params |
| GET    | /api/items/{id} | Single item by ID                                             |
| POST   | /api/items      | Create a new item                                             |
| PUT    | /api/items/{id} | **Not implemented** - see Task 2                              |
| DELETE | /api/items/{id} | **Not implemented** - see Task 2                              |
| GET    | /api/stats      | `{ total, averagePrice }`                                     |

### Example item shape

```json
{ "id": 1, "name": "Laptop Pro", "category": "Electronics", "price": 2499 }
```

### GET /api/items - query parameters

| Param      | Default | Description                          |
| ---------- | ------- | ------------------------------------ |
| `q`        | `""`    | Case-insensitive substring on `name` |
| `page`     | `1`     | 1-based page number                  |
| `pageSize` | `50`    | Items per page (max 200)             |

---

## Your Tasks

### 🐛 Task 1 - Find & Fix 3 Bugs

The bugs are marked with `# BUG:` comments in the source. Read the comments carefully.

**Bug 1 - Cache race condition (`app/items/handler.py` · `Handler.read_data`)**

The cache read-check and cache write are not properly synchronised.
Under concurrent load (e.g. several requests hitting the server at once)
this lets multiple threads all decide to re-read and re-parse
`items.json`, racing to overwrite each other's cache entry.

- Find the exact point where the lock is released too early.
- Fix it so the check-then-act sequence is atomic with respect to other
  readers/writers (e.g. hold a single lock across the whole check and
  update).

**Bug 2 - No input validation (`app/items/handler.py` · `create_item`)**

`POST /api/items` accepts any payload without checking it.
A blank `name` or a negative `price` silently persists to disk.

- Add validation and return `400 Bad Request` with a JSON error body when:
  - `name` is missing or blank (whitespace only counts as blank)
  - `price` is negative

**Bug 3 - Stats recomputed on every request (`app/stats/handler.py` · `get_stats`)**

`GET /api/stats` reads and parses the entire JSON file on every call.
For a large dataset this is wasteful.

- Introduce an in-memory cache.
- Recompute only when `items.json` has been modified since the last computation.
- Hint: `os.path.getmtime(...)` gives you a comparable timestamp.
- The cache must be safe for concurrent access (e.g. `threading.Lock`).

---

### ✨ Task 2 - Implement 2 New Endpoints

Both handlers already exist in `app/items/handler.py` and are registered in `main.py`.
They currently return `501 Not Implemented`. Replace the stub body with a real implementation.

**`PUT /api/items/{id}`**

- Decode the JSON request body into an item payload (already handled via the `ItemInput` model).
- Apply the same validation rules as `POST`.
- Find the item by ID. Return `404` if not found.
- Update `name`, `category`, and `price`. The `id` must not change.
- Persist and return the updated item with `200 OK`.

**`DELETE /api/items/{id}`**

- Parse `{id}` from the path.
- Find the item. Return `404` if not found.
- Remove it, persist the updated list.
- Return `204 No Content` (no response body).

---

## Evaluation Criteria

| Area                     | What we look for                                               |
| ------------------------ | -----------------------------------------------------------------|
| **Correctness**          | Bugs genuinely fixed; new endpoints behave as specified          |
| **Concurrency**          | Proper locking; no lost updates or torn reads                    |
| **Error handling**       | Errors surfaced with appropriate HTTP status codes                |
| **Code clarity**         | Idiomatic Python; no unnecessary complexity                       |
| **Edge cases**           | Invalid IDs, empty body, boundary page values                     |
| **End-to-end behavior**  | Frontend and backend integrate correctly across all core user flows |

---

## Submission

Once completed, submit one of the following:

- **short video** recording your work.
- **Github Link** where your assessment result were pushed.

---
