# 🤖 AI Watch

> Automated AI research digest — scrapes top academic and community sources daily, summarizes papers with Mistral AI, and delivers a clean HTML email.

---

## Features

- **7 sources** across research publications and community newsletters
- **AI-powered summaries** via Mistral (optional)
- **Exponential retry** on scraper failures (up to 3 attempts)
- **Beautiful HTML email** with color-coded sections per source
- **Easy configuration** — everything in a single `config.py`
- **Local HTML backup** saved on every run

---

## Sources

### 📄 Research & Publications
| Source | Type |
|---|---|
| [arXiv](https://arxiv.org/list/cs.AI/recent) | CS preprints |
| [Hugging Face Papers](https://huggingface.co/papers) | Daily papers, sorted by upvotes |
| [Frontiers](https://www.frontiersin.org) | Peer-reviewed AI articles |
| [JMLR](https://jmlr.org) | Journal of Machine Learning Research |
| [Google Research Blog](https://research.google/blog/) | Industry research |
| [Meta AI Blog](https://ai.meta.com/blog/) | Industry research |

### 💬 Community & News
| Source | Type |
|---|---|
| [Ahead of AI](https://magazine.sebastianraschka.com) | Newsletter |
| [Import AI](https://importai.substack.com) | Newsletter |
| [The Gradient](https://thegradient.pub) | Newsletter |
| [Interconnects](https://www.interconnects.ai) | Newsletter |
| [Ben's Bites](https://www.bensbites.com) | Newsletter |
| [Last Week in AI](https://lastweekin.ai) | Newsletter |

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure

Copy and edit `config.py`:

```python
MISTRAL_API_KEY = "your_mistral_api_key"

SMTP_HOST = "smtp-relay.brevo.com"
SMTP_PORT = 587
SMTP_USER = "your_brevo_smtp_user"
SMTP_PASS = "your_brevo_smtp_password"
MAIL_FROM = "you@example.com"
MAIL_TO   = "you@example.com"
```

> **SMTP**: the project uses [Brevo](https://www.brevo.com) (free tier: 300 emails/day).  
> **Mistral API**: get your key at [console.mistral.ai](https://console.mistral.ai).

### 3. Run

```bash
# Full run — scrape + summarize + send email
python main.py

# Scrape only, no Mistral summaries (faster)
python main.py --no-summary

# Generate HTML locally, do not send email
python main.py --no-mail

# Both flags combined
python main.py --no-summary --no-mail
```

A `.html` file is always saved locally for inspection.

---

## Project Structure

```
veille_ia/
├── config.py          # All settings (API keys, SMTP, sources, limits)
├── main.py            # Orchestrator
├── summarizer.py      # Mistral AI summarization
├── email_builder.py   # HTML email template
├── requirements.txt
└── scrapers/
    ├── __init__.py
    ├── arxiv.py
    ├── huggingface.py
    ├── frontiers.py
    ├── jmlr.py
    ├── google_research.py
    ├── meta_ai.py
    └── substack.py
```

---

## Configuration Reference

| Variable | Default | Description |
|---|---|---|
| `MAX_ITEMS_PER_SOURCE` | `20` | Max articles per research source |
| `MAX_ITEMS_PER_FEED` | `4` | Max articles per Substack feed |
| `MISTRAL_MODEL` | `mistral-small-latest` | Mistral model used for summaries |
| `REQUEST_TIMEOUT` | `15` | HTTP timeout in seconds |
| `RETRY_MAX` | `3` | Max retry attempts per source |
| `RETRY_DELAY` | `5` | Initial retry delay in seconds (doubles each attempt) |

### Enabling / disabling sources

```python
SOURCES_RESEARCH = {
    "arxiv":           True,   # set to False to skip
    "huggingface":     True,
    "frontiers":       True,
    "jmlr":            True,
    "google_research": True,
    "meta_ai":         True,
}
```

### Adding a Substack feed

```python
SUBSTACK_FEEDS = [
    ("My Newsletter", "https://mynewsletter.substack.com/feed"),
    # ...
]
```

---

## Scheduling (Windows)

Run automatically every morning using Task Scheduler:

```
Program : python
Arguments: C:\path\to\veille_ia\main.py
Start in : C:\path\to\veille_ia\
Trigger  : Daily at 07:00
```

---

## ⚠️ Security Note

`config.py` contains sensitive credentials. **Never commit it to a public repository.**  
Add it to `.gitignore`:

```
config.py
*.html
```
