#!/usr/bin/env python3
"""
Sit & Go Tournament System
Manages blind levels, eliminations, and tournament flow.
"""

import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from datetime import datetime

from .game_engine import Player, PokerGame, Action


@dataclass
class BlindLevel:
    """A blind level in the tournament."""
    small_blind: int
    big_blind: int
    ante: int = 0
    duration_hands: int = 10  # Hands before level increase
    duration_minutes: int = 5  # Minutes before level increase (whichever first)


# Aggressive blind structure for 30-60 min tournaments
DEFAULT_BLIND_STRUCTURE = [
    BlindLevel(100, 200, 0, 10, 5),      # Level 1
    BlindLevel(150, 300, 0, 10, 5),      # Level 2
    BlindLevel(200, 400, 50, 10, 5),     # Level 3
    BlindLevel(300, 600, 75, 10, 5),     # Level 4
    BlindLevel(400, 800, 100, 10, 5),    # Level 5
    BlindLevel(600, 1200, 150, 10, 5),   # Level 6
    BlindLevel(800, 1600, 200, 10, 5),   # Level 7
    BlindLevel(1000, 2000, 250, 10, 5),  # Level 8
    BlindLevel(1500, 3000, 400, 10, 5),  # Level 9
    BlindLevel(2000, 4000, 500, 10, 5),  # Level 10
    BlindLevel(3000, 6000, 750, 10, 5),  # Level 11
    BlindLevel(4000, 8000, 1000, 10, 5), # Level 12
]


@dataclass
class TournamentConfig:
    """Tournament configuration."""
    starting_chips: int = 10000
    blind_structure: List[BlindLevel] = field(default_factory=lambda: DEFAULT_BLIND_STRUCTURE)


@dataclass
class HandResult:
    """Result of a completed hand."""
    hand_number: int
    winners: List[str]
    pot: int
    eliminations: List[str]
    showdown: bool
    final_board: List[str]
    summary: str


@dataclass
class TournamentResult:
    """Final tournament result."""
    winner: str
    final_standings: List[Dict]  # [{"name": ..., "place": 1, "chips_at_end": ...}]
    total_hands: int
    duration_seconds: float
    hand_history: List[HandResult]


class Tournament:
    """
    Sit & Go Tournament Manager.
    Runs a complete tournament with 5 AI players.
    """

    def __init__(self, player_names: List[str], config: TournamentConfig = None):
        self.config = config or TournamentConfig()
        self.players = [
            Player(name=name, chips=self.config.starting_chips)
            for name in player_names
        ]
        self.current_level = 0
        self.hands_at_level = 0
        self.level_start_time = time.time()
        self.tournament_start_time = None
        self.hand_number = 0
        self.hand_history: List[HandResult] = []
        self.game: Optional[PokerGame] = None
        self.eliminations: List[str] = []

        # Callbacks for external integration
        self.on_hand_start: Optional[Callable] = None
        self.on_action_needed: Optional[Callable] = None
        self.on_hand_complete: Optional[Callable] = None
        self.on_elimination: Optional[Callable] = None
        self.on_level_up: Optional[Callable] = None
        self.on_tournament_complete: Optional[Callable] = None
        self.on_community_cards: Optional[Callable] = None  # (stage, cards)

    @property
    def current_blinds(self) -> BlindLevel:
        """Get current blind level."""
        level_idx = min(self.current_level, len(self.config.blind_structure) - 1)
        return self.config.blind_structure[level_idx]

    def active_players(self) -> List[Player]:
        """Get players still in tournament."""
        return [p for p in self.players if p.is_active]

    def is_complete(self) -> bool:
        """Check if tournament is over."""
        return len(self.active_players()) <= 1

    def check_level_up(self):
        """Check if blinds should increase."""
        blinds = self.current_blinds
        elapsed = time.time() - self.level_start_time

        should_level = (
            self.hands_at_level >= blinds.duration_hands or
            elapsed >= blinds.duration_minutes * 60
        )

        if should_level and self.current_level < len(self.config.blind_structure) - 1:
            self.current_level += 1
            self.hands_at_level = 0
            self.level_start_time = time.time()

            if self.on_level_up:
                self.on_level_up(self.current_level, self.current_blinds)

    def start_tournament(self):
        """Initialize tournament."""
        self.tournament_start_time = time.time()
        self.level_start_time = time.time()

    def start_hand(self) -> PokerGame:
        """Start a new hand."""
        self.check_level_up()
        self.hand_number += 1
        self.hands_at_level += 1

        blinds = self.current_blinds
        self.game = PokerGame(
            players=self.players,
            small_blind=blinds.small_blind,
            big_blind=blinds.big_blind,
            ante=blinds.ante
        )
        self.game.start_hand()

        if self.on_hand_start:
            self.on_hand_start(self.hand_number, self.game)

        return self.game

    def complete_hand(self, winners: List[tuple]) -> HandResult:
        """Complete current hand and record result."""
        # Check for eliminations
        eliminated_this_hand = []
        for p in self.players:
            if p.chips <= 0 and p.is_active:
                p.is_active = False
                eliminated_this_hand.append(p.name)
                self.eliminations.append(p.name)

                if self.on_elimination:
                    place = len(self.players) - len(self.eliminations) + 1
                    self.on_elimination(p.name, place)

        # Create hand result
        result = HandResult(
            hand_number=self.hand_number,
            winners=[w[0].name for w in winners],
            pot=sum(w[1] for w in winners),
            eliminations=eliminated_this_hand,
            showdown=len([p for p in self.game.active_players()]) > 1,
            final_board=[str(c) for c in self.game.state.community_cards],
            summary=self._create_hand_summary(winners, eliminated_this_hand)
        )
        self.hand_history.append(result)

        # Advance button
        self.game.advance_button()

        if self.on_hand_complete:
            self.on_hand_complete(result)

        return result

    def _create_hand_summary(self, winners: List[tuple], eliminations: List[str]) -> str:
        """Create human-readable hand summary."""
        lines = [f"Hand #{self.hand_number}"]

        if len(winners) == 1:
            lines.append(f"{winners[0][0].name} wins ${winners[0][1]}")
        else:
            names = ", ".join(w[0].name for w in winners)
            lines.append(f"Split pot: {names}")

        if self.game.state.community_cards:
            board = " ".join(str(c) for c in self.game.state.community_cards)
            lines.append(f"Board: {board}")

        if eliminations:
            for name in eliminations:
                lines.append(f"{name} ELIMINATED!")

        return " | ".join(lines)

    def get_final_results(self) -> TournamentResult:
        """Get final tournament results."""
        # Build standings
        standings = []

        # Winner (last player standing)
        active = self.active_players()
        if active:
            winner = active[0]
            standings.append({
                "name": winner.name,
                "place": 1,
                "chips_at_end": winner.chips
            })

        # Add eliminated players in reverse order
        for i, name in enumerate(reversed(self.eliminations)):
            place = i + 2
            standings.append({
                "name": name,
                "place": place,
                "chips_at_end": 0
            })

        return TournamentResult(
            winner=standings[0]["name"] if standings else "None",
            final_standings=standings,
            total_hands=self.hand_number,
            duration_seconds=time.time() - self.tournament_start_time,
            hand_history=self.hand_history
        )

    def get_chip_counts(self) -> Dict[str, int]:
        """Get current chip counts for all players."""
        return {p.name: p.chips for p in self.players}

    def get_tournament_state(self) -> Dict:
        """Get current tournament state for display."""
        return {
            "hand_number": self.hand_number,
            "level": self.current_level + 1,
            "blinds": f"{self.current_blinds.small_blind}/{self.current_blinds.big_blind}",
            "ante": self.current_blinds.ante,
            "players_remaining": len(self.active_players()),
            "chip_counts": self.get_chip_counts(),
            "eliminations": self.eliminations,
            "elapsed_seconds": time.time() - self.tournament_start_time if self.tournament_start_time else 0
        }


