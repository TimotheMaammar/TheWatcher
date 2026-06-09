#!/usr/bin/env python3
"""Scraper for recent AI/CS papers on arXiv."""
import requests, re
from config import REQUEST_TIMEOUT, MAX_ITEMS_PER_SOURCE

SOURCE_NAME = "arXiv"
URL = "https://arxiv.org/search/cs?query=artificial+intelligence&searchtype=all&abstracts=show&order=-announced_date_first&size=50"

def fetch():
    resp = requests.get(URL, timeout=REQUEST_TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    blocks = re.findall(r'<li class="arxiv-result">(.*?)</li>', resp.text, re.DOTALL)
    papers = []
    for block in blocks[:MAX_ITEMS_PER_SOURCE]:
        id_m      = re.search(r'href="https://arxiv\.org/abs/([^"]+)"', block)
        title_m   = re.search(r'<p class="title is-5 mathjax">\s*(.*?)\s*</p>', block, re.DOTALL)
        date_m    = re.search(r'<span class="has-text-black-bis has-text-weight-semibold">Submitted</span>\s*([^;.<]+)', block)
        cats      = re.findall(r'data-tooltip="([^"]+)"', block)
        full_abs  = re.search(r'<span class="abstract-full[^"]*"[^>]*>(.*?)</span>', block, re.DOTALL)
        short_abs = re.search(r'<span class="abstract-short[^"]*"[^>]*>(.*?)<a class', block, re.DOTALL)

        # Skip entries without a valid arXiv ID
        if not id_m:
            continue
        arxiv_id = id_m.group(1)

        raw_abs  = full_abs or short_abs
        abstract = ""
        if raw_abs:
            abstract = re.sub(r'<[^>]+>', '', raw_abs.group(1))
            abstract = re.sub(r'&hellip;', '...', abstract)
            abstract = re.sub(r'&[a-z]+;', ' ', abstract)
            abstract = re.sub(r'\s+', ' ', abstract).strip()

        papers.append({
            "title":    re.sub(r'\s+', ' ', title_m.group(1)).strip() if title_m else "N/A",
            "url":      f"https://arxiv.org/abs/{arxiv_id}",
            "date":     date_m.group(1).strip() if date_m else "",
            "tags":     " | ".join(cats) if cats else "",  # pipe-separated for email_builder
            "abstract": abstract,
        })
    return papers
