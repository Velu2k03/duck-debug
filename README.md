# Duck Debug

Your friendly rubber-duck debugger. Paste broken code and the error message, and the duck explains what went wrong in plain language, no jargon.

Built for the Devpost **Build With AI: Basics** hackathon.

## Try it

1. **Get a free API key** at [Google AI Studio](https://aistudio.google.com/apikey).
2. **Install and configure:**
   ```bash
   npm install
   cp .env.example .env
   # edit .env and paste your key after GEMINI_API_KEY=
   ```
3. **Run it:**
   ```bash
   npm start
   ```
4. Open **http://localhost:3000**, paste some broken code, and hit **Ask the Duck**.

No key? The app tells you exactly how to set one up instead of crashing.

## How it works

- `server.js` — Express server, one endpoint (`POST /api/ask`). Builds a "duck persona" system prompt and calls the Gemini API. Maps API failures (bad key, rate limits, timeouts) into friendly messages.
- `public/` — single-page UI: conversation history, code + error inputs, sample broken program to try, setup card.
- The duck always answers in the same beginner-friendly shape: one-sentence explanation, the culprit line, why it happened, one guiding question, and one fix to try.

## Configuration

| Variable | Default | What it does |
|---|---|---|
| `GEMINI_API_KEY` | (none) | Your free Gemini API key. Required for real answers. |
| `GEMINI_MODEL` | `gemini-3.1-flash-lite` | Model name, if your key needs a different one. |
| `PORT` | `3000` | Port to listen on. |

## Demo video

https://www.youtube.com/watch?v=cuCroIKtxFM

## License

MIT
