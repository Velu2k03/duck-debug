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

## What's new for DATANOVA (Nov 10, 2026) — Error Insights

**Track:** Generative AI and Responsible AI.

Duck Debug now learns from its own sessions. Every `/api/ask` call logs only
session metadata, never pasted code: language, error signature (first line of
the error), outcome, latency, and whether the reply named the faulty line.
The **Error Insights** page (`/insights.html`, also at `GET /api/insights`)
aggregates it: total sessions, sessions by language, most common errors,
median answer time, and the share of replies that named the line.

**Evaluation, run Nov 10, 2026:** 8 real debug sessions (Python 4,
JavaScript 2, Java 1, C++ 1) run against the Gemini API
(`gemini-3.1-flash-lite`) with the duck's exact system prompt. Results: 8/8
answered OK, 8/8 replies named the faulty line (100%), median answer time
2.3s. The full dataset, with the model's real replies, is in
`data/eval-sessions.json`, produced by `scripts/run-eval.py`. Live sessions
are appended to `data/sessions.jsonl` (git-ignored runtime log).

**Pre-existing work, disclosed:** Duck Debug was built Oct 17, 2026 for the
Devpost "Build With AI: Basics" hackathon (see the demo video above). The
Error Insights logging, aggregation, page, and evaluation above are new work
done Nov 10, 2026 for the DATANOVA 2026 Global Data-thon.

## License

MIT
