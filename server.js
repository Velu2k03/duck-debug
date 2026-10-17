require("dotenv").config();
const express = require("express");
const path = require("path");

const app = express();
const PORT = process.env.PORT || 3000;
const MAX_CHARS = 6000;
const GEMINI_KEY = process.env.GEMINI_API_KEY || "";
const GEMINI_MODEL = process.env.GEMINI_MODEL || "gemini-3.1-flash-lite";
const GEMINI_URL = (model) =>
  `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`;

app.use(express.json({ limit: "1mb" }));
app.use(express.static(path.join(__dirname, "public")));

const SYSTEM_PROMPT = `You are Duck, a friendly rubber-duck debugging companion for beginner programmers.
Explain errors in plain language with zero unexplained jargon. Format every answer exactly like this:

Quack!

In one sentence: (one simple sentence saying what went wrong)
The line: (the line number or snippet causing it)
Why it happens: (2 to 3 simple sentences)
One question for you: (one guiding question that helps them think, not the answer)
Try this: (one concrete fix to attempt)

Rules: warm and encouraging tone, never condescending, whole answer under 200 words,
no markdown tables, no code longer than 6 lines.
CRITICAL: output ONLY the final formatted answer starting with "Quack!".
Never include thinking, analysis, notes to yourself, bullet-point critiques,
or any meta-commentary before or after the answer.`;

const SETUP_MESSAGE =
  "The duck needs a brain first. Add your free Gemini API key: copy .env.example to .env, " +
  "paste your key from Google AI Studio after GEMINI_API_KEY=, then restart with npm start.";

async function askGemini({ code, error, language }) {
  const userPrompt =
    `Language: ${language}\n\nCode:\n${code}\n\n` +
    (error ? `Error message:\n${error}` : "No error message was given. Explain what this code does and flag anything suspicious for a beginner.");

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 25000);
  try {
    const res = await fetch(`${GEMINI_URL(GEMINI_MODEL)}?key=${encodeURIComponent(GEMINI_KEY)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        system_instruction: { parts: [{ text: SYSTEM_PROMPT }] },
        contents: [{ parts: [{ text: userPrompt }] }],
        generationConfig: { maxOutputTokens: 600, temperature: 0.7 },
      }),
      signal: controller.signal,
    });
    if (!res.ok) {
      const err = new Error(`gemini-${res.status}`);
      err.status = res.status;
      throw err;
    }
    const data = await res.json();
    let text = data?.candidates?.[0]?.content?.parts?.map((p) => p.text || "").join("");
    if (!text) throw new Error("gemini-empty");
    text = text.trim();
    // Some models emit deliberation before the answer; the real answer starts at "Quack!".
    const quackAt = text.indexOf("Quack!");
    if (quackAt > 0) text = text.slice(quackAt).trim();
    return text;
  } finally {
    clearTimeout(timer);
  }
}

function friendlyError(err) {
  if (err.name === "AbortError") {
    return "The duck is thinking too hard and timed out. Try again with a shorter snippet.";
  }
  switch (err.status) {
    case 400:
    case 401:
    case 403:
      return "Your API key didn't work. Grab a fresh one at Google AI Studio and check GEMINI_API_KEY in your .env file.";
    case 404:
      return `The model "${GEMINI_MODEL}" isn't available on your key. Set GEMINI_MODEL in .env to a model your key can use (e.g. gemini-3-flash-preview).`;
    case 429:
      return "The duck is quacking too fast (rate limit). Wait a minute and try again.";
    case 503:
      return "The AI is very busy right now. Wait a bit and try again.";
    default:
      return "Oh no, my beak slipped talking to the AI. Try again in a moment.";
  }
}

app.post("/api/ask", async (req, res) => {
  const { code, error, language } = req.body || {};
  if (!code || !String(code).trim()) {
    return res.status(400).json({ error: "The duck needs some code to look at first. Paste your code above!" });
  }
  if (String(code).length > MAX_CHARS || String(error || "").length > MAX_CHARS) {
    return res.status(400).json({ error: `Whoa, that's a lot of code. Keep each box under ${MAX_CHARS} characters.` });
  }
  if (!GEMINI_KEY) {
    return res.status(503).json({ error: SETUP_MESSAGE, setup: true });
  }
  try {
    const reply = await askGemini({ code, error, language: language || "Python" });
    res.json({ reply });
  } catch (err) {
    res.status(502).json({ error: friendlyError(err) });
  }
});

app.get("/api/health", (req, res) => {
  res.json({ ok: true, model: GEMINI_MODEL, keyConfigured: Boolean(GEMINI_KEY) });
});

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Duck Debug waddling on http://localhost:${PORT}`);
  });
}
module.exports = app;
