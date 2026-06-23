from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..database import connection_scope
from ..models import LoginPayload, ModerationPayload, PostPayload
from ..security import create_token, require_admin, verify_password


router = APIRouter(prefix="/api/admin")


@router.post("/login")
def login(payload: LoginPayload) -> dict[str, str]:
    with connection_scope() as db:
        row = db.execute("SELECT username, password_hash FROM users WHERE username = ?", (payload.username,)).fetchone()

    if not row or not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {"token": create_token(row["username"])}


@router.get("/me")
def me(username: str = Depends(require_admin)) -> dict[str, str]:
    return {"username": username}


@router.get("/posts")
def admin_list_posts(_: str = Depends(require_admin)) -> dict:
    with connection_scope() as db:
        rows = db.execute(
            """
            SELECT id, title, slug, excerpt, body, category, status, published_at, created_at, updated_at, view_count
            FROM posts
            ORDER BY updated_at DESC, id DESC
            """
        ).fetchall()
    return {"items": [dict(row) for row in rows]}


@router.post("/posts", status_code=201)
def admin_create_post(payload: PostPayload, _: str = Depends(require_admin)) -> dict:
    with connection_scope() as db:
        cursor = db.execute(
            """
            INSERT INTO posts (title, slug, excerpt, body, category, status, published_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.title,
                payload.slug,
                payload.excerpt,
                payload.body,
                payload.category,
                payload.status,
                payload.published_at,
            ),
        )
    return {"id": cursor.lastrowid}


@router.put("/posts/{post_id}")
def admin_update_post(post_id: int, payload: PostPayload, _: str = Depends(require_admin)) -> dict[str, str]:
    with connection_scope() as db:
        cursor = db.execute(
            """
            UPDATE posts
            SET title = ?, slug = ?, excerpt = ?, body = ?, category = ?, status = ?,
                published_at = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                payload.title,
                payload.slug,
                payload.excerpt,
                payload.body,
                payload.category,
                payload.status,
                payload.published_at,
                post_id,
            ),
        )
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"status": "updated"}


@router.delete("/posts/{post_id}")
def admin_delete_post(post_id: int, _: str = Depends(require_admin)) -> dict[str, str]:
    with connection_scope() as db:
        cursor = db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"status": "deleted"}


@router.get("/comments")
def admin_list_comments(_: str = Depends(require_admin)) -> dict:
    with connection_scope() as db:
        rows = db.execute(
            """
            SELECT comments.id, comments.nickname, comments.content, comments.status, comments.created_at,
                   posts.title AS post_title, posts.slug AS post_slug
            FROM comments
            JOIN posts ON posts.id = comments.post_id
            ORDER BY comments.created_at DESC, comments.id DESC
            """
        ).fetchall()
    return {"items": [dict(row) for row in rows]}


@router.put("/comments/{comment_id}")
def admin_update_comment(comment_id: int, payload: ModerationPayload, _: str = Depends(require_admin)) -> dict[str, str]:
    with connection_scope() as db:
        cursor = db.execute(
            "UPDATE comments SET status = ?, reviewed_at = CURRENT_TIMESTAMP WHERE id = ?",
            (payload.status, comment_id),
        )
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"status": "updated"}


@router.delete("/comments/{comment_id}")
def admin_delete_comment(comment_id: int, _: str = Depends(require_admin)) -> dict[str, str]:
    with connection_scope() as db:
        cursor = db.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"status": "deleted"}


@router.get("/messages")
def admin_list_messages(_: str = Depends(require_admin)) -> dict:
    with connection_scope() as db:
        rows = db.execute(
            """
            SELECT id, nickname, content, status, created_at, reviewed_at
            FROM messages
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()
    return {"items": [dict(row) for row in rows]}


@router.put("/messages/{message_id}")
def admin_update_message(message_id: int, payload: ModerationPayload, _: str = Depends(require_admin)) -> dict[str, str]:
    with connection_scope() as db:
        cursor = db.execute(
            "UPDATE messages SET status = ?, reviewed_at = CURRENT_TIMESTAMP WHERE id = ?",
            (payload.status, message_id),
        )
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"status": "updated"}


@router.delete("/messages/{message_id}")
def admin_delete_message(message_id: int, _: str = Depends(require_admin)) -> dict[str, str]:
    with connection_scope() as db:
        cursor = db.execute("DELETE FROM messages WHERE id = ?", (message_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"status": "deleted"}


@router.get("/stats")
def admin_stats(_: str = Depends(require_admin)) -> dict:
    with connection_scope() as db:
        row = db.execute("SELECT value FROM site_stats WHERE key = 'total_visits'").fetchone()
        post_count = db.execute("SELECT COUNT(*) AS count FROM posts").fetchone()["count"]
        comment_count = db.execute("SELECT COUNT(*) AS count FROM comments").fetchone()["count"]
        message_count = db.execute("SELECT COUNT(*) AS count FROM messages").fetchone()["count"]

    return {
        "total_visits": row["value"] if row else 0,
        "post_count": post_count,
        "comment_count": comment_count,
        "message_count": message_count,
    }
