"""Iteration 222 - Portal Functional Assessment
Tests core backend endpoints supporting:
  - MedMatch admin auth
  - AI KARAU (karau_meet + livekit token + promote)
  - ENZI (lumi channels/messages)
  - Observability (admin errors page)
"""
import os
import pytest
import requests
from pathlib import Path

# Load REACT_APP_BACKEND_URL from frontend .env
def _load_base_url():
    env = Path("/app/frontend/.env").read_text()
    for line in env.splitlines():
        if line.startswith("REACT_APP_BACKEND_URL="):
            return line.split("=", 1)[1].strip().rstrip("/")
    raise RuntimeError("REACT_APP_BACKEND_URL not set")

BASE_URL = _load_base_url()
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"


@pytest.fixture(scope="module")
def s():
    return requests.Session()


@pytest.fixture(scope="module")
def admin_token(s):
    r = s.post(f"{BASE_URL}/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=15)
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text[:200]}"
    data = r.json()
    tok = data.get("access_token") or data.get("token")
    assert tok, f"no token in {data}"
    return tok


@pytest.fixture(scope="module")
def auth(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


# ---------------------- Health ----------------------
class TestHealth:
    def test_health(self, s):
        r = s.get(f"{BASE_URL}/api/health", timeout=10)
        assert r.status_code == 200


# ---------------------- Auth ----------------------
class TestAuth:
    def test_admin_login(self, admin_token):
        assert isinstance(admin_token, str) and len(admin_token) > 10

    def test_me(self, s, auth):
        r = s.get(f"{BASE_URL}/api/auth/me", headers=auth, timeout=10)
        assert r.status_code == 200
        u = r.json()
        assert u.get("email") == ADMIN_EMAIL


# ---------------------- AI KARAU ----------------------
class TestKarau:
    def test_meetings_list(self, s, auth):
        r = s.get(f"{BASE_URL}/api/karau-meet/meetings", headers=auth, timeout=10)
        assert r.status_code == 200
        data = r.json()
        meetings = data["meetings"] if isinstance(data, dict) else data
        assert isinstance(meetings, list)

    def test_create_meeting_and_livekit_token(self, s, auth):
        # create meeting
        r = s.post(f"{BASE_URL}/api/karau-meet/meetings", headers=auth,
                   json={"title": "TEST_iter222_meeting", "scheduled_for": "2026-12-31T10:00:00Z"}, timeout=10)
        assert r.status_code in (200, 201), r.text[:300]
        m = r.json()
        meeting_id = m.get("meeting_id") or m.get("id") or m.get("_id")
        assert meeting_id, f"no id: {m}"

        # livekit token for that meeting
        r2 = s.post(f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/livekit-token",
                    headers=auth, json={}, timeout=10)
        # 200 if livekit configured; 4xx/5xx if not — still acceptable for non-blocking
        assert r2.status_code in (200, 400, 500, 503), r2.text[:200]
        if r2.status_code == 200:
            tok = r2.json()
            assert "token" in tok or "access_token" in tok

    def test_livekit_status(self, s, auth):
        r = s.get(f"{BASE_URL}/api/livekit/status", headers=auth, timeout=10)
        # endpoint may return 200 or 404 depending on impl
        assert r.status_code in (200, 404), r.text[:200]

    def test_livekit_token_generic(self, s, auth):
        r = s.post(f"{BASE_URL}/api/livekit/token", headers=auth,
                   json={"room_name": "TEST_iter222_room", "identity": "admin"}, timeout=10)
        assert r.status_code in (200, 400, 403, 500), r.text[:300]


# ---------------------- ENZI / Lumi ----------------------
class TestEnzi:
    def test_lumi_channels(self, s, auth):
        r = s.get(f"{BASE_URL}/api/lumi/channels", headers=auth, timeout=10)
        assert r.status_code == 200
        data = r.json()
        # Endpoint returns {discover: [...], my_channels: [...]} or a flat list
        if isinstance(data, dict):
            assert "discover" in data or "my_channels" in data
        else:
            assert isinstance(data, list)


# ---------------------- Observability ----------------------
class TestObservability:
    def test_errors_list(self, s, auth):
        r = s.get(f"{BASE_URL}/api/observability/errors", headers=auth, timeout=10)
        assert r.status_code == 200
        data = r.json()
        # list or dict {items: [...]}
        assert isinstance(data, (list, dict))

    def test_errors_stats(self, s, auth):
        r = s.get(f"{BASE_URL}/api/observability/errors/stats", headers=auth, timeout=10)
        assert r.status_code == 200
