#!/usr/bin/env python3
"""Build the DATANOVA PPT for Duck Debug (python-pptx, 16:9).

All numbers are real: evaluation results come from data/eval-sessions.json
(8 sessions, Nov 10, 2026). No invented statistics.
"""
import json
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "datanova"
OUT = DOCS / "duck-debug-datanova.pptx"

CREAM = RGBColor(0xFF, 0xF8, 0xE7)
INK = RGBColor(0x2E, 0x2A, 0x1E)
AMBER = RGBColor(0xE8, 0xA1, 0x00)
GREEN = RGBColor(0x2E, 0x7D, 0x32)
SOFT = RGBColor(0x6B, 0x5D, 0x3F)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

prs = Presentation()
prs.slide_width = Inches(13.33)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


def bg(slide, color=CREAM):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def textbox(slide, x, y, w, h, text, size=20, bold=False, color=INK, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.alignment = align
    return box


def bullets(slide, x, y, w, h, items, size=20, gap=14):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    for i, (head, body) in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        p.font.size = Pt(size)
        p.font.color.rgb = INK
        r = p.add_run()
        r.text = "•  " + head
        r.font.bold = True
        r.font.size = Pt(size)
        if body:
            r2 = p.add_run()
            r2.text = " — " + body
            r2.font.size = Pt(size)
    return box


def title_slide(slide, title, subtitle=None):
    textbox(slide, 0.7, 0.5, 12, 0.9, title, size=40, bold=True)
    if subtitle:
        textbox(slide, 0.7, 1.5, 12, 0.6, subtitle, size=22, color=SOFT)
    textbox(slide, 0.7, 6.9, 12, 0.4, "Duck Debug  •  DATANOVA 2026 Global Data-thon",
              size=13, color=SOFT)


def content_slide(title, subtitle, items, size=20):
    s = prs.slides.add_slide(BLANK)
    bg(s)
    title_slide(s, title, subtitle)
    bullets(s, 0.7, 2.3, 11.9, 4.3, items, size=size)
    return s


# 1. Title
s = prs.slides.add_slide(BLANK)
bg(s)
textbox(s, 0.7, 1.1, 12, 1.2, "Duck Debug", size=66, bold=True)
textbox(s, 0.7, 2.4, 12, 0.8, "Your friendly rubber-duck debugger", size=30, color=AMBER)
textbox(s, 0.7, 3.6, 12, 0.6, "DATANOVA 2026 Global Data-thon", size=24, bold=True)
textbox(s, 0.7, 4.3, 12, 0.6, "Track: Generative AI and Responsible AI", size=20, color=SOFT)
textbox(s, 0.7, 5.2, 12, 0.6, "Velu Murugan  •  Solo  •  November 10, 2026", size=18, color=SOFT)
textbox(s, 0.7, 6.9, 12, 0.4, "github.com/Velu2k03/duck-debug", size=13, color=SOFT)

# 2. Problem
content_slide("The problem", "Error messages are written for experts, not beginners.", [
    ("New programmers hit errors in their first week.", "The message names the problem in jargon they have not learned yet."),
    ("The failing line is not obvious.", "A traceback points at the crash, not the cause."),
    ("Most tools hand over an answer.", "A copy-paste fix teaches nothing, so the same error comes back."),
    ("Asking for help feels risky.", "Beginners stay stuck rather than look foolish."),
])

# 3. Solution
content_slide("The solution", "Paste broken code. The duck explains it in plain language.", [
    ("One fixed shape, every time.", "One sentence, the line, why it happens, one guiding question, one fix to try."),
    ("Zero unexplained jargon.", "Under 200 words, warm tone, never condescending."),
    ("It teaches, not just fixes.", "The guiding question makes the learner think, so the error stays fixed."),
    ("Free to start.", "Runs on the free Gemini API tier; no key needed to try a sample answer."),
])

# 4. How it works
content_slide("How it works", "A small web app with one AI call.", [
    ("Browser UI.", "Paste code and the error, pick a language, ask the duck."),
    ("Express server.", "One endpoint builds the duck persona prompt and calls Gemini."),
    ("Gemini API, free tier.", "Model gemini-3.1-flash-lite, structured reply, 25-second timeout."),
    ("Friendly failures.", "Missing key, bad key, rate limit and timeout each get a plain-language fix, not a stack trace."),
    ("Safe by design.", "Answers render as text, inputs are length-checked, pasted code is never stored."),
])

# 5. What's new for DATANOVA
content_slide("What is new for DATANOVA", "Error Insights: the duck learns from its own sessions.", [
    ("Session logging, metadata only.", "Language, error signature, outcome, latency, whether the reply named the line. Pasted code is never logged."),
    ("Insights page and API.", "/insights.html and GET /api/insights aggregate live sessions plus the evaluation set."),
    ("Sample-answer mode.", "Try the duck with no API key: a real recorded answer, labeled as a sample."),
    ("Honest about reuse.", "Duck Debug was built Oct 17, 2026 for Build With AI: Basics. Error Insights is the new work for DATANOVA."),
])

# 6. Evaluation results
s = prs.slides.add_slide(BLANK)
bg(s)
title_slide(s, "Evaluation results", "Eight real debug sessions, run Nov 10, 2026 against the Gemini API.")
bullets(s, 0.7, 2.3, 5.6, 4.3, [
    ("8 of 8 answered OK.", "Every session got a full duck reply."),
    ("8 of 8 named the faulty line.", "100% of replies pointed at the right line."),
    ("Median answer time 2.3s.", "Fastest 1.5s, slowest 30.1s (first-call warm-up)."),
    ("Languages: Python 4, JavaScript 2, Java 1, C++ 1.", "Real errors: ZeroDivisionError, TypeError, NameError, NullPointerException, SyntaxError, IndentationError."),
], size=19)
# crop the stat cards + lists out of the insights screenshot
im = Image.open(DOCS / "insights.png")
crop = im.crop((0, 240, 1280, 700))
crop_path = DOCS / "insights-crop.png"
crop.save(crop_path)
s.shapes.add_picture(str(crop_path), Inches(6.7), Inches(2.3), width=Inches(5.9))

# 7. Demo
s = prs.slides.add_slide(BLANK)
bg(s)
title_slide(s, "Try it", "Live demo, repository, and video.")
s.shapes.add_picture(str(DOCS / "home.png"), Inches(0.7), Inches(2.3), width=Inches(7.0))
bullets(s, 8.5, 2.3, 4.1, 4.3, [
    ("Repository.", "github.com/Velu2k03/duck-debug (MIT)."),
    ("Demo video.", "youtube.com/watch?v=cuCroIKtxFM, plus a new 31-second DATANOVA clip."),
    ("Live demo.", "Deploying to Vercel; link goes on the Devpost form once the deploy lands."),
    ("Insights.", "Live at /insights.html on the demo."),
], size=18)

# 8. Tech stack + responsible AI
content_slide("Tech stack and responsible AI", "Small, free-tier, and honest about data.", [
    ("Node.js + Express 5.", "One server file, one endpoint, static frontend."),
    ("Gemini API, free tier.", "No paid services anywhere in the project."),
    ("Open source, MIT.", "Anyone can read, run, and improve it."),
    ("Privacy first.", "Pasted code is never logged or stored; only session metadata is counted."),
    ("Beginner-safe by design.", "Plain language, no jargon, encouragement over condescension."),
])

# 9. Impact and next steps
content_slide("Impact and next steps", "Who it helps, and what comes next.", [
    ("Beginners and students.", "A patient explainer that is always available, in plain language."),
    ("Teachers and bootcamps.", "The Insights page shows which errors a class hits most."),
    ("Next: more languages.", "Go, Rust, and SQL error patterns."),
    ("Next: a bigger evaluation.", "100 sessions with a second judge checking the named line."),
    ("Next: classroom mode.", "Shared class dashboards from the same metadata log."),
])

# 10. Links
s = prs.slides.add_slide(BLANK)
bg(s)
textbox(s, 0.7, 1.1, 12, 1.2, "Thank you", size=66, bold=True)
bullets(s, 0.7, 2.6, 11.9, 4.0, [
    ("Repository.", "github.com/Velu2k03/duck-debug"),
    ("Demo video.", "youtube.com/watch?v=cuCroIKtxFM"),
    ("Contact.", "velu2k03@gmail.com  •  drvelu.com"),
], size=22)

prs.save(str(OUT))
print("saved", OUT)
