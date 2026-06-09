#!/usr/bin/env python3
"""Scraper for Meta AI blog posts."""
import requests, re
from config import REQUEST_TIMEOUT, MAX_ITEMS_PER_SOURCE

SOURCE_NAME = "Meta AI"
URL = "https://ai.meta.com/blog/"

def fetch():
    resp = requests.get(URL, timeout=REQUEST_TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    html = resp.text

    papers = []
    seen   = set()

    # Structure: <a href="https://ai.meta.com/blog/slug/"><h2>Title</h2><p>Date</p></a>
    for m in re.finditer(
        r'<a\s[^>]*href="(https://ai\.meta\.com/blog/[a-z0-9][^"]+)"[^>]*>(.*?)</a>',
        html, re.DOTALL
    ):
        url   = m.group(1).rstrip('/')
        inner = m.group(2)

        title_m = re.search(r'<h[2-4][^>]*>(.*?)</h[2-4]>', inner, re.DOTALL)
        if not title_m:
            continue
        title = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', title_m.group(1))).strip()

        if url in seen or len(title) < 8:
            continue
        seen.add(url)

        # Date pattern covers both "April 8, 2026" and "Apr 8, 2026"
        date_m = re.search(
            r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
            r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
            r'\s+\d{1,2},?\s+\d{4}',
            inner
        )

        papers.append({
            "title":    title,
            "url":      url,
            "date":     date_m.group(0) if date_m else "",
            "tags":     "Meta AI",
            "abstract": "",
        })
        if len(papers) >= MAX_ITEMS_PER_SOURCE:
            break

    return papers
