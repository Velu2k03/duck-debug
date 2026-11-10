#!/usr/bin/env python3
"""Run Duck Debug evaluation sessions (Nov 10, 2026, DATANOVA).

Calls the Gemini API through the registered custom.gemini helper with the
duck's exact system prompt, for 8 real beginner broken programs. Writes
data/eval-sessions.json: language, code, error, error signature, real model
reply, latency, whether the reply named the line. No pasted code is logged
by the app itself; this file is the disclosed evaluation dataset.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

HELPER = "/home/hatch/workspace/custom-connectors/custom.gemini/bin/gemini.py"
MODEL = "gemini-3.1-flash-lite"
OUT = Path(__file__).resolve().parent.parent / "data" / "eval-sessions.json"

SYSTEM_PROMPT = """You are Duck, a friendly rubber-duck debugging companion for beginner programmers.
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
or any meta-commentary before or after the answer."""

SAMPLES = [
    {
        "language": "Python",
        "code": "def calculate_average(scores):\n    total = 0\n    for s in scores:\n        total += s\n    return total / len(scores)\n\nprint(calculate_average([]))",
        "error": "ZeroDivisionError: division by zero",
    },
    {
        "language": "Python",
        "code": "def greet(name):\n    print(\"Hello \" + name)\n\ngreet()",
        "error": "TypeError: greet() missing 1 required positional argument: 'name'",
    },
    {
        "language": "Python",
        "code": "def add(a, b):\n    return a + b\n\nprint(add(2, 3))\nprint(total)",
        "error": "NameError: name 'total' is not defined",
    },
    {
        "language": "JavaScript",
        "code": "const user = undefined;\nconsole.log(user.name);",
        "error": "TypeError: Cannot read properties of undefined (reading 'name')",
    },
    {
        "language": "JavaScript",
        "code": "const numbers = [1, 2, 3];\nconsole.log(numbers.length;",
        "error": "SyntaxError: missing ) after argument list",
    },
    {
        "language": "Java",
        "code": "public class Main {\n    public static void main(String[] args) {\n        String name = null;\n        System.out.println(name.length());\n    }\n}",
        "error": "NullPointerException",
    },
    {
        "language": "C++",
        "code": '#include <iostream>\n\nint main() {\n    cout << "Hello!" << endl;\n    return 0;\n}',
        "error": "error: 'cout' was not declared in this scope",
    },
    {
        "language": "Python",
        "code": "def hello():\nprint(\"hi\")\n\nhello()",
        "error": "IndentationError: unexpected indent",
    },
]


def run_one(sample):
    prompt = (
        f"Language: {sample['language']}\n\nCode:\n{sample['code']}\n\n"
        f"Error message:\n{sample['error']}"
    )
    start = time.monotonic()
    try:
        proc = subprocess.run(
            ["python3", HELPER, "generate", MODEL, prompt, SYSTEM_PROMPT],
            capture_output=True,
            text=True,
            timeout=70,
        )
        latency_ms = int((time.monotonic() - start) * 1000)
        if proc.returncode != 0:
            return {"outcome": "api-error", "latencyMs": latency_ms, "reply": None,
                    "error": proc.stderr.strip()[-300:]}
        text = proc.stdout.strip()
        quack_at = text.find("Quack!")
        if quack_at > 0:
            text = text[quack_at:].strip()
        return {"outcome": "ok", "latencyMs": latency_ms, "reply": text}
    except Exception as exc:  # noqa: BLE001 - record and continue
        return {"outcome": "api-error",
                "latencyMs": int((time.monotonic() - start) * 1000),
                "reply": None, "error": str(exc)[-300:]}


def main():
    sessions = []
    for i, sample in enumerate(SAMPLES, start=1):
        print(f"[{i}/{len(SAMPLES)}] {sample['language']}: {sample['error'][:60]}", flush=True)
        result = run_one(sample)
        entry = {
            "id": f"eval-{i:02d}",
            "ts": "2026-11-10",
            "language": sample["language"],
            "code": sample["code"],
            "error": sample["error"],
            "errorSig": sample["error"].split("\n")[0][:120],
            "hasError": True,
            "outcome": result["outcome"],
            "latencyMs": result["latencyMs"],
            "namedLine": bool(result.get("reply")) and "The line:" in result["reply"],
            "reply": result.get("reply"),
            "source": "eval-2026-11-10",
        }
        sessions.append(entry)
        print(f"    -> {entry['outcome']} in {entry['latencyMs']}ms, named line: {entry['namedLine']}", flush=True)
        if i < len(SAMPLES):
            time.sleep(7)  # free-tier rate discipline (~10 req/min)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(sessions, indent=2))
    ok = sum(1 for s in sessions if s["outcome"] == "ok")
    named = sum(1 for s in sessions if s["namedLine"])
    lat = sorted(s["latencyMs"] for s in sessions if s["outcome"] == "ok")
    print(f"Wrote {OUT}: {ok}/{len(sessions)} ok, {named} named the line, "
          f"median latency {lat[len(lat)//2] if lat else 'n/a'}ms")


if __name__ == "__main__":
    main()
