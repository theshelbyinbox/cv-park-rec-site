#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py — the one command that rebuilds the site.

    python3 tools/build.py

What it does, in order:

  1. Looks in documents/ and writes archive-data.js to match what is actually
     on disk. Adding a new Desert Whispers issue or a new set of minutes means
     dropping a correctly named PDF into the right folder. Nothing else.

  2. Reads the plain-language files in content/ and puts that text into the
     pages. Events, the lake status, the board roster and the office details
     all live there, one file each.

  3. Runs tools/build-archives.py, which rebuilds whispers.html and
     minutes.html from archive-data.js.

Nothing here is destructive. Labels that already exist in archive-data.js are
kept exactly as they are, so hand-written ones (the old Gazette issues, for
example) survive every rebuild. Entries whose file is missing stay listed and
are marked "Not available" rather than quietly disappearing.

FILE NAMING, which is the whole trick:

    documents/desert-whispers/2026/2026-10-01.pdf      October 1, 2026
    documents/minutes/2026/2026-10-13.pdf              October 13, 2026
    documents/minutes/2026/2026-10-13-special.pdf      marked Special Meeting
    documents/gazette/1967/1967-02.pdf                 February 1967

Year folder must match the year in the file name.
"""

import json, os, re, subprocess, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

try:
    import yaml
except ImportError:
    sys.exit("This needs PyYAML.  Install it with:  pip3 install pyyaml")

# --------------------------------------------------------------------------
# 1. DOCUMENTS  ->  archive-data.js
# --------------------------------------------------------------------------

# folder name            key in archive-data.js
COLLECTIONS = [
    ("desert-whispers", "whispers"),
    ("minutes",         "minutes"),
    ("gazette",         "gazette"),
]

# the bit after the date in a file name -> the label shown beside the entry
TAGS = {
    "":                    {"minutes": "Regular Meeting"},
    "special":             {"minutes": "Special Meeting"},
    "revised":             {"minutes": "Regular Meeting (Revised)"},
    "attachments":         {"minutes": "Attachments"},
    "budget":              {"minutes": "Budget Meeting"},
    "budget-regular":      {"minutes": "Budget & Regular Meeting"},
    "budget-committee":    {"minutes": "Budget Committee Meeting"},
    "supplemental-budget": {"minutes": "Supplemental Budget Meeting"},
    "board":               {"minutes": "Board Meeting"},
}

MONTHS = ["January","February","March","April","May","June",
          "July","August","September","October","November","December"]

DATED = re.compile(r"^(\d{4})-(\d{2})(?:-(\d{2}))?(?:-([a-z0-9-]+?))?(?:-(\d+))?\.pdf$", re.I)

# a loose date read, used to keep entries in date order even when the file
# itself has gone missing
LOOSE = re.compile(r"(\d{4})-(\d{2})(?:-(\d{2}))?")


def sort_key(path, year):
    """(year, month, day) pulled from the file name, so every entry sits in
    date order whether or not the file is still on disk."""
    m = LOOSE.search(os.path.basename(path))
    if m:
        y, mo, d = m.groups()
        return (y, mo, d or "00")
    return (year, "00", "00")


def read_archive():
    """Load the current archive-data.js as a plain dict."""
    if not os.path.exists("archive-data.js"):
        return {}
    raw = open("archive-data.js", encoding="utf-8").read()
    return json.loads(raw[raw.find("{"): raw.rfind("}") + 1])


def label_for(collection, year, month, day):
    if day:
        return "%s %d, %s" % (MONTHS[month - 1], day, year)
    return "%s %s" % (MONTHS[month - 1], year)


def scan(folder, key, overrides, known=frozenset()):
    """Every PDF under documents/<folder>/, newest first."""
    found = {}
    base = os.path.join("documents", folder)
    if not os.path.isdir(base):
        return found, []

    problems = []
    for year in sorted(os.listdir(base), reverse=True):
        ydir = os.path.join(base, year)
        if not os.path.isdir(ydir) or not year.isdigit():
            continue
        for name in sorted(os.listdir(ydir), reverse=True):
            if not name.lower().endswith(".pdf"):
                continue
            path = "%s/%s/%s" % (base.replace(os.sep, "/"), year, name)
            m = DATED.match(name)
            if not m:
                # already in the archive with a hand-written label: leave it be
                if path not in known:
                    problems.append("%s  (name does not look like YYYY-MM-DD.pdf)" % path)
                continue
            fy, fm, fd, suffix, _dup = m.groups()
            if fy != year:
                problems.append("%s  (file says %s, folder says %s)" % (path, fy, year))
                continue
            mo = int(fm)
            if not 1 <= mo <= 12:
                problems.append("%s  (month %s is not 1-12)" % (path, fm))
                continue
            found[path] = {
                "label": label_for(key, fy, mo, int(fd) if fd else None),
                "tag": TAGS.get((suffix or "").lower(), {}).get(key, ""),
                "file": path,
                "_year": fy,
                "_sort": sort_key(path, fy),
                "_name": name,
            }
    # hand-written labels win over generated ones
    for path, o in overrides.items():
        if path in found:
            if "label" in o: found[path]["label"] = o["label"]
            if "tag" in o:   found[path]["tag"] = o["tag"]
    return found, problems


def build_archive_data():
    existing = read_archive()
    overrides = {}
    if os.path.exists("content/archive-labels.yml"):
        loaded = yaml.safe_load(open("content/archive-labels.yml", encoding="utf-8")) or {}
        overrides = loaded.get("overrides") or {}

    out, all_problems, stats = {}, [], []

    for folder, key in COLLECTIONS:
        known = {it["file"] for g in existing.get(key, []) for it in g["items"]}
        # position in the current archive, so entries that already exist keep
        # the order someone chose for them
        was_at = {}
        for g in existing.get(key, []):
            for it in g["items"]:
                was_at[it["file"]] = len(was_at)
        found, problems = scan(folder, key, overrides, known)
        all_problems += problems

        # keep everything already listed, even when the file has gone missing
        kept_missing = 0
        for group in existing.get(key, []):
            for item in group["items"]:
                path = item["file"]
                if path in found:
                    # an existing label is a human decision; never overwrite it
                    found[path]["label"] = item.get("label", found[path]["label"])
                    if item.get("tag"):
                        found[path]["tag"] = item["tag"]
                else:
                    y = group["year"]
                    found[path] = {
                        "label": item.get("label", path),
                        "tag": item.get("tag", ""),
                        "file": path,
                        "_year": y,
                        "_sort": sort_key(path, y),
                        "_name": os.path.basename(path),
                    }
                    kept_missing += 1

        # group by year, newest first
        by_year = {}
        for entry in found.values():
            by_year.setdefault(entry["_year"], []).append(entry)

        # Order rule: whatever order a year is already in, it stays in. Someone
        # chose it, and the oldest years run oldest-first on purpose. Only files
        # that are genuinely new get placed, and they follow that year's own
        # direction — on top where the year runs newest-first, on the end where
        # it runs oldest-first.
        groups = []
        for y in sorted(by_year, reverse=True):
            entries = by_year[y]
            old_ones = sorted((e for e in entries if e["file"] in was_at),
                              key=lambda e: was_at[e["file"]])
            new_ones = sorted((e for e in entries if e["file"] not in was_at),
                              key=lambda e: (e["_sort"], e.get("_name", "")),
                              reverse=True)

            ascending = False
            if len(old_ones) > 1:
                ascending = old_ones[0]["_sort"] < old_ones[-1]["_sort"]
            if ascending:
                new_ones.reverse()
                items = old_ones + new_ones
            else:
                items = new_ones + old_ones

            groups.append({
                "year": y,
                "items": [{"label": i["label"], "tag": i["tag"], "file": i["file"]}
                          for i in items],
            })
        out[key] = groups

        on_disk = sum(1 for e in found.values() if os.path.exists(e["file"]))
        stats.append((key, sum(len(g["items"]) for g in groups), on_disk, kept_missing))

    banner = ("// Generated by tools/build.py on %s — do not edit by hand.\n"
              "// Add or remove a PDF in documents/ and run the build again.\n"
              % datetime.date.today().isoformat())
    open("archive-data.js", "w", encoding="utf-8").write(
        banner + "window.ARCHIVE=" + json.dumps(out, indent=1, ensure_ascii=False) + ";\n")

    print("  archive-data.js rebuilt from documents/")
    for key, listed, on_disk, missing in stats:
        print("    %-9s %4d listed, %4d on disk%s"
              % (key, listed, on_disk,
                 ", %d listed but missing" % missing if missing else ""))
    if all_problems:
        print("\n  %d file(s) were SKIPPED because of the name:" % len(all_problems))
        for p in all_problems:
            print("     -", p)
        print("  Rename them to YYYY-MM-DD.pdf and run the build again.\n")
    return len(all_problems)


# --------------------------------------------------------------------------
# 2. content/*.yml  ->  the pages
# --------------------------------------------------------------------------

def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def load(name):
    path = os.path.join("content", name)
    if not os.path.exists(path):
        return None
    return yaml.safe_load(open(path, encoding="utf-8"))


def render_events(data):
    rows = []
    for e in data.get("events", []):
        where = esc(e.get("where", ""))
        time = esc(e.get("time", ""))
        place = where + ("<br />" + time if where and time else time)
        rows.append(
            '        <div class="event">\n'
            '          <div class="event__date tabular">%s</div>\n'
            '          <div class="event__main">\n'
            '            <h3 class="event__title">%s</h3>\n'
            '            <p class="event__text">%s</p>\n'
            '          </div>\n'
            '          <div class="event__where">%s</div>\n'
            '        </div>'
            % (esc(e.get("date", "")), esc(e.get("title", "")),
               esc(e.get("text", "")), place))
    return "\n".join(rows)


def render_roster(data):
    rows = []
    for p in data.get("board", []) + data.get("staff", []):
        phone = p.get("phone")
        price = ""
        if phone:
            digits = re.sub(r"\D", "", str(phone))
            price = ('<div class="rate__price"><a href="tel:1%s">%s</a></div>'
                     % (digits, esc(phone)))
        rows.append(
            '            <div class="rate"><div class="rate__main">'
            '<div class="rate__name">%s</div>'
            '<div class="rate__note">%s</div></div>%s</div>'
            % (esc(p.get("name", "")), esc(p.get("role", "")), price))
    return "\n".join(rows)


def render_notice(data):
    n = data.get("notice") or {}
    if not n.get("show"):
        return ""
    return ('<div class="notice">\n  <div class="notice__inner">\n'
            '    <span class="notice__label">%s</span>\n'
            '    <span class="notice__text">%s</span>\n'
            '  </div>\n</div>'
            % (esc(n.get("label", "District Notice")), esc(n.get("text", ""))))


BLOCKS = [
    # content file        marker name   renderer         pages to write into
    ("events.yml",        "events",     render_events,   ["events.html"]),
    ("board.yml",         "roster",     render_roster,   ["minutes.html"]),
    ("status.yml",        "notice",     render_notice,   ["index.html", "events.html"]),
]


def apply_content():
    if not os.path.isdir("content"):
        print("  content/ not found — skipping the text step")
        return 0

    touched, warnings = 0, 0
    for filename, marker, render, pages in BLOCKS:
        data = load(filename)
        if data is None:
            continue
        html = render(data)
        start, end = "<!-- BUILD:%s -->" % marker, "<!-- /BUILD:%s -->" % marker
        for page in pages:
            if not os.path.exists(page):
                continue
            src = open(page, encoding="utf-8").read()
            if start not in src or end not in src:
                print("  note: %s has no %s markers, left alone" % (page, marker))
                warnings += 1
                continue
            new = re.sub(re.escape(start) + r".*?" + re.escape(end),
                         lambda _m: start + "\n" + html + "\n" + end,
                         src, flags=re.S)
            if new != src:
                open(page, "w", encoding="utf-8").write(new)
                touched += 1
            print("    %-14s <- content/%s" % (page, filename))
    print("  %d page(s) updated from content/" % touched)
    return warnings


# --------------------------------------------------------------------------
# 3. rebuild the archive pages
# --------------------------------------------------------------------------

def build_pages():
    script = os.path.join("tools", "build-archives.py")
    if not os.path.exists(script):
        print("  tools/build-archives.py not found — skipping")
        return 1
    r = subprocess.run([sys.executable, script], capture_output=True, text=True)
    for line in (r.stdout or "").splitlines():
        print("  " + line)
    if r.returncode != 0:
        print(r.stderr)
        return 1
    return 0


def main():
    print("\nRebuilding the Christmas Valley Park & Recreation site\n")

    print("1. Documents")
    skipped = build_archive_data()

    print("\n2. Archive pages")
    failed = build_pages()

    print("\n3. Text from content/")
    apply_content()

    print("\nDone.")
    if skipped:
        print("WARNING: %d file(s) were skipped. See the list above." % skipped)
    if failed:
        print("WARNING: the archive pages did not rebuild cleanly.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
