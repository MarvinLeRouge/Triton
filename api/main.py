import asyncio
import random

from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

from engine.entities import BlueDrone, BlueMothership, RedVessel
from engine.grid import Grid
from engine.simulation import GameResult, Simulation

app = FastAPI(title="Triton API")

STEP_INTERVAL = 0.2  # seconds between turns


def _new_game() -> Simulation:
    """Create a fresh simulation with randomly placed entities."""
    rng = random.Random()
    grid = Grid()

    ms = BlueMothership(grid=grid, row=rng.randint(0, grid.rows - 1), col=rng.randint(2, 6))

    occupied = {(ms.row, ms.col)}
    drones: list[BlueDrone] = []
    for _ in range(2):
        while True:
            row = max(0, min(grid.rows - 1, ms.row + rng.randint(-3, 3)))
            col = max(0, min(grid.cols - 1, ms.col + rng.randint(-3, 3)))
            if (row, col) not in occupied:
                occupied.add((row, col))
                drones.append(BlueDrone(grid=grid, row=row, col=col))
                break

    border = rng.choice(["north", "east", "south"])
    dist = rng.randint(2, 6)
    match border:
        case "north":
            v_row, v_col = dist, rng.randint(0, grid.cols - 1)
        case "east":
            v_row, v_col = rng.randint(0, grid.rows - 1), grid.cols - 1 - dist
        case _:
            v_row, v_col = grid.rows - 1 - dist, rng.randint(0, grid.cols - 1)
    vessel = RedVessel(grid=grid, row=v_row, col=v_col)

    return Simulation(
        grid=grid,
        mothership=ms,
        drones=drones,
        red_vessel=vessel,
        rng=random.Random(),
    )


def _random_move(
    entity: BlueDrone | RedVessel, grid: Grid, rng: random.Random, max_delta: int
) -> None:
    """Move entity by a random delta, clamped to grid bounds."""
    new_row, new_col = grid.clamp(
        entity.row + rng.randint(-max_delta, max_delta),
        entity.col + rng.randint(-max_delta, max_delta),
    )
    entity.move(new_row, new_col)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.websocket("/ws/game")
async def ws_game(websocket: WebSocket) -> None:
    await websocket.accept()
    sim = _new_game()
    rng = random.Random()
    try:
        await websocket.send_json(sim.to_dict())
        while sim.result is GameResult.IN_PROGRESS:
            await asyncio.sleep(STEP_INTERVAL)
            for drone in sim.drones:
                _random_move(drone, sim.grid, rng, max_delta=2)
            prev_row, prev_col = sim.vessel.row, sim.vessel.col
            _random_move(sim.vessel, sim.grid, rng, max_delta=1)
            sim.notify_vessel_moved((sim.vessel.row, sim.vessel.col) != (prev_row, prev_col))
            sim.advance()
            await websocket.send_json(sim.to_dict())
    except WebSocketDisconnect:
        pass
