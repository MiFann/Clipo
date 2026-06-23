from backend.app.database import connection_scope


def test_pending_comments_and_messages_are_hidden(seeded_client):
    seeded_client.post("/api/posts/public-tech/comments", json={"nickname": "访客", "content": "待审核"})
    seeded_client.post("/api/messages", json={"nickname": "访客", "content": "待审核"})

    assert seeded_client.get("/api/posts/public-tech/comments").json()["items"] == []
    assert seeded_client.get("/api/messages").json()["items"] == []


def test_approved_comments_and_messages_are_visible(seeded_client):
    seeded_client.post("/api/posts/public-tech/comments", json={"nickname": "访客", "content": "已通过"})
    seeded_client.post("/api/messages", json={"nickname": "访客", "content": "已通过"})

    with connection_scope() as db:
        db.execute("UPDATE comments SET status = 'approved'")
        db.execute("UPDATE messages SET status = 'approved'")

    comments = seeded_client.get("/api/posts/public-tech/comments").json()["items"]
    messages = seeded_client.get("/api/messages").json()["items"]

    assert comments[0]["content"] == "已通过"
    assert messages[0]["content"] == "已通过"


def test_interaction_input_validation(seeded_client):
    response = seeded_client.post("/api/messages", json={"nickname": "", "content": ""})

    assert response.status_code == 422
