# Setup guide

How to run your own copy. Expect about an hour the first time.

## 1. Run n8n

```bash
docker run -d --name n8n --restart unless-stopped -p 5678:5678 \
  -e GENERIC_TIMEZONE=Europe/Dublin -e TZ=Europe/Dublin \
  -v n8n_data:/home/node/.n8n n8nio/n8n:latest
```

Open http://localhost:5678 and create your owner account.

## 2. Create the console sheet

Create a Google Sheet with these tabs. Column headers for each are in [`templates/sheet_headers.csv`](../templates/sheet_headers.csv):

`Dashboard`, `JobsData`, `ConnectionLog`, `ContentQueue`, `EngagementQueue`, `Watchlist`, `Feedback`, `AgentMemory`, `Heartbeat`

Copy the sheet ID from its URL (the long part between `/d/` and `/edit`).

## 3. Accounts and keys (all have free tiers)

| Service | Used for | Where |
|---|---|---|
| Google Cloud OAuth client | Sheets, Docs, Drive, Gmail | console.cloud.google.com, enable the 4 APIs |
| Groq | drafting and extraction | console.groq.com |
| Google AI Studio | Gemini for job scoring | aistudio.google.com |
| Slack app (bot token) | approvals and alerts | api.slack.com/apps |
| LinkedIn developer app | publishing approved posts | developer.linkedin.com, "Share on LinkedIn" product |
| Jooble | job search API | jooble.org/api/about |
| Serper | finding posts to comment on | serper.dev |
| SerpAPI (optional) | Google Jobs | serpapi.com |

OAuth redirect URL for Google and LinkedIn: `http://localhost:5678/rest/oauth2-credential/callback`

## 4. Import the workflows

For each file in `workflows/`: n8n, **Create workflow**, then **⋯ > Import from File**. Import into a new, empty workflow each time so node names stay exact (the code refers to nodes by name).

Then in every workflow:
1. Replace each `YOUR_GOOGLE_ID` with your sheet ID, Drive folder ID or CV document ID.
2. Select your credentials on each Google, Slack, Groq, Gemini and LinkedIn node.
3. Point every **Execute Workflow** node at your published Voice Drafter.
4. Set **Settings > Error Workflow** to the Error Alerter.
5. Invite your Slack bot to the approvals channel (`/invite @your-bot`).

## 5. Make it yours

- **Voice Drafter > Build Voice Prompt:** replace `ME`, `MY_FACTS` and `PROJECT_FACTS` with your own true facts. Only numbers listed there may appear in drafts.
- **Job Intake:** edit the Jooble queries, ATS company list and Title Filter for your target roles.
- **Job Matcher:** point it at your own CV document.
- **Watchlist tab:** add your target companies with a priority.

## 6. Test before publishing

Run each workflow once with **Execute workflow**, check the sheet and Slack, then **Publish**. Test the Publisher last: it posts publicly.

## Before you share your own exports

```bash
python tools/sanitize.py workflows/
```

It strips credentials, Google IDs, emails and API keys, and stops if anything still looks secret.
