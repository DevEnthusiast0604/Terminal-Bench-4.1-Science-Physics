"""Connect to the debug Chrome over CDP with a 60 s limit, do nothing, and disconnect. Run with DEBUG=pw:protocol to
see which reply the connection waits for. Run from the folder root."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    try:
        b = p.chromium.connect_over_cdp("http://127.0.0.1:9224", timeout=60000)
        print("connected:", len(b.contexts), "contexts,", sum(len(c.pages) for c in b.contexts), "pages")
    except Exception as exc:
        print("failed:", str(exc).splitlines()[0])
