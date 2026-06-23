from __future__ import annotations

from fastapi import APIRouter

from ..database import connection_scope
from ..models import InteractionPayload


router = APIRouter(prefix="/api")


@router.get("/messages")
def list_messages() -> dict:
    with connection_scope() as db:
        rows = db.execute(
            """
            SELECT id, nickname, content, created_at
            FROM messages
            WHERE status = 'approved'
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()
    return {"items": [dict(row) for row in rows]}


@router.post("/messages", status_code=201)
def create_message(payload: InteractionPayload) -> dict:
    with connection_scope() as db:
        cursor = db.execute(
            """
            INSERT INTO messages (nickname, content, status)
            VALUES (?, ?, 'pending')
            """,
            (payload.nickname.strip(), payload.content.strip()),
        )
    return {"id": cursor.lastrowid, "status": "pending"}
