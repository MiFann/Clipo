from __future__ import annotations

import os

from .database import connection_scope, initialize_database
from .security import hash_password


STARTER_POSTS = [
    {
        "title": "动态博客上线记录",
        "slug": "dynamic-blog-launch-notes",
        "excerpt": "从静态页面迁移到 FastAPI 与 SQLite 后，内容发布和互动会变得更自由。",
        "body": "这篇文章用于验证动态博客的发布、列表、详情和访问统计流程。",
        "category": "tech",
        "status": "published",
        "published_at": "2026-06-23",
    },
    {
        "title": "安静界面仍然适合动态内容",
        "slug": "quiet-interface-dynamic-content",
        "excerpt": "动态能力不意味着界面要变重，后台和前台都可以保持克制。",
        "body": "评论、留言和搜索都应该服务阅读，而不是抢走内容的注意力。",
        "category": "notes",
        "status": "published",
        "published_at": "2026-06-23",
    },
]


def seed_admin(username: str | None = None, password: str | None = None) -> None:
    initialize_database()
    admin_username = username or os.getenv("BLOG_ADMIN_USERNAME", "admin")
    admin_password = password or os.getenv("BLOG_ADMIN_PASSWORD", "admin123456")

    with connection_scope() as db:
        exists = db.execute("SELECT id FROM users WHERE username = ?", (admin_username,)).fetchone()
        if not exists:
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (admin_username, hash_password(admin_password)),
            )


def seed_posts() -> None:
    initialize_database()
    with connection_scope() as db:
        for post in STARTER_POSTS:
            exists = db.execute("SELECT id FROM posts WHERE slug = ?", (post["slug"],)).fetchone()
            if exists:
                continue
            db.execute(
                """
                INSERT INTO posts (title, slug, excerpt, body, category, status, published_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    post["title"],
                    post["slug"],
                    post["excerpt"],
                    post["body"],
                    post["category"],
                    post["status"],
                    post["published_at"],
                ),
            )


def seed_all() -> None:
    seed_admin()
    seed_posts()


if __name__ == "__main__":
    seed_all()
