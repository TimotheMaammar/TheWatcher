#!/usr/bin/env python3
"""HTML email generation for the AI Watch digest."""
from datetime import date

# ── Source color palette ───────────────────────────────────────────────────────
# Format: "Display name": (background, foreground)
SOURCE_COLORS = {
    "arXiv":               ("#1a1a2e", "#e94560"),
    "Hugging Face Papers": ("#f5a623", "#1a1a1a"),
    "Frontiers":           ("#e8f5e9", "#2e7d32"),
    "JMLR":                ("#e3f2fd", "#1565c0"),
    "Google Research":     ("#fce4ec", "#c62828"),
    "Meta AI":             ("#e0f7fa", "#00695c"),
    "Substack":            ("#fff9f0", "#bf4f0f"),
}

DEFAULT_COLORS = ("#f5f5f5", "#333333")

# ── Styles ─────────────────────────────────────────────────────────────────────
CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', Arial, sans-serif; background: #f0f2f5; color: #222; }
.wrapper { max-width: 800px; margin: 0 auto; padding: 24px 16px; }

.header { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
          border-radius: 12px; padding: 36px 32px; margin-bottom: 28px; text-align: center; }
.header h1 { color: #fff; font-size: 28px; font-weight: 700; letter-spacing: 1px; }
.header .subtitle { color: #b0b8d4; font-size: 14px; margin-top: 8px; }
.header .date-badge { display: inline-block; background: rgba(255,255,255,0.12);
                      color: #e0e6ff; border-radius: 20px; padding: 4px 16px;
                      font-size: 13px; margin-top: 12px; }

.stats-bar { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap;
             margin: 16px 0 24px; }
.stat { background: #fff; border-radius: 8px; padding: 10px 18px; text-align: center;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08); min-width: 100px; }
.stat .val { font-size: 22px; font-weight: 700; color: #3949ab; }
.stat .lbl { font-size: 11px; color: #888; margin-top: 2px; }

.section-title { display: flex; align-items: center; gap: 14px;
                 margin: 32px 0 16px; padding: 14px 18px;
                 background: #fff; border-radius: 10px;
                 box-shadow: 0 1px 4px rgba(0,0,0,0.06);
                 border-left: 5px solid #3949ab; }
.section-emoji { font-size: 28px; }
.section-name  { font-size: 17px; font-weight: 700; color: #1a237e; }
.section-sub   { font-size: 12px; color: #888; margin-top: 2px; }

.source-block { background: #fff; border-radius: 10px; margin-bottom: 24px;
                overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.07); }
.source-header { padding: 14px 20px; }
.source-header h2 { font-size: 16px; font-weight: 700; letter-spacing: 0.5px; }
.source-header .count { font-size: 12px; opacity: 0.75; margin-top: 2px; }

.article { border-top: 1px solid #f0f0f0; padding: 14px 20px; }
.article-num { display: inline-block; width: 24px; height: 24px; border-radius: 50%;
               background: #e8eaf6; color: #3949ab; font-size: 11px; font-weight: 700;
               text-align: center; line-height: 24px; margin-right: 10px; flex-shrink: 0; }
.article-title { font-size: 14px; font-weight: 600; color: #1a237e; text-decoration: none; }
.article-title:hover { text-decoration: underline; }
.article-meta { font-size: 12px; color: #757575; margin: 4px 0 4px 34px; }
.tag { display: inline-block; background: #eeeeee; color: #555; border-radius: 4px;
       padding: 1px 7px; font-size: 11px; margin-right: 4px; }
.summary { font-size: 13px; color: #444; line-height: 1.55; margin: 6px 0 0 34px;
           padding: 8px 12px; background: #f7f8fc; border-left: 3px solid #7986cb;
           border-radius: 0 4px 4px 0; }

.error-block { background: #fff8f8; border: 1px solid #ffcdd2; border-radius: 8px;
               padding: 12px 18px; margin-bottom: 16px; color: #c62828; font-size: 13px; }

.footer { text-align: center; color: #9e9e9e; font-size: 12px; margin-top: 32px; padding: 16px; }
"""

# ── Helpers ────────────────────────────────────────────────────────────────────

def _source_header(name: str, count: int) -> str:
    bg, fg = SOURCE_COLORS.get(name, DEFAULT_COLORS)
    return (
        f'<div class="source-header" style="background:{bg}; color:{fg};">'
        f'<h2>{name}</h2>'
        f'<div class="count">{count} article{"s" if count > 1 else ""}</div>'
        f'</div>'
    )


def _article_card(idx: int, item: dict) -> str:
    title   = item.get("title", "Untitled")
    url     = item.get("url") or "#"
    date_   = item.get("date", "")
    tags    = item.get("tags", "")
    summary = item.get("summary", "")

    tags_html  = "".join(
        f'<span class="tag">{t.strip()}</span>'
        for t in tags.split("|") if t.strip()
    )
    meta_parts = [p for p in [date_, tags_html] if p]
    meta_html  = " &nbsp;·&nbsp; ".join(meta_parts)

    summary_html = f'<div class="summary">{summary}</div>' if summary else ""

    return f"""
    <div class="article">
      <div style="display:flex; align-items:flex-start;">
        <span class="article-num">{idx}</span>
        <div style="flex:1;">
          <a class="article-title" href="{url}">{title}</a>
          <div class="article-meta">{meta_html}</div>
          {summary_html}
        </div>
      </div>
    </div>"""


def _render_sections(sections: list[dict]) -> str:
    html = ""
    for sec in sections:
        items = sec.get("items", [])
        if not items:
            continue
        cards = "".join(_article_card(i + 1, it) for i, it in enumerate(items))
        html += f"""
        <div class="source-block">
          {_source_header(sec["name"], len(items))}
          {cards}
        </div>"""
    return html


def _section_title(emoji: str, title: str, subtitle: str) -> str:
    return f"""
    <div class="section-title">
      <span class="section-emoji">{emoji}</span>
      <div>
        <div class="section-name">{title}</div>
        <div class="section-sub">{subtitle}</div>
      </div>
    </div>"""


# ── Entry point ────────────────────────────────────────────────────────────────

def build_html(sections_research: list[dict], sections_community: list[dict], errors: list[str]) -> str:
    today     = date.today().strftime("%d %B %Y")
    total_art = sum(len(s["items"]) for s in sections_research + sections_community)
    total_src = len(sections_research) + len(sections_community)

    # Section subtitles are built dynamically from active sources
    research_subtitle  = " · ".join(s["name"] for s in sections_research)
    community_subtitle = " · ".join(s["name"] for s in sections_community)

    stats = f"""
    <div class="stats-bar">
      <div class="stat"><div class="val">{total_src}</div><div class="lbl">Sources</div></div>
      <div class="stat"><div class="val">{total_art}</div><div class="lbl">Articles</div></div>
      <div class="stat"><div class="val">{len(sections_research)}</div><div class="lbl">Research</div></div>
      <div class="stat"><div class="val">{len(sections_community)}</div><div class="lbl">Community</div></div>
    </div>"""

    errors_html = "".join(f'<div class="error-block">⚠️ {e}</div>' for e in errors)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Watch — {today}</title>
  <style>{CSS}</style>
</head>
<body>
<div class="wrapper">

  <div class="header">
    <h1>🤖 AI Watch</h1>
    <div class="subtitle">Latest research papers and news in Artificial Intelligence</div>
    <div class="date-badge">📅 {today}</div>
  </div>

  {stats}
  {errors_html}

  {_section_title("📄", "Research and Publications", research_subtitle)}
  {_render_sections(sections_research)}

  {_section_title("💬", "Community and News", community_subtitle)}
  {_render_sections(sections_community)}

  <div class="footer">Auto-generated digest • {today}</div>

</div>
</body>
</html>"""
