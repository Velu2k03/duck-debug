---
doc: spec
status: approved
---

# Duck Debug — Spec

## Stack
Node.js 20+, Express 5, no frontend framework (vanilla HTML/CSS/JS, one page). Gemini API via direct HTTPS REST call (no SDK, fewer deps). `dotenv` for the API key.

## Components
- `server.js` — Express server. Serves `public/`. One endpoint: `POST /api/ask` {code, error, language} → {reply}. Builds the duck system prompt, calls Gemini, returns the text. Validates input length, handles API errors into friendly messages.
- `public/index.html` — the whole UI: header, history, inputs, setup card.
- `public/style.css` — warm playful styling.
- `public/app.js` — form handling, fetch to /api/ask, renders bubbles, sample-question button, clear chat, char counters.
- `public/duck.svg` — cute duck illustration.

## File Structure
```
duck-debug/
  server.js
  package.json
  .env.example        # GEMINI_API_KEY=your_key_here
  .gitignore
  public/
    index.html
    style.css
    app.js
    duck.svg
  devpost/            # planning docs (learner-profile.md git-ignored)
  README.md
```

## Data Model
No database. In-memory per-session history lives in the browser DOM only. Server is stateless.

## External Services
Google Gemini API (`generativelanguage.googleapis.com`), model `gemini-2.5-flash`. Key from `GEMINI_API_KEY` env var. System prompt forces: one-sentence explanation first, name the line, explain cause simply, one guiding question, suggest a fix, no unexplained jargon, warm tone, under 200 words.

## Failure Modes
- No key: server starts fine; `/api/ask` returns 503 with setup instructions; UI shows setup card.
- Bad key / 4xx: "Your API key didn't work. Check it in Google AI Studio."
- Timeout (>25s): "The duck is thinking too hard. Try again."
- Empty code: 400, "paste some code first."

## Where It Runs and How Someone Tries It
`npm install`, `npm start`, open http://localhost:3000. Needs `GEMINI_API_KEY` in `.env` (see `.env.example`; get a free key at Google AI Studio).

## Decisions and Open Issues
- REST instead of SDK: fewer dependencies, smaller install. Resolved.
- Model choice: gemini-2.5-flash for speed/cost. If unavailable, fall back to gemini-2.0-flash. Open: verify model name at build time.
