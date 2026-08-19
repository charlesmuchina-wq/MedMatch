"""Iteration 224 — ENZI @AI channel assistant + LiveKit live captions backend regression."""
import os

import pytest
import requests
from dotenv import dotenv_values

frontend_env = dotenv_values("/app/frontend/.env")
base_url = os.environ.get("REACT_APP_BACKEND_URL") or frontend_env.get("REACT_APP_BACKEND_URL")
if not base_url:
    raise RuntimeError("REACT_APP_BACKEND_URL missing")
BASE_URL = base_url.rstrip("/")

ADMIN = {"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}


@pytest.fixture(scope="module")
def token():
    r = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN, timeout=60)
    if r.status_code != 200:
        pytest.fail(f"login failed {r.status_code}: {r.text[:300]}")
    t = r.json().get("access_token") or r.json().get("token")
    assert t
    return t


@pytest.fixture(scope="module")
def auth(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


@pytest.fixture(scope="module")
def channel_id(auth):
    r = requests.get(f"{BASE_URL}/api/lumi/channels", headers=auth, timeout=60)
    assert r.status_code == 200, r.text[:300]
    body = r.json()
    chans = body if isinstance(body, list) else (body.get("my_channels") or body.get("channels") or [])
    assert len(chans) > 0, "no channels for admin"
    return chans[0]["id"]


# ---------- LUMI existing routes regression ----------
class TestLumiRegression:
    def test_channels_list_auth(self, auth):
        r = requests.get(f"{BASE_URL}/api/lumi/channels", headers=auth, timeout=60)
        assert r.status_code == 200
        assert '"_id"' not in r.text

    def test_channels_requires_auth(self):
        r = requests.get(f"{BASE_URL}/api/lumi/channels", timeout=60)
        assert r.status_code in (401, 403), r.status_code

    def test_messages_list(self, auth, channel_id):
        r = requests.get(f"{BASE_URL}/api/lumi/channels/{channel_id}/messages", headers=auth, timeout=60)
        assert r.status_code == 200
        assert '"_id"' not in r.text


# ---------- ENZI AI agent ----------
class TestEnziAI:
    def test_ai_requires_auth(self, channel_id):
        r = requests.post(f"{BASE_URL}/api/lumi/channels/{channel_id}/ai",
                          json={"query": "summarize"}, timeout=60)
        assert r.status_code in (401, 403), f"{r.status_code} {r.text[:200]}"

    def test_ai_forbidden_for_non_member(self, auth):
        r = requests.post(f"{BASE_URL}/api/lumi/channels/ch_does_not_exist_zzz/ai",
                          json={"query": "summarize"}, headers=auth, timeout=60)
        assert r.status_code == 403, f"{r.status_code} {r.text[:200]}"

    def test_ai_empty_query_rejected(self, auth, channel_id):
        r = requests.post(f"{BASE_URL}/api/lumi/channels/{channel_id}/ai",
                          json={"query": "   "}, headers=auth, timeout=60)
        assert r.status_code == 400, f"{r.status_code} {r.text[:200]}"

    def test_ai_summarize_posts_message(self, auth, channel_id):
        r = requests.post(f"{BASE_URL}/api/lumi/channels/{channel_id}/ai",
                          json={"query": "summarize this conversation"}, headers=auth, timeout=120)
        assert r.status_code == 200, f"{r.status_code} {r.text[:300]}"
        d = r.json()
        assert d["ai_intent"] == "summarize"
        assert d["sender_name"] == "ENZI AI"
        assert d["type"] == "ai_assistant"
        assert isinstance(d["content"], str) and len(d["content"]) > 10
        assert "_id" not in d
        # persistence check
        g = requests.get(f"{BASE_URL}/api/lumi/channels/{channel_id}/messages",
                         headers=auth, timeout=60)
        assert g.status_code == 200
        assert d["id"] in g.text

    def test_ai_actions_intent(self, auth, channel_id):
        r = requests.post(f"{BASE_URL}/api/lumi/channels/{channel_id}/ai",
                          json={"query": "extract action items"}, headers=auth, timeout=120)
        assert r.status_code == 200, f"{r.status_code} {r.text[:300]}"
        d = r.json()
        assert d["ai_intent"] == "actions"
        assert len(d["content"]) > 5


# ---------- Captions dependencies ----------
class TestCaptionsBackend:
    def test_translate_languages_endpoint(self):
        r = requests.get(f"{BASE_URL}/api/translate/languages", timeout=60)
        assert r.status_code == 200, f"{r.status_code} {r.text[:200]}"
        langs = r.json().get("languages")
        assert isinstance(langs, list) and len(langs) >= 50, f"only {len(langs or [])} languages"
        assert "code" in langs[0] and "name" in langs[0]

    def test_realtime_stt_status(self, auth):
        r = requests.get(f"{BASE_URL}/api/realtime-stt/status", headers=auth, timeout=60)
        assert r.status_code == 200, r.text[:200]
        assert r.json().get("available") is True

    def test_lumi_translate(self):
        r = requests.post(f"{BASE_URL}/api/lumi/ai/translate",
                          json={"text": "Hello everyone", "target_language": "French"}, timeout=90)
        assert r.status_code == 200, f"{r.status_code} {r.text[:300]}"
        assert r.json().get("translated_text")
