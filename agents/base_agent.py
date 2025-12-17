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

    @abstractmethod
    async def _call_llm(self, prompt: str) -> str:
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
            response = await self._call_llm(prompt)
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
            response = await self._call_llm(prompt)
            return response.strip()
        except Exception as e:
            print(f"[{self.name}] Error reflecting: {e}")
            return ""


class GrokAgent(BaseLLMAgent):
    """Grok (XAI) powered agent."""

    def __init__(self, name: str = "Grok"):
        super().__init__(
            name=name,
            model_name="grok-beta",
            personality="Witty, slightly rebellious, enjoys dark humor. Not afraid to call out bluffs."
        )
        self.api_key = os.getenv("XAI_API_KEY")
        self.api_url = "https://api.x.ai/v1/chat/completions"

    async def _call_llm(self, prompt: str) -> str:
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
                    "model": "grok-beta",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


class GPT4Agent(BaseLLMAgent):
    """GPT-4 (OpenAI) powered agent."""

    def __init__(self, name: str = "GPT-4"):
        super().__init__(
            name=name,
            model_name="gpt-4-turbo-preview",
            personality="Analytical, calculated, patient. Prefers mathematical approach to poker."
        )
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_url = "https://api.openai.com/v1/chat/completions"

    async def _call_llm(self, prompt: str) -> str:
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
                    "max_tokens": 500
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


class DeepSeekAgent(BaseLLMAgent):
    """DeepSeek powered agent."""

    def __init__(self, name: str = "DeepSeek"):
        super().__init__(
            name=name,
            model_name="deepseek-chat",
            personality="Value-oriented, looks for exploits. Remembers everything."
        )
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"

    async def _call_llm(self, prompt: str) -> str:
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
                    "max_tokens": 500
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


class GeminiAgent(BaseLLMAgent):
    """Gemini (Google) powered agent."""

    def __init__(self, name: str = "Gemini"):
        super().__init__(
            name=name,
            model_name="gemini-pro",
            personality="Unpredictable, creative. Sometimes makes wild plays just to see what happens."
        )
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

    async def _call_llm(self, prompt: str) -> str:
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not set")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.api_url}?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 500
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]


class QwenAgent(BaseLLMAgent):
    """Qwen (local/proxy) powered agent."""

    def __init__(self, name: str = "Qwen"):
        super().__init__(
            name=name,
            model_name="qwen3-235b",
            personality="Methodical, studies opponents carefully. Quiet but deadly."
        )
        self.api_url = os.getenv("QWEN_API_URL", "http://localhost:8000/v1")
        self.model = os.getenv("QWEN_MODEL", "qwen3-235b")

    async def _call_llm(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.api_url}/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 500
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
