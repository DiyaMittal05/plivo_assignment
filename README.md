# InspireWorks IVR Demo (Plivo Voice API)

A demo IVR that places an outbound call with Plivo, authenticates the caller with
a 4-digit OTP (birthdate in DDMM format, hardcoded in `app.py` as `2108`), then runs a two-level IVR menu
(language selection, then play audio or forward to a live associate).
Built with Python + Flask, and all call control uses Plivo XML.

## Call flow

```
Web UI / CLI ──> POST /make-call ──> Plivo API (calls.create) ──> rings your phone
                                                                    │ answer
/answer           "Enter your 4 digit OTP" (GetInput, DTMF, 4 digits)
/verify-otp       wrong/empty → "Incorrect, try again" → back to /answer (loops)
                  correct     → /language-menu
/language-menu    Level 1: "1 English / 2 Español"   invalid → repeat
/action-menu      Level 2 (in chosen language):      invalid → repeat
                    1 → <Play> public MP3 → back to Level 2 menu
                    2 → <Dial> associate number (call forwarding)
```

No input (timeout) on any menu repeats that menu. The chosen language travels in
the URL (`?lang=en|es`), so no database or session is needed.

## Project structure

| File | Purpose |
|---|---|
| `app.py` | Flask server: outbound call trigger + all Plivo XML endpoints |
| `make_call.py` | CLI to trigger the call |
| `ivr_texts.py` | English / Spanish prompts |
| `templates/index.html` | Simple web page with a "Call me" button |
| `.env.example` | Configuration template |

## Required Plivo credentials

From the [Plivo Console](https://console.plivo.com/):

- **Auth ID** and **Auth Token** (Console → Overview)
- A **Plivo phone number** with voice enabled (Console → Phone Numbers)

> **Trial accounts:** Plivo trial accounts can only call verified numbers. Add
> your phone and the associate number under **Phone Numbers → Sandbox Numbers**
> before testing.

## Setup

**Prerequisites:** Python 3.8+ and [ngrok](https://ngrok.com/download).

```bash
cd plivo_assignment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and fill in:

| Variable | Description |
|---|---|
| `PLIVO_AUTH_ID` / `PLIVO_AUTH_TOKEN` | Your Plivo credentials |
| `PLIVO_FROM_NUMBER` | Your Plivo number, E.164 (e.g. `+14155551234`) |
| `TARGET_NUMBER` | Phone to call (your number) |
| `ASSOCIATE_NUMBER` | Number to forward to for "live associate" |
| `BASE_URL` | Your public ngrok URL (step 2 below) |
| `AUDIO_URL` | Public MP3 (default: Plivo sample audio) |

## Run

1. **Start ngrok** (terminal 1):
   ```bash
   ngrok http 5050
   ```
   Copy the `https://....ngrok-free.app` URL into `BASE_URL` in `.env`.

2. **Start the server** (terminal 2):
   ```bash
   source venv/bin/activate
   python app.py
   ```

3. **Trigger the call**, using either:
   - Web UI: open http://localhost:5050, enter the number, click **Call me**
   - CLI: `python make_call.py` (uses `TARGET_NUMBER`) or `python make_call.py +919876543210`

## Test steps

1. Answer the call and you'll hear the OTP prompt.
2. Enter a **wrong** 4-digit code. You hear "incorrect" and are prompted again.
3. Enter the **correct** OTP (`2108`). You hear "authenticated" and the language menu plays.
4. Press **1** (English) or **2** (Spanish).
5. Press **1** to hear the audio message (you're returned to the menu afterwards).
6. Press **2** to be forwarded to the associate number.
7. Optional: press an invalid key (e.g. 9) at any menu. That menu repeats.

The server logs each keypress (OTP, language and action) in the terminal.
