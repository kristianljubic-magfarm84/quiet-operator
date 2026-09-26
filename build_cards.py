#!/usr/bin/env python3
"""Pre-render every card in quotes.json to docs/cards/.

Run this after editing quotes.json, then commit. Cards are built ahead of time
so the daily publish job never races GitHub's CDN.
"""
import json, os
from render import render

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "docs", "cards")
os.makedirs(OUT, exist_ok=True)

quotes = json.load(open(os.path.join(ROOT, "quotes.json")))
built = skipped = 0

for q in quotes:
    path = os.path.join(OUT, f"{q['id']:03d}.png")
    if os.path.exists(path):
        skipped += 1
        continue
    render(q["text"], q["id"], path)
    built += 1

print(f"built {built}, already present {skipped}, total {len(quotes)}")
