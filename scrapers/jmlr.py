#!/usr/bin/env python3
"""Scraper for the latest papers from the Journal of Machine Learning Research."""
import requests, re
from config import REQUEST_TIMEOUT, MAX_ITEMS_PER_SOURCE

SOURCE_NAME = "JMLR"
BASE_URL = "https://jmlr.org/papers"

def fetch():
    # Step 1: find the latest volume number
    resp = requests.get(BASE_URL, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()

    vol_m = re.search(r'<a href="v(\d+)">', resp.text)
    if not vol_m:
        return []

    volume = vol_m.group(1)

    # Step 2: fetch that volume's paper list
    resp2 = requests.get(f"{BASE_URL}/v{volume}/", timeout=REQUEST_TIMEOUT)
    resp2.raise_for_status()

    papers_raw = re.findall(
        r'<dt>([^<]+)</dt>.*?<a[^>]*href=[\'"]([^\'"]*?\.pdf)[\'"]',
        resp2.text, re.DOTALL
    )
    papers = []
    for title, link in papers_raw[-MAX_ITEMS_PER_SOURCE:]:
        papers.append({
            "title":    title.strip(),
            "url":      f"https://jmlr.org{link}",
            "date":     f"Volume {volume}",
            "tags":     "JMLR",
            "abstract": "",
        })
    return list(reversed(papers))
