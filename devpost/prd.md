---
doc: prd
status: approved
---

# Duck Debug — PRD

## What We're Building
A single-page web app. A beginner pastes code and an error message, clicks "Ask the Duck," and gets a plain-language explanation: what went wrong in one sentence, which line, why it happened, and one guiding question. The duck has a friendly personality and never uses unexplained jargon.

## Core Journey
1. Learner opens the page. Sees the duck, a short tagline, two boxes (code, error), and an "Ask the Duck" button.
2. Learner pastes broken Python code and the traceback, clicks the button.
3. A typing/loading state shows the duck is thinking (under ~10 seconds).
4. The duck's answer appears in a chat-style bubble: one-sentence explanation, the culprit line, the cause, one guiding question, and a suggested fix to try.
5. Past exchanges stay visible above as a scrollable history for the session.
6. If the API key is missing or the call fails, a clear, friendly error tells them exactly what to do.

## Screens
One screen, one page. Header (duck logo + name + tagline). Main area: conversation history (empty state shows a sample question they can click to try). Input area: two textareas (Your code / Error message), language picker (defaults to Python), Ask the Duck button. Footer: tiny "built for Build With AI: Basics" note.

## Look and Feel
Warm and playful, not corporate. Soft yellow/cream background, rounded bubbles, a cute duck illustration (emoji-free, CSS/SVG duck). Big readable text. Beginner-proof: labels say "Paste your code here" not "Source input."

## Behavior Details
- Empty code + clicked button: gentle nudge, "The duck needs some code to look at first."
- Error box optional: if empty, duck explains what the code does and flags suspicious lines.
- Long inputs: capped at ~6000 chars per box with a counter.
- History: kept in memory only, cleared on refresh. "Clear chat" button.
- No API key configured: the input area is replaced by a setup card explaining how to add GEMINI_API_KEY in .env, with a link to Google AI Studio.

## Edge Cases
- API timeout/failure: friendly retry message, never a raw stack trace.
- Non-code pasted: duck still tries, asks what language it is.
- Rate limits: tell them to wait a minute and retry.

## Now / Later
Now: everything above. Later: follow-up questions, more languages UI polish, user accounts, history persistence.

## Acceptance Criteria
- Paste the sample broken code, get an answer naming the right line and cause.
- Missing key shows the setup card, not a crash.
- Page works with no build step: `npm install && npm start`, open localhost:3000.
