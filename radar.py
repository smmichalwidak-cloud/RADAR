#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RADAR — automat zbierający materiały do biuletynu o marketingu hotelowym.
Uruchamiany przez GitHub Actions (pon/śr/pt). Efekt: plik digest/RRRR-MM-DD.md
z nowymi materiałami z feedów RSS, posortowanymi wg trafności słów kluczowych.
Jeśli w sekretach repo jest ANTHROPIC_API_KEY, na końcu digestu pojawia się
sekcja "Propozycje tematów" wygenerowana przez Claude.
"""

import feedparser
import yaml
import json
import os
import re
import html
import hashlib
import datetime
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
FEEDS_FILE = os.path.join(BASE, "feeds.yml")
KEYWORDS_FILE = os.path.join(BASE, "keywords.yml")
SEEN_FILE = os.path.join(BASE, "seen.json")
DIGEST_DIR = os.path.join(BASE, "digest")

WINDOW_DAYS = 4          # okno świeżości wpisów (nakładka bezpieczeństwa przy rytmie co 2-3 dni)
SEEN_RETENTION_DAYS = 60 # jak długo pamiętamy widziane wpisy
MAX_SUMMARY_CHARS = 320  # długość zajawki w digeście
CLAUDE_MODEL = "claude-sonnet-4-6"


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def entry_id(entry) -> str:
    raw = entry.get("id") or entry.get("link") or entry.get("title", "")
    return hashlib.sha256(raw.encode("utf-8", "ignore")).hexdigest()[:16]


def entry_date(entry):
    for key in ("published_parsed", "updated_parsed"):
        t = entry.get(key)
        if t:
            return datetime.datetime(*t[:6], tzinfo=datetime.timezone.utc)
    return None


def score_text(text: str, keywords: dict) -> int:
    low = text.lower()
    return sum(w for kw, w in keywords.items() if kw.lower() in low)


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def claude_topics(items):
    """Opcjonalna selekcja tematów przez Claude API. Zwraca markdown albo None."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key or not items:
        return None
    lines = [
        f"- [{it['category']}] {it['title']} — {it['summary'][:200]} ({it['link']})"
        for it in items[:60]
    ]
    prompt = (
        "Jesteś redaktorem polskiego biuletynu o marketingu hotelowym (nowoczesnym i tradycyjnym), "
        "pisanego przez praktyka dla dyrektorów marketingu hoteli w Polsce. "
        "Oto nowe materiały z monitoringu branżowego:\n\n" + "\n".join(lines) +
        "\n\nWybierz maksymalnie 5 najlepszych kandydatów na temat artykułu lub wzmiankę w biuletynie. "
        "Dla każdego podaj: tytuł roboczy po polsku, 1-2 zdania dlaczego to dobry temat dla polskiego hotelarza, "
        "oraz link źródłowy. Priorytet: tematy praktyczne, dane i liczby, rynek niemiecki (DE), marketing offline. "
        "Pomiń newsy czysto inwestycyjne i personalne. Odpowiedz zwięźle w markdown, bez wstępu."
    )
    body = json.dumps({
        "model": CLAUDE_MODEL,
        "max_tokens": 1200,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text").strip() or None
    except Exception as e:  # brak klucza/limit/sieć — digest ma powstać mimo wszystko
        return f"_(Selekcja Claude niedostępna: {e})_"


def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    cutoff = now - datetime.timedelta(days=WINDOW_DAYS)

    with open(FEEDS_FILE, "r", encoding="utf-8") as f:
        feeds_cfg = yaml.safe_load(f) or {}
    keywords = (yaml.safe_load(open(KEYWORDS_FILE, encoding="utf-8")) or {}) if os.path.exists(KEYWORDS_FILE) else {}

    seen = load_json(SEEN_FILE, {})
    # czyszczenie starych wpisów z pamięci
    seen = {k: v for k, v in seen.items()
            if (now - datetime.datetime.fromisoformat(v)).days <= SEEN_RETENTION_DAYS}

    items, dead_feeds = [], []
    for category, sources in feeds_cfg.items():
        for name, url in (sources or {}).items():
            parsed = feedparser.parse(url)
            if parsed.get("bozo") and not parsed.get("entries"):
                dead_feeds.append(f"{name} ({url})")
                continue
            for e in parsed.entries[:40]:
                eid = entry_id(e)
                if eid in seen:
                    continue
                d = entry_date(e)
                if d and d < cutoff:
                    continue  # stare — pomijamy, ale NIE oznaczamy jako widziane (oszczędność pamięci zbędna)
                title = strip_html(e.get("title", "(bez tytułu)"))
                summary = strip_html(e.get("summary", "") or e.get("description", ""))[:MAX_SUMMARY_CHARS]
                items.append({
                    "id": eid,
                    "category": category,
                    "source": name,
                    "title": title,
                    "link": e.get("link", ""),
                    "date": d.strftime("%Y-%m-%d") if d else "b.d.",
                    "summary": summary,
                    "score": score_text(f"{title} {summary}", keywords),
                })
                seen[eid] = now.isoformat()

    items.sort(key=lambda x: (-x["score"], x["category"]))

    # budowa digestu
    os.makedirs(DIGEST_DIR, exist_ok=True)
    today = now.strftime("%Y-%m-%d")
    out_path = os.path.join(DIGEST_DIR, f"{today}.md")
    lines = [f"# RADAR — {today}", "",
             f"Nowych materiałów: **{len(items)}** (okno: {WINDOW_DAYS} dni)", ""]

    if items:
        hot = [i for i in items if i["score"] > 0][:10]
        if hot:
            lines += ["## 🔥 Najtrafniejsze (słowa kluczowe)", ""]
            for it in hot:
                lines.append(f"- **{it['title']}** — {it['source']} ({it['date']}, punkty: {it['score']})  \n  {it['summary']}  \n  {it['link']}")
            lines.append("")
        by_cat = {}
        for it in items:
            by_cat.setdefault(it["category"], []).append(it)
        for cat, its in by_cat.items():
            lines += [f"## {cat}", ""]
            for it in its:
                lines.append(f"- [{it['title']}]({it['link']}) — {it['source']}, {it['date']}")
            lines.append("")
        topics = claude_topics(items)
        if topics:
            lines += ["## 🎯 Propozycje tematów (selekcja Claude)", "", topics, ""]
    else:
        lines += ["_Brak nowych materiałów w tym oknie._", ""]

    if dead_feeds:
        lines += ["## ⚠ Feedy do sprawdzenia (nie odpowiedziały)", ""]
        lines += [f"- {d}" for d in dead_feeds]
        lines.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False, indent=0)

    print(f"OK: {out_path} | nowe: {len(items)} | martwe feedy: {len(dead_feeds)}")


if __name__ == "__main__":
    main()
