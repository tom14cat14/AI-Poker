#!/usr/bin/env python3
"""
AI Player System with Self-Learning Notes
Each AI maintains their own notes file with observations about opponents.
"""

import os
import json
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

from .game_engine import Action


NOTES_DIR = Path(__file__).parent.parent / "notes"
NOTES_DIR.mkdir(exist_ok=True)

MAX_NOTES_SIZE = 2000  # Max characters in notes file


@dataclass
class AIDecision:
    """Decision from an AI player."""
    action: Action
    amount: int
    reasoning: str
    inner_thoughts: Optional[str] = None  # For viewers only - other AIs don't see this
    trash_talk: Optional[str] = None  # Directed at opponents - they can hear and remember this


@dataclass
class TrashTalkEvent:
    """A trash talk event to remember."""
    speaker: str
    target: str
    message: str
    hand_number: int


class AIPlayer(ABC):
    """
    Base class for AI poker players.
    Each AI maintains their own notes file.
    """

    def __init__(self, name: str, model_name: str):
        self.name = name
        self.model_name = model_name
        self.notes_file = NOTES_DIR / f"{name.lower()}_notes.md"
        self.trash_talk_log: List[TrashTalkEvent] = []  # Trash talk I've received

        # Initialize notes file if doesn't exist
        if not self.notes_file.exists():
            self._init_notes()

    def _init_notes(self):
        """Initialize empty notes file. Notes PERSIST across tournaments."""
        initial_notes = f"""# {self.name}'s Poker Notes
*These notes persist across all tournaments. I write my own observations.*

## Opponent Reads

## Social Dynamics
*Who trash talks? Who's quiet? Any rivalries?*

## Strategy Evolution
*What I've learned works/doesn't work*

---
*Notes begin below:*
"""
        self.notes_file.write_text(initial_notes)

    def receive_trash_talk(self, speaker: str, message: str, hand_number: int):
        """Record trash talk received from another player."""
        event = TrashTalkEvent(speaker, self.name, message, hand_number)
        self.trash_talk_log.append(event)
        # Keep only last 10 trash talk events in memory
        self.trash_talk_log = self.trash_talk_log[-10:]

    def get_recent_trash_talk(self) -> List[TrashTalkEvent]:
        """Get recent trash talk directed at this player."""
        return self.trash_talk_log[-5:]  # Last 5 for context

    def get_notes(self) -> str:
        """Read current notes."""
        if self.notes_file.exists():
            return self.notes_file.read_text()
        return ""

    def update_notes(self, new_content: str):
        """
        Update notes file with new content.
        Truncates oldest content if exceeds max size.
        """
        current = self.get_notes()

        # Append new observations
        updated = current + "\n" + new_content

        # Truncate if too long (keep most recent)
        if len(updated) > MAX_NOTES_SIZE:
            # Keep header and recent content
            lines = updated.split("\n")
            header = "\n".join(lines[:10])  # Keep header
            recent = "\n".join(lines[-50:])  # Keep recent
            updated = header + "\n\n[...older notes truncated...]\n\n" + recent

        self.notes_file.write_text(updated)

    def clear_notes(self):
        """Clear notes (for new tournament if desired)."""
        self._init_notes()

    @abstractmethod
    async def get_decision(
        self,
        game_state: Dict,
        valid_actions: List[Tuple[Action, int, int]]
    ) -> AIDecision:
        """Get poker decision from AI."""
        pass

    @abstractmethod
    async def reflect_on_hand(
        self,
        hand_summary: Dict,
        my_result: str  # "won", "lost", "folded"
    ) -> str:
        """
        Reflect on completed hand and return notes to add.
        The AI writes its own observations.
        """
        pass

    def _build_decision_prompt(
        self,
        game_state: Dict,
        valid_actions: List[Tuple[Action, int, int]]
    ) -> str:
        """Build prompt for decision-making."""
        notes = self.get_notes()

        actions_str = []
        for action, min_amt, max_amt in valid_actions:
            if min_amt == max_amt == 0:
                actions_str.append(action.value)
            elif min_amt == max_amt:
                actions_str.append(f"{action.value} {min_amt}")
            else:
                actions_str.append(f"{action.value} {min_amt}-{max_amt}")

        opponents_str = "\n".join([
            f"- {o['name']}: {o['chips']} chips, bet {o['bet']}" +
            (" (folded)" if o['folded'] else "") +
            (" (all-in)" if o['all_in'] else "")
            for o in game_state['opponents']
        ])

        history_str = "\n".join([
            f"- {a['player']}: {a['action']}" + (f" {a['amount']}" if a['amount'] else "")
            for a in game_state['action_history']
        ]) or "No actions yet"

        # Include recent trash talk directed at this player
        trash_talk_str = ""
        recent_trash = self.get_recent_trash_talk()
        if recent_trash:
            trash_talk_str = "\n\nRECENT TRASH TALK DIRECTED AT YOU:\n" + "\n".join([
                f"- {t.speaker} (hand #{t.hand_number}): \"{t.message}\""
                for t in recent_trash
            ])

        prompt = f"""You are {self.name}, an AI playing Texas Hold'em poker.

=== YOUR NOTES (your own observations - these persist across tournaments) ===
{notes}
=== END NOTES ==={trash_talk_str}

CURRENT SITUATION:
- Your cards: {' '.join(game_state['your_cards'])}
- Your chips: {game_state['your_chips']}
- Your current bet: {game_state['your_bet']}
- Pot: {game_state['pot']}
- Community cards: {' '.join(game_state['community_cards']) or 'None (preflop)'}
- Current bet to call: {game_state['current_bet']}
- Stage: {game_state['stage']}

OPPONENTS:
{opponents_str}

RECENT ACTIONS THIS HAND:
{history_str}

VALID ACTIONS: {', '.join(actions_str)}

Based on your notes and the current situation, what do you do?

Respond in this exact JSON format:
{{
    "action": "fold|check|call|bet|raise|all_in",
    "amount": <number or 0>,
    "reasoning": "<brief explanation>",
    "inner_thoughts": "<what you're REALLY thinking - this is for viewers only, other AIs cannot see this. Be honest about your reads, concerns, strategy.>",
    "trash_talk": "<optional - say something TO THE OTHER PLAYERS if you want. They will hear this and remember it. Or null to stay quiet.>"
}}
"""
        return prompt

    def _build_reflection_prompt(
        self,
        hand_summary: Dict,
        my_result: str
    ) -> str:
        """Build prompt for post-hand reflection."""
        actions_str = "\n".join([
            f"- {a['player']}: {a['action']}" + (f" {a['amount']}" if a.get('amount') else "")
            for a in hand_summary.get('actions', [])
        ])

        prompt = f"""You are {self.name}. A poker hand just ended.

HAND SUMMARY:
- Result for you: {my_result}
- Final pot: {hand_summary.get('pot', 0)}
- Board: {' '.join(hand_summary.get('community_cards', [])) or 'No showdown'}

ACTIONS THAT OCCURRED:
{actions_str}

Based on what happened, update your notes about opponents.
What patterns did you notice? Who played how?

Write a SHORT update (2-4 lines max) to add to your notes.
Focus on opponent tendencies you observed.
Example: "GPT-4 folded to my river bet - might be exploitable."

Just write the note content, no JSON needed:
"""
        return prompt

    def _parse_decision(self, response: str) -> AIDecision:
        """Parse AI response into decision."""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                action_str = data.get('action', 'fold').lower()
                action_map = {
                    'fold': Action.FOLD,
                    'check': Action.CHECK,
                    'call': Action.CALL,
                    'bet': Action.BET,
                    'raise': Action.RAISE,
                    'all_in': Action.ALL_IN,
                    'all-in': Action.ALL_IN,
                    'allin': Action.ALL_IN
                }
                action = action_map.get(action_str, Action.FOLD)
                amount = int(data.get('amount', 0))
                reasoning = data.get('reasoning', '')
                inner_thoughts = data.get('inner_thoughts')  # For viewers only
                trash_talk = data.get('trash_talk')  # For other AIs

                return AIDecision(action, amount, reasoning, inner_thoughts, trash_talk)
        except Exception as e:
            print(f"[{self.name}] Failed to parse response: {e}")

        # Default to fold if parsing fails
        return AIDecision(Action.FOLD, 0, "Parse error - defaulting to fold")


