#!/usr/bin/env python3
"""Screenshot Duck Debug home + insights pages for the DATANOVA PPT."""
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
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.goto("http://localhost:3000/", wait_until="networkidle")
            page.screenshot(path=str(OUT / "home.png"))
            print("home.png")
            page.goto("http://localhost:3000/insights.html", wait_until="networkidle")
            page.wait_for_timeout(800)
            page.screenshot(path=str(OUT / "insights.png"), full_page=True)
            print("insights.png")
            browser.close()
    finally:
        server.terminate()
        server.wait(timeout=5)


if __name__ == "__main__":
    main()
