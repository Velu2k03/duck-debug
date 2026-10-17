---
doc: checklist
status: approved
mode: fast
---

# Duck Debug — Build Checklist

## Slices

- [ ] **1. Server, page shell, and duck UI with canned reply** · Becomes usable: the page loads, you can paste code and get a canned duck answer back. · Why now: proves the full request loop end to end before touching the AI API (risk-first: the API is the unknown). · PRD ref: Core Journey 1-4, Screens, Look and Feel · Spec ref: Components (server.js, public/*), File Structure · Build: Express server with GET / and POST /api/ask returning a canned duck JSON; full single-page UI (header, history, inputs, sample question, clear chat, char counters); warm styling; duck SVG. · Verify (mechanical): `npm install && npm start`, curl `/` returns HTML, POST /api/ask with sample code returns the canned reply JSON. · Learner check: open localhost:3000, paste the sample broken code, click Ask the Duck, see the canned answer appear. · Commit: "Slice 1: server + duck UI with canned reply"

- [ ] **2. Real Gemini integration** · Becomes usable: the duck gives real AI explanations of your actual code. · Why now: the unique kernel, the AI duck, comes early per plan. · PRD ref: Core Journey 3-4, Behavior Details · Spec ref: External Services, Failure Modes · Build: server builds the duck system prompt, calls Gemini REST API with GEMINI_API_KEY, returns text; friendly error mapping for missing/bad key, timeouts. · Verify (mechanical): POST /api/ask with the sample broken Python returns an explanation naming the right line; POST with no key configured returns the setup message. · Learner check: ask about a real bug of yours and check the duck names the line and cause correctly. · Commit: "Slice 2: real Gemini-powered duck replies"

- [ ] **3. Polish, error states, README** · Becomes usable: a stranger can set it up and use it with no help. · Why now: last mile for the Definition of Done. · PRD ref: Behavior Details, Edge Cases, Acceptance Criteria · Spec ref: Where It Runs and How Someone Tries It · Build: no-key setup card UI, empty-input nudge, loading state, .env.example, README with setup steps and screenshots note, .gitignore audit. · Verify (mechanical): fresh clone simulation, `npm install && npm start` works; /api/ask with empty code returns 400 nudge; README lists all submission requirements. · Learner check: read the README and follow it exactly as a stranger would. · Commit: "Slice 3: polish, error states, README"

## Hands-on Checkpoints
- [ ] After slice 2: try a real bug, confirm the duck's answer quality.

## Final Review
- [ ] Kick the tires: awkward inputs (empty, huge paste, non-code), missing key, bad key.
- [ ] Revisions: (none yet)

## Code Tour and App Map
- [ ] Pending build completion.

## Revisions
- (none yet)
