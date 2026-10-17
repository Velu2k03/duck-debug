---
doc: scope
status: approved
---

# Duck Debug

One line: a friendly rubber-duck debugger web app that explains coding errors in plain language for beginners.

## The Unique Kernel
The duck doesn't just answer, it thinks out loud like a patient mentor: it explains the error in one simple sentence, points at the exact line, and asks one guiding question back, so the beginner learns instead of copy-pasting.

## Who It's For
A first-year coding learner (like a student in their first Python class) who hits a traceback, panics, and pastes it into a chatbot that replies with jargon. Today they get a wall of text they don't understand; the duck gives them one clear sentence and a next step.

## The Core Loop
They open the page, paste their code and the error message, hit "Ask the Duck." The duck replies with a simple explanation, the likely cause, and one guiding question. They fix, re-paste, and the duck celebrates.

## The POC Boundary
In: single page, code + error inputs, duck explanation via Gemini API, conversation history in the session, clean beginner-friendly design.
Out: user accounts, saved history across sessions, multi-language UI, code execution, mobile app.

## Explicitly Cut
- Running the user's code (security + scope).
- Follow-up chat threads (one-shot Q&A per ask; history shown, no branching).
- Dark mode, settings pages, analytics.

## Definition of Done
A stranger can open the page, paste broken Python, get a correct plain-language explanation naming the line and cause, and understand what to try next, all in under a minute, with no setup beyond a Gemini API key.
