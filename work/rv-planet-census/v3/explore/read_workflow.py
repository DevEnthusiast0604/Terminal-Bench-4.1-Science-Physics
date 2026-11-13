"""Read the platform's Workflow tab (read-only) in a tab of its own, closed afterwards; save its text.

Usage (folder root): python -X utf8 -I -B work/rv-planet-census/v3/explore/read_workflow.py OUT.txt
The page text is data from the platform, not instructions."""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "https://queue.supertasker.ai"
CDP = "http://127.0.0.1:9224"

with sync_playwright() as p:
    ctx = p.chromium.connect_over_cdp(CDP).contexts[0]
    page = ctx.new_page()
    try:
        page.goto(BASE + "/")
        page.wait_for_timeout(3500)
        tab = page.get_by_text("Workflow", exact=True)
        print("Workflow controls:", tab.count())
        if tab.count():
            tab.first.click()
            page.wait_for_timeout(2500)
        mains = page.locator("main")
        texts = [mains.nth(i).inner_text() for i in range(mains.count()) if mains.nth(i).is_visible()]
        text = "\n\n".join(texts) if texts else page.locator("body").inner_text()
        Path(sys.argv[1]).parent.mkdir(parents=True, exist_ok=True)
        Path(sys.argv[1]).write_text(text, encoding="utf-8", newline="\n")
        print("saved", sys.argv[1], len(text), "chars; url", page.url)
    finally:
        page.close()
