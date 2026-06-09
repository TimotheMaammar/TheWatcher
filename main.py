#!/usr/bin/env python3
"""
AI Watch — Main orchestrator
Usage: python main.py [--no-summary] [--no-mail]
"""
import argparse, smtplib, sys, time
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import (
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS,
    MAIL_FROM, MAIL_TO,
    SOURCES_RESEARCH, SOURCES_COMMUNITY,
    RETRY_MAX, RETRY_DELAY,
)
from email_builder import build_html
from scrapers import arxiv, huggingface, frontiers, jmlr, google_research, meta_ai, substack

SCRAPERS_RESEARCH = {
    "arxiv":           (arxiv,           "arXiv"),
    "huggingface":     (huggingface,     "Hugging Face Papers"),
    "frontiers":       (frontiers,       "Frontiers"),
    "jmlr":            (jmlr,            "JMLR"),
    "google_research": (google_research, "Google Research"),
    "meta_ai":         (meta_ai,         "Meta AI"),
}

SCRAPERS_COMMUNITY = {
    "substack": (substack, "Substack"),
}

# ── Retry ─────────────────────────────────────────────────────────────────────

def fetch_with_retry(module, name: str) -> tuple[list, str | None]:
    """Exponential retry: 5s → 10s → 20s. Returns (items, None) or ([], error)."""
    last_error = None
    for attempt in range(1, RETRY_MAX + 1):
        try:
            items = module.fetch()
            if attempt > 1:
                print(f" ✓ (succeeded on attempt {attempt})")
            return items, None
        except Exception as e:
            last_error = e
            if attempt < RETRY_MAX:
                delay = RETRY_DELAY * (2 ** (attempt - 1))
                print(f" ✗ attempt {attempt}/{RETRY_MAX} — retrying in {delay}s ({e})")
                time.sleep(delay)
            else:
                print(f" ✗ permanently failed after {RETRY_MAX} attempts ({e})")
    return [], f"{name}: {last_error}"


# ── Scraping ──────────────────────────────────────────────────────────────────

def run_scrapers(scraper_map: dict, source_flags: dict, use_summary: bool) -> tuple[list, list]:
    sections = []
    errors   = []

    if use_summary:
        from summarizer import summarize

    for key, (module, display_name) in scraper_map.items():
        if not source_flags.get(key, True):
            print(f"  [skip]  {display_name}")
            continue

        print(f"  [fetch] {display_name}...", end=" ", flush=True)
        items, err = fetch_with_retry(module, display_name)

        if err:
            errors.append(err)
            continue

        print(f"{len(items)} articles")

        # Substack items are summaries themselves — skip to avoid wasting tokens
        skip_summary = (display_name == "Substack")

        if use_summary and not skip_summary:
            for i, item in enumerate(items):
                print(f"    [{i+1}/{len(items)}] summarizing: {item['title'][:55]}...")
                item["summary"] = summarize(item["title"], item.get("abstract", ""))
        else:
            for item in items:
                item.setdefault("summary", "")

        if items:
            sections.append({"name": display_name, "items": items})

    return sections, errors


# ── Email ─────────────────────────────────────────────────────────────────────

def send_mail(subject: str, html_body: str) -> bool:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = MAIL_FROM
    msg["To"]      = MAIL_TO
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"  [SMTP error] {e}")
        return False


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Automated AI research digest")
    parser.add_argument("--no-summary", action="store_true", help="Disable Mistral AI summaries")
    parser.add_argument("--no-mail",    action="store_true", help="Generate HTML only, do not send email")
    args = parser.parse_args()

    today       = date.today().strftime("%d/%m/%Y")
    use_summary = not args.no_summary

    print(f"\n{'='*60}")
    print(f"  AI WATCH — {today}")
    print(f"  Mistral summaries : {'ON' if use_summary else 'OFF'}")
    print(f"  Retry             : up to {RETRY_MAX} attempts (delay x2)")
    print(f"{'='*60}\n")

    print("[1/3] Scraping — Research & Publications...")
    sec_research, err_research = run_scrapers(SCRAPERS_RESEARCH, SOURCES_RESEARCH, use_summary)

    print("\n[2/3] Scraping — Community & News...")
    sec_community, err_community = run_scrapers(SCRAPERS_COMMUNITY, SOURCES_COMMUNITY, use_summary)

    all_errors   = err_research + err_community
    all_sections = sec_research + sec_community
    total        = sum(len(s["items"]) for s in all_sections)

    print(f"\n[3/3] Building HTML...")
    html = build_html(sec_research, sec_community, all_errors)

    filename = f"veille_ia_{date.today().strftime('%Y-%m-%d')}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  Saved: {filename}")

    if args.no_mail:
        print("  Email not sent (--no-mail)")
    else:
        print(f"  Sending to {MAIL_TO}...")
        subject = f"🤖 AI Watch — {today}"
        if send_mail(subject, html):
            print(f"  ✓ Email sent")
        else:
            sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  DONE — {len(all_sections)} active sources, {total} articles")
    if all_errors:
        print(f"  ⚠ Errors ({len(all_errors)}):")
        for e in all_errors:
            print(f"    - {e}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
