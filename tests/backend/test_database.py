from backend.app.database import connection_scope


def test_database_initializes_tables(client):
    with connection_scope() as db:
        tables = {
            row["name"]
            for row in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        }

    assert {"users", "posts", "comments", "messages", "visits", "site_stats"}.issubset(tables)


def test_interactions_default_to_pending(seeded_client):
    comment = seeded_client.post(
        "/api/posts/public-tech/comments",
        json={"nickname": "访客", "content": "评论内容"},
    )
    message = seeded_client.post(
        "/api/messages",
        json={"nickname": "访客", "content": "留言内容"},
    )

    assert comment.status_code == 201
    assert comment.json()["status"] == "pending"
    assert message.status_code == 201
    assert message.json()["status"] == "pending"