class AIPlayerManager:
    """Manages all AI players and their interactions."""

    def __init__(self):
        self.players: Dict[str, AIPlayer] = {}

    def register_player(self, player: AIPlayer):
        """Register an AI player."""
        self.players[player.name] = player

    def get_player(self, name: str) -> Optional[AIPlayer]:
        """Get player by name."""
        return self.players.get(name)

    async def get_action(
        self,
        player_name: str,
        game_state: Dict,
        valid_actions: List[Tuple[Action, int, int]]
    ) -> Tuple[Action, int]:
        """Get action from specified player."""
        player = self.players.get(player_name)
        if not player:
            return (Action.FOLD, 0)

        decision = await player.get_decision(game_state, valid_actions)

        # Validate action
        valid_action_types = [a[0] for a in valid_actions]
        if decision.action not in valid_action_types:
            # Default to first valid action
            return (valid_actions[0][0], valid_actions[0][1])

        # Validate amount
        for action, min_amt, max_amt in valid_actions:
            if action == decision.action:
                if decision.action in [Action.BET, Action.RAISE]:
                    amount = max(min_amt, min(decision.amount, max_amt))
                    return (decision.action, amount)
                else:
                    return (decision.action, min_amt)

        return (Action.FOLD, 0)

    async def update_all_notes(
        self,
        hand_summary: Dict,
        player_results: Dict[str, str]  # name -> "won"/"lost"/"folded"
    ):
        """Have all players reflect and update their notes."""
        tasks = []
        for name, player in self.players.items():
            result = player_results.get(name, "unknown")
            tasks.append(self._update_player_notes(player, hand_summary, result))

        await asyncio.gather(*tasks)

    async def _update_player_notes(
        self,
        player: AIPlayer,
        hand_summary: Dict,
        result: str
    ):
        """Update single player's notes."""
        try:
            new_notes = await player.reflect_on_hand(hand_summary, result)
            if new_notes and new_notes.strip():
                player.update_notes(f"\n**Hand observation:** {new_notes.strip()}")
        except Exception as e:
            print(f"[{player.name}] Failed to update notes: {e}")

    def get_all_notes(self) -> Dict[str, str]:
        """Get all players' notes for debugging."""
        return {name: player.get_notes() for name, player in self.players.items()}
