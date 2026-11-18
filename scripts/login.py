"""One-time (or when expired) manual login into the saved browser profile.

Usage: python scripts/login.py linkedin   (or upwork)
A browser window opens; log in yourself, then press Enter in the terminal.
"""
import sys

from common import close, open_context, profile_dir, sync_playwright

URLS = {
    "linkedin": "https://www.linkedin.com/login",
    "upwork": "https://www.upwork.com/ab/account-security/login",
}

if __name__ == "__main__":
    site = sys.argv[1] if len(sys.argv) > 1 else ""
    if site not in URLS:
        sys.exit("Usage: python scripts/login.py linkedin|upwork")
    with sync_playwright() as p:
        ctx = open_context(p, site, headless=False, require_login=False)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(URLS[site])
        input(f"Log in to {site} in the browser window (finish any 2FA), then press Enter here...")
        close(ctx)
    print(f"Saved {site} login in {profile_dir(site)}")
