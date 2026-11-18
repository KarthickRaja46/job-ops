"""Shared helpers: load saved login state and open a browser context.

Login state comes from an uploaded file (linkedin_state.json / upwork_state.json)
or from $LINKEDIN_STATE_B64 / $UPWORK_STATE_B64, decoded into /tmp with mode 600.
Its contents are never printed or logged.
"""
import base64
import json
import os
import random
import stat
import sys
import time
from pathlib import Path

if Path("/opt/pw-browsers").is_dir():  # cloud container; on a PC Playwright's default path is used
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")

from playwright.sync_api import sync_playwright  # noqa: E402

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
SEARCH_DIRS = [Path.cwd(), Path(__file__).resolve().parent.parent, Path("/tmp"), Path.home()]


def state_path(site: str) -> Path | None:
    """Return a path to the site's storage-state file, or None if unavailable."""
    name = f"{site}_state.json"
    for d in SEARCH_DIRS:
        p = d / name
        if p.is_file():
            return p
    b64 = os.environ.get(f"{site.upper()}_STATE_B64", "").strip()
    if not b64:
        return None
    out = Path("/tmp") / name
    try:
        data = base64.b64decode(b64)
        json.loads(data)  # validate without echoing anything
    except Exception:
        return None
    out.write_bytes(data)
    out.chmod(stat.S_IRUSR | stat.S_IWUSR)
    return out


def open_context(p, site: str):
    sp = state_path(site)
    if sp is None:
        return None, None
    browser = p.chromium.launch()
    ctx = browser.new_context(storage_state=str(sp), user_agent=UA, locale="en-US",
                              timezone_id="Asia/Dubai", viewport={"width": 1366, "height": 850})
    return browser, ctx


BLOCK_MARKERS = ("/login", "/checkpoint", "/authwall", "/uas/", "account-security", "captcha", "/challenge")


def is_blocked(page) -> bool:
    url = page.url.lower()
    if any(m in url for m in BLOCK_MARKERS):
        return True
    try:
        return page.locator("iframe[src*='captcha'], iframe[src*='challenges.cloudflare'], #captcha").count() > 0
    except Exception:
        return False


def human_pause(lo: int = 40, hi: int = 120):
    time.sleep(random.uniform(lo, hi))


def emit(obj):
    """Print compact JSON only."""
    sys.stdout.write(json.dumps(obj, separators=(",", ":")) + "\n")


__all__ = ["sync_playwright", "open_context", "is_blocked", "human_pause", "emit", "state_path"]
