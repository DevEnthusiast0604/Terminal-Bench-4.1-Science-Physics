"""One-off check: open a fresh tab in the debug Chrome, load the T-1563 page up to DOMContentLoaded, print the task
view's text, close the tab. Reads no cookies or profile files."""
import sys, time
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    br = pw.chromium.connect_over_cdp("http://127.0.0.1:9224")
    ctx = br.contexts[0]
    page = ctx.new_page()
    t0 = time.time()
    try:
        page.goto("https://queue.supertasker.ai/task/T-1563", wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(6000)
        print("loaded in %.1f s; title: %s" % (time.time() - t0, page.title()))
        mains = page.locator("main")
        for i in range(mains.count()):
            m = mains.nth(i)
            if m.is_visible() and "T-1563" in m.inner_text():
                txt = m.inner_text()
                print(" | ".join(s.strip() for s in txt.splitlines() if s.strip())[:2500])
                break
        else:
            print("no task view; body starts:", page.locator("body").inner_text()[:400].replace("\n", " | "))
    except Exception as e:
        print("failed after %.1f s: %s" % (time.time() - t0, str(e).splitlines()[0]))
    finally:
        page.close()
