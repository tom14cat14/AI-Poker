#!/usr/bin/env python3
"""
AI Poker Arena - WebSocket Server
Real-time game streaming for viewers.
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, asdict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Global state
class GameState:
    """Shared game state for broadcasting."""
    def __init__(self):
        self.current_hand: Optional[Dict] = None
        self.tournament_info: Optional[Dict] = None
        self.players: Dict[str, Dict] = {}
        self.hand_history: List[Dict] = []
        self.is_running = False
        self.connections: Set[WebSocket] = set()

game_state = GameState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    print("[API] WebSocket server starting...")
    yield
    print("[API] WebSocket server shutting down...")


app = FastAPI(
    title="AI Poker Arena",
    description="5 LLMs playing Texas Hold'em 24/7",
    lifespan=lifespan
)


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"[WS] Client connected. Total: {len(self.active_connections)}")

        # Send current state to new connection
        await self.send_personal(websocket, {
            "type": "init",
            "data": {
                "tournament": game_state.tournament_info,
                "current_hand": game_state.current_hand,
                "players": game_state.players,
                "is_running": game_state.is_running
            }
        })

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        print(f"[WS] Client disconnected. Total: {len(self.active_connections)}")

    async def send_personal(self, websocket: WebSocket, message: dict):
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"[WS] Send error: {e}")

    async def broadcast(self, message: dict):
        """Broadcast to all connected clients."""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)

        # Clean up disconnected
        for conn in disconnected:
            self.active_connections.discard(conn)


manager = ConnectionManager()


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, handle client messages
            data = await websocket.receive_text()
            msg = json.loads(data)

            # Handle ping/pong
            if msg.get("type") == "ping":
                await manager.send_personal(websocket, {"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"[WS] Error: {e}")
        manager.disconnect(websocket)


# Tournament runner (runs in same process for WebSocket integration)
tournament_task = None

async def run_tournament_in_server():
    """Run tournament with WebSocket broadcasts."""
    global tournament_task
    from run_tournament import PokerArena

    try:
        arena = PokerArena()
        results = await arena.run_tournament()
        return results
    except Exception as e:
        print(f"[API] Tournament error: {e}")
        import traceback
        traceback.print_exc()
        return None


@app.post("/api/start")
async def start_tournament():
    """Start a new tournament."""
    global tournament_task

    if game_state.is_running:
        return {"status": "error", "message": "Tournament already running"}

    game_state.is_running = True
    tournament_task = asyncio.create_task(run_tournament_in_server())

    return {"status": "started", "message": "Tournament starting..."}


# REST endpoints
@app.get("/api/status")
async def get_status():
    """Get current game status."""
    return {
        "is_running": game_state.is_running,
        "tournament": game_state.tournament_info,
        "players": game_state.players,
        "viewers": len(manager.active_connections)
    }


@app.get("/api/players")
async def get_players():
    """Get all player info."""
    return game_state.players


@app.get("/api/hand")
async def get_current_hand():
    """Get current hand state."""
    return game_state.current_hand or {"status": "no_hand"}


@app.get("/api/history")
async def get_history(limit: int = 10):
    """Get recent hand history."""
    return game_state.hand_history[-limit:]


# Event broadcasting functions (called by tournament runner)
async def broadcast_hand_start(hand_number: int, players: List[Dict], blinds: Dict, button_player: str = None, deal_order: List[str] = None):
    """Broadcast new hand starting."""
    event = {
        "type": "hand_start",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "hand_number": hand_number,
            "players": players,
            "blinds": blinds,
            "button_player": button_player,
            "deal_order": deal_order or []
        }
    }
    game_state.current_hand = event["data"]
    print(f"[WS BROADCAST] hand_start #{hand_number} - players: {[p['name'] for p in players]} - SB: {blinds.get('sb_player')} BB: {blinds.get('bb_player')} - clients: {len(manager.active_connections)}")
    await manager.broadcast(event)


async def broadcast_hole_cards(player_cards: Dict[str, List[str]], deal_order: List[str] = None):
    """Broadcast all players' hole cards to spectators."""
    event = {
        "type": "hole_cards",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "cards": player_cards,  # {player_name: [card1, card2]}
            "deal_order": deal_order or list(player_cards.keys())
        }
    }
    print(f"[WS BROADCAST] hole_cards - {len(player_cards)} players - deal_order: {deal_order} - clients: {len(manager.active_connections)}")
    await manager.broadcast(event)


