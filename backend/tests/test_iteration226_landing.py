"""Iteration 226 — Landing page public webinar API tests."""
import os
import requests
import pytest
from dotenv import dotenv_values

frontend_env = dotenv_values("/app/frontend/.env")
base_url = os.environ.get("REACT_APP_BACKEND_URL") or frontend_env.get("REACT_APP_BACKEND_URL")
if not base_url:
    raise RuntimeError("REACT_APP_BACKEND_URL missing")
BASE_URL = base_url.rstrip("/")
PUBLIC = f"{BASE_URL}/api/karau/webinar/public/upcoming"


@pytest.fixture(scope="module")
def client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


class TestPublicUpcomingWebinars:
    def test_no_auth_required(self, client):
        r = client.get(PUBLIC, timeout=30)
        assert r.status_code == 200, r.text[:300]
        data = r.json()
        assert "webinars" in data and "count" in data
        assert isinstance(data["webinars"], list)
        assert data["count"] == len(data["webinars"])
        assert data["count"] > 0, "no public webinars returned — landing page will fall back to demo card"

    def test_webinar_shape_and_no_mongo_id(self, client):
        webs = client.get(PUBLIC, timeout=30).json()["webinars"]
        for w in webs:
            assert "_id" not in w
            assert isinstance(w.get("webinar_id"), str) and w["webinar_id"]
            assert isinstance(w.get("title"), str) and w["title"]
            assert w.get("status") in ("scheduled", "live")
            assert isinstance(w.get("registered_count"), int)
            assert "registrations" not in w
            assert len(w.get("description") or "") <= 180

    def test_no_test_titles(self, client):
        webs = client.get(PUBLIC, timeout=30).json()["webinars"]
        offenders = [w["title"] for w in webs if "test" in w["title"].lower()]
        assert offenders == [], f"test-titled webinars leaked to public: {offenders}"

    def test_default_limit_max_6(self, client):
        assert len(client.get(PUBLIC, timeout=30).json()["webinars"]) <= 6

    def test_limit_param_respected(self, client):
        r = client.get(f"{PUBLIC}?limit=2", timeout=30)
        assert r.status_code == 200
        assert len(r.json()["webinars"]) <= 2

    def test_limit_capped_at_12(self, client):
        r = client.get(f"{PUBLIC}?limit=100", timeout=30)
        assert r.status_code == 200
        assert len(r.json()["webinars"]) <= 12

    def test_sorted_by_scheduled_time(self, client):
        times = [w.get("scheduled_time") for w in client.get(PUBLIC, timeout=30).json()["webinars"]]
        assert times == sorted(times), f"not sorted ascending: {times}"

    def test_detail_route_still_works_after_public_route(self, client):
        webs = client.get(PUBLIC, timeout=30).json()["webinars"]
        wid = webs[0]["webinar_id"]
        r = client.get(f"{BASE_URL}/api/karau/webinar/{wid}", timeout=30)
        assert r.status_code == 200, r.text[:300]
        d = r.json()
        assert d["webinar_id"] == wid
        assert d["title"] == webs[0]["title"]
        assert "_id" not in d

    def test_unknown_webinar_404(self, client):
        r = client.get(f"{BASE_URL}/api/karau/webinar/WEB-DOESNOTEXIST", timeout=30)
        assert r.status_code == 404


class TestAuthRegression:
    def test_admin_login(self, client):
        r = client.post(f"{BASE_URL}/api/auth/login",
                        json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"},
                        timeout=30)
        assert r.status_code == 200, r.text[:300]
        assert r.json().get("access_token")
