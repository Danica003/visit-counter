import redis

from app import app, redis_client


def test_rootreturns_200():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Hello DevOps"

def test_visits_returns_counter(monkeypatch):
    monkeypatch.setattr(redis_client,"incr",lambda key:42)
    response = app.test_client().get("/visits")
    assert response.status_code == 200
    assert response.get_json() =={"visits":42}

def test_health_ok_when_redis_available(monkeypatch):
    monkeypatch.setattr(redis_client,"ping",lambda: True)
    response = app.test_client().get("/health")
    assert response.status_code == 200
    assert response.get_json()=={"status":"ok"}

def test_health_503_when_redis_down(monkeypatch):
    def fail():
        raise redis.exceptions.ConnectionError()
    monkeypatch.setattr(redis_client, "ping",fail)
    response = app.test_client().get("/health")
    assert response.status_code ==503
    assert response.get_json()=={"status":"error"}