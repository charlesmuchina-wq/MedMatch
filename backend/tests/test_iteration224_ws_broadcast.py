"""Iteration 224 — verify LUMI WS broadcasts the ENZI AI reply to a single stable socket."""
import asyncio
import json
import os

import pytest
import requests
import websockets
from dotenv import dotenv_values

frontend_env = dotenv_values("/app/frontend/.env")
BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL") or frontend_env["REACT_APP_BACKEND_URL"]).rstrip("/")
WS_URL = BASE_URL.replace("https://", "wss://").replace("http://", "ws://")

ADMIN = {"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}


@pytest.mark.asyncio
async def test_ai_reply_broadcast_over_ws():
    r = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN, timeout=60)
    assert r.status_code == 200
    token = r.json().get("access_token") or r.json().get("token")
    me = requests.get(f"{BASE_URL}/api/auth/me", headers={"Authorization": f"Bearer {token}"}, timeout=60).json()
    user_id = me.get("user_id") or me.get("id")
    assert user_id
    ch = requests.get(f"{BASE_URL}/api/lumi/channels", headers={"Authorization": f"Bearer {token}"}, timeout=60).json()
    channel_id = (ch.get("my_channels") or ch.get("channels"))[0]["id"]

    received = []

    async with websockets.connect(f"{WS_URL}/api/lumi/ws/{user_id}") as ws:
        await asyncio.sleep(1.5)

        def post_ai():
            return requests.post(
                f"{BASE_URL}/api/lumi/channels/{channel_id}/ai",
                json={"query": "summarize this conversation"},
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                timeout=120,
            )

        task = asyncio.get_running_loop().run_in_executor(None, post_ai)
        deadline = asyncio.get_running_loop().time() + 60
        while asyncio.get_running_loop().time() < deadline:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=5)
            except asyncio.TimeoutError:
                if task.done() and received:
                    break
                continue
            msg = json.loads(raw)
            received.append(msg)
            if msg.get("type") == "message" and msg.get("data", {}).get("type") == "ai_assistant":
                break
        resp = await task

    assert resp.status_code == 200, resp.text[:200]
    ai_frames = [m for m in received if m.get("type") == "message" and m.get("data", {}).get("type") == "ai_assistant"]
    assert ai_frames, f"AI message not broadcast over WS; frames={[m.get('type') for m in received]}"
    assert ai_frames[0]["data"]["sender_name"] == "ENZI AI"
