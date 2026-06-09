#!/usr/bin/env python3
"""Article summarization via Mistral AI."""
import time
from mistralai.client import Mistral
from config import MISTRAL_API_KEY, MISTRAL_MODEL, RETRY_MAX, RETRY_DELAY

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = Mistral(api_key=MISTRAL_API_KEY)
    return _client

def summarize(title: str, abstract: str) -> str:
    """
    Returns a short English summary.
    If no abstract is available, infers from the title alone.
    """
    if not abstract or len(abstract.strip()) < 30:
        prompt = (
            f"In 2-3 sentences, explain what this research work likely contributes, "
            f"based solely on its title: \"{title}\""
        )
    else:
        prompt = (
            f"Summarize the following research paper in 2-3 sentences.\n"
            f"Title: {title}\n\n"
            f"Abstract: {abstract[:1200]}"
        )
    for attempt in range(1, RETRY_MAX + 1):
        try:
            r = _get_client().chat.complete(
                model=MISTRAL_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            return r.choices[0].message.content.strip()
        except Exception as e:
            err_str = str(e)
            # Retry only on rate limit (429), fail immediately on other errors
            if "429" in err_str and attempt < RETRY_MAX:
                delay = RETRY_DELAY * (2 ** (attempt - 1))
                print(f" ⏳ rate limited — retrying in {delay}s...")
                time.sleep(delay)
            else:
                return f"(summary unavailable: {e})"
    return "(summary unavailable: max retries exceeded)"
