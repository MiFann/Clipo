from __future__ import annotations

import hashlib

from fastapi import APIRouter, Request

from ..database import connection_scope
from ..models import VisitPayload


router = APIRouter(prefix="/api")


@router.post("/stats/visit", status_code=201)
def record_visit(payload: VisitPayload, request: Request) -> dict[str, str]:
    ip = request.client.host if request.client else ""
    ip_hash = hashlib.sha256(ip.encode("utf-8")).hexdigest() if ip else None
    user_agent = request.headers.get("user-agent", "")

    with connection_scope() as db:
        post_id = None
        if payload.slug:
            row = db.execute("SELECT id FROM posts WHERE slug = ?", (payload.slug,)).fetchone()
            post_id = row["id"] if row else None

        db.execute(
            """
            INSERT INTO visits (path, post_id, ip_hash, user_agent)
            VALUES (?, ?, ?, ?)
            """,
            (payload.path, post_id, ip_hash, user_agent[:300]),
        )
        db.execute(
            """
            INSERT INTO site_stats (key, value)
            VALUES ('total_visits', 1)
            ON CONFLICT(key) DO UPDATE SET
              value = value + 1,
              updated_at = CURRENT_TIMESTAMP
            """
        )

    return {"status": "recorded"}
