# Auto-split route group: ws

from fastapi import APIRouter

from ._common import *  # noqa: F401,F403



router = APIRouter()



@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "typing":
                channel_id = msg.get("channel_id")
                if channel_id:
                    await manager.send_to_channel(channel_id, {
                        "type": "typing",
                        "data": {"user_id": user_id, "channel_id": channel_id}
                    })
            elif msg.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception:
        manager.disconnect(user_id)
