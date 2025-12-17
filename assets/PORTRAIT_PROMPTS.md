# AI Poker Arena - Character Portrait Prompts

**Style**: Neon Casino Noir (Sin City x Ocean's Eleven x Arcane)

**Base Prompt Template**:
```
Neon Casino Noir portrait of [NAME], an AI poker legend channeling [PRO], [DESCRIPTION], smoky high-stakes poker room background with holographic cards floating, [ACCENT_COLOR] neon glow accents, [EYE_EFFECT], wearing [OUTFIT], [EXPRESSION] expression, dramatic chiaroscuro lighting with [ACCENT_COLOR] rim light, stylized digital art like Sin City meets Ocean's Eleven meets Arcane, high detail, cinematic
```

---

## THE PLAYERS

### 1. GROK - The Gunslinger (Tom Dwan)
**Style**: LAG Aggressor, Fearless Bluffer
**Accent Color**: Red/Orange (aggressive energy)
**Pro Reference**: Young white male, thin angular face, messy brown hair, intense piercing eyes, slight stubble
```
Neon Casino Noir portrait of Grok, an AI poker legend resembling Tom Dwan, young thin angular face with messy brown hair and slight stubble, smoky high-stakes poker room background with holographic cards floating, red-orange neon glow accents on chips and cards, piercing intense blue eyes with slight glow, wearing black hoodie under dark jacket casual style, confident smirk like he knows he's got the best hand expression, dramatic chiaroscuro lighting with red rim light, stylized digital art like Sin City meets Ocean's Eleven meets Arcane, high detail, cinematic
```

### 2. GPT-4 - The Professor (Phil Ivey)
**Style**: TAG Stone Cold, Calculated Killer
**Accent Color**: Ice Blue/White (cold precision)
**Pro Reference**: Black male, shaved head, calm intense stare, athletic build, extremely focused
```
Neon Casino Noir portrait of GPT-4, an AI poker legend resembling Phil Ivey, black male with shaved head and incredibly calm intense stare, smoky high-stakes poker room background with holographic cards floating, ice blue neon glow accents, cold piercing dark eyes that see through souls, wearing crisp designer black shirt no tie casual luxury style, completely unreadable stone cold expression like nothing can phase him, dramatic chiaroscuro lighting with blue rim light, stylized digital art like Sin City meets Ocean's Eleven meets Arcane, high detail, cinematic
```

### 3. DEEPSEEK - The Monk (Jennifer Harman)
**Style**: Nit Trapper, Patient Assassin
**Accent Color**: Deep Purple/Violet (zen mystery)
**Pro Reference**: White female, blonde hair, petite but fierce, determined focused expression
```
Neon Casino Noir portrait of DeepSeek, an AI poker legend resembling Jennifer Harman, petite fierce blonde woman with determined focused expression, smoky high-stakes poker room background with holographic cards floating, deep purple neon glow accents like meditation aura, piercing blue-green eyes that have won millions, wearing elegant dark blazer feminine but powerful style, calm knowing smile of someone who's beaten all the men expression, dramatic chiaroscuro lighting with purple rim light, stylized digital art like Sin City meets Ocean's Eleven meets Arcane, high detail, cinematic
```

### 4. GEMINI - The Wildcard (Gus Hansen + Hellmuth)
**Style**: Maniac Chaos, Tilt Master
**Accent Color**: Chaotic Rainbow/Shifting (unpredictable)
**Pro Reference**: Blend of Hansen (blonde Danish, wild eyes) and Hellmuth (dramatic expressions, attitude)
```
Neon Casino Noir portrait of Gemini, an AI poker legend blending Gus Hansen and Phil Hellmuth, blonde white male with wild tousled hair and manic intense blue eyes, smoky high-stakes poker room background with holographic cards floating, shifting rainbow neon glow accents that seem unstable, expressive animated face mid-outburst, wearing designer sunglasses pushed up on head with expensive but flashy shirt, about to either celebrate or explode expression capturing the poker brat energy, dramatic chiaroscuro lighting with multicolor rim light, stylized digital art like Sin City meets Ocean's Eleven meets Arcane, high detail, cinematic
```

### 5. QWEN - The Legend (Doyle Brunson)
**Style**: Old School Trap, Texas Wisdom
**Accent Color**: Gold/Amber (legendary status)
**Pro Reference**: Older white male, large build, white hair, cowboy hat, wise weathered face, Texas legend
```
Neon Casino Noir portrait of Qwen, an AI poker legend resembling Doyle Brunson, older large white male with white hair and weathered wise face, smoky high-stakes poker room background with holographic cards floating, warm gold neon glow accents like sunset, deep knowing eyes that have seen fifty years of poker, wearing classic cowboy hat and western-style blazer with bolo tie Texas Dolly style, quiet confident smile of someone who literally wrote the book on poker expression, dramatic chiaroscuro lighting with gold rim light, stylized digital art like Sin City meets Ocean's Eleven meets Arcane, high detail, cinematic
```

---

## SCENE PROMPTS

### Poker Table (Main View)
```
Neon Casino Noir scene of high-stakes AI poker arena, five AI players seated at luxury oval poker table, holographic pot display floating center, smoky atmosphere with dramatic spotlights, each player has distinct colored neon glow aura (red, blue, purple, rainbow, gold), felt table with subtle circuit pattern, floating holographic cards and chips, tense dramatic atmosphere, stylized digital art like Sin City meets Ocean's Eleven meets Arcane, cinematic wide shot
```

### Action Shot (Player Decision)
```
Neon Casino Noir close-up of AI poker player making critical decision, intense focus on face and hands, holographic cards visible, chips being pushed forward, dramatic spotlight from above, opponent silhouettes in background, [PLAYER_COLOR] neon glow intensifying, thought bubble with strategy forming, stylized digital art like Sin City meets Ocean's Eleven meets Arcane, dramatic angle
```

### Showdown
```
Neon Casino Noir scene of poker showdown, two AI players facing off across table, cards being revealed, massive holographic pot display, chips scattered dramatically, winner's neon glow brightening while loser dims, spectators (other AIs) in background with reactions, explosive dramatic lighting, stylized digital art like Sin City meets Ocean's Eleven meets Arcane, cinematic action shot
```

### Trash Talk Moment
```
Neon Casino Noir scene of AI poker trash talk, speaker leaning forward aggressively with neon glow intensifying, speech bubble with bold text, target player reacting (stoic/tilted/amused), other players watching, dramatic lighting emphasizing confrontation, stylized digital art like Sin City meets Ocean's Eleven meets Arcane, comic panel composition
```

---

## VOICE ASSIGNMENTS (ElevenLabs)

| AI | Voice Style | ElevenLabs Voice ID | Notes |
|----|-------------|---------------------|-------|
| Grok | Young, cocky, slight drawl | TBD - "Josh" or similar | Dwan's confident swagger |
| GPT-4 | Deep, measured, calm | TBD - "Adam" or similar | Ivey's stone cold demeanor |
| DeepSeek | Soft, zen, deliberate | TBD - "Rachel" or similar | Harman's patient wisdom |
| Gemini | Erratic, loud, emotional | TBD - "Antoni" or similar | Hellmuth's brat energy |
| Qwen | Gravelly, wise, Texan | TBD - "Clyde" or similar | Doyle's legendary presence |

---

## GENERATION NOTES

**Recommended Tools**:
- Flux.1 Dev on Replicate (~$0.003/image)
- Leonardo AI (150 free/day)
- Midjourney (for highest quality)

**For Consistency**:
- Generate base character, then use Character Reference for variations
- Keep same seed for same character across poses
- Match "Neon Casino Noir" lighting across all images

**File Naming Convention**:
```
assets/
├── portraits/
│   ├── grok_portrait_v1.png
│   ├── grok_action_v1.png
│   ├── gpt4_portrait_v1.png
│   ...
├── scenes/
│   ├── table_main.png
│   ├── showdown_01.png
│   ...
├── audio/
│   ├── tournament_01/
│   │   ├── 001_grok_trashtalk.mp3
│   │   ├── 002_gpt4_thought.mp3
│   ...
```

---

## WEBSITE DESIGN TOOLS (Beyond Images/Voices)

### Animation Libraries
| Tool | Use Case | Cost |
|------|----------|------|
| **Lottie** | Card flips, chip movements, reactions | Free |
| **GSAP** | Smooth UI transitions, page animations | Free |
| **Rive** | Interactive character animations | Free tier |
| **Three.js** | 3D table, floating cards, 3D chips | Free |
| **Spline** | Browser-based 3D design | Free tier |

### Sound Design
- **Ambient casino sounds** - Murmuring crowd, distant slots
- **Card sounds** - Shuffle, deal, flip
- **Chip sounds** - Stack, push, collect
- **Action sounds** - Check tap, raise chip slide, all-in dramatic
- **Sources**: Freesound.org, Epidemic Sound, custom Foley

### Typography
| Font | Use Case | Style |
|------|----------|-------|
| **Playfair Display** | Headers | Elegant casino |
| **Bebas Neue** | Player names | Bold impact |
| **JetBrains Mono** | Stats/numbers | Tech readable |
| **Custom neon font** | Logo/titles | Unique identity |

### Visual Effects
- **Particle effects** - Chip splashes on big pots
- **Glow effects** - Neon accents on active player
- **Blur/focus** - Highlight decision-maker
- **Screen shake** - All-in moments

### Unique Touches to Avoid "AI Generic" Look
1. **Hand-drawn elements** - Sketchy overlays, imperfect lines
2. **Film grain** - Slight texture overlay
3. **Chromatic aberration** - Subtle RGB split on edges
4. **Custom cursor** - Poker chip or card
5. **Easter eggs** - Hidden animations, 10-2 Doyle tribute
6. **Dynamic lighting** - Flicker effects, spotlight movement

---

## COLOR PALETTE

| Player | Primary | Accent | Glow |
|--------|---------|--------|------|
| Grok | #1a1a1a | #ff4444 | Red-Orange |
| GPT-4 | #1a1a1a | #44aaff | Ice Blue |
| DeepSeek | #1a1a1a | #9944ff | Purple |
| Gemini | #1a1a1a | Rainbow | Shifting |
| Qwen | #1a1a1a | #ffaa44 | Gold |
| Background | #0a0a0f | - | - |
| Table Felt | #1a3a2a | #2a4a3a | Dark Green |
