#!/usr/bin/env python3
"""Scraper for recent Artificial Intelligence articles on Frontiers."""
import requests, re
from config import REQUEST_TIMEOUT, MAX_ITEMS_PER_SOURCE

SOURCE_NAME = "Frontiers"
URLS = [
    'https://www.frontiersin.org/articles?query="Artificial+Intelligence"&sort=Most+recent',
    'https://www.frontiersin.org/articles?query="Artificial+Intelligence"&sort=Most+recent&page=2',
]

def fetch():
    papers = []
    for url in URLS:
        resp   = requests.get(url, timeout=REQUEST_TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
        blocks = re.findall(r'<article class="CardArticle">.*?</article>', resp.text, re.DOTALL)
        for block in blocks:
            title_m   = re.search(r'<h2 class="CardArticle__title">([^<]+)</h2>', block)
            url_m     = re.search(r'href="([^"]+)"[^>]*class="CardArticle__wrapper"', block)
            date_m    = re.search(r'<p class="CardArticle__date">\s*([^<]+?)\s*</p>', block)
            type_m    = re.search(r'<p class="CardArticle__type">([^<]+)</p>', block)
            journal_m = re.search(r'<div class="CardArticle__journal__name">([^<]+)</div>', block)
            authors   = re.findall(r'<li>([^<]+)</li>', block)
            if not title_m:
                continue
            tag_parts = [t for t in [
                type_m.group(1).strip()    if type_m    else "",
                journal_m.group(1).strip() if journal_m else "",
            ] if t]
            papers.append({
                "title":    title_m.group(1).strip(),
                "url":      url_m.group(1) if url_m else "",
                "date":     date_m.group(1).strip() if date_m else "",
                "tags":     " | ".join(tag_parts),
                "abstract": ", ".join(authors) if authors else "",
            })
        if len(papers) >= MAX_ITEMS_PER_SOURCE:
            break
    return papers[:MAX_ITEMS_PER_SOURCE]
