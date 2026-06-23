from backend.app.database import connection_scope


def test_visit_stats_are_recorded(seeded_client):
    response = seeded_client.post("/api/stats/visit", json={"path": "/#post/public-tech", "slug": "public-tech"})

    assert response.status_code == 201
    assert response.json() == {"status": "recorded"}

    with connection_scope() as db:
        total = db.execute("SELECT value FROM site_stats WHERE key = 'total_visits'").fetchone()["value"]

    assert total == 1
