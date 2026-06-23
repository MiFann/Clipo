from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "blog.db"


def get_database_path() -> Path:
    configured = os.getenv("BLOG_DB_PATH")
    return Path(configured).resolve() if configured else DEFAULT_DB_PATH


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or get_database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def connection_scope(db_path: Path | None = None) -> Iterator[sqlite3.Connection]:
    connection = connect(db_path)
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def initialize_database(db_path: Path | None = None) -> None:
    with connection_scope(db_path) as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL UNIQUE,
              password_hash TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS posts (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              title TEXT NOT NULL,
              slug TEXT NOT NULL UNIQUE,
              excerpt TEXT NOT NULL DEFAULT '',
              body TEXT NOT NULL,
              category TEXT NOT NULL CHECK (category IN ('notes', 'tech', 'works')),
              status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'published')),
              published_at TEXT,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              view_count INTEGER NOT NULL DEFAULT 0
            );

            CREATE INDEX IF NOT EXISTS idx_posts_status_category
              ON posts(status, category, published_at);

            CREATE TABLE IF NOT EXISTS comments (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
              nickname TEXT NOT NULL,
              content TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'hidden')),
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              reviewed_at TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_comments_post_status
              ON comments(post_id, status, created_at);

            CREATE TABLE IF NOT EXISTS messages (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              nickname TEXT NOT NULL,
              content TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'hidden')),
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              reviewed_at TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_messages_status_created
              ON messages(status, created_at);

            CREATE TABLE IF NOT EXISTS visits (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              path TEXT NOT NULL,
              post_id INTEGER REFERENCES posts(id) ON DELETE SET NULL,
              ip_hash TEXT,
              user_agent TEXT,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS site_stats (
              key TEXT PRIMARY KEY,
              value INTEGER NOT NULL DEFAULT 0,
              updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )


def row_to_dict(row: sqlite3.Row | None) -> dict | None:
    return dict(row) if row is not None else None
