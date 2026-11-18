"""Shared helpers: open a logged-in browser for a site.

On a PC (recommended): a persistent browser profile in profiles/<site>/, created once
with `python scripts/login.py <site>`. Every run reuses that same browser, so the
site always sees one consistent device. No user agent is faked.

In a cloud container: falls back to <site>_state.json or $<SITE>_STATE_B64
(decoded to /tmp, mode 600). Note: LinkedIn rejects logins moved to cloud servers.

Login data is never printed or logged, and profiles/ and *_state.json are gitignored.
"""
import base64
import json
import os
import random
import stat
import sys
import time
from pathlib import Path

CLOUD = Path("/opt/pw-browsers").is_dir()
if CLOUD:
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")

from playwright.sync_api import sync_playwright  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
PROFILES = REPO / "profiles"
# On a PC show the window by default (looks like normal use); set JOBOPS_HEADLESS=1 to hide it.
HEADLESS = os.environ.get("JOBOPS_HEADLESS", "1" if CLOUD else "0") == "1"
CTX_OPTS = dict(locale="en-US", timezone_id="Asia/Dubai", viewport={"width": 1366, "height": 850})
SEARCH_DIRS = [Path.cwd(), REPO, Path("/tmp"), Path.home()]


def profile_dir(site: str) -> Path:
    return PROFILES / site


def state_path(site: str) -> Path | None:
    name = f"{site}_state.json"
    for d in SEARCH_DIRS:
        p = d / name
        if p.is_file():
            return p
    b64 = os.environ.get(f"{site.upper()}_STATE_B64", "").strip()
    if not b64:
        return None
    try:
        data = base64.b64decode(b64)
        json.loads(data)  # validate without echoing anything
    except Exception:
        return None
    out = Path("/tmp") / name
    out.write_bytes(data)
    out.chmod(stat.S_IRUSR | stat.S_IWUSR)
    return out


def open_context(p, site: str, headless: bool | None = None, require_login: bool = True):
    """Return a browser context for `site`, or None if no login exists. Close it with close()."""
    headless = HEADLESS if headless is None else headless
    prof = profile_dir(site)
    if prof.is_dir() or not require_login:
        prof.mkdir(parents=True, exist_ok=True)
        return p.chromium.launch_persistent_context(str(prof), headless=headless, **CTX_OPTS)
    sp = state_path(site)
    if sp is None:
        return None
    browser = p.chromium.launch(headless=headless)
    return browser.new_context(storage_state=str(sp), **CTX_OPTS)


def close(ctx):
    browser = ctx.browser
    ctx.close()
    if browser is not None:
        browser.close()


BLOCK_MARKERS = ("/login", "/checkpoint", "/authwall", "/uas/", "account-security", "captcha", "/challenge")


def is_blocked(page) -> bool:
    url = page.url.lower().split("?")[0]
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
