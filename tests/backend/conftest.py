import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("BLOG_DB_PATH", str(tmp_path / "test.db"))

    from backend.app.main import create_app
    from backend.app.security import clear_tokens

    clear_tokens()
    return TestClient(create_app())


@pytest.fixture()
def seeded_client(client):
    from backend.app.database import connection_scope
    from backend.app.security import hash_password

    with connection_scope() as db:
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ("admin", hash_password("secret")),
        )
        db.execute(
            """
            INSERT INTO posts (title, slug, excerpt, body, category, status, published_at)
            VALUES
              ('公开技术文', 'public-tech', '公开摘要', '公开正文', 'tech', 'published', '2026-06-23'),
              ('草稿文', 'draft-note', '草稿摘要', '草稿正文', 'notes', 'draft', NULL),
              ('公开随笔', 'public-note', '随笔摘要', '随笔正文', 'notes', 'published', '2026-06-22')
            """
        )

    return client
