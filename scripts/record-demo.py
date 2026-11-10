#!/usr/bin/env python3
"""Record a ~60s demo clip of Duck Debug for DATANOVA (optional video).

Shows the home page, a real recorded sample answer, and the Error Insights
page. No API key is used; the sample answer is labeled as a sample.
"""
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "datanova"
OUT.mkdir(parents=True, exist_ok=True)


def wait_ready(url, timeout=20):
    for _ in range(timeout * 2):
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def main():
    server = subprocess.Popen(
        ["node", "server.js"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env={"PATH": "/usr/bin:/bin:/usr/local/bin", "PORT": "3000"},
    )
    try:
        if not wait_ready("http://localhost:3000/api/health"):
            print("server did not start", file=sys.stderr)
            sys.exit(1)
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            ctx = browser.new_context(
                viewport={"width": 1280, "height": 800},
                record_video_dir=str(OUT),
                record_video_size={"width": 1280, "height": 800},
            )
            page = ctx.new_page()
            page.goto("http://localhost:3000/", wait_until="networkidle")
            page.wait_for_timeout(2500)
            page.click("#show-sample-answer")
            page.wait_for_timeout(3500)
            page.evaluate("document.querySelector('#history').scrollTop = 99999")
            page.wait_for_timeout(6000)
            page.goto("http://localhost:3000/insights.html", wait_until="networkidle")
            page.wait_for_timeout(2500)
            page.evaluate("window.scrollTo(0, 600)")
            page.wait_for_timeout(4000)
            page.evaluate("window.scrollTo(0, 1400)")
            page.wait_for_timeout(4000)
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(2000)
            video_path = page.video.path()
            ctx.close()
            browser.close()
            print("video:", video_path)
    finally:
        server.terminate()
        server.wait(timeout=5)


if __name__ == "__main__":
    main()