class TournamentRunner:
    """
    High-level tournament runner with AI integration.
    """

    def __init__(self, tournament: Tournament, get_ai_action: Callable):
        """
        Args:
            tournament: Tournament instance
            get_ai_action: Callback to get AI action
                           Signature: (player_name, game_state, valid_actions, notes) -> (Action, amount)
        """
        self.tournament = tournament
        self.get_ai_action = get_ai_action

    async def run_hand(self) -> HandResult:
        """Run a single hand with AI players."""
        game = self.tournament.start_hand()

        # Preflop betting
        await self._run_betting_round(game)

        # Continue through streets if multiple players remain
        while len([p for p in game.active_players() if not p.all_in]) > 1:
            if game.state.stage == "river":
                break

            game.deal_community()
            # Notify of community cards
            if self.tournament.on_community_cards:
                cards = [str(c) for c in game.state.community_cards]
                self.tournament.on_community_cards(game.state.stage, cards)
            game.reset_betting_round()
            await self._run_betting_round(game)

        # If players remain but all-in, deal remaining cards
        while len(game.active_players()) > 1 and game.state.stage != "river":
            game.deal_community()
            # Notify of community cards
            if self.tournament.on_community_cards:
                cards = [str(c) for c in game.state.community_cards]
                self.tournament.on_community_cards(game.state.stage, cards)

        # Showdown
        winners = game.determine_winners()
        return self.tournament.complete_hand(winners)

    async def _run_betting_round(self, game: PokerGame):
        """Run a betting round with AI decisions."""
        # Determine action order
        active = game.active_players()
        if not active:
            return

        # Start after big blind for preflop, or from button+1 for other streets
        start_idx = 0
        if game.state.stage == "preflop":
            # UTG (after BB) acts first preflop
            start_idx = 3 % len(active) if len(active) > 2 else 0

        acted = set()
        current_idx = start_idx
        last_raiser = None

        while True:
            player = active[current_idx % len(active)]

            # Skip folded/all-in players
            if player.folded or player.all_in:
                current_idx += 1
                if current_idx >= len(active) * 2:  # Safety
                    break
                continue

            # Check if betting is complete
            if game.is_betting_complete() and player.name in acted:
                break

            # Get valid actions
            valid_actions = game.get_valid_actions(player)
            if not valid_actions:
                current_idx += 1
                continue

            # Get AI decision
            game_state = game.get_game_state_for_player(player)
            action, amount = await self.get_ai_action(
                player.name,
                game_state,
                valid_actions
            )

            # Apply action
            game.apply_action(player, action, amount)
            acted.add(player.name)

            # Track raises for round completion
            if action in [Action.BET, Action.RAISE, Action.ALL_IN]:
                if player.current_bet > game.state.current_bet:
                    last_raiser = player.name
                    acted = {player.name}  # Reset - everyone needs to act again

            current_idx += 1

            # Safety check for infinite loops
            if current_idx >= len(active) * 10:
                break

    async def run_tournament(self) -> TournamentResult:
        """Run complete tournament."""
        self.tournament.start_tournament()

        while not self.tournament.is_complete():
            await self.run_hand()

        results = self.tournament.get_final_results()

        if self.tournament.on_tournament_complete:
            self.tournament.on_tournament_complete(results)

        return results
