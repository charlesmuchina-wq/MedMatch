"""Iteration 223 — Regression smoke for refactored route packages (translation/, lumi_messenger/)
   plus LiveKit token endpoint role parity for webinar speaker-queue feature.
"""
import os
import pytest
import requests

def _load_base_url():
    v = os.environ.get("REACT_APP_BACKEND_URL")
    if not v:
        # fallback to frontend/.env
        try:
            with open("/app/frontend/.env") as f:
                for line in f:
                    if line.startswith("REACT_APP_BACKEND_URL="):
                        v = line.split("=", 1)[1].strip()
                        break
        except Exception:
            pass
    assert v, "REACT_APP_BACKEND_URL not set"
    return v.rstrip("/")


BASE_URL = _load_base_url()
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"
HOST_EMAIL = "info@charstan.com"
HOST_PASSWORD = "Swampdigger26!"
WEBINAR_ID = "6EEC4A83"


@pytest.fixture(scope="session")
def admin_token():
    r = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=15,
    )
    assert r.status_code == 200, f"admin login failed: {r.status_code} {r.text}"
    tok = r.json().get("access_token")
    assert tok, "no access_token in admin login response"
    return tok


@pytest.fixture(scope="session")
def host_token():
    r = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": HOST_EMAIL, "password": HOST_PASSWORD},
        timeout=15,
    )
    if r.status_code != 200:
        pytest.skip(f"host login failed: {r.status_code} {r.text}")
    return r.json().get("access_token")


def _auth(tok):
    return {"Authorization": f"Bearer {tok}"}


# ---------- translation/ package ----------

class TestTranslationPackage:
    def test_languages_public(self):
        r = requests.get(f"{BASE_URL}/api/translate/languages", timeout=15)
        assert r.status_code == 200, r.text
        data = r.json()
        # response should contain list of languages
        assert isinstance(data, (list, dict))

    def test_analytics_admin(self, admin_token):
        r = requests.get(
            f"{BASE_URL}/api/translate/analytics", headers=_auth(admin_token), timeout=15
        )
        assert r.status_code == 200, r.text

    def test_memory_stats_admin(self, admin_token):
        r = requests.get(
            f"{BASE_URL}/api/translate/memory/stats",
            headers=_auth(admin_token),
            timeout=15,
        )
        assert r.status_code == 200, r.text

    def test_quality_stats_admin(self, admin_token):
        r = requests.get(
            f"{BASE_URL}/api/translate/quality/stats",
            headers=_auth(admin_token),
            timeout=15,
        )
        assert r.status_code == 200, r.text


# ---------- lumi_messenger/ package ----------

class TestLumiMessengerPackage:
    def test_channels_no_auth_is_401(self):
        r = requests.get(f"{BASE_URL}/api/lumi/channels", timeout=15)
        assert r.status_code in (401, 403), f"expected 401/403 got {r.status_code}"

    def test_channels_admin_200(self, admin_token):
        r = requests.get(
            f"{BASE_URL}/api/lumi/channels", headers=_auth(admin_token), timeout=15
        )
        assert r.status_code == 200, r.text

    def test_presence_admin(self, admin_token):
        r = requests.get(
            f"{BASE_URL}/api/lumi/presence", headers=_auth(admin_token), timeout=15
        )
        assert r.status_code == 200, r.text

    def test_compliance_frameworks_admin(self, admin_token):
        r = requests.get(
            f"{BASE_URL}/api/lumi/compliance/frameworks",
            headers=_auth(admin_token),
            timeout=15,
        )
        assert r.status_code == 200, r.text

    def test_admin_org_settings(self, admin_token):
        r = requests.get(
            f"{BASE_URL}/api/lumi/admin/org-settings",
            headers=_auth(admin_token),
            timeout=15,
        )
        # admin can fetch; allow 200 or 404 if org-settings not yet created
        assert r.status_code in (200, 404), r.text


# ---------- LiveKit token role parity for webinar speaker queue ----------

class TestLiveKitTokenRoles:
    def test_host_can_publish(self, host_token):
        r = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{WEBINAR_ID}/livekit-token",
            headers=_auth(host_token),
            timeout=20,
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert "token" in data, data
        assert data.get("is_host") is True, f"host should be host: {data}"

    def test_attendee_subscribe_only(self, admin_token):
        # admin@medmatch.com is NOT the webinar host; should get subscribe-only attendee token
        r = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{WEBINAR_ID}/livekit-token",
            headers=_auth(admin_token),
            timeout=20,
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert "token" in data
        assert data.get("is_host") is False, f"non-host should be attendee: {data}"
