def _admin_headers(client):
    response = client.post("/api/admin/login", json={"username": "admin", "password": "secret"})
    return {"Authorization": f"Bearer {response.json()['token']}"}


def test_admin_login_success_and_failure(seeded_client):
    success = seeded_client.post("/api/admin/login", json={"username": "admin", "password": "secret"})
    failure = seeded_client.post("/api/admin/login", json={"username": "admin", "password": "wrong"})

    assert success.status_code == 200
    assert "token" in success.json()
    assert failure.status_code == 401


def test_admin_routes_require_token(seeded_client):
    response = seeded_client.get("/api/admin/posts")

    assert response.status_code == 401


def test_admin_post_crud(seeded_client):
    headers = _admin_headers(seeded_client)
    payload = {
        "title": "后台文章",
        "slug": "admin-post",
        "excerpt": "摘要",
        "body": "正文",
        "category": "works",
        "status": "draft",
        "published_at": None,
    }

    created = seeded_client.post("/api/admin/posts", json=payload, headers=headers)
    post_id = created.json()["id"]
    updated = seeded_client.put(
        f"/api/admin/posts/{post_id}",
        json={**payload, "status": "published", "published_at": "2026-06-23"},
        headers=headers,
    )
    listed = seeded_client.get("/api/admin/posts", headers=headers)
    deleted = seeded_client.delete(f"/api/admin/posts/{post_id}", headers=headers)

    assert created.status_code == 201
    assert updated.status_code == 200
    assert any(item["slug"] == "admin-post" for item in listed.json()["items"])
    assert deleted.status_code == 200


def test_admin_moderation_updates_public_visibility(seeded_client):
    headers = _admin_headers(seeded_client)
    seeded_client.post("/api/posts/public-tech/comments", json={"nickname": "访客", "content": "评论"})
    seeded_client.post("/api/messages", json={"nickname": "访客", "content": "留言"})

    comments = seeded_client.get("/api/admin/comments", headers=headers).json()["items"]
    messages = seeded_client.get("/api/admin/messages", headers=headers).json()["items"]

    seeded_client.put(f"/api/admin/comments/{comments[0]['id']}", json={"status": "approved"}, headers=headers)
    seeded_client.put(f"/api/admin/messages/{messages[0]['id']}", json={"status": "approved"}, headers=headers)

    assert seeded_client.get("/api/posts/public-tech/comments").json()["items"][0]["content"] == "评论"
    assert seeded_client.get("/api/messages").json()["items"][0]["content"] == "留言"


def test_admin_stats(seeded_client):
    headers = _admin_headers(seeded_client)
    stats = seeded_client.get("/api/admin/stats", headers=headers)

    assert stats.status_code == 200
    assert stats.json()["post_count"] == 3
