"""First check of every run: confirm each saved login is me.

Usage: python scripts/check_login.py
Prints one JSON line: {"linkedin": "OK"|"BLOCKED: ...", "upwork": ...}
"""
import os

from common import close, emit, is_blocked, open_context, sync_playwright

LINKEDIN_NAME = os.environ.get("LINKEDIN_EXPECTED_NAME", "Karthick Raja L")
UPWORK_NAME = os.environ.get("UPWORK_EXPECTED_NAME", "Karthick")
BLOCKED = "BLOCKED: needs fresh login (python scripts/login.py {site})"


def _url(page):
    return page.url.split("?")[0]


def check_linkedin(p):
    blocked = BLOCKED.format(site="linkedin")
    ctx = open_context(p, "linkedin")
    if ctx is None:
        return blocked + " (no login saved)"
    try:
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto("https://www.linkedin.com/in/me/", wait_until="domcontentloaded", timeout=45000)
        # LinkedIn keeps polling, so never wait for "networkidle": wait for the name heading instead.
        heading = page.get_by_role("heading", name=LINKEDIN_NAME, exact=True)
        try:
            heading.first.wait_for(timeout=30000)
        except Exception:
            pass
        if heading.count() > 0:
            return "OK"
        if is_blocked(page):
            return f"{blocked} (sent to {_url(page)})"
        return f"{blocked} (profile name not found at {_url(page)})"
    except Exception as e:
        return f"{blocked} ({type(e).__name__})"
    finally:
        close(ctx)


def check_upwork(p):
    blocked = BLOCKED.format(site="upwork")
    ctx = open_context(p, "upwork")
    if ctx is None:
        return blocked + " (no login saved)"
    try:
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto("https://www.upwork.com/nx/find-work/", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(5000)
        if is_blocked(page):
            return f"{blocked} (sent to {_url(page)})"
        text = page.locator("body").inner_text(timeout=10000)
        return "OK" if UPWORK_NAME.lower() in text.lower() else f"{blocked} (account name not found)"
    except Exception as e:
        return f"{blocked} ({type(e).__name__})"
    finally:
        close(ctx)


if __name__ == "__main__":
    with sync_playwright() as p:
        emit({"linkedin": check_linkedin(p), "upwork": check_upwork(p)})
