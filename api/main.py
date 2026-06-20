from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

app = FastAPI(title="Triton API")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.websocket("/ws/game")
async def ws_game(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json({"type": "connected"})
    try:
        while True:
            data = await websocket.receive_json()
            match data.get("type"):
                case "ping":
                    await websocket.send_json({"type": "pong"})
                case _:
                    await websocket.send_json(
                        {"type": "error", "detail": f"unknown message type: {data.get('type')!r}"}
                    )
    except WebSocketDisconnect:
        pass
