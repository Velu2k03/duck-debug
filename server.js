require("dotenv").config();
const express = require("express");
const fs = require("fs");
const path = require("path");

const app = express();
const PORT = process.env.PORT || 3000;
const MAX_CHARS = 6000;
const GEMINI_KEY = process.env.GEMINI_API_KEY || "";
const GEMINI_MODEL = process.env.GEMINI_MODEL || "gemini-3.1-flash-lite";
const GEMINI_URL = (model) =>
  `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`;

// Error Insights (added Nov 10, 2026 for DATANOVA): the app logs only
// session metadata, never pasted code. The bundled data/eval-sessions.json
// holds real evaluation sessions run Nov 10, 2026; data/sessions.jsonl holds
// live sessions logged at runtime. Both feed GET /api/insights.
const DATA_DIR = path.join(__dirname, "data");
const SESSIONS_FILE = path.join(DATA_DIR, "sessions.jsonl");
const EVAL_FILE = path.join(DATA_DIR, "eval-sessions.json");

function errorSignature(error) {
  const first = String(error || "").split("\n")[0].trim();
  return first.slice(0, 120);
}

function logSession(entry) {
  try {
    fs.mkdirSync(DATA_DIR, { recursive: true });
    fs.appendFileSync(SESSIONS_FILE, JSON.stringify(entry) + "\n");
  } catch (_) {
    // Logging must never break the API (serverless filesystems are read-only).
  }
}

function loadSessions() {
  let sessions = [];
  try {
    const evalSessions = JSON.parse(fs.readFileSync(EVAL_FILE, "utf8"));
    if (Array.isArray(evalSessions)) sessions = sessions.concat(evalSessions);
  } catch (_) {}
  try {
    const lines = fs.readFileSync(SESSIONS_FILE, "utf8").split("\n").filter(Boolean);
    for (const line of lines) {
      try { sessions.push(JSON.parse(line)); } catch (_) {}
    }
  } catch (_) {}
  return sessions;
}

function summarizeInsights(sessions) {
  const byLanguage = {};
  const errorCounts = {};
  const outcomes = {};
  const latencies = [];
  let namedLine = 0;
  let okCount = 0;
  for (const s of sessions) {
    byLanguage[s.language || "Unknown"] = (byLanguage[s.language || "Unknown"] || 0) + 1;
    if (s.errorSig) errorCounts[s.errorSig] = (errorCounts[s.errorSig] || 0) + 1;
    outcomes[s.outcome || "unknown"] = (outcomes[s.outcome || "unknown"] || 0) + 1;
    if (s.outcome === "ok") {
      okCount += 1;
      if (typeof s.latencyMs === "number") latencies.push(s.latencyMs);
      if (s.namedLine) namedLine += 1;
    }
  }
  latencies.sort((a, b) => a - b);
  const medianLatencyMs = latencies.length
    ? latencies[Math.floor(latencies.length / 2)]
    : null;
  const topErrors = Object.entries(errorCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([error, count]) => ({ error, count }));
  return {
    totalSessions: sessions.length,
    okSessions: okCount,
    pctNamedLine: okCount ? Math.round((namedLine / okCount) * 100) : null,
    medianLatencyMs,
    byLanguage,
    topErrors,
    outcomes,
  };
}

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
  const started = Date.now();
  const { code, error, language } = req.body || {};
  const lang = language || "Python";
  const record = (outcome, replyText) => {
    logSession({
      ts: new Date().toISOString(),
      language: lang,
      errorSig: errorSignature(error),
      hasError: Boolean(String(error || "").trim()),
      outcome,
      latencyMs: Date.now() - started,
      namedLine: typeof replyText === "string" && replyText.includes("The line:"),
      source: "live",
    });
  };
  if (!code || !String(code).trim()) {
    record("invalid");
    return res.status(400).json({ error: "The duck needs some code to look at first. Paste your code above!" });
  }
  if (String(code).length > MAX_CHARS || String(error || "").length > MAX_CHARS) {
    record("invalid");
    return res.status(400).json({ error: `Whoa, that's a lot of code. Keep each box under ${MAX_CHARS} characters.` });
  }
  if (!GEMINI_KEY) {
    record("no-key");
    return res.status(503).json({ error: SETUP_MESSAGE, setup: true });
  }
  try {
    const reply = await askGemini({ code, error, language: lang });
    record("ok", reply);
    res.json({ reply });
  } catch (err) {
    record("api-error");
    res.status(502).json({ error: friendlyError(err) });
  }
});

app.get("/api/insights", (req, res) => {
  const sessions = loadSessions();
  const evalSessions = sessions.filter((s) => s.source === "eval-2026-11-10");
  res.json({
    summary: summarizeInsights(sessions),
    evalSessions: evalSessions.map((s) => ({
      language: s.language,
      errorSig: s.errorSig,
      outcome: s.outcome,
      latencyMs: s.latencyMs,
      namedLine: s.namedLine,
      reply: s.reply || null,
    })),
    note: "Insights count session metadata only. Pasted code is never logged or stored.",
  });
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
