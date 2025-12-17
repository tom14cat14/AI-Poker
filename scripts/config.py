"""
AI Poker Arena - Asset Pipeline Configuration
==============================================
Central configuration for image and voice generation.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from ~/.env.keys or local .env
load_dotenv(Path.home() / ".env.keys")
load_dotenv()

# =============================================================================
# API KEYS
# =============================================================================

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# =============================================================================
# PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
PORTRAITS_DIR = ASSETS_DIR / "portraits"
SCENES_DIR = ASSETS_DIR / "scenes"
AUDIO_DIR = ASSETS_DIR / "audio"

# =============================================================================
# IMAGE GENERATION SETTINGS
# =============================================================================

# Flux model on Replicate (best quality/price)
FLUX_MODEL = "black-forest-labs/flux-1.1-pro"

# Default image settings
IMAGE_WIDTH = 1024
IMAGE_HEIGHT = 1024
IMAGE_FORMAT = "png"

# =============================================================================
# VOICE SETTINGS (ElevenLabs)
# =============================================================================

ELEVENLABS_MODEL = "eleven_turbo_v2_5"  # Fast, good quality

# Voice IDs - matching poker pro personalities (using available ElevenLabs voices)
VOICE_ASSIGNMENTS = {
    # Grok - Tom Dwan style: Young, cocky, confident
    "Grok": {
        "voice_id": "IKne3meq5aSn9XLyUdCD",  # Charlie - Deep, Confident, Energetic
        "name": "Charlie",
        "style": "cocky, confident swagger"
    },

    # GPT-4 - Phil Ivey style: Deep, calm, measured
    "GPT-4": {
        "voice_id": "pNInz6obpgDQGcFmaJgB",  # Adam - Dominant, Firm
        "name": "Adam",
        "style": "stone cold, minimal emotion"
    },

    # DeepSeek - Jennifer Harman style: Calm, determined, feminine
    "DeepSeek": {
        "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Sarah - Mature, Reassuring, Confident
        "name": "Sarah",
        "style": "patient, quietly fierce"
    },

    # Gemini - Hansen/Hellmuth style: Dramatic, emotional, loud
    "Gemini": {
        "voice_id": "SOYHLrjzK2X1ezoPC6cr",  # Harry - Fierce Warrior
        "name": "Harry",
        "style": "animated, dramatic, can tilt"
    },

    # Qwen - Doyle Brunson style: Gravelly, wise, older
    "Qwen": {
        "voice_id": "pqHfZKP75CvOlQylNhV4",  # Bill - Wise, Mature, Balanced
        "name": "Bill",
        "style": "wise, mature, legendary presence"
    },

    # Narrator - Commentary voice
    "Narrator": {
        "voice_id": "onwK4e9ZLuTAKqWW03F9",  # Daniel - Steady Broadcaster
        "name": "Daniel",
        "style": "poker commentator, dramatic"
    },
}

# =============================================================================
# PLAYER DATA (Poker Pros)
# =============================================================================

PLAYERS = {
    "Grok": {
        "pro": "Tom Dwan",
        "style": "LAG",
        "accent_color": "red-orange",
        "description": "young thin angular face with messy brown hair and slight stubble",
        "expression": "confident smirk like he knows he's got the best hand",
        "outfit": "black hoodie under dark jacket casual style",
        "eye_effect": "piercing intense blue eyes with slight glow",
    },

    "GPT-4": {
        "pro": "Phil Ivey",
        "style": "TAG",
        "accent_color": "ice-blue",
        "description": "black male with shaved head and incredibly calm intense stare",
        "expression": "completely unreadable stone cold expression like nothing can phase him",
        "outfit": "crisp designer black shirt no tie casual luxury style",
        "eye_effect": "cold piercing dark eyes that see through souls",
    },

    "DeepSeek": {
        "pro": "Jennifer Harman",
        "style": "Nit",
        "accent_color": "purple-violet",
        "description": "petite fierce blonde woman with determined focused expression",
        "expression": "calm knowing smile of someone who's beaten all the men",
        "outfit": "elegant dark blazer feminine but powerful style",
        "eye_effect": "piercing blue-green eyes that have won millions",
    },

    "Gemini": {
        "pro": "Gus Hansen + Phil Hellmuth",
        "style": "Maniac",
        "accent_color": "rainbow-shifting",
        "description": "blonde white male with wild tousled hair and manic intense blue eyes",
        "expression": "about to either celebrate or explode expression capturing poker brat energy",
        "outfit": "designer sunglasses pushed up on head with expensive flashy shirt",
        "eye_effect": "expressive animated eyes that shift with mood",
    },

    "Qwen": {
        "pro": "Doyle Brunson",
        "style": "Legend",
        "accent_color": "gold-amber",
        "description": "distinguished older gentleman with silver hair and wise weathered features",
        "expression": "quiet confident knowing smile of a poker legend",
        "outfit": "classic western hat and elegant dark blazer with bolo tie",
        "eye_effect": "deep warm amber eyes full of wisdom and experience",
    },
}

# =============================================================================
# PROMPT TEMPLATES
# =============================================================================

PORTRAIT_PROMPT_TEMPLATE = """Neon Casino Noir portrait of {name}, an AI poker legend resembling {pro}, {description}, smoky high-stakes poker room background with holographic cards floating, {accent_color} neon glow accents, {eye_effect}, wearing {outfit}, {expression}, dramatic chiaroscuro lighting with {accent_color} rim light, stylized digital art like Sin City meets Ocean's Eleven meets Arcane, high detail, cinematic"""

SCENE_PROMPTS = {
    "poker_table": """Neon Casino Noir scene of high-stakes AI poker arena, five AI players seated at luxury oval poker table, holographic pot display floating center, smoky atmosphere with dramatic spotlights, each player has distinct colored neon glow aura (red, blue, purple, rainbow, gold), felt table with subtle circuit pattern, floating holographic cards and chips, tense dramatic atmosphere, stylized digital art like Sin City meets Ocean's Eleven meets Arcane, cinematic wide shot""",

    "showdown": """Neon Casino Noir scene of poker showdown moment, two AI players facing off across table, cards being dramatically revealed, massive holographic pot display glowing, chips scattered dramatically, winner's neon glow brightening, explosive dramatic lighting, stylized digital art like Sin City meets Ocean's Eleven meets Arcane, cinematic action shot""",

    "all_in": """Neon Casino Noir scene of all-in moment, single player pushing massive chip stack forward, dramatic spotlight from above, tension visible in air, other players silhouettes watching, neon glow intensifying around the bettor, stylized digital art like Sin City meets Ocean's Eleven meets Arcane, dramatic angle""",

    "trash_talk": """Neon Casino Noir scene of poker trash talk confrontation, two players facing each other intensely, speech bubbles with neon edges, other players watching reaction, dramatic lighting emphasizing the confrontation, smoky atmosphere, stylized digital art like Sin City meets Ocean's Eleven meets Arcane, comic panel composition""",
}

# Expression variants
EXPRESSIONS = ["neutral", "winning", "losing", "bluffing", "tilted"]
