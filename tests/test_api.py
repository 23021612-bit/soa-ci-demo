API = "/api/v1/tasks"


def create(client, title="Learn CI/CD", **extra):
    return client.post(API, json={"title": title, **extra})


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}


def test_list_empty(client):
    r = client.get(API)
    assert r.status_code == 200
    assert r.get_json() == {"items": [], "total": 0}


def test_create_task(client):
    r = create(client)
    assert r.status_code == 201
    body = r.get_json()
    assert body == {"id": 1, "title": "Learn CI/CD", "done": False}
    assert r.headers["Location"] == f"{API}/1"


def test_create_requires_title(client):
    assert client.post(API, json={}).status_code == 400
    assert client.post(API, json={"title": "   "}).status_code == 400


def test_create_rejects_non_json(client):
    r = client.post(API, data="not json", content_type="text/plain")
    assert r.status_code == 400


def test_create_rejects_bad_done(client):
    r = create(client, done="yes")
    assert r.status_code == 400


def test_get_task(client):
    create(client)
    r = client.get(f"{API}/1")
    assert r.status_code == 200
    assert r.get_json()["title"] == "Learn CI/CD"


def test_get_missing_task(client):
    r = client.get(f"{API}/999")
    assert r.status_code == 404
    assert r.get_json()["error"]["code"] == 404


def test_update_task(client):
    create(client)
    r = client.put(f"{API}/1", json={"title": "Done!", "done": True})
    assert r.status_code == 200
    assert r.get_json() == {"id": 1, "title": "Done!", "done": True}


def test_update_validation(client):
    create(client)
    assert client.put(f"{API}/1", json={"title": "x"}).status_code == 400
    assert client.put(f"{API}/999", json={"title": "x", "done": True}).status_code == 404


def test_delete_task(client):
    create(client)
    assert client.delete(f"{API}/1").status_code == 204
    assert client.get(f"{API}/1").status_code == 404
    assert client.delete(f"{API}/1").status_code == 404


def test_filter_by_done(client):
    create(client, "a", done=True)
    create(client, "b", done=False)
    r = client.get(f"{API}?done=true")
    assert [t["title"] for t in r.get_json()["items"]] == ["a"]
    assert client.get(f"{API}?done=maybe").status_code == 400


def test_unknown_route_returns_json_404(client):
    r = client.get("/nope")
    assert r.status_code == 404
    assert "error" in r.get_json()


def test_method_not_allowed(client):
    r = client.patch(f"{API}/1")
    assert r.status_code == 405
