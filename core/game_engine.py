#!/usr/bin/env python3
"""
Texas Hold'em Poker Game Engine
Core logic for dealing, betting, and hand evaluation.
"""

import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum, auto
from itertools import combinations


class Suit(Enum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"


class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


class HandRank(Enum):
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10


class Action(Enum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all_in"


@dataclass
class Card:
    rank: Rank
    suit: Suit

    def __str__(self):
        rank_str = {
            Rank.TWO: "2", Rank.THREE: "3", Rank.FOUR: "4", Rank.FIVE: "5",
            Rank.SIX: "6", Rank.SEVEN: "7", Rank.EIGHT: "8", Rank.NINE: "9",
            Rank.TEN: "T", Rank.JACK: "J", Rank.QUEEN: "Q", Rank.KING: "K", Rank.ACE: "A"
        }
        return f"{rank_str[self.rank]}{self.suit.value}"

    def __repr__(self):
        return str(self)


@dataclass
class Player:
    name: str
    chips: int
    hole_cards: List[Card] = field(default_factory=list)
    current_bet: int = 0
    folded: bool = False
    all_in: bool = False
    is_active: bool = True  # Still in tournament

    def reset_for_hand(self):
        """Reset player state for new hand."""
        self.hole_cards = []
        self.current_bet = 0
        self.folded = False
        self.all_in = False


class Deck:
    """Standard 52-card deck."""

    def __init__(self):
        self.cards: List[Card] = []
        self.reset()

    def reset(self):
        """Reset and shuffle deck."""
        self.cards = [
            Card(rank, suit)
            for suit in Suit
            for rank in Rank
        ]
        random.shuffle(self.cards)

    def deal(self, count: int = 1) -> List[Card]:
        """Deal cards from deck."""
        dealt = self.cards[:count]
        self.cards = self.cards[count:]
        return dealt


class HandEvaluator:
    """Evaluate poker hands and determine winners."""

    @staticmethod
    def evaluate(cards: List[Card]) -> Tuple[HandRank, List[int]]:
        """
        Evaluate best 5-card hand from given cards.
        Returns (HandRank, tiebreaker_values) for comparison.
        """
        if len(cards) < 5:
            raise ValueError("Need at least 5 cards to evaluate")

        best_rank = HandRank.HIGH_CARD
        best_values = []

        # Check all 5-card combinations
        for combo in combinations(cards, 5):
            rank, values = HandEvaluator._evaluate_five(list(combo))
            if rank.value > best_rank.value or \
               (rank.value == best_rank.value and values > best_values):
                best_rank = rank
                best_values = values

        return best_rank, best_values

    @staticmethod
    def _evaluate_five(cards: List[Card]) -> Tuple[HandRank, List[int]]:
        """Evaluate exactly 5 cards."""
        ranks = sorted([c.rank.value for c in cards], reverse=True)
        suits = [c.suit for c in cards]

        is_flush = len(set(suits)) == 1
        is_straight = HandEvaluator._is_straight(ranks)

        # Check for wheel (A-2-3-4-5)
        if ranks == [14, 5, 4, 3, 2]:
            is_straight = True
            ranks = [5, 4, 3, 2, 1]  # Ace plays low

        rank_counts = {}
        for r in ranks:
            rank_counts[r] = rank_counts.get(r, 0) + 1

        counts = sorted(rank_counts.values(), reverse=True)
        unique_ranks = sorted(rank_counts.keys(), key=lambda x: (rank_counts[x], x), reverse=True)

        # Determine hand rank
        if is_straight and is_flush:
            if ranks[0] == 14 and ranks[1] == 13:
                return HandRank.ROYAL_FLUSH, ranks
            return HandRank.STRAIGHT_FLUSH, ranks

        if counts == [4, 1]:
            return HandRank.FOUR_OF_A_KIND, unique_ranks

        if counts == [3, 2]:
            return HandRank.FULL_HOUSE, unique_ranks

        if is_flush:
            return HandRank.FLUSH, ranks

        if is_straight:
            return HandRank.STRAIGHT, ranks

        if counts == [3, 1, 1]:
            return HandRank.THREE_OF_A_KIND, unique_ranks

        if counts == [2, 2, 1]:
            return HandRank.TWO_PAIR, unique_ranks

        if counts == [2, 1, 1, 1]:
            return HandRank.PAIR, unique_ranks

        return HandRank.HIGH_CARD, ranks

    @staticmethod
    def _is_straight(ranks: List[int]) -> bool:
        """Check if sorted ranks form a straight."""
        for i in range(len(ranks) - 1):
            if ranks[i] - ranks[i + 1] != 1:
                return False
        return True

    @staticmethod
    def compare_hands(hand1: Tuple[HandRank, List[int]],
                      hand2: Tuple[HandRank, List[int]]) -> int:
        """
        Compare two hands. Returns:
        1 if hand1 wins, -1 if hand2 wins, 0 if tie.
        """
        if hand1[0].value > hand2[0].value:
            return 1
        if hand1[0].value < hand2[0].value:
            return -1

        # Same rank, compare tiebreakers
        for v1, v2 in zip(hand1[1], hand2[1]):
            if v1 > v2:
                return 1
            if v1 < v2:
                return -1

        return 0  # Tie


@dataclass
class HandState:
    """State of current hand."""
    pot: int = 0
    community_cards: List[Card] = field(default_factory=list)
    current_bet: int = 0
    min_raise: int = 0
    stage: str = "preflop"  # preflop, flop, turn, river, showdown
    action_history: List[Dict] = field(default_factory=list)

    def add_action(self, player: str, action: Action, amount: int = 0):
        self.action_history.append({
            "player": player,
            "action": action.value,
            "amount": amount,
            "stage": self.stage
        })


class PokerGame:
    """
    Main poker game controller.
    Manages a single hand of Texas Hold'em.
    """

    def __init__(self, players: List[Player], small_blind: int, big_blind: int, ante: int = 0):
        self.players = players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.ante = ante
        self.deck = Deck()
        self.state = HandState()
        self.button_pos = 0  # Dealer button position
        self.evaluator = HandEvaluator()

    def active_players(self) -> List[Player]:
        """Players still in the hand (not folded, not busted)."""
        return [p for p in self.players if not p.folded and p.is_active]

    def players_in_tournament(self) -> List[Player]:
        """Players still in tournament (have chips)."""
        return [p for p in self.players if p.is_active]

    def start_hand(self):
        """Start a new hand."""
        self.deck.reset()
        self.state = HandState()
        self.state.min_raise = self.big_blind

        # Reset players for new hand
        for p in self.players:
            if p.is_active:
                p.reset_for_hand()

        # Collect antes
        if self.ante > 0:
            for p in self.active_players():
                ante_amount = min(self.ante, p.chips)
                p.chips -= ante_amount
                self.state.pot += ante_amount

        # Post blinds
        active = self.active_players()
        if len(active) >= 2:
            sb_pos = (self.button_pos + 1) % len(active)
            bb_pos = (self.button_pos + 2) % len(active)

            # Small blind
            sb_player = active[sb_pos]
            sb_amount = min(self.small_blind, sb_player.chips)
            sb_player.chips -= sb_amount
            sb_player.current_bet = sb_amount
            self.state.pot += sb_amount

            # Big blind
            bb_player = active[bb_pos]
            bb_amount = min(self.big_blind, bb_player.chips)
            bb_player.chips -= bb_amount
            bb_player.current_bet = bb_amount
            self.state.pot += bb_amount
            self.state.current_bet = bb_amount

        # Deal hole cards
        for p in self.active_players():
            p.hole_cards = self.deck.deal(2)

    def deal_community(self):
        """Deal next community cards based on stage."""
        if self.state.stage == "preflop":
            # Deal flop
            self.deck.deal(1)  # Burn
            self.state.community_cards.extend(self.deck.deal(3))
            self.state.stage = "flop"
        elif self.state.stage == "flop":
            # Deal turn
            self.deck.deal(1)  # Burn
            self.state.community_cards.extend(self.deck.deal(1))
            self.state.stage = "turn"
        elif self.state.stage == "turn":
            # Deal river
            self.deck.deal(1)  # Burn
            self.state.community_cards.extend(self.deck.deal(1))
            self.state.stage = "river"

    def get_valid_actions(self, player: Player) -> List[Tuple[Action, int, int]]:
        """
        Get valid actions for player.
        Returns list of (Action, min_amount, max_amount).
        """
        actions = []

        if player.folded or player.all_in:
            return actions

        to_call = self.state.current_bet - player.current_bet

        # Can always fold
        actions.append((Action.FOLD, 0, 0))

        if to_call == 0:
            # No bet to call - can check
            actions.append((Action.CHECK, 0, 0))
            # Or bet
            if player.chips > 0:
                min_bet = self.big_blind
                max_bet = player.chips
                actions.append((Action.BET, min_bet, max_bet))
        else:
            # Must call, raise, or fold
            if player.chips <= to_call:
                # Can only call all-in
                actions.append((Action.ALL_IN, player.chips, player.chips))
            else:
                actions.append((Action.CALL, to_call, to_call))
                # Can raise
                min_raise = to_call + self.state.min_raise
                max_raise = player.chips
                if max_raise >= min_raise:
                    actions.append((Action.RAISE, min_raise, max_raise))

        return actions

    def apply_action(self, player: Player, action: Action, amount: int = 0):
        """Apply player action to game state."""
        if action == Action.FOLD:
            player.folded = True
        elif action == Action.CHECK:
            pass
        elif action == Action.CALL:
            to_call = self.state.current_bet - player.current_bet
            call_amount = min(to_call, player.chips)
            player.chips -= call_amount
            player.current_bet += call_amount
            self.state.pot += call_amount
            if player.chips == 0:
                player.all_in = True
        elif action == Action.BET:
            player.chips -= amount
            player.current_bet += amount
            self.state.pot += amount
            self.state.current_bet = player.current_bet
            self.state.min_raise = amount
            if player.chips == 0:
                player.all_in = True
        elif action == Action.RAISE:
            raise_to = player.current_bet + amount
            additional = amount
            player.chips -= additional
            player.current_bet += additional
            self.state.pot += additional
            self.state.min_raise = raise_to - self.state.current_bet
            self.state.current_bet = player.current_bet
            if player.chips == 0:
                player.all_in = True
        elif action == Action.ALL_IN:
            all_in_amount = player.chips
            player.chips = 0
            player.current_bet += all_in_amount
            self.state.pot += all_in_amount
            if player.current_bet > self.state.current_bet:
                self.state.min_raise = player.current_bet - self.state.current_bet
                self.state.current_bet = player.current_bet
            player.all_in = True

        self.state.add_action(player.name, action, amount)

    def is_betting_complete(self) -> bool:
        """Check if betting round is complete."""
        active = [p for p in self.active_players() if not p.all_in]

        if len(active) <= 1:
            return True

        # All active players must have matched current bet
        for p in active:
            if p.current_bet != self.state.current_bet:
                return False

        return True

    def reset_betting_round(self):
        """Reset for new betting round."""
        for p in self.active_players():
            p.current_bet = 0
        self.state.current_bet = 0

    def determine_winners(self) -> List[Tuple[Player, int]]:
        """
        Determine winners and distribute pot.
        Returns list of (player, amount_won).
        """
        active = self.active_players()

        # Edge case: everyone folded (shouldn't happen, but handle it)
        if len(active) == 0:
            # Find who contributed most to pot - they get it back
            # (This handles API error edge cases where all fold)
            max_bet = 0
            winner = None
            for p in self.players:
                if p.is_active and p.current_bet >= max_bet:
                    max_bet = p.current_bet
                    winner = p
            if winner is None:
                # Ultimate fallback - first active player
                for p in self.players:
                    if p.is_active:
                        winner = p
                        break
            if winner:
                won = self.state.pot
                winner.chips += won
                return [(winner, won)]
            return []

        if len(active) == 1:
            # Everyone else folded
            winner = active[0]
            won = self.state.pot
            winner.chips += won
            return [(winner, won)]

        # Showdown - evaluate hands
        hands = {}
        for p in active:
            all_cards = p.hole_cards + self.state.community_cards
            hands[p.name] = self.evaluator.evaluate(all_cards)

        # Find best hand(s)
        best_hand = None
        winners = []

        for p in active:
            if best_hand is None:
                best_hand = hands[p.name]
                winners = [p]
            else:
                cmp = self.evaluator.compare_hands(hands[p.name], best_hand)
                if cmp > 0:
                    best_hand = hands[p.name]
                    winners = [p]
                elif cmp == 0:
                    winners.append(p)

        # Split pot among winners
        share = self.state.pot // len(winners)
        remainder = self.state.pot % len(winners)

        results = []
        for i, w in enumerate(winners):
            won = share + (1 if i < remainder else 0)
            w.chips += won
            results.append((w, won))

        return results

    def advance_button(self):
        """Move dealer button to next active player."""
        active_indices = [i for i, p in enumerate(self.players) if p.is_active]
        if active_indices:
            current = self.button_pos % len(self.players)
            for i in range(1, len(self.players) + 1):
                next_pos = (current + i) % len(self.players)
                if next_pos in active_indices:
                    self.button_pos = next_pos
                    break

    def eliminate_busted_players(self):
        """Mark players with 0 chips as inactive."""
        for p in self.players:
            if p.chips <= 0 and p.is_active:
                p.is_active = False

    def get_game_state_for_player(self, player: Player) -> Dict:
        """Get game state from player's perspective."""
        return {
            "your_cards": [str(c) for c in player.hole_cards],
            "your_chips": player.chips,
            "your_bet": player.current_bet,
            "pot": self.state.pot,
            "community_cards": [str(c) for c in self.state.community_cards],
            "current_bet": self.state.current_bet,
            "stage": self.state.stage,
            "opponents": [
                {
                    "name": p.name,
                    "chips": p.chips,
                    "bet": p.current_bet,
                    "folded": p.folded,
                    "all_in": p.all_in
                }
                for p in self.players if p.name != player.name and p.is_active
            ],
            "action_history": self.state.action_history[-10:]  # Last 10 actions
        }

    def get_hand_summary(self) -> Dict:
        """Get summary of completed hand for notes."""
        return {
            "pot": self.state.pot,
            "community_cards": [str(c) for c in self.state.community_cards],
            "actions": self.state.action_history,
            "stage": self.state.stage
        }
