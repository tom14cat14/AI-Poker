#!/usr/bin/env python3
"""
AI Poker Arena - Tournament Runner
Runs a complete 5-player SNG tournament with LLM players.
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/.env.keys"))

from core import (
    Tournament, TournamentConfig, TournamentRunner,
    AIPlayerManager, Action, AIDecision
)
from agents import create_all_agents

# Import broadcast functions for WebSocket updates
try:
    from api import (
        broadcast_hand_start, broadcast_action,
        broadcast_community_cards, broadcast_hand_result,
        broadcast_elimination, broadcast_blinds_up, broadcast_tournament_end,
        update_player_chips
    )
    WEBSOCKET_ENABLED = True
except ImportError:
    WEBSOCKET_ENABLED = False


class PokerArena:
    """
    Main poker arena controller.
    Manages tournaments, AI players, and game flow.
    """

    def __init__(self):
        self.manager = AIPlayerManager()
        self.current_tournament = None
        self.tournament_history = []
        self.hand_number = 0

        # Initialize agents
        self._setup_agents()

    def _setup_agents(self):
        """Set up all AI players."""
        agents = create_all_agents()
        for agent in agents:
            self.manager.register_player(agent)
            print(f"[ARENA] Registered: {agent.name} ({agent.model_name})")

    async def get_ai_action(
        self,
        player_name: str,
        game_state: Dict,
        valid_actions: List[Tuple]
    ) -> Tuple[Action, int]:
        """Get action from AI player and broadcast it."""
        decision = await self.manager.get_action(player_name, game_state, valid_actions)

        # Print action to console
        action_str = decision.action.name.lower()
        if decision.amount > 0:
            print(f"  [{player_name}] {action_str} {decision.amount}")
        else:
            print(f"  [{player_name}] {action_str}")
        if decision.reasoning:
            print(f"    \"{decision.reasoning}\"")

        # Broadcast to WebSocket
        if WEBSOCKET_ENABLED:
            asyncio.create_task(broadcast_action(
                player_name,
                action_str,
                decision.amount,
                decision.reasoning,
                decision.inner_thoughts,
                decision.trash_talk
            ))

        return (decision.action, decision.amount)

    def on_hand_start(self, hand_number: int, game):
        """Called when a new hand starts."""
        self.hand_number = hand_number
        print(f"\n{'='*50}")
        print(f"HAND #{hand_number}")
        print(f"Blinds: {game.small_blind}/{game.big_blind}")
        chips = {p.name: p.chips for p in game.players if p.is_active}
        print(f"Chips: {chips}")

        # Get button player name
        active_players = [p for p in game.players if p.is_active]
        button_player = None
        if active_players and hasattr(game, 'button_pos'):
            button_idx = game.button_pos % len(active_players)
            button_player = active_players[button_idx].name
            print(f"Button: {button_player}")

        # Broadcast to WebSocket
        if WEBSOCKET_ENABLED:
            asyncio.create_task(broadcast_hand_start(
                hand_number,
                [{"name": p.name, "chips": p.chips} for p in game.players if p.is_active],
                {"small_blind": game.small_blind, "big_blind": game.big_blind},
                button_player
            ))

    def on_hand_complete(self, result):
        """Called when a hand completes."""
        print(f"\n{result.summary}")

        # Broadcast to WebSocket
        if WEBSOCKET_ENABLED:
            asyncio.create_task(broadcast_hand_result(
                result.winners[0] if result.winners else "Unknown",
                result.pot,
                result.final_board,
                result.summary
            ))

    def on_elimination(self, name: str, place: int):
        """Called when a player is eliminated."""
        print(f"\n{'*'*50}")
        print(f"ELIMINATED: {name} (finished {place}th)")
        print(f"{'*'*50}")

        # Broadcast to WebSocket
        if WEBSOCKET_ENABLED:
            asyncio.create_task(broadcast_elimination(name, place))

    def on_level_up(self, level: int, blinds):
        """Called when blinds increase."""
        print(f"\n[BLINDS UP] Level {level}: {blinds.small_blind}/{blinds.big_blind}" +
              (f" ante {blinds.ante}" if blinds.ante else ""))

        # Broadcast to WebSocket
        if WEBSOCKET_ENABLED:
            asyncio.create_task(broadcast_blinds_up(
                level, blinds.small_blind, blinds.big_blind, blinds.ante
            ))

    def on_community_cards(self, stage: str, cards: list):
        """Called when community cards are dealt."""
        print(f"  [BOARD] {stage.upper()}: {' '.join(cards)}")

        # Broadcast to WebSocket
        if WEBSOCKET_ENABLED:
            asyncio.create_task(broadcast_community_cards(cards, stage))

    def on_tournament_complete(self, results):
        """Called when tournament ends."""
        print(f"\n{'='*60}")
        print("TOURNAMENT COMPLETE!")
        print(f"{'='*60}")
        print(f"Winner: {results.winner}")
        print(f"Total hands: {results.total_hands}")
        print(f"Duration: {results.duration_seconds:.1f}s")
        print("\nFinal Standings:")
        for standing in results.final_standings:
            print(f"  {standing['place']}. {standing['name']}")

        # Broadcast to WebSocket
        if WEBSOCKET_ENABLED:
            asyncio.create_task(broadcast_tournament_end(
                results.winner,
                results.final_standings,
                {
                    "total_hands": results.total_hands,
                    "duration_seconds": results.duration_seconds
                }
            ))

    async def run_tournament(self):
        """Run a complete tournament."""
        print("\n" + "="*60)
        print("AI POKER ARENA - Tournament Starting!")
        print("="*60)

        # Get player names from registered agents
        player_names = list(self.manager.players.keys())
        print(f"Players: {', '.join(player_names)}")

        # Create tournament
        config = TournamentConfig(starting_chips=10000)
        tournament = Tournament(player_names, config)

        # Set up callbacks
        tournament.on_hand_start = self.on_hand_start
        tournament.on_hand_complete = self.on_hand_complete
        tournament.on_elimination = self.on_elimination
        tournament.on_level_up = self.on_level_up
        tournament.on_tournament_complete = self.on_tournament_complete
        tournament.on_community_cards = self.on_community_cards

        # Create runner
        runner = TournamentRunner(tournament, self.get_ai_action)

        # Run tournament
        results = await runner.run_tournament()

        # Update notes for all players after tournament
        await self._post_tournament_reflection(tournament, results)

        # Save results
        self._save_results(results)

        return results

    async def _post_tournament_reflection(self, tournament, results):
        """Have all players reflect on the tournament."""
        summary = {
            "winner": results.winner,
            "my_placement": None,
            "total_hands": results.total_hands,
            "notable_moments": []
        }

        # Get notable hands (big pots, eliminations)
        for hand in results.hand_history[-10:]:  # Last 10 hands
            if hand.eliminations or hand.pot > 5000:
                summary["notable_moments"].append(hand.summary)

        # Have each player reflect
        for name, player in self.manager.players.items():
            for standing in results.final_standings:
                if standing["name"] == name:
                    summary["my_placement"] = standing["place"]
                    break

            try:
                reflection = await player.reflect_on_hand(
                    {"tournament_summary": summary},
                    "won" if name == results.winner else "lost"
                )
                if reflection:
                    player.update_notes(f"\n**Tournament #{len(self.tournament_history)+1}** (placed {summary['my_placement']}): {reflection}")
            except Exception as e:
                print(f"[{name}] Post-tournament reflection failed: {e}")

    def _save_results(self, results):
        """Save tournament results to file."""
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = results_dir / f"tournament_{timestamp}.json"

        data = {
            "timestamp": timestamp,
            "winner": results.winner,
            "final_standings": results.final_standings,
            "total_hands": results.total_hands,
            "duration_seconds": results.duration_seconds,
            "hand_summaries": [h.summary for h in results.hand_history]
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        print(f"\nResults saved to: {filename}")
        self.tournament_history.append(data)


async def main():
    """Main entry point."""
    arena = PokerArena()

    print("\nStarting AI Poker Arena...")
    print("Notes persist across tournaments - AIs will learn over time.\n")

    # Run a single tournament for now
    results = await arena.run_tournament()

    return results


if __name__ == "__main__":
    asyncio.run(main())
