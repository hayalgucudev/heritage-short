# Ethics, Consent & Licences

## 1. Real-Person Consent & Privacy Record

- **2026-11-26, director consent recorded:** the director uploaded a photograph of a **jebena** and explicitly approved sending that one image to the existing Cloudflare FLUX endpoint as an image-conditioning input for `shot_07`. No new service receives it; no `.env` value is printed. **I cannot view images**, so the director confirmed on 2026-11-26 that the photo contains **no real person's face — the jebena object only**. The photo was then sent to FLUX for `shot_07` seed `1074` (latency 33,875 ms). No new service received it and no `.env` value was printed.
- **Subject choice:** Fictionalized, stylized family elder (`"Grandmother"` in `"the village"`).
- **Real likeness or voice:** **None.** No real person's face, photograph, or cloned voice is used anywhere in the pipeline. Voiceover is synthetic AI narration only.
- **Approved character reference:** `outputs/keyframes/ref_real_seed1025.png` is an AI-generated fictional composite; no photo of any real person was used as input, and no real person's likeness appears anywhere in the film.
- **Privacy boundary:** No real full names, exact addresses, phone numbers, or private family anecdotes are included in `storyboard.json` or sent to any cloud AI endpoint.

## 2. Public AI Disclosure
- Both 9:16 and 16:9 exports include a 2–3 second end card explicitly stating the film was made with AI.
- Public posts will carry clear AI-generated disclosure labels.

## 3. Model & Asset Licences
*(Verified model IDs and licence terms as actually used in this repo; updated 2026-11-26.)*

| Stage | Provider | Verified Model ID | Licence / Terms | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Script & Translation | Google Gemini | `gemini-3.6-flash` (fallback tested: `3.8` / `3.7` 503, `2.5` 404, `3.5` 60s timeout) | Google Gemini API Terms of Service | Live verified & used 2026-11-25 (`33.9 s`) |
| Narration (TTS) | Google Gemini | `gemini-3.8-flash-tts` | Google Gemini API Terms of Service | Live verified 2026-11-25 |
| Ceiling translation (Afaan Oromo) | Google Gemini | `gemini-3.8-flash` | Google Gemini API Terms of Service | Director consented on 2026-11-25 to sending the locked **fictional** story text; no real family details are added. **Four translation calls failed on 2026-11-26; ceiling CLOSED AS FAILED. No translation was produced.** |
| Ceiling narration (Afaan Oromo) | Google Gemini | `gemini-3.8-flash-tts` | Google Gemini API Terms of Service | One long call, split locally; fictional character voice only. **Never reached: no TTS call was made and no `_om` film exists.** |
| Keyframes (Production) | Cloudflare Workers AI | `@cf/black-forest-labs/flux-2-klein-4b` | **Apache 2.0** (commercial / public-post safe) | Selected over `flux-2-klein-9b` (which is non-commercial) |
| Keyframes (Experiment only) | Cloudflare Workers AI | `@cf/black-forest-labs/flux-2-klein-9b` / `@cf/black-forest-labs/flux-1-schnell` | `9b`: BFL Non-Commercial Licence; `1-schnell`: Apache 2.0 | `9b` kept strictly for non-public benchmark comparison if tested |
| Video Clips | Kaggle GPU (Wan 2.2 TI2V-5B) | `Wan-AI/Wan2.2-TI2V-5B-Diffusers` | **Apache 2.0** (model card checked on Hugging Face 2026-11-25) | Open weights. Notebook prepared but not run; floor uses local Ken Burns clips derived from the approved fictional stills. No real person appears. |
| Music Score | Kaggle GPU (ACE-Step 1.5) | `ACE-Step/Ace-Step1.5` | **MIT** (commercial-safe, verified on HF repo) | Open weights |

### Afaan Oromo native-speaker check
- The director chose a **family/community member** to check names and places. Their name was deliberately not recorded, to keep private details out of the repo and free endpoints.
- Status on 2026-11-26: **MOOT — ceiling closed as failed.** Four translation calls failed before any TTS call; no Afaan Oromo translation, voice or film exists, and no quality or consent-to-publish claim is made. The director ruled the native-speaker check moot; no Oromo variant will be published.
