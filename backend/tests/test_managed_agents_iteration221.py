"""Backend tests for Managed Agents feature (iteration 221)."""
import os
import time
import pytest
import requests
from pathlib import Path

# Load REACT_APP_BACKEND_URL from frontend/.env if not in env
def _load_base_url():
    v = os.environ.get("REACT_APP_BACKEND_URL")
    if v:
        return v.rstrip("/")
    fenv = Path("/app/frontend/.env")
    if fenv.exists():
        for line in fenv.read_text().splitlines():
            if line.startswith("REACT_APP_BACKEND_URL="):
                return line.split("=", 1)[1].strip().rstrip("/")
    raise RuntimeError("REACT_APP_BACKEND_URL not found")

BASE_URL = _load_base_url()
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"


@pytest.fixture(scope="module")
def token():
    # Use the email-based login endpoint
    r = requests.post(f"{BASE_URL}/api/auth/login/email",
                      json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=30)
    if r.status_code != 200:
        # Fall back to legacy paths
        r = requests.post(f"{BASE_URL}/api/auth/login",
                          json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=30)
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    data = r.json()
    tok = data.get("access_token") or data.get("token") or (data.get("user") or {}).get("access_token")
    assert tok, f"no token in login response: {data}"
    return tok


@pytest.fixture(scope="module")
def H(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


# ── Auth enforcement ────────────────────────────────────────────────
def test_status_requires_auth():
    r = requests.get(f"{BASE_URL}/api/agents/status", timeout=15)
    assert r.status_code == 401


def test_tasks_requires_auth():
    r = requests.get(f"{BASE_URL}/api/agents/tasks", timeout=15)
    assert r.status_code == 401


# ── Status ──────────────────────────────────────────────────────────
def test_status_ok(H):
    r = requests.get(f"{BASE_URL}/api/agents/status", headers=H, timeout=15)
    assert r.status_code == 200
    j = r.json()
    assert j.get("available") is True
    assert j.get("model") == "claude-sonnet-4-6"
    tools = j.get("tools") or []
    for t in ("list_tasks", "create_task", "update_task", "send_followup_email"):
        assert t in tools, f"missing tool {t}"


# ── Task CRUD ───────────────────────────────────────────────────────
def test_task_crud_flow(H):
    # create blank -> 400
    r = requests.post(f"{BASE_URL}/api/agents/tasks", headers=H, json={"title": "  "}, timeout=15)
    assert r.status_code == 400

    # create
    r = requests.post(f"{BASE_URL}/api/agents/tasks", headers=H,
                      json={"title": "TEST_iter221 task", "priority": "high", "assignee": "Maria"}, timeout=15)
    assert r.status_code == 200, r.text
    task = r.json()
    tid = task["id"]
    assert task["status"] == "open"
    assert task["priority"] == "high"
    assert "_id" not in task

    # list contains
    r = requests.get(f"{BASE_URL}/api/agents/tasks", headers=H, timeout=15)
    assert r.status_code == 200
    ids = [t["id"] for t in r.json()["tasks"]]
    assert tid in ids

    # invalid status -> 400
    r = requests.patch(f"{BASE_URL}/api/agents/tasks/{tid}", headers=H, json={"status": "bogus"}, timeout=15)
    assert r.status_code == 400
    r = requests.patch(f"{BASE_URL}/api/agents/tasks/{tid}", headers=H, json={"priority": "urgent"}, timeout=15)
    assert r.status_code == 400

    # valid update
    r = requests.patch(f"{BASE_URL}/api/agents/tasks/{tid}", headers=H,
                       json={"status": "in_progress", "priority": "low", "assignee": "John"}, timeout=15)
    assert r.status_code == 200
    upd = r.json()
    assert upd["status"] == "in_progress"
    assert upd["priority"] == "low"
    assert upd["assignee"] == "John"

    # patch missing -> 404
    r = requests.patch(f"{BASE_URL}/api/agents/tasks/task_doesnotexist", headers=H,
                       json={"status": "done"}, timeout=15)
    assert r.status_code == 404

    # stats
    r = requests.get(f"{BASE_URL}/api/agents/tasks-stats", headers=H, timeout=15)
    assert r.status_code == 200
    s = r.json()
    for k in ("total", "open", "in_progress", "done", "completion_rate"):
        assert k in s

    # delete
    r = requests.delete(f"{BASE_URL}/api/agents/tasks/{tid}", headers=H, timeout=15)
    assert r.status_code == 200
    assert r.json().get("deleted") is True

    # delete again -> 404
    r = requests.delete(f"{BASE_URL}/api/agents/tasks/{tid}", headers=H, timeout=15)
    assert r.status_code == 404


# ── Definitions ─────────────────────────────────────────────────────
def test_definitions_templates_and_custom(H):
    r = requests.get(f"{BASE_URL}/api/agents/definitions", headers=H, timeout=15)
    assert r.status_code == 200
    d = r.json()
    assert len(d.get("templates", [])) == 3
    tpl_ids = {t["id"] for t in d["templates"]}
    assert {"tpl_meeting_followup", "tpl_worklist_manager", "tpl_recruiting_ops"} <= tpl_ids

    # create with missing -> 400
    r = requests.post(f"{BASE_URL}/api/agents/definitions", headers=H,
                      json={"name": "", "system_prompt": "x"}, timeout=15)
    assert r.status_code == 400
    r = requests.post(f"{BASE_URL}/api/agents/definitions", headers=H,
                      json={"name": "n", "system_prompt": ""}, timeout=15)
    assert r.status_code == 400

    # create ok
    r = requests.post(f"{BASE_URL}/api/agents/definitions", headers=H,
                      json={"name": "TEST_iter221 agent", "system_prompt": "Be helpful."}, timeout=15)
    assert r.status_code == 200
    aid = r.json()["id"]

    # delete missing
    r = requests.delete(f"{BASE_URL}/api/agents/definitions/nope_xx", headers=H, timeout=15)
    assert r.status_code == 404

    # delete created
    r = requests.delete(f"{BASE_URL}/api/agents/definitions/{aid}", headers=H, timeout=15)
    assert r.status_code == 200


# ── Extract worklist ────────────────────────────────────────────────
def test_extract_worklist_validation(H):
    r = requests.post(f"{BASE_URL}/api/agents/extract-worklist", headers=H, json={}, timeout=15)
    assert r.status_code == 400


def test_extract_worklist_from_transcript(H):
    transcript = (
        "Q3 planning sync on Mon. "
        "Maria will draft the contract review by Friday. "
        "John needs to send the budget spreadsheet to finance by Wednesday. "
        "Priya will schedule onboarding interviews with three candidates next week. "
        "Carlos: follow up with the legal team about the NDA changes."
    )
    r = requests.post(f"{BASE_URL}/api/agents/extract-worklist", headers=H,
                      json={"transcript": transcript, "source_label": "TEST_iter221_meeting"}, timeout=120)
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["extracted"] >= 1
    assert isinstance(j["tasks"], list)
    sample = j["tasks"][0]
    assert sample["title"]
    assert sample["priority"] in ("low", "medium", "high")
    assert sample["status"] == "open"


# ── Conversational agent tool loop ──────────────────────────────────
def test_chat_tool_loop_creates_task(H):
    # snapshot tasks first
    r = requests.get(f"{BASE_URL}/api/agents/tasks", headers=H, timeout=15)
    before = {t["id"] for t in r.json()["tasks"]}

    msg = ("Create a high priority task titled 'TEST_iter221 Review contract' "
           "assigned to Maria, then list my open tasks.")
    r = requests.post(f"{BASE_URL}/api/agents/chat", headers=H,
                      json={"message": msg, "agent_id": "tpl_worklist_manager"}, timeout=180)
    assert r.status_code == 200, r.text
    j = r.json()
    assert j.get("reply")
    actions = j.get("actions") or []
    tools_called = [a.get("tool") for a in actions]
    assert "create_task" in tools_called, f"create_task not called: {tools_called}"
    # list_tasks expected too but not strict

    # Verify persisted
    time.sleep(0.5)
    r = requests.get(f"{BASE_URL}/api/agents/tasks", headers=H, timeout=15)
    titles = [t["title"] for t in r.json()["tasks"] if t["id"] not in before]
    assert any("Review contract" in t for t in titles), f"new task not found, new titles={titles}"
