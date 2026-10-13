# Build log

What changed, what broke, and what I learned, roughly in order.

## v0.1 Core pipeline
- n8n in Docker on a Windows ARM laptop.
- Job Intake from company job boards (Greenhouse, Lever, Ashby) and Jooble.
- Job Matcher scoring jobs against a Master CV read live from Google Docs.
- Google Sheet console with a Dashboard of live formulas.

## v0.2 Alert emails and Slack
- Gmail label `job-alerts` collects LinkedIn, Indeed, IrishJobs and Jobs.ie alerts.
- LLM extracts jobs from each email as JSON; code verifies titles exist in the email.
- Slack approvals channel and an Error Alerter wired to every workflow.

## v0.3 Voice Drafter
- Three draft variants per request, scored by a rule-based lint, one self-correction retry.
- **Lesson:** reasoning models need a generous token budget and `Reasoning: low`, or they spend the budget thinking and return nothing.

## v0.4 The Brain (chat agent)
- **Bug:** the agent called its drafting tool five times in one request and hit the 8,000 tokens-per-minute limit.
- **Root cause:** the drafting sub-workflow itself was failing on the same model, so the agent kept retrying.
- **Fix:** separate model per job, a tool description that says the result is final, and a hard cap on agent iterations.

## v0.5 Data quality
- **Bug:** every Indeed job had the same dead link. The cleaner cut URLs at `?`, where Indeed keeps the job ID.
  **Fix:** parse the `jk` parameter and rebuild `viewjob?jk=...`; normalise LinkedIn job links by ID.
- **Bug:** every job's description was the email subject line, so scoring was blind.
  **Fix:** extract a real per-job snippet, and require the link to appear in the email.
- **Bug:** "Graduate Mechanical Engineer" passed the role filter.
  **Fix:** one shared Title Filter for every source, with a core-role list and a block list.
- Paced email extraction with Loop + Wait so a burst of alerts does not break the rate limit.
- Rotating Jooble searches: 24 searches covered every 6 hours with fewer API calls.

## v0.6 Honest content
- **Bug:** a draft claimed a report that did not exist and the wrong job title.
- **Fix:** a written list of true project facts in the prompt, a false-claim check in the lint, and posts now require 1 to 2 emoji and 3 to 5 hashtags on the last line.

## v0.7 Content Studio and Publisher with images
- Content Studio keeps two episodes of a build-in-public series ready; rejecting one with a reason triggers a rewrite and logs the reason.
- Publisher looks for `<post_id>.png` in a Drive folder, waits up to 24 hours, then posts text-only; posts over 3,000 characters go back to the Studio automatically.

## v0.8 Outreach and engagement
- Connection Assistant fills free slots with watchlist companies (speculative outreach, 30-day cooldown).
- Engagement Scout searches public LinkedIn posts three times a day and drafts comments for me to review and paste.

## Next
- Move to an always-on Oracle Cloud VM (Docker Compose, n8n behind Caddy with HTTPS).
- Heartbeat workflow to prove the server is alive.
- Track which comment styles get author replies.