async def broadcast_action(player: str, action: str, amount: int,
                           reasoning: str, inner_thoughts: str = None,
                           trash_talk: str = None, trash_talk_target: str = None,
                           pot: int = None, player_chips: Dict[str, int] = None):
    """Broadcast a player action."""
    event = {
        "type": "action",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "player": player,
            "action": action,
            "amount": amount,
            "reasoning": reasoning,
            "inner_thoughts": inner_thoughts,  # For viewers only
            "trash_talk": trash_talk,
            "trash_talk_target": trash_talk_target,
            "pot": pot,  # Current pot after action
            "player_chips": player_chips  # All players' chip counts
        }
    }
    print(f"[WS BROADCAST] action: {player} {action} - pot: {pot} - clients: {len(manager.active_connections)}")
    await manager.broadcast(event)


async def broadcast_community_cards(cards: List[str], stage: str):
    """Broadcast community cards dealt."""
    event = {
        "type": "community_cards",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "cards": cards,
            "stage": stage
        }
    }
    print(f"[WS BROADCAST] community_cards: {stage} - {cards} - clients: {len(manager.active_connections)}")
    await manager.broadcast(event)


async def broadcast_hand_result(winner: str, pot: int,
                                 winning_hand: str, summary: str,
                                 showdown_cards: Dict[str, List[str]] = None):
    """Broadcast hand result."""
    event = {
        "type": "hand_result",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "winner": winner,
            "pot": pot,
            "winning_hand": winning_hand,
            "summary": summary,
            "showdown_cards": showdown_cards
        }
    }
    game_state.hand_history.append(event["data"])
    game_state.hand_history = game_state.hand_history[-50:]  # Keep last 50
    await manager.broadcast(event)


async def broadcast_elimination(player: str, place: int):
    """Broadcast player elimination."""
    event = {
        "type": "elimination",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "player": player,
            "place": place
        }
    }
    await manager.broadcast(event)


async def broadcast_blinds_up(level: int, small_blind: int, big_blind: int, ante: int):
    """Broadcast blind level increase."""
    event = {
        "type": "blinds_up",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "level": level,
            "small_blind": small_blind,
            "big_blind": big_blind,
            "ante": ante
        }
    }
    await manager.broadcast(event)


async def broadcast_tournament_start(players: List[str], config: Dict):
    """Broadcast tournament starting."""
    game_state.is_running = True
    game_state.tournament_info = {
        "players": players,
        "config": config,
        "start_time": datetime.now().isoformat()
    }
    game_state.players = {p: {"chips": config.get("starting_chips", 10000), "active": True} for p in players}

    event = {
        "type": "tournament_start",
        "timestamp": datetime.now().isoformat(),
        "data": game_state.tournament_info
    }
    print(f"[WS BROADCAST] tournament_start - players: {players} - clients: {len(manager.active_connections)}")
    await manager.broadcast(event)


async def broadcast_tournament_end(winner: str, standings: List[Dict], stats: Dict):
    """Broadcast tournament ending."""
    game_state.is_running = False

    event = {
        "type": "tournament_end",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "winner": winner,
            "standings": standings,
            "stats": stats
        }
    }
    await manager.broadcast(event)


async def update_player_chips(player: str, chips: int):
    """Update player chip count."""
    if player in game_state.players:
        game_state.players[player]["chips"] = chips

    event = {
        "type": "chip_update",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "player": player,
            "chips": chips
        }
    }
    await manager.broadcast(event)


# Serve static files (viewer)
static_path = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# Serve assets (portraits, audio)
assets_path = os.path.join(os.path.dirname(__file__), "..", "assets")
if os.path.exists(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")


@app.get("/")
async def serve_viewer():
    """Serve the main viewer page."""
    index_path = os.path.join(static_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "AI Poker Arena API", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
