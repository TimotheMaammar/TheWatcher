#!/usr/bin/env python3
"""Article summarization via Mistral AI, with Gemini as backup."""
import re
import time
from mistralai.client import Mistral
from google import genai
from config import (
    MISTRAL_API_KEY, MISTRAL_MODEL,
    GEMINI_API_KEY, GEMINI_MODEL,
    RETRY_MAX, RETRY_DELAY,
)

_mistral_client    = None
_gemini_client     = None
_mistral_available = True  # Flipped to False for the rest of the run after the first Mistral failure

_last_gemini_call    = 0.0
GEMINI_MIN_INTERVAL  = 4.5  # seconds — free tier allows 15 requests/minute for gemini-3.5-flash-lite

def _throttle_gemini():
    """Proactively space out calls to stay under the free-tier 5 req/min quota."""
    global _last_gemini_call
    elapsed = time.monotonic() - _last_gemini_call
    if elapsed < GEMINI_MIN_INTERVAL:
        time.sleep(GEMINI_MIN_INTERVAL - elapsed)
    _last_gemini_call = time.monotonic()

def _get_mistral_client():
    global _mistral_client
    if _mistral_client is None:
        _mistral_client = Mistral(api_key=MISTRAL_API_KEY)
    return _mistral_client

def _get_gemini_client():
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    return _gemini_client

def _build_prompt(title: str, abstract: str) -> str:
    if not abstract or len(abstract.strip()) < 30:
        return (
            f"In 2-3 sentences, explain what this research work likely contributes, "
            f"based solely on its title: \"{title}\""
        )
    return (
        f"Summarize the following research paper in 2-3 sentences.\n"
        f"Title: {title}\n\n"
        f"Abstract: {abstract[:1200]}"
    )

def _summarize_mistral(prompt: str) -> str | None:
    """Single attempt. Returns the summary, or None if Mistral failed (fall back to Gemini)."""
    try:
        r = _get_mistral_client().chat.complete(
            model=MISTRAL_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return r.choices[0].message.content.strip()
    except Exception as e:
        print(f" ⚠ Mistral failed ({e}) — switching to Gemini for the rest of this run...")
        return None

GEMINI_RETRY_MAX = 4  # Gemini's suggested retryDelay can exceed a minute, so allow more attempts

def _extract_retry_delay(err_str: str) -> int:
    """Parses Google's suggested 'retryDelay': 'Ns' from the error, falls back to exponential backoff."""
    m = re.search(r"'retryDelay': '(\d+)s'", err_str)
    return int(m.group(1)) + 1 if m else RETRY_DELAY

def _summarize_gemini(prompt: str) -> str:
    for attempt in range(1, GEMINI_RETRY_MAX + 1):
        _throttle_gemini()
        try:
            r = _get_gemini_client().models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )
            return r.text.strip()
        except Exception as e:
            err_str = str(e)
            if ("RESOURCE_EXHAUSTED" in err_str or "UNAVAILABLE" in err_str) and attempt < GEMINI_RETRY_MAX:
                delay = _extract_retry_delay(err_str)
                print(f" ⏳ Gemini rate limited — retrying in {delay}s...")
                time.sleep(delay)
            else:
                return f"(summary unavailable: {e})"
    return "(summary unavailable: max retries exceeded)"

def summarize(title: str, abstract: str) -> str:
    """
    Returns a short English summary.
    If no abstract is available, infers from the title alone.
    Tries Mistral first; after its first failure, switches to Gemini
    for the rest of the run instead of retrying Mistral on every article.
    """
    global _mistral_available
    prompt = _build_prompt(title, abstract)

    if _mistral_available:
        result = _summarize_mistral(prompt)
        if result is not None:
            return result
        _mistral_available = False

    return _summarize_gemini(prompt)
