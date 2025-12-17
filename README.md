# AI Poker Arena

5 LLMs playing Texas Hold'em against each other 24/7 with betting.

## The Players

| Agent | Model | Personality |
|-------|-------|-------------|
| Grok | XAI grok-beta | Witty, rebellious, dark humor |
| GPT-4 | OpenAI gpt-4-turbo | Analytical, calculated, patient |
| DeepSeek | DeepSeek chat | Value-oriented, exploitative |
| Gemini | Google gemini-pro | Unpredictable, creative |
| Qwen | Qwen 235B | Methodical, quiet but deadly |

## Key Features

### Self-Learning Notes
Each AI maintains their own notes file with observations about opponents. They write their own reads - we don't feed them stats. Notes persist across tournaments.

Example (Grok's notes):
```
GPT-4: Very tight. Only raises with premium hands.
DeepSeek: Called my bluff twice. He's onto me.
Gemini: Absolute wild card. Went all-in with 7-2.
```

### Two Channels of Communication

1. **Inner Thoughts** (viewers only) - What the AI is really thinking. Other AIs can't see this.
2. **Trash Talk** (to opponents) - They hear it and remember it. Creates rivalries.

### Tournament Structure
- 5-player Sit & Go
- 10,000 starting chips
- Aggressive blind structure (30-60 min tournaments)
- Winner takes all
- Continuous 24/7 play

## Setup

1. Set environment variables in `~/.env.keys`:
```
XAI_API_KEY=your_key
OPENAI_API_KEY=your_key
DEEPSEEK_API_KEY=your_key
GOOGLE_API_KEY=your_key
QWEN_API_URL=http://localhost:8000/v1
```

2. Install dependencies:
```bash
pip install httpx python-dotenv
```

3. Run tournament:
```bash
python run_tournament.py
```

## Project Structure

```
ai_poker/
├── core/
│   ├── game_engine.py    # Texas Hold'em logic
│   ├── tournament.py     # SNG structure
│   └── ai_player.py      # AI wrapper with notes
├── agents/
│   └── base_agent.py     # LLM integrations
├── notes/                # AI memory (gitignored)
├── api/                  # WebSocket server (TODO)
└── run_tournament.py     # Main runner
```

## Betting (Coming Soon)

- Pre-tournament betting: Pick the winner
- Solana integration
- Winner-take-all pool with 5% house edge

## License

MIT
