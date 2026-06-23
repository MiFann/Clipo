def test_posts_list_only_published_posts(seeded_client):
    response = seeded_client.get("/api/posts")

    assert response.status_code == 200
    slugs = [item["slug"] for item in response.json()["items"]]
    assert "public-tech" in slugs
    assert "public-note" in slugs
    assert "draft-note" not in slugs


def test_posts_filter_by_category_and_query(seeded_client):
    category_response = seeded_client.get("/api/posts?category=notes")
    query_response = seeded_client.get("/api/posts?query=技术")

    assert [item["slug"] for item in category_response.json()["items"]] == ["public-note"]
    assert [item["slug"] for item in query_response.json()["items"]] == ["public-tech"]


def test_post_detail_by_slug_and_missing_slug(seeded_client):
    response = seeded_client.get("/api/posts/public-tech")
    missing = seeded_client.get("/api/posts/missing")

    assert response.status_code == 200
    assert response.json()["slug"] == "public-tech"
    assert response.json()["view_count"] == 1
    assert missing.status_code == 404
