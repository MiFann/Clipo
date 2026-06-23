from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from ..database import connection_scope, row_to_dict


router = APIRouter(prefix="/api")


@router.get("/posts")
def list_posts(
    category: str | None = Query(default=None),
    query: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> dict:
    clauses = ["status = 'published'"]
    params: list[object] = []

    if category and category != "all":
        clauses.append("category = ?")
        params.append(category)

    if query:
        clauses.append("(title LIKE ? OR excerpt LIKE ? OR body LIKE ?)")
        pattern = f"%{query}%"
        params.extend([pattern, pattern, pattern])

    where = " AND ".join(clauses)
    offset = (page - 1) * page_size

    with connection_scope() as db:
        total = db.execute(f"SELECT COUNT(*) AS count FROM posts WHERE {where}", params).fetchone()["count"]
        rows = db.execute(
            f"""
            SELECT id, title, slug, excerpt, category, published_at, created_at, view_count
            FROM posts
            WHERE {where}
            ORDER BY COALESCE(published_at, created_at) DESC, id DESC
            LIMIT ? OFFSET ?
            """,
            [*params, page_size, offset],
        ).fetchall()

    return {"items": [dict(row) for row in rows], "page": page, "page_size": page_size, "total": total}


@router.get("/posts/{slug}")
def get_post(slug: str) -> dict:
    with connection_scope() as db:
        row = db.execute(
            """
            SELECT id, title, slug, excerpt, body, category, published_at, created_at, updated_at, view_count
            FROM posts
            WHERE slug = ? AND status = 'published'
            """,
            (slug,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Post not found")

        db.execute("UPDATE posts SET view_count = view_count + 1 WHERE id = ?", (row["id"],))

    post = row_to_dict(row)
    post["view_count"] += 1
    return post
