"""
Real-time WebSocket hub for pushing live updates to the admin dashboard.
Connected clients receive instant notifications when:
- A new booking is created
- A booking is cancelled
- A new review is submitted
"""
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

router = APIRouter(tags=["Realtime"])

# Track all connected dashboard clients
_connected_clients: List[WebSocket] = []


async def broadcast(event_type: str, data: dict):
    """Push a real-time event to all connected dashboard clients."""
    message = json.dumps({"type": event_type, "data": data})
    disconnected = []
    for ws in _connected_clients:
        try:
            await ws.send_text(message)
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        _connected_clients.remove(ws)


def broadcast_sync(event_type: str, data: dict):
    """Synchronous wrapper for broadcasting from non-async contexts (e.g., FastAPI routes)."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(broadcast(event_type, data))
        else:
            loop.run_until_complete(broadcast(event_type, data))
    except RuntimeError:
        # No event loop — skip (e.g., during testing)
        pass


@router.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    """Dashboard clients connect here to receive live push updates."""
    await websocket.accept()
    _connected_clients.append(websocket)
    print(f"[WS] Dashboard client connected ({len(_connected_clients)} total)")

    try:
        while True:
            # Keep connection alive — clients can send heartbeat pings
            await websocket.receive_text()
    except WebSocketDisconnect:
        _connected_clients.remove(websocket)
        print(f"[WS] Dashboard client disconnected ({len(_connected_clients)} remaining)")
