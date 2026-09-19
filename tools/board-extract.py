#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reads for-the-board.html and writes an ordered list of its editable text
blocks to JSON. The same extractor is used to build the .docx and, later, to
put Shelby's edits back, so the two stay in step.
"""
import json, re, sys
from bs4 import BeautifulSoup, NavigableString

SRC = sys.argv[1] if len(sys.argv) > 1 else "/tmp/out/for-the-board.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/tmp/out/board-blocks.json"

soup = BeautifulSoup(open(SRC, encoding="utf-8").read(), "html.parser")

def txt(el):
    """Visible text, with <em> kept as markers so italics survive the trip."""
    parts = []
    for n in el.descendants:
        if isinstance(n, NavigableString):
            parts.append(str(n))
        elif n.name == "em":
            pass
    s = el.get_text(" ", strip=False)
    s = re.sub(r"\s+", " ", s).strip()
    return s

blocks = []

def add(kind, text, **extra):
    if not text:
        return
    b = {"id": len(blocks) + 1, "kind": kind, "text": text}
    b.update(extra)
    blocks.append(b)

# ---- masthead -------------------------------------------------------------
mh = soup.find("header", class_="masthead")
add("kicker", txt(mh.find(class_="masthead__kicker")))
add("title",  txt(mh.find("h1")))
add("lede",   txt(mh.find(class_="masthead__lede")))
for sp in mh.find(class_="byline").find_all("span", recursive=False):
    add("byline", txt(sp))

# ---- each section ---------------------------------------------------------
for sec in soup.find_all("section"):
    for el in sec.descendants:
        if not getattr(el, "name", None):
            continue
        cls = el.get("class") or []

        if el.name == "div" and "eyebrow" in cls:
            add("eyebrow", txt(el))
        elif el.name == "h2":
            add("h2", txt(el))
        elif el.name == "h3":
            add("h3", txt(el))
        elif el.name == "p":
            if "tour__text" in cls:      add("tour_text", txt(el))
            elif "lede" in cls:          add("lede_p", txt(el))
            elif el.find_parent(class_="panel"): add("panel_p", txt(el))
            else:                        add("p", txt(el))
        elif el.name == "span" and "findings__what" in cls:
            add("finding_what", txt(el))
        elif el.name == "span" and "findings__why" in cls:
            add("finding_why", txt(el))
        elif el.name == "li" and el.find_parent(class_="panel"):
            add("panel_li", txt(el))
        elif el.name == "div" and "data__label" in cls:
            add("data_label", txt(el))
        elif el.name == "div" and "data__figure" in cls:
            add("data_figure", txt(el))
        elif el.name == "div" and "data__note" in cls:
            add("data_note", txt(el))
        elif el.name == "div" and "pair__label" in cls:
            add("pair_label", txt(el))
        elif el.name == "figcaption":
            add("figcaption", txt(el))
        elif el.name == "img" and el.get("src", "").startswith("images/"):
            add("image", el.get("alt", ""), src=el["src"])
        elif el.name == "a" and el.find_parent(class_="linkline"):
            add("link", txt(el), href=el.get("href", ""))
        elif el.name == "b" and el.find_parent(class_="sign"):
            add("sign_name", txt(el))

# the signature block's trailing lines are loose text, grab them separately
sign = soup.find(class_="sign")
if sign:
    tail = sign.get_text("\n", strip=True).split("\n")
    for line in tail[1:]:
        line = line.strip()
        if line:
            add("sign_line", line)

json.dump(blocks, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

from collections import Counter
c = Counter(b["kind"] for b in blocks)
print("%d blocks written to %s" % (len(blocks), OUT))
for k, n in c.most_common():
    print("   %-14s %d" % (k, n))
