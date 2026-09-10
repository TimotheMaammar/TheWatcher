#!/usr/bin/env python3
"""Central configuration — edit only this file."""

# ── API ───────────────────────────────────────────────────────────────────────
MISTRAL_API_KEY = "XXXXX"
GEMINI_API_KEY  = "XXXXX"

# ── SMTP (Brevo) ──────────────────────────────────────────────────────────────
SMTP_HOST  = "smtp-relay.brevo.com"
SMTP_PORT  = 587
SMTP_USER  = "xxxxx@smtp-brevo.com"   # Brevo SMTP login
SMTP_PASS  = "XXXXX"            # Brevo SMTP password
MAIL_FROM  = "XXXXX@domain.com"  # Sender address (must match Brevo sender)
MAIL_TO    = "XXXXX@domain.com"

# ── Scraping ──────────────────────────────────────────────────────────────────
MAX_ITEMS_PER_SOURCE = 20   # Max articles per research source
MAX_ITEMS_PER_FEED   = 4    # Max articles per Substack feed
MISTRAL_MODEL        = "mistral-small-latest"
GEMINI_MODEL         = "gemini-3.5-flash-lite"  # Backup summarizer, used if Mistral fails
REQUEST_TIMEOUT      = 15   # seconds

# ── Retry ─────────────────────────────────────────────────────────────────────
RETRY_MAX   = 3   # Max attempts per source
RETRY_DELAY = 5   # Initial delay in seconds (doubled each attempt)

# ── Sources — Research & Publications ─────────────────────────────────────────
SOURCES_RESEARCH = {
    "arxiv":           True,
    "huggingface":     True,
    "frontiers":       True,
    "jmlr":            True,
    "google_research": True,
    "meta_ai":         True,
}

# ── Sources — Community & News ────────────────────────────────────────────────
SOURCES_COMMUNITY = {
    "substack": True,
}

# ── Substack — RSS feeds to follow ────────────────────────────────────────────
# Format: ("Display name", "RSS feed URL")
RSS_FEEDS = [
    ("Ahead of AI",     "https://magazine.sebastianraschka.com/feed"),
    ("Import AI",       "https://importai.substack.com/feed"),
    ("The Gradient",    "https://thegradient.pub/rss/"),
    ("Interconnects",   "https://www.interconnects.ai/feed"),
    ("Ben's Bites",     "https://www.bensbites.com/feed"),
    ("Last Week in AI", "https://lastweekin.ai/feed"),
]
