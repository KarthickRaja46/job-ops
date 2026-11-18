"""First check of every run: confirm each saved session is logged in as me.

Usage: python3 scripts/check_login.py
Prints one JSON line: {"linkedin": "OK"|"BLOCKED: ...", "upwork": ...}
"""
import os

from common import emit, is_blocked, open_context, sync_playwright

LINKEDIN_NAME = os.environ.get("LINKEDIN_EXPECTED_NAME", "Karthick Raja L")
UPWORK_NAME = os.environ.get("UPWORK_EXPECTED_NAME", "Karthick")
BLOCKED = "BLOCKED: needs fresh state file"


def check_linkedin(p):
    browser, ctx = open_context(p, "linkedin")
    if ctx is None:
        return BLOCKED + " (no state found)"
    try:
        page = ctx.new_page()
        page.goto("https://www.linkedin.com/in/me/", wait_until="domcontentloaded", timeout=45000)
        # LinkedIn keeps polling, so never wait for "networkidle": wait for the name heading instead.
        heading = page.get_by_role("heading", name=LINKEDIN_NAME, exact=True)
        try:
            heading.first.wait_for(timeout=30000)
        except Exception:
            pass
        if is_blocked(page) or "login" in page.url or "authwall" in page.url:
            return BLOCKED + " (LinkedIn sent the session to login/authwall)"
        if heading.count() > 0:
            return "OK"
        return f"{BLOCKED} (profile name not found; url={page.url.split('?')[0]})"
    except Exception as e:
        return f"{BLOCKED} ({type(e).__name__})"
    finally:
        browser.close()


def check_upwork(p):
    browser, ctx = open_context(p, "upwork")
    if ctx is None:
        return BLOCKED + " (no state found)"
    try:
        page = ctx.new_page()
        page.goto("https://www.upwork.com/nx/find-work/", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(4000)
        if is_blocked(page):
            return BLOCKED
        text = page.locator("body").inner_text(timeout=10000)
        return "OK" if UPWORK_NAME.lower() in text.lower() else f"{BLOCKED} (account name not found)"
    except Exception as e:
        return f"{BLOCKED} ({type(e).__name__})"
    finally:
        browser.close()


if __name__ == "__main__":
    with sync_playwright() as p:
        emit({"linkedin": check_linkedin(p), "upwork": check_upwork(p)})
