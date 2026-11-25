# Architecture & Dependency Map

## "What Changes What" Map
```mermaid
flowchart LR
  SB["storyboard.json"] --> VAL["validate.py"]
  VAL --> NARR["narration.py (Gemini TTS)"]
  VAL --> KEY["keyframes.py (Cloudflare FLUX)"]
  VAL --> MUS["music.py (Kaggle ACE-Step 1.5)"]
  CHAR["Character Reference Sheet"] --> KEY
  STYLE["Fixed Style Block"] --> KEY
  KEY --> SHOTS["shots.py (Kaggle Wan 2.2 TI2V-5B / FFmpeg Ken Burns fallback)"]
  NARR --> TIMING["Shot Timing & Subtitles"]
  TIMING --> ASM["assemble.py (FFmpeg 9:16 & 16:9)"]
  SHOTS --> ASM
  MUS --> ASM
```

## Change Impact Rules
- Changing **shot `N` `image_prompt`** -> regenerates **keyframe `N`** -> **clip `N`** -> **final edit**.
- Changing **shot `N` `narration`** -> regenerates **narration `N`** -> **timing/subtitles** -> **final edit**.
- Changing **`style_block` or `character.selected_reference_image`** -> regenerates **ALL keyframes** -> **ALL clips** -> **final edit**.
- Changing **`music.caption` / `tempo_bpm` / `seed`** -> regenerates **score** -> **ducking & final edit**.
