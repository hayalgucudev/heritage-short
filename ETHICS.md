# Ethics, Consent & Licences

## 1. Real-Person Consent & Privacy Record
- **Subject choice:** Fictionalized, stylized family elder (`"Grandmother"` in `"the village"`).
- **Real likeness or voice:** **None.** No real person's face, photograph, or cloned voice is used anywhere in the pipeline. Voiceover is synthetic AI narration only.
- **Privacy boundary:** No real full names, exact addresses, phone numbers, or private family anecdotes are included in `storyboard.json` or sent to any cloud AI endpoint.

## 2. Public AI Disclosure
- Both 9:16 and 16:9 exports include a 2–3 second end card explicitly stating the film was made with AI.
- Public posts will carry clear AI-generated disclosure labels.

## 3. Model & Asset Licences
*(Populated and verified as each live model ID is confirmed in Stage 1+.)*

| Stage | Provider | Verified Model ID | Licence / Terms | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Script & Translation | Google Gemini | `gemini-3.8-flash` | Gemini API Terms | Live verified 2026-11-25 (`gemini-3.8-flash-lite` not listed; `gemini-3.5-flash-lite` available) |
| Narration (TTS) | Google Gemini | `gemini-3.8-flash-tts` | Gemini API Terms | Live verified 2026-11-25 (`gemini-3.8-flash-lite-tts` also live) |
| Keyframes | Cloudflare Workers AI | `@cf/black-forest-labs/flux-2-klein-9b` / `@cf/black-forest-labs/flux-1-schnell` | Cloudflare Workers AI / Black Forest Labs Terms | Live verified 2026-11-25 (`flux-2-klein-4b` and `flux-2-dev` also live) |
| Video Clips | Kaggle GPU (Wan 2.2 TI2V-5B) | Wan 2.2 TI2V-5B | Apache 2.0 (verify at run) | Open weights |
| Music Score | Kaggle GPU (ACE-Step 1.5) | ACE-Step 1.5 | Verify repo licence at run | Open weights |
