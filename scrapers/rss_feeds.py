#!/usr/bin/env python3
"""Aggregates multiple RSS newsletter feeds into a single article list."""
import re
import requests
import xml.etree.ElementTree as ET
from config import REQUEST_TIMEOUT, MAX_ITEMS_PER_FEED, RSS_FEEDS

SOURCE_NAME = "Newsletters"

def _parse_feed(name: str, url: str) -> list[dict]:
    resp = requests.get(url, timeout=REQUEST_TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    root = ET.fromstring(resp.content)

    ns    = {"atom": "http://www.w3.org/2005/Atom"}
    items = root.findall(".//item") or root.findall(".//atom:entry", ns)

    articles = []
    for item in items[:MAX_ITEMS_PER_FEED]:
        # Title
        title_el = item.find("title")
        title    = (title_el.text or "").strip() if title_el is not None else "N/A"

        # Link
        link_el   = item.find("link")
        atom_link = item.find("{http://www.w3.org/2005/Atom}link")
        link = ""
        if link_el is not None and link_el.text:
            link = link_el.text.strip()
        elif atom_link is not None:
            link = atom_link.get("href", "")

        # Date — strip leading weekday ("Mon, ") then trim to readable length
        date_el = item.find("pubDate") or item.find("{http://www.w3.org/2005/Atom}published")
        date    = ""
        if date_el is not None and date_el.text:
            date = re.sub(r"^[A-Za-z]{3},\s*", "", date_el.text.strip())[:16].strip()

        # Abstract — strip HTML tags and HTML entities from description
        desc_el  = item.find("description") or item.find("{http://www.w3.org/2005/Atom}summary")
        abstract = ""
        if desc_el is not None and desc_el.text:
            abstract = re.sub(r"<[^>]+>", "", desc_el.text)
            abstract = re.sub(r"&[a-z]+;", " ", abstract)
            abstract = re.sub(r"\s+", " ", abstract).strip()[:500]

        if not title or not link:
            continue

        articles.append({
            "title":    title,
            "url":      link,
            "date":     date,
            "tags":     name,
            "abstract": abstract,
        })
    return articles


def fetch() -> list[dict]:
    all_articles = []
    for name, url in RSS_FEEDS:
        try:
            all_articles.extend(_parse_feed(name, url))
        except Exception as e:
            print(f"    [rss] Error on '{name}': {e}")
    return all_articles
