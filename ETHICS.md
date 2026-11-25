# Ethics, Consent & Licences

## 1. Real-Person Consent & Privacy Record
- **Subject choice:** Fictionalized, stylized family elder (`"Grandmother"` in `"the village"`).
- **Real likeness or voice:** **None.** No real person's face, photograph, or cloned voice is used anywhere in the pipeline. Voiceover is synthetic AI narration only.
- **Approved character reference:** `outputs/keyframes/ref_real_seed1025.png` is an AI-generated fictional composite; no photo of any real person was used as input, and no real person's likeness appears anywhere in the film.
- **Privacy boundary:** No real full names, exact addresses, phone numbers, or private family anecdotes are included in `storyboard.json` or sent to any cloud AI endpoint.

## 2. Public AI Disclosure
- Both 9:16 and 16:9 exports include a 2–3 second end card explicitly stating the film was made with AI.
- Public posts will carry clear AI-generated disclosure labels.

## 3. Model & Asset Licences
*(Populated and verified as each live model ID is confirmed in Stage 1+.)*

| Stage | Provider | Verified Model ID | Licence / Terms | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Script & Translation | Google Gemini | `gemini-3.6-flash` (fallback tested: `3.8` / `3.7` 503, `2.5` 404, `3.5` 60s timeout) | Google Gemini API Terms of Service | Live verified & used 2026-11-25 (`33.9 s`) |
| Narration (TTS) | Google Gemini | `gemini-3.8-flash-tts` | Google Gemini API Terms of Service | Live verified 2026-11-25 |
| Ceiling translation (Afaan Oromo) | Google Gemini | `gemini-3.8-flash` | Google Gemini API Terms of Service | Director consented on 2026-11-25 to sending the locked **fictional** story text; no real family details are added. Scheduled, not yet run. |
| Ceiling narration (Afaan Oromo) | Google Gemini | `gemini-3.8-flash-tts` | Google Gemini API Terms of Service | One long call, split locally; fictional character voice only. Scheduled, not yet run. |
| Keyframes (Production) | Cloudflare Workers AI | `@cf/black-forest-labs/flux-2-klein-4b` | **Apache 2.0** (commercial / public-post safe) | Selected over `flux-2-klein-9b` (which is non-commercial) |
| Keyframes (Experiment only) | Cloudflare Workers AI | `@cf/black-forest-labs/flux-2-klein-9b` / `@cf/black-forest-labs/flux-1-schnell` | `9b`: BFL Non-Commercial Licence; `1-schnell`: Apache 2.0 | `9b` kept strictly for non-public benchmark comparison if tested |
| Video Clips | Kaggle GPU (Wan 2.2 TI2V-5B) | `Wan-AI/Wan2.2-TI2V-5B-Diffusers` | **Apache 2.0** (model card checked on Hugging Face 2026-11-25) | Open weights. Notebook prepared but not run; floor uses local Ken Burns clips derived from the approved fictional stills. No real person appears. |
| Music Score | Kaggle GPU (ACE-Step 1.5) | `ACE-Step/Ace-Step1.5` | **MIT** (commercial-safe, verified on HF repo) | Open weights |

### Afaan Oromo native-speaker check
- The director chose a **family/community member** to check names and places. Their name was deliberately not recorded, to keep private details out of the repo and free endpoints.
- Status on 2026-11-25: **pending**. No Afaan Oromo model call has been made yet, so no quality or consent-to-publish claim is made. If the check is not completed, the alternate film stays a private experiment and is not posted publicly.
