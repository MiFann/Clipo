from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..database import connection_scope
from ..models import InteractionPayload


router = APIRouter(prefix="/api")


def _find_published_post_id(slug: str) -> int:
    with connection_scope() as db:
        row = db.execute("SELECT id FROM posts WHERE slug = ? AND status = 'published'", (slug,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Post not found")
    return int(row["id"])


@router.get("/posts/{slug}/comments")
def list_comments(slug: str) -> dict:
    post_id = _find_published_post_id(slug)
    with connection_scope() as db:
        rows = db.execute(
            """
            SELECT id, nickname, content, created_at
            FROM comments
            WHERE post_id = ? AND status = 'approved'
            ORDER BY created_at ASC, id ASC
            """,
            (post_id,),
        ).fetchall()
    return {"items": [dict(row) for row in rows]}


@router.post("/posts/{slug}/comments", status_code=201)
def create_comment(slug: str, payload: InteractionPayload) -> dict:
    post_id = _find_published_post_id(slug)
    with connection_scope() as db:
        cursor = db.execute(
            """
            INSERT INTO comments (post_id, nickname, content, status)
            VALUES (?, ?, ?, 'pending')
            """,
            (post_id, payload.nickname.strip(), payload.content.strip()),
        )
    return {"id": cursor.lastrowid, "status": "pending"}
