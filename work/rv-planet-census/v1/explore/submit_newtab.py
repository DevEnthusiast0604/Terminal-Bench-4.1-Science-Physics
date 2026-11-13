"""Run tools/supertasker.py's submit in a tab of its own.

cmd_submit takes the first platform tab it finds, which can be the tab a running poller reloads every few minutes
(another session's poller watches T-1383). Handing it a context whose page list is empty makes it open a new tab;
the tab is closed afterwards. Usage: submit_newtab.py ZIP DAS-ID"""
import importlib.util
import sys

from playwright.sync_api import sync_playwright

spec = importlib.util.spec_from_file_location("supertasker", "tools/supertasker.py")
st = importlib.util.module_from_spec(spec)
spec.loader.exec_module(st)


class FreshTab:
    def __init__(self, ctx):
        self.ctx = ctx
        self.opened = []

    @property
    def pages(self):
        return []

    def new_page(self):
        pg = self.ctx.new_page()
        self.opened.append(pg)
        return pg


with sync_playwright() as p:
    ctx = p.chromium.connect_over_cdp(st.CDP).contexts[0]
    fresh = FreshTab(ctx)
    try:
        st.cmd_submit(fresh, sys.argv[1], sys.argv[2])
    finally:
        for pg in fresh.opened:
            print("tab left at", pg.url)
            pg.close()
