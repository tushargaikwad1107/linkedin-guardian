"""
sanitize.py - make exported n8n workflows safe to publish on GitHub.

What it does to every .json file in a folder:
  1. Removes all "credentials" blocks (n8n credential names and IDs).
  2. Replaces Google Sheet / Doc / Drive folder IDs with placeholders.
  3. Masks email addresses, API keys, bearer tokens and webhook IDs.
  4. Removes pinned test data, instance IDs and version IDs.
  5. Prints a report and refuses to finish if anything still looks secret.

Usage:
    python tools/sanitize.py workflows/

It edits the files in place, so keep your originals somewhere private.
"""
import json
import re
import sys
from pathlib import Path

# Long Google IDs (Sheets, Docs, Drive folders) look like 25-60 chars of [A-Za-z0-9_-]
GOOGLE_ID = re.compile(r"\b1[A-Za-z0-9_-]{24,60}\b")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SECRETS = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}"),          # OpenAI-style keys
    re.compile(r"\bgsk_[A-Za-z0-9]{20,}"),            # Groq keys
    re.compile(r"\bAIza[0-9A-Za-z_-]{30,}"),          # Google API keys
    re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),    # Slack tokens
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|app_key|token|secret)=[A-Za-z0-9_-]{12,}"),
]
ALLOWED_EMAILS = {"noreply@anthropic.com"}
DROP_KEYS = {"credentials", "pinData", "instanceId", "versionId", "id", "webhookId", "meta", "shared", "tags"}


def clean_value(text, report):
    def sub_id(m):
        report.add("google_id")
        return "YOUR_GOOGLE_ID"
    text = GOOGLE_ID.sub(sub_id, text)

    def sub_mail(m):
        if m.group(0) in ALLOWED_EMAILS:
            return m.group(0)
        report.add("email")
        return "you@example.com"
    text = EMAIL.sub(sub_mail, text)

    for rx in SECRETS:
        if rx.search(text):
            report.add("secret")
            text = rx.sub("REDACTED", text)
    return text


def walk(obj, report, top=False):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            # node ids are harmless, but workflow-level ids and credentials are not
            if k in DROP_KEYS and (k != "id" or top):
                report.add(f"removed:{k}")
                continue
            out[k] = walk(v, report)
        return out
    if isinstance(obj, list):
        return [walk(v, report) for v in obj]
    if isinstance(obj, str):
        return clean_value(obj, report)
    return obj


def main(folder):
    files = sorted(Path(folder).glob("*.json"))
    if not files:
        sys.exit(f"No .json files in {folder}")
    leaks = []
    for f in files:
        report = set()
        data = json.loads(f.read_text(encoding="utf-8"))
        data = walk(data, report, top=True)
        text = json.dumps(data, ensure_ascii=False, indent=2)
        f.write_text(text, encoding="utf-8")
        print(f"{f.name:40s} {', '.join(sorted(report)) or 'nothing to clean'}")
        for rx in SECRETS:
            if rx.search(text):
                leaks.append(f.name)
    if leaks:
        sys.exit(f"\nSTOP: something still looks secret in {set(leaks)}. Check by hand before publishing.")
    print("\nDone. Open one file and skim it once before you upload.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "workflows")
