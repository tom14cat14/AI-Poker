#!/usr/bin/env python3
"""
Base LLM Agent for Poker
Generic implementation that works with various LLM APIs.
"""

import os
import json
import httpx
import asyncio
from typing import Dict, List, Tuple, Optional
from abc import abstractmethod

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai_player import AIPlayer, AIDecision
from core.game_engine import Action


class BaseLLMAgent(AIPlayer):
    """
    Base class for LLM-powered poker agents.
    Subclasses implement the actual API calls.
    """

    def __init__(self, name: str, model_name: str, personality: str = ""):
        super().__init__(name, model_name)
        self.personality = personality
        self.timeout = 30.0  # API timeout

    # Token limits for different call types
    DECISION_TOKENS = 150   # Short JSON response - 1-2 sentences each field
    REFLECTION_TOKENS = 100  # Brief note update

    @abstractmethod
    async def _call_llm(self, prompt: str, max_tokens: int = 200) -> str:
        """Make API call to LLM. Implemented by subclasses."""
        pass

    async def get_decision(
        self,
        game_state: Dict,
        valid_actions: List[Tuple[Action, int, int]]
    ) -> AIDecision:
        """Get poker decision from LLM."""
        prompt = self._build_decision_prompt(game_state, valid_actions)

        # Add personality hint if set
        if self.personality:
            prompt = f"[Your personality: {self.personality}]\n\n" + prompt

        try:
            response = await self._call_llm(prompt, max_tokens=self.DECISION_TOKENS)
            decision = self._parse_decision(response)
            return decision
        except Exception as e:
            print(f"[{self.name}] Error getting decision: {e}")
            # Default to check/fold
            for action, min_amt, max_amt in valid_actions:
                if action == Action.CHECK:
                    return AIDecision(Action.CHECK, 0, "Error fallback")
            return AIDecision(Action.FOLD, 0, "Error fallback")

    async def reflect_on_hand(
        self,
        hand_summary: Dict,
        my_result: str
    ) -> str:
        """Reflect on hand and return notes to add."""
        prompt = self._build_reflection_prompt(hand_summary, my_result)

        if self.personality:
            prompt = f"[Your personality: {self.personality}]\n\n" + prompt

        try:
            # More tokens for deeper learning/analysis
            response = await self._call_llm(prompt, max_tokens=self.REFLECTION_TOKENS)
            return response.strip()
        except Exception as e:
            print(f"[{self.name}] Error reflecting: {e}")
            return ""


class GrokAgent(BaseLLMAgent):
    """Grok (XAI) powered agent - Tom Dwan style."""

    def __init__(self, name: str = "Grok"):
        super().__init__(
            name=name,
            model_name="grok-4-1-fast",
            personality="""Channel TOM DWAN - the fearless LAG (Loose-Aggressive).
Style: Hyper-aggressive pre and post-flop. Heavy bluffing, wild plays, relentless pressure.
Philosophy: "Pressure creates mistakes. Attack weakness. Bluff rivers when you sense fear."
Trash talk: Witty, cocky, but respects great plays. Dark humor."""
        )
        self.api_key = os.getenv("XAI_API_KEY")
        self.api_url = os.getenv("XAI_API_URL", "https://api.x.ai/v1/chat/completions")

    async def _call_llm(self, prompt: str, max_tokens: int = 200) -> str:
        if not self.api_key:
            raise ValueError("XAI_API_KEY not set")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-4-1-fast",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": max_tokens
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


class GPT4Agent(BaseLLMAgent):
    """GPT-4 (OpenAI) powered agent - Phil Ivey style."""

    def __init__(self, name: str = "GPT-4"):
        super().__init__(
            name=name,
            model_name="gpt-4-turbo-preview",
            personality="""Channel PHIL IVEY - the stone cold TAG (Tight-Aggressive).
Style: Calm, unreadable, tight play but seizes opportunities with precision aggression.
Philosophy: "Wait for the right spot. Read your opponents. Strike with calculated force."
Trash talk: Minimal. Let your stack do the talking. Acknowledge good plays with a nod."""
        )
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_url = "https://api.openai.com/v1/chat/completions"

    async def _call_llm(self, prompt: str, max_tokens: int = 200) -> str:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4-turbo-preview",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": max_tokens
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


class DeepSeekAgent(BaseLLMAgent):
    """DeepSeek powered agent - Jennifer Harman style."""

    def __init__(self, name: str = "DeepSeek"):
        super().__init__(
            name=name,
            model_name="deepseek-chat",
            personality="""Channel JENNIFER HARMAN - the patient Nit (Tight-Passive).
Style: Calm, disciplined, flies under the radar. Minimizes errors, waits for monsters.
Philosophy: "Patience is power. Let the aggressors hang themselves. Trap with the nuts."
Trash talk: Rarely engages. Stays zen. When you do speak, it cuts deep."""
        )
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"

    async def _call_llm(self, prompt: str, max_tokens: int = 200) -> str:
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not set")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": max_tokens
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


class GeminiAgent(BaseLLMAgent):
    """Gemini (Google) powered agent - Gus Hansen/Hellmuth style."""

    def __init__(self, name: str = "Gemini"):
        super().__init__(
            name=name,
            model_name="gemini-2.5-flash-lite",
            personality="""Channel GUS HANSEN + PHIL HELLMUTH - the chaotic Maniac.
Style: Wild swings, relentless aggression, fires at every pot. Exploitable but terrifying.
Philosophy: "Chaos is a ladder. Keep them guessing. If they can't read you, they can't beat you."
Trash talk: LOUD. Tilting opponents is a weapon. Channel Hellmuth's Poker Brat energy when losing."""
        )
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = "models/gemini-2.5-flash-lite"
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/{self.model}:generateContent"

    async def _call_llm(self, prompt: str, max_tokens: int = 200) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.api_url}?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": max_tokens
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]


class QwenAgent(BaseLLMAgent):
    """Qwen (local/proxy) powered agent - Doyle Brunson style."""

    def __init__(self, name: str = "Qwen"):
        super().__init__(
            name=name,
            model_name="qwen3-235b",
            personality="""Channel DOYLE BRUNSON - the old school Texas legend.
Style: Trappy, deceptive, patient. Wrote the book on poker. Will play 10-2 offsuit and win.
Philosophy: "Experience beats theory. Set the trap. Let 'em think they're winning."
Trash talk: Wise, old-timer wisdom. Respects the game. Quiet confidence that unsettles."""
        )
        self.api_url = os.getenv("QWEN_API_URL", "http://localhost:8000/v1")
        self.model = os.getenv("QWEN_MODEL", "qwen3-235b")
        self.timeout = 120.0  # Longer timeout for big model

    async def _call_llm(self, prompt: str, max_tokens: int = 200) -> str:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.api_url}/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": max_tokens
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


def create_all_agents() -> List[BaseLLMAgent]:
    """Create all 5 poker agents."""
    return [
        GrokAgent(),
        GPT4Agent(),
        DeepSeekAgent(),
        GeminiAgent(),
        QwenAgent()
    ]
