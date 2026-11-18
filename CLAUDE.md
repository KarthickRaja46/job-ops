# job-ops — LinkedIn + Upwork runs (cloud session)

Runs on my own PC (Windows), not in the cloud: LinkedIn cancels logins that are moved to cloud servers.
No Claude in Chrome. Use Python Playwright scripts.

## Login
- Each site uses a saved browser profile in `profiles/<site>/`, created by me with
  `python scripts/login.py linkedin` (or `upwork`). Every run reuses that same profile, and no user agent is faked.
  Never commit, print or log login data (`.gitignore` covers `profiles/` and `*_state.json`).
- Locale en-US, timezone Asia/Dubai (see `scripts/common.py`). The window is visible by default; `JOBOPS_HEADLESS=1` hides it.
- Start every run with `python scripts/check_login.py`. A site that is not `OK` is
  "BLOCKED: needs fresh login". Skip it, carry on with the other one, and never retry a login automatically.

## Method
- Work through scripts in `scripts/*.py` run with Bash. They print compact JSON only (title, company, link, status).
  Never put full page HTML into the chat. Fix and reuse scripts rather than rewriting them.
- Run long raw page text through Headroom before reading it.

## Trackers (check both before acting; never duplicate)
- `tracker/linkedin.csv`: date,type(apply/message/follow-up/comment/post),company,role_or_person,link,status,next_action,next_date
- `tracker/upwork.csv`: date,type(proposal/message/follow-up),client,job,link,rate_bid,connects_used,status,next_action,next_date

## Daily limits
- LinkedIn: ≤10 Easy Apply, ≤10 messages/follow-ups, ≤3 comments, ≤1 post/week; wait a random 40–120 s between actions.
- Upwork: ≤3 proposals/day, ≤30 Connects/week; only jobs that match my skills, from payment-verified clients.
- Follow-ups: 5 days after no reply, at most 2 per person.

## Rules
- LinkedIn and Upwork only. No other job sites, no email.
- Fill forms only from MY DETAILS. If anything else is needed, skip and log `needs answer: <question>`.
- Never invent experience, certificates or salary. Never accept offers, sign contracts, start paid work or
  change account settings: log these as `waiting on me`.
- Comments and posts: short and specific to the post, no generic praise.

## End of run
- `graphify` over `tracker/` and `notes/` → `graphify-out/`; commit and push `tracker/ notes/ scripts/ graphify-out/`.
- Final line, exactly:
  `LinkedIn: applied X / messaged X / commented X | Upwork: proposals X / connects X | blocked: ... | waiting on me: ...`

## MY DETAILS
TODO: paste the MY DETAILS block here. Until it's filled in, skip every form.
