#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reads the edited .docx, works out which words changed, and writes them back
into for-the-board.html.

    python3 apply_docx.py edited.docx for-the-board.html            # report only
    python3 apply_docx.py edited.docx for-the-board.html --write    # apply

The .docx was generated from the HTML block by block, so the paragraphs come
back in the same order. The two sequences are diffed against each other, which
handles a paragraph being added or dropped without everything after it sliding
out of step. Anything that cannot be matched confidently is reported rather
than guessed at.
"""
import json, os, re, subprocess, sys, difflib, html as htmllib

DOCX  = sys.argv[1]
HTML  = sys.argv[2]
WRITE = "--write" in sys.argv

HERE = os.path.dirname(os.path.abspath(__file__))
BLOCKS_JSON = os.path.join(HERE, "board-blocks.json")

# Always read the blocks straight out of the page as it stands right now, so
# there is no saved index that can fall out of step with it.
subprocess.run([sys.executable, os.path.join(HERE, "board-extract.py"), HTML, BLOCKS_JSON],
               check=True, capture_output=True)
blocks = json.load(open(BLOCKS_JSON, encoding="utf-8"))


def norm(s):
    s = (s.replace("’", "'").replace("‘", "'")
          .replace("“", '"').replace("”", '"')
          .replace("—", "-").replace("–", "-")
          .replace("·", "-").replace("•", ""))
    return re.sub(r"\s+", " ", s).strip().lower()


# --------------------------------------------------------------- build units
# A unit is one line as it appears in the .docx, and the block(s) behind it.
units = []
i = 0
while i < len(blocks):
    b = blocks[i]
    k = b["kind"]

    if k == "image":                       # no words to edit
        i += 1
        continue

    if k == "byline":                      # the three spans became one line
        grp = []
        while i < len(blocks) and blocks[i]["kind"] == "byline":
            grp.append(blocks[i]); i += 1
        units.append({"blocks": grp, "text": "   ·   ".join(g["text"] for g in grp),
                      "editable": False})
        continue

    if k == "data_label":                  # label + figure + note became one line
        grp = [b]; i += 1
        while i < len(blocks) and blocks[i]["kind"] in ("data_figure", "data_note"):
            grp.append(blocks[i]); i += 1
        d = {g["kind"]: g["text"] for g in grp}
        units.append({"blocks": grp,
                      "text": "%s  %s  —  %s" % (d.get("data_figure", ""),
                                                 d.get("data_label", ""),
                                                 d.get("data_note", "")),
                      "editable": False})
        continue

    text = b["text"]
    if k in ("kicker", "eyebrow", "pair_label"):
        text = text.upper()                # the .docx sets these in caps
    units.append({"blocks": [b], "text": text, "editable": True})
    i += 1

# --------------------------------------------------------------- read docx
raw = subprocess.run(["pandoc", "-t", "plain", "--wrap=none", DOCX],
                     capture_output=True, text=True, check=True).stdout
lines = [re.sub(r"\s+", " ", l).strip() for l in raw.split("\n")]
# pandoc writes a bare [] where each picture sits; those are not text
lines = [l for l in lines if l and not re.fullmatch(r"\[\s*\]", l)]
# the .docx draws its own bullet before each finding; that glyph is not content
lines = [re.sub(r"^[\u2022\u2013\-\*]\s+", "", l) for l in lines]

# drop everything before the kicker, which is the instruction block
first = norm(units[0]["text"])
for n, l in enumerate(lines):
    if difflib.SequenceMatcher(None, norm(l), first).ratio() > 0.75:
        lines = lines[n:]
        break

A = [norm(u["text"]) for u in units]
B = [norm(l) for l in lines]

# --------------------------------------------------------------- align
sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
changes, unchanged, problems = [], [], []

for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        for k in range(i2 - i1):
            unchanged.append(units[i1 + k])
    elif tag == "replace":
        if (i2 - i1) == (j2 - j1):
            for k in range(i2 - i1):
                u, new = units[i1 + k], lines[j1 + k]
                if u["editable"]:
                    changes.append((u, new,
                        difflib.SequenceMatcher(None, A[i1 + k], B[j1 + k]).ratio()))
                else:
                    problems.append((u, "a combined line was edited: %r" % new[:70]))
        else:
            for k in range(i1, i2):
                problems.append((units[k], "this stretch was rewritten or reordered"))
            for k in range(j1, j2):
                problems.append((None, "extra text in the document: %r" % lines[k][:70]))
    elif tag == "delete":
        for k in range(i1, i2):
            problems.append((units[k], "missing from the document"))
    elif tag == "insert":
        for k in range(j1, j2):
            problems.append((None, "new text added: %r" % lines[k][:70]))

# --------------------------------------------------------------- report
print("=" * 74)
print("lines expected from the page : %d" % len(units))
print("paragraphs read from the doc : %d" % len(lines))
print("unchanged                    : %d" % len(unchanged))
print("CHANGED                      : %d" % len(changes))
print("needs a look                 : %d" % len(problems))
print("=" * 74)

for u, new, s in changes:
    b = u["blocks"][0]
    print("\n[%s, block %d]  similarity %.2f" % (b["kind"], b["id"], s))
    print("  was: %s" % u["text"])
    print("  now: %s" % new)

for u, why in problems:
    if u:
        b = u["blocks"][0]
        print("\n!! block %d (%s): %s" % (b["id"], b["kind"], why))
        print("   %s" % u["text"][:95])
    else:
        print("\n!! %s" % why)

# --------------------------------------------------------------- write back
if WRITE and changes:
    src = open(HTML, encoding="utf-8").read()
    applied, failed = 0, []
    for u, new, s in changes:
        b = u["blocks"][0]
        old = b["text"]
        if b["kind"] in ("kicker", "eyebrow", "pair_label"):
            new = new if not new.isupper() else new.capitalize()
            # keep the page's own capitalisation for these small labels
            if old.upper() == new.upper():
                continue
        cands = [old,
                 old.replace("'", "&rsquo;"),
                 old.replace("&", "&amp;"),
                 old.replace("'", "&rsquo;").replace("&", "&amp;"),
                 htmllib.escape(old, quote=False)]
        hit = next((c for c in cands if c in src), None)
        if not hit:
            failed.append(b); continue
        repl = new
        if "&rsquo;" in hit: repl = repl.replace("'", "&rsquo;")
        if "&amp;" in hit:   repl = repl.replace("&", "&amp;")
        src = src.replace(hit, repl, 1)
        applied += 1
    open(HTML, "w", encoding="utf-8").write(src)
    print("\nwrote %d change(s) into %s" % (applied, HTML))

    for b in failed:
        print("   could not place block %d (%s): its text is broken up by tags inside"
              " the page, so change that one by hand" % (b["id"], b["kind"]))
elif changes:
    print("\n(report only — pass --write to apply)")
