# Design decisions

Short records of the choices that shaped LinkedIn Guardian, and why.

## 1. A human approves everything that reaches another person
**Decision:** The agent drafts; I send. No workflow has a tool that can message, connect or comment on LinkedIn. The Publisher posts only rows with status `Approved`.
**Why:** My name is on every message. Automated outreach also risks the account I am job hunting with. Approval costs me seconds per item.

## 2. Code checks the model, not the other way round
**Decision:** Every draft passes a deterministic lint (plain JavaScript, no LLM) before I see it.
**Checks:** length limits, banned AI phrasing, em and en dashes, hashtag and emoji rules per message type, a false-claim list, and an *unverified number* guard: any number not present in the written fact list or the input context is flagged.
**Why:** LLMs produce confident, plausible, wrong details. A rule engine is cheap, predictable and testable.

## 3. Read alert emails, do not scrape
**Decision:** Job sites already email me matching jobs. A Gmail label collects them; the agent extracts jobs from the email text.
**Why:** Reliable, free and within each site's terms. Extraction is guarded: a job is kept only if its title and link literally appear in the email.

## 4. One model per job on free tiers
**Decision:** The chat agent, the drafter, the email extractor and the matcher each use a different model.
**Why:** Free-tier limits are per model (Groq: 8,000 tokens per minute). Sharing one model made unrelated workflows fail each other. Groq also counts `max_tokens` against the limit, so token budgets are set per task.

## 5. Pace with Loop + Wait instead of paying
**Decision:** Anything that calls a model several times processes one item at a time with a Wait between calls (40 to 60 seconds).
**Why:** Keeps every call under the per-minute limit. Nobody is waiting on these jobs, so slower is fine.

## 6. Google Sheets is the database and the console
**Decision:** All state lives in one Google Sheet with a formula-only Dashboard tab.
**Why:** I can read, edit, approve and reject from my phone. Dedupe reads the sheet, so a failed run never loses data.

## 7. Feedback is data
**Decision:** Rejecting a post with a written reason triggers a rewrite that includes the reason, and the reason is stored in a Feedback tab that later drafts read.
**Why:** The agent should get closer to my voice over time without me rewriting prompts.

## 8. Images wait, then fall back
**Decision:** An approved post waits up to 24 hours for a screenshot named `<post_id>.png` in a Drive folder, then posts text-only.
**Why:** Real screenshots of the work beat generic AI images, but a missing image must never block the queue forever.

## 9. Speculative outreach from a watchlist
**Decision:** When fewer than two strong job matches exist, one slot goes to a target company from my watchlist (priority order, 30-day cooldown per company).
**Why:** Many roles are never advertised. Outreach should not depend only on what job boards show.
