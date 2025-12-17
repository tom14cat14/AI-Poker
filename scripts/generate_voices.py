#!/usr/bin/env python3
"""
AI Poker Arena - Voice Generator
=================================
Generates character voice lines using ElevenLabs.

Usage:
    python generate_voices.py --test Grok          # Test voice for a player
    python generate_voices.py --test-all           # Test all player voices
    python generate_voices.py --list-voices        # List available ElevenLabs voices
    python generate_voices.py script.json          # Generate from script file

Requirements:
    pip install elevenlabs

Environment:
    ELEVENLABS_API_KEY=your_key_here
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    ELEVENLABS_API_KEY,
    ELEVENLABS_MODEL,
    AUDIO_DIR,
    VOICE_ASSIGNMENTS,
    PLAYERS,
)

try:
    from elevenlabs import ElevenLabs, VoiceSettings
except ImportError:
    print("Error: elevenlabs package not installed")
    print("Run: pip install elevenlabs")
    sys.exit(1)


class VoiceGenerator:
    """Generates character voice lines using ElevenLabs."""

    def __init__(self):
        if not ELEVENLABS_API_KEY:
            raise ValueError(
                "ELEVENLABS_API_KEY not set. Add it to ~/.env.keys or set environment variable."
            )
        self.client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        self.generated_count = 0
        self.failed_count = 0
        self.total_characters = 0

    def get_voice_id(self, player: str) -> str:
        """Get the ElevenLabs voice ID for a player."""
        voice_data = VOICE_ASSIGNMENTS.get(player)
        if not voice_data:
            voice_data = VOICE_ASSIGNMENTS.get("Narrator")
        return voice_data["voice_id"]

    def get_voice_style(self, player: str) -> str:
        """Get the voice style description for a player."""
        voice_data = VOICE_ASSIGNMENTS.get(player)
        if voice_data:
            return voice_data.get("style", "")
        return ""

    def generate_audio(
        self,
        text: str,
        player: str,
        output_path: Path,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
    ) -> bool:
        """Generate audio for a single line of dialogue."""
        try:
            voice_id = self.get_voice_id(player)

            audio_generator = self.client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id=ELEVENLABS_MODEL,
                voice_settings=VoiceSettings(
                    stability=stability,
                    similarity_boost=similarity_boost,
                    style=0.0,
                    use_speaker_boost=True,
                ),
            )

            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                for chunk in audio_generator:
                    f.write(chunk)

            self.total_characters += len(text)
            return True

        except Exception as e:
            print(f"  Error generating audio: {e}")
            return False

    def test_voice(self, player: str) -> bool:
        """Generate a test voice line for a player."""
        player_data = PLAYERS.get(player)
        pro = player_data["pro"] if player_data else player

        # Poker-themed test lines for each personality
        test_lines = {
            "Grok": f"I'm putting you all in. Let's see if you've got the guts to call. Time to rustle some chips, partner.",
            "GPT-4": f"The math says fold. But you won't. You never do. Calculate... eliminate.",
            "DeepSeek": f"I've been waiting for this moment all night. Patience strikes true.",
            "Gemini": f"You think you can read me? I don't even know what I'm doing! Chaos reigns!",
            "Qwen": f"Son, I've been playing this game since before you were born. That's poker. Deal with it.",
            "Narrator": f"And with that bold move, the pressure is on. Who will crack first in this high-stakes showdown?",
        }

        test_text = test_lines.get(player, f"Hello, I'm {player}. This is my voice in AI Poker Arena.")

        output_path = AUDIO_DIR / "tests" / f"{player.lower()}_test.mp3"

        print(f"\nGenerating test voice for {player}...")
        print(f"  Pro: {pro}")
        print(f"  Voice ID: {self.get_voice_id(player)}")
        print(f"  Style: {self.get_voice_style(player)}")
        print(f"  Text: {test_text[:60]}...")

        success = self.generate_audio(test_text, player, output_path)

        if success:
            print(f"  Saved: {output_path}")
            self.generated_count += 1
            return True
        else:
            self.failed_count += 1
            return False

    def list_voices(self):
        """List all available voices from ElevenLabs account."""
        try:
            voices = self.client.voices.get_all()
            print("\nAvailable ElevenLabs Voices:")
            print("-" * 60)
            for voice in voices.voices:
                print(f"  {voice.name}: {voice.voice_id}")
            print("-" * 60)

            print("\nCurrent Voice Assignments:")
            print("-" * 60)
            for player, data in VOICE_ASSIGNMENTS.items():
                print(f"  {player}: {data['name']} ({data['voice_id'][:8]}...)")
            print("-" * 60)
        except Exception as e:
            print(f"Error listing voices: {e}")

    def generate_from_script(self, script_path: Path, tournament_id: str = None) -> bool:
        """
        Generate all voice lines from a tournament script.

        Script format (JSON):
        {
            "tournament": 1,
            "lines": [
                {"player": "Narrator", "text": "Welcome to AI Poker Arena...", "type": "intro"},
                {"player": "Grok", "text": "I'm all in.", "type": "action"},
                {"player": "Grok", "text": "You're going down, GPT-4.", "type": "trash_talk"},
                ...
            ]
        }
        """
        if not script_path.exists():
            print(f"Error: Script file not found: {script_path}")
            return False

        with open(script_path) as f:
            script = json.load(f)

        t_id = tournament_id or f"tournament_{script.get('tournament', '01'):02d}"
        output_dir = AUDIO_DIR / t_id

        lines = script.get("lines", [])
        print(f"\n{'='*60}")
        print(f"AI POKER ARENA - Voice Generator")
        print(f"{'='*60}")
        print(f"Tournament: {t_id}")
        print(f"Lines: {len(lines)}")
        print(f"Output: {output_dir}")
        print(f"{'='*60}\n")

        for i, line in enumerate(lines, 1):
            player = line.get("player", "Narrator")
            text = line.get("text", "")
            line_type = line.get("type", "dialogue")
            line_id = line.get("id", f"{i:03d}")

            if not text:
                continue

            filename = f"{line_id}_{player.lower()}_{line_type}.mp3"
            output_path = output_dir / filename

            if output_path.exists():
                print(f"  [{i}/{len(lines)}] Skipping {filename} (exists)")
                continue

            print(f"  [{i}/{len(lines)}] {player}: {text[:50]}...")

            success = self.generate_audio(text, player, output_path)
            if success:
                self.generated_count += 1
            else:
                self.failed_count += 1

        self._print_summary()
        return self.failed_count == 0

    def _print_summary(self):
        """Print generation summary."""
        print(f"\n{'='*60}")
        print(f"SUMMARY")
        print(f"{'='*60}")
        print(f"Generated: {self.generated_count}")
        print(f"Failed: {self.failed_count}")
        print(f"Characters used: ~{self.total_characters:,}")
        print(f"{'='*60}\n")


async def main():
    parser = argparse.ArgumentParser(description="Generate AI Poker Arena voice lines")
    parser.add_argument(
        "script",
        nargs="?",
        help="Path to tournament script JSON",
    )
    parser.add_argument(
        "--test",
        metavar="PLAYER",
        help="Generate test voice for a player",
    )
    parser.add_argument(
        "--test-all",
        action="store_true",
        help="Generate test voices for all players",
    )
    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="List available ElevenLabs voices",
    )
    parser.add_argument(
        "--tournament",
        help="Tournament ID for output directory",
    )

    args = parser.parse_args()

    try:
        generator = VoiceGenerator()

        if args.list_voices:
            generator.list_voices()
        elif args.test:
            generator.test_voice(args.test)
            generator._print_summary()
        elif args.test_all:
            print("\nTesting all player voices...")
            for player in list(PLAYERS.keys()) + ["Narrator"]:
                generator.test_voice(player)
            generator._print_summary()
        elif args.script:
            script_path = Path(args.script)
            generator.generate_from_script(script_path, args.tournament)
        else:
            parser.print_help()

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
