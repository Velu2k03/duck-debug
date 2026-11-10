const $ = (id) => document.getElementById(id);
const history = $("history");
const emptyState = $("empty-state");

const SAMPLE_CODE = `def calculate_average(scores):\n    total = 0\n    for s in scores:\n        total += s\n    return total / len(scores)\n\nprint(calculate_average([]))`;
const SAMPLE_ERROR = `ZeroDivisionError: division by zero`;

function addMessage(who, text) {
  emptyState?.remove();
  const div = document.createElement("div");
  div.className = "message " + who;
  const avatar = document.createElement("img");
  avatar.className = "avatar";
  avatar.alt = who === "duck" ? "Duck" : "You";
  avatar.src = who === "duck" ? "duck.svg" : "data:image/svg+xml," + encodeURIComponent(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="42" fill="#8a7a5c"/><circle cx="50" cy="38" r="14" fill="#fff8e7"/><ellipse cx="50" cy="72" rx="20" ry="16" fill="#fff8e7"/></svg>');
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  div.append(avatar, bubble);
  history.append(div);
  history.scrollTop = history.scrollHeight;
  return bubble;
}

function updateCounts() {
  $("code-count").textContent = $("code").value.length;
  $("error-count").textContent = $("error").value.length;
}
$("code").addEventListener("input", updateCounts);
$("error").addEventListener("input", updateCounts);

$("try-sample")?.addEventListener("click", () => {
  $("code").value = SAMPLE_CODE;
  $("error").value = SAMPLE_ERROR;
  updateCounts();
});

// Sample answer: shows a real recorded answer from the Nov 10, 2026
// evaluation (data/eval-sessions.json), so the duck can be tried with no
// API key. It is labeled as a sample, never presented as a live answer.
$("show-sample-answer")?.addEventListener("click", async () => {
  const btn = $("show-sample-answer");
  btn.disabled = true;
  try {
    const res = await fetch("/api/insights");
    const data = await res.json();
    const sample = data.evalSessions && data.evalSessions[0];
    if (!sample || !sample.reply) throw new Error("No sample answer available yet.");
    addMessage("user", "Sample: average of an empty list (Python)");
    addMessage("duck", "Sample answer, recorded Nov 10, 2026:\n\n" + sample.reply);
  } catch (e) {
    addMessage("duck", "Could not load a sample answer. " + e.message);
  } finally {
    btn.disabled = false;
  }
});

$("clear").addEventListener("click", () => {
  history.innerHTML = "";
  history.append(emptyState);
  $("form-error").classList.add("hidden");
});

function showFormError(msg) {
  const el = $("form-error");
  el.textContent = msg;
  el.classList.remove("hidden");
}

$("ask").addEventListener("click", async () => {
  const btn = $("ask");
  const code = $("code").value.trim();
  const error = $("error").value.trim();
  const language = $("language").value;
  $("form-error").classList.add("hidden");

  if (!code) {
    showFormError("The duck needs some code to look at first. Paste your code above!");
    return;
  }

  addMessage("user", code.slice(0, 400) + (code.length > 400 ? "…" : ""));
  const thinking = addMessage("duck", "The duck is thinking…");
  thinking.classList.add("thinking");
  btn.disabled = true;

  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, error, language }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Something went wrong.");
    thinking.classList.remove("thinking");
    thinking.textContent = data.reply;
    if (data.setup) $("setup-card").classList.remove("hidden");
  } catch (e) {
    thinking.classList.remove("thinking");
    thinking.textContent = "Oh no, my beak slipped. " + e.message;
  } finally {
    btn.disabled = false;
    history.scrollTop = history.scrollHeight;
  }
});
