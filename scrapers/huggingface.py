#!/usr/bin/env python3
"""Scraper for Hugging Face daily papers, sorted by upvotes."""
import requests, json, re
from config import REQUEST_TIMEOUT, MAX_ITEMS_PER_SOURCE

SOURCE_NAME = "Hugging Face Papers"
URL = "https://huggingface.co/papers"

def fetch():
    resp = requests.get(URL, timeout=REQUEST_TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()

    # Papers are embedded as JSON in a data attribute
    match = re.search(r'data-target="DailyPapers"\s+data-props="([^"]+)"', resp.text)
    if not match:
        return []

    raw     = match.group(1).replace("&quot;", '"').replace("&amp;", "&").replace("&#39;", "'")
    data    = json.loads(raw)
    entries = data.get("dailyPapers", [])
    entries.sort(key=lambda e: e.get("paper", {}).get("upvotes", 0), reverse=True)

    papers = []
    for entry in entries[:MAX_ITEMS_PER_SOURCE]:
        paper    = entry.get("paper", {})
        arxiv_id = paper.get("id", "")
        papers.append({
            "title":    paper.get("title") or entry.get("title", "N/A"),
            "url":      f"https://huggingface.co/papers/{arxiv_id}" if arxiv_id else "",
            "date":     paper.get("publishedAt", "")[:10],
            "tags":     f"{paper.get('upvotes', 0)} upvotes",
            "abstract": paper.get("summary") or entry.get("summary", ""),
        })
    return papers
