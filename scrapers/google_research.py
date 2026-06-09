#!/usr/bin/env python3
"""Scraper for Google Research blog posts."""
import requests, re
from config import REQUEST_TIMEOUT, MAX_ITEMS_PER_SOURCE

SOURCE_NAME = "Google Research"
URL = "https://research.google/blog/"

def fetch():
    resp = requests.get(URL, timeout=REQUEST_TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    html = resp.text

    papers = []
    seen   = set()

    # Pattern 1: <a href="/blog/slug/"> blocks containing a heading
    for href, inner in re.findall(
        r'<a\s[^>]*href="(/blog/[a-z0-9][a-z0-9\-]+/)"[^>]*>(.*?)</a>',
        html, re.DOTALL
    ):
        title_m = re.search(r'<h[2-4][^>]*>(.*?)</h[2-4]>', inner, re.DOTALL)
        if title_m:
            title = re.sub(r'<[^>]+>', '', title_m.group(1))
        else:
            # Fall back to raw text inside the anchor
            title = re.sub(r'<[^>]+>', ' ', inner)
        title = re.sub(r'\s+', ' ', title).strip()

        if not title or href in seen or len(title) < 10:
            continue
        seen.add(href)

        # Look for a date near this link in the surrounding HTML
        pos    = html.find(href)
        nearby = html[max(0, pos - 300):pos + 800]
        date_m = re.search(
            r'(?:January|February|March|April|May|June|July|August|'
            r'September|October|November|December)\s+\d{1,2},?\s+\d{4}',
            nearby
        )

        papers.append({
            "title":    title,
            "url":      f"https://research.google{href}",
            "date":     date_m.group(0) if date_m else "",
            "tags":     "Google Research",
            "abstract": "",
        })
        if len(papers) >= MAX_ITEMS_PER_SOURCE:
            break

    # Pattern 2 (fallback): headings that directly contain a /blog/ link
    if not papers:
        for m in re.finditer(r'<h[2-4][^>]*>(.*?)</h[2-4]>', html, re.DOTALL):
            inner  = m.group(1)
            link_m = re.search(r'href="(/blog/[^"]+)"', inner)
            if not link_m:
                continue
            href  = link_m.group(1)
            title = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', inner)).strip()
            if href in seen or len(title) < 10:
                continue
            seen.add(href)
            papers.append({
                "title":    title,
                "url":      f"https://research.google{href}",
                "date":     "",
                "tags":     "Google Research",
                "abstract": "",
            })
            if len(papers) >= MAX_ITEMS_PER_SOURCE:
                break

    return papers
