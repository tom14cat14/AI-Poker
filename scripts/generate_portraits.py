#!/usr/bin/env python3
"""
AI Poker Arena - Portrait Generator
====================================
Generates character portraits using Flux on Replicate.

Usage:
    python generate_portraits.py                    # Generate all 5 portraits
    python generate_portraits.py Grok GPT-4        # Generate specific players
    python generate_portraits.py --scenes          # Generate scene backgrounds
    python generate_portraits.py --expressions     # Generate expression variants

Requirements:
    pip install replicate aiohttp python-dotenv

Environment:
    REPLICATE_API_TOKEN=your_token_here
"""

import asyncio
import argparse
import sys
import time
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    REPLICATE_API_TOKEN,
    PORTRAITS_DIR,
    SCENES_DIR,
    PLAYERS,
    PORTRAIT_PROMPT_TEMPLATE,
    SCENE_PROMPTS,
    EXPRESSIONS,
    FLUX_MODEL,
    IMAGE_WIDTH,
    IMAGE_HEIGHT,
)

try:
    import replicate
except ImportError:
    print("Error: replicate package not installed")
    print("Run: pip install replicate")
    sys.exit(1)

import aiohttp


class PortraitGenerator:
    """Generates character portraits using Flux on Replicate."""

    def __init__(self):
        if not REPLICATE_API_TOKEN:
            raise ValueError(
                "REPLICATE_API_TOKEN not set. Add it to ~/.env.keys or set environment variable."
            )
        self.client = replicate.Client(api_token=REPLICATE_API_TOKEN)
        self.generated_count = 0
        self.failed_count = 0

    def build_portrait_prompt(self, name: str, expression: str = None) -> str:
        """Build a portrait prompt for a player."""
        player = PLAYERS.get(name)
        if not player:
            raise ValueError(f"Unknown player: {name}")

        # Modify expression if specified
        expr = expression if expression else player["expression"]

        return PORTRAIT_PROMPT_TEMPLATE.format(
            name=name,
            pro=player["pro"],
            description=player["description"],
            accent_color=player["accent_color"],
            eye_effect=player["eye_effect"],
            outfit=player["outfit"],
            expression=expr,
        )

    async def download_image(self, url: str, output_path: Path) -> bool:
        """Download image from URL to local file."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        content = await response.read()
                        output_path.write_bytes(content)
                        return True
                    else:
                        print(f"  Error: HTTP {response.status}")
                        return False
        except Exception as e:
            print(f"  Download error: {e}")
            return False

    def generate_image(self, prompt: str) -> str | None:
        """Generate an image using Flux and return the URL."""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                output = self.client.run(
                    FLUX_MODEL,
                    input={
                        "prompt": prompt,
                        "width": IMAGE_WIDTH,
                        "height": IMAGE_HEIGHT,
                        "num_outputs": 1,
                        "output_format": "png",
                        "output_quality": 90,
                    },
                )
                # Handle different Replicate response formats
                if output is None:
                    return None
                if hasattr(output, 'url'):
                    return str(output.url)
                try:
                    first = next(iter(output))
                    if hasattr(first, 'url'):
                        return str(first.url)
                    return str(first)
                except (TypeError, StopIteration):
                    return str(output)
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "throttled" in error_str.lower():
                    wait_time = 12 * (attempt + 1)
                    print(f"  Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                print(f"  Generation error: {e}")
                return None

        print(f"  Failed after {max_retries} retries")
        return None

    async def generate_portrait(
        self, name: str, expression: str = None, version: int = 1
    ) -> bool:
        """Generate a single character portrait."""
        expr_suffix = f"_{expression}" if expression else ""
        filename = f"{name.lower()}_portrait{expr_suffix}_v{version}.png"
        output_path = PORTRAITS_DIR / filename

        # Skip if already exists
        if output_path.exists():
            print(f"  Skipping {filename} (already exists)")
            return True

        prompt = self.build_portrait_prompt(name, expression)
        print(f"  Generating {filename}...")
        print(f"    Player: {name} ({PLAYERS[name]['pro']} style)")
        print(f"    Prompt: {prompt[:80]}...")

        url = self.generate_image(prompt)
        if url:
            success = await self.download_image(url, output_path)
            if success:
                print(f"  Saved: {output_path}")
                self.generated_count += 1
                # Rate limit delay
                print(f"  Waiting 12s for rate limit...")
                time.sleep(12)
                return True

        self.failed_count += 1
        return False

    async def generate_scene(self, scene_name: str, version: int = 1) -> bool:
        """Generate a scene background."""
        filename = f"{scene_name}_v{version}.png"
        output_path = SCENES_DIR / filename

        if output_path.exists():
            print(f"  Skipping {filename} (already exists)")
            return True

        prompt = SCENE_PROMPTS.get(scene_name)
        if not prompt:
            print(f"  Unknown scene: {scene_name}")
            return False

        print(f"  Generating {filename}...")
        print(f"    Prompt: {prompt[:80]}...")

        url = self.generate_image(prompt)
        if url:
            success = await self.download_image(url, output_path)
            if success:
                print(f"  Saved: {output_path}")
                self.generated_count += 1
                print(f"  Waiting 12s for rate limit...")
                time.sleep(12)
                return True

        self.failed_count += 1
        return False

    async def generate_all_portraits(self, players: list[str] = None):
        """Generate portraits for all or specified players."""
        player_list = players if players else list(PLAYERS.keys())

        print(f"\n{'='*60}")
        print(f"AI POKER ARENA - Portrait Generator")
        print(f"{'='*60}")
        print(f"Players: {len(player_list)}")
        print(f"Output: {PORTRAITS_DIR}")
        print(f"Model: {FLUX_MODEL}")
        print(f"{'='*60}\n")

        for name in player_list:
            player = PLAYERS.get(name)
            if player:
                print(f"\n[{name}] - {player['pro']} style")
                await self.generate_portrait(name)

        self._print_summary()

    async def generate_all_expressions(self, players: list[str] = None):
        """Generate all expression variants for players."""
        player_list = players if players else list(PLAYERS.keys())

        print(f"\n{'='*60}")
        print(f"AI POKER ARENA - Expression Variants")
        print(f"{'='*60}")
        print(f"Players: {len(player_list)}")
        print(f"Expressions: {EXPRESSIONS}")
        print(f"{'='*60}\n")

        for name in player_list:
            print(f"\n[{name}]")
            for expr in EXPRESSIONS:
                await self.generate_portrait(name, expression=expr)

        self._print_summary()

    async def generate_all_scenes(self):
        """Generate all scene backgrounds."""
        print(f"\n{'='*60}")
        print(f"AI POKER ARENA - Scene Generator")
        print(f"{'='*60}")
        print(f"Scenes: {list(SCENE_PROMPTS.keys())}")
        print(f"Output: {SCENES_DIR}")
        print(f"{'='*60}\n")

        for scene_name in SCENE_PROMPTS:
            await self.generate_scene(scene_name)

        self._print_summary()

    def _print_summary(self):
        """Print generation summary."""
        print(f"\n{'='*60}")
        print(f"SUMMARY")
        print(f"{'='*60}")
        print(f"Generated: {self.generated_count}")
        print(f"Failed: {self.failed_count}")
        print(f"Cost: ~${self.generated_count * 0.003:.3f} (Flux 1.1 Pro)")
        print(f"{'='*60}\n")


async def main():
    parser = argparse.ArgumentParser(description="Generate AI Poker Arena portraits")
    parser.add_argument(
        "players",
        nargs="*",
        help="Specific players to generate (default: all)",
    )
    parser.add_argument(
        "--scenes",
        action="store_true",
        help="Generate scene backgrounds instead of portraits",
    )
    parser.add_argument(
        "--expressions",
        action="store_true",
        help="Generate all expression variants",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available players and scenes",
    )

    args = parser.parse_args()

    if args.list:
        print("\nPlayers:")
        for name, data in PLAYERS.items():
            print(f"  {name} - {data['pro']} ({data['style']})")
        print("\nScenes:")
        for scene in SCENE_PROMPTS:
            print(f"  {scene}")
        print("\nExpressions:")
        for expr in EXPRESSIONS:
            print(f"  {expr}")
        return

    try:
        generator = PortraitGenerator()

        if args.scenes:
            await generator.generate_all_scenes()
        elif args.expressions:
            await generator.generate_all_expressions(args.players or None)
        else:
            await generator.generate_all_portraits(args.players or None)

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
