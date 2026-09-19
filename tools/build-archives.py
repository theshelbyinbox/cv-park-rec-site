#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regenerates whispers.html and minutes.html from archive-data.js.

Run this after adding new issues or minutes:
    python3 tools/build-archives.py

Everything is baked into plain HTML at build time, so the archive pages need
no JavaScript, work with Ctrl+F, and can be indexed by search engines.
"""
import json, os, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

data = open('archive-data.js').read()
A = json.loads(data[data.find('{'):data.rfind('}')+1])

FACILITIES = [
    ("lake","Baert Lake"), ("golf","Golf Course"), ("hall","Community Hall"),
    ("rodeo","Rodeo Grounds &amp; Arena"), ("airport","Airport (62-S)"),
    ("field","Multipurpose Field"),
]

def head(title, desc, og):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title} &middot; Christmas Valley Park &amp; Recreation District</title>
<meta name="description" content="{desc}" />
<meta property="og:title" content="{title} &middot; Christmas Valley Park &amp; Recreation District" />
<meta property="og:description" content="{desc}" />
<meta property="og:image" content="{og}" />
<meta property="og:type" content="website" />
<link rel="icon" href="images/logo.png" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="css/site.css" />
</head>
<body>

<a class="skip" href="#main">Skip to content</a>
"""

def header(active):
    cur = lambda k: ' aria-current="page"' if active == k else ''
    items = "\n".join(f'            <a class="navmenu__link" href="{s}.html">{n}</a>' for s, n in FACILITIES)
    return f"""
<header class="site-head">
  <div class="wrap">
    <div class="site-head__inner">
      <a class="brand" href="index.html">
        <div class="brand__name">Christmas Valley</div>
        <div class="brand__sub">Park &amp; Recreation District</div>
      </a>
        <input class="navtoggle" type="checkbox" id="nav-open" />
        <label class="burger" for="nav-open" aria-label="Open and close the menu"><span class="burger__box"><span class="burger__bar"></span></span><span class="burger__text">Menu</span></label>
      <nav class="nav">
        <div class="navitem navitem--menu">
          <a class="nav-link" href="facilities.html">Facilities</a>
          <div class="navmenu">
            <div class="navmenu__inner">
{items}
            </div>
          </div>
        </div>
        <div class="navitem"><a class="nav-link" href="resources.html">Resources</a></div>
        <div class="navitem"><a class="nav-link" href="events.html">Events</a></div>
        <div class="navitem"><a class="nav-link" href="whispers.html"{cur('whispers')}>Desert Whispers</a></div>
        <div class="navitem"><a class="nav-link" href="minutes.html"{cur('minutes')}>District Board</a></div>
      </nav>
      <div class="site-head__actions">
        <a class="cta-phone" href="tel:15415762216">(541) 576-2216</a>
      </div>
    </div>
  </div>
</header>
"""

CLOSER = """
  <section class="closer">
    <img class="closer__media" src="images/sage-pink-sky.jpg" alt="Sagebrush and rabbitbrush under a pink high-desert sky" loading="lazy" />
    <div class="closer__scrim"></div>
    <div class="closer__inner">
      <div class="eyebrow eyebrow--light mb-22">Come by the office</div>
      <h2 class="h2 h2--xl">Looking for something that isn&rsquo;t here?</h2>
      <p class="lead lead--lg">The office keeps paper copies of a good deal more than we&rsquo;ve scanned. Call and we&rsquo;ll go looking.</p>
      <div class="btnrow">
        <a class="btn btn--white btn--lg" href="tel:15415762216">(541) 576-2216</a>
        <a class="btn btn--hairline-light btn--hairline-photo btn--lg" href="mailto:cvparkrec@yahoo.com">cvparkrec@yahoo.com</a>
      </div>
    </div>
  </section>
"""

FOOTER = """
<footer class="site-foot">
  <div class="wrap">
    <div class="site-foot__cols">
      <div class="site-foot__brand">
        <div class="site-foot__name">Christmas Valley</div>
        <div class="site-foot__sub">Park &amp; Recreation District</div>
        <p class="site-foot__blurb">A special taxing district preserving the assets of Christmas Valley for this generation and the next. Established 1963.</p>
      </div>
      <div class="site-foot__col">
        <div class="site-foot__head">Explore</div>
        <div class="site-foot__links">
          <a class="foot-link" href="facilities.html">Facilities &amp; Properties</a>
          <a class="foot-link" href="rentals.html">Rentals</a>
          <a class="foot-link" href="events.html">Events</a>
          <a class="foot-link" href="visit.html">Things to See Nearby</a>
        </div>
      </div>
      <div class="site-foot__col">
        <div class="site-foot__head">The District</div>
        <div class="site-foot__links">
          <a class="foot-link" href="minutes.html">Board &amp; Minutes</a>
          <a class="foot-link" href="whispers.html">Desert Whispers archive</a>
          <a class="foot-link" href="advertise.html">Advertise in the Whispers</a>
          <a class="foot-link" href="resources.html">Resources</a>
        </div>
      </div>
      <div class="site-foot__col">
        <div class="site-foot__head">Office</div>
        <div class="site-foot__links site-foot__links--address">
          <span>57334 Christmas Tree Lane<br />P.O. Box 181<br />Christmas Valley, OR 97641</span>
          <a class="foot-link" href="tel:15415762216">(541) 576-2216 &middot; Tue&ndash;Fri 10&ndash;2</a>
        </div>
      </div>
    </div>
    <div class="site-foot__base">
      <span>&copy; 2026 Christmas Valley Park &amp; Recreation District</span>
      <span>Photography by Robert Petitt, Hunter Kittredge, Shelly Leehmann, Julie Peterson &amp; neighbors</span>
    </div>
  </div>
</footer>

</body>
</html>
"""

def subhero(photo, alt, label, h1, blurb, busy=False):
    return f"""
  <section class="section section--hero-top section--flush-bottom">
    <div class="wrap">
      <div class="photoblock subhero">
        <img class="photoblock__media" src="images/{photo}" alt="{alt}" />
        <div class="photoblock__scrim{" photoblock__scrim--busy" if busy else ""}"></div>
        <div class="photoblock__body">
          <div class="photoblock__main">
            <div class="rulemark">
              <span class="rulemark__line"></span>
              <span class="rulemark__text">{label}</span>
            </div>
            <h1 class="display on-photo">{h1}</h1>
          </div>
          <div class="photoblock__aside">
            <p class="lead lead--light measure-36">{blurb}</p>
          </div>
        </div>
      </div>
    </div>
  </section>
"""

def strip(cells):
    out = "".join(f"""        <div class="datacell">
          <div class="datacell__label">{l}</div>
          <div class="datacell__figure{' tabular' if tab else ''}">{v}</div>
          <div class="datacell__note">{n}</div>
        </div>
""" for l, v, n, tab in cells)
    return f"""
  <section class="section section--strip">
    <div class="wrap">
      <div class="datastrip">
{out}      </div>
    </div>
  </section>
"""

MISSING = []

def groups(key, prefix, noun="issue"):
    """Year sections plus the year index, straight out of archive-data.js."""
    coll = A.get(key, [])
    nav = "\n".join(
        f'        <a class="yearnav__link" href="#{prefix}-{g["year"]}">{g["year"]}</a>'
        for g in coll)
    out = []
    for g in coll:
        rows = []
        for it in g["items"]:
            f = it["file"]
            here = os.path.exists(f)
            if not here:
                MISSING.append(f)
            tag = it.get("tag") or ""
            tagh = f'<span class="doc__tag">{tag}</span>' if tag else ""
            if here:
                rows.append(
                    f'          <a class="doc" href="{f}">'
                    f'<span class="doc__label">{it["label"]}</span>{tagh}</a>')
            else:
                rows.append(
                    f'          <div class="doc doc--missing">'
                    f'<span class="doc__label">{it["label"]}</span>'
                    f'<span class="doc__tag">Not available</span></div>')
        n = len(g["items"])
        # the newest year of each collection starts open; the rest are closed
        # so the page does not run for thousands of pixels
        first = " checked" if not out else ""
        tid = f"y-{prefix}-{g['year']}"
        out.append(f"""      <div class="yeargroup" id="{prefix}-{g['year']}">
        <input class="yeartoggle" type="checkbox" id="{tid}"{first} />
        <label class="yeargroup__head" for="{tid}">
          <span class="yeargroup__year">{g['year']}</span>
          <span class="yeargroup__meta">
            <span class="yeargroup__count">{n} {noun if n == 1 else noun + 's'}</span>
            <span class="yeargroup__chev"></span>
          </span>
        </label>
        <div class="doccols">
{chr(10).join(rows)}
        </div>
      </div>""")
    return nav, "\n".join(out), sum(len(g["items"]) for g in coll)

# ------------------------------------------------------------------ WHISPERS
wnav, wbody, wn = groups("whispers", "w")
gnav, gbody, gn = groups("gazette", "g")
wyears = [int(g["year"]) for g in A["whispers"]] + [int(g["year"]) for g in A["gazette"]]

whis = (head("The Desert Whispers",
             f"Every surviving issue of the Desert Whispers, the Christmas Valley community newspaper, from {min(wyears)} to {max(wyears)}. Free to read on any device.",
             "images/newspaper.jpg")
 + header("whispers")
 + '\n<main id="main">\n'
 + subhero("newspaper.jpg", "Desert Whispers front pages", "The Desert Whispers",
           "Six decades of the Desert Whispers, in one place.",
           "The Desert Whispers has chronicled life in Christmas Valley since the 1960s. Every issue we have is free to open, on any device.",
           busy=True)
 + strip([("Issues online", f"{wn + gn}", "Every one we could find", True),
          ("Spanning", f"{min(wyears)}&ndash;{max(wyears)}", "The Gazette came first", True),
          ("Cost to read", "Free", "No account, no sign-in", False),
          ("Rebuilt since 2020", "131", "Page by page from scans", True)])
 + f"""
  <section class="section section--tight-top">
    <div class="wrap">
      <div class="sec-head sec-head--tight">
        <div class="sec-head__main">
          <div class="eyebrow eyebrow--accent">Jump to a year</div>
          <h2 class="h2">Pick a year and start reading.</h2>
        </div>
        <p class="sec-head__aside lead">Tap a year to open it, and tap again to close it. Each issue opens as a PDF. A handful of the oldest are missing from our shelves and are marked as such rather than sending you to a dead link.</p>
      </div>
      <div class="yearnav">
{wnav}
{gnav}
      </div>
{wbody}
    </div>
  </section>

  <section class="section section--tint">
    <div class="wrap">
      <div class="sec-head sec-head--tight">
        <div class="sec-head__main">
          <div class="eyebrow eyebrow--accent">Before the Whispers</div>
          <h2 class="h2 h2--sm">The Christmas Valley Gazette.</h2>
        </div>
        <p class="sec-head__aside lead">Christmas Valley&rsquo;s first paper, published as the town was being built. {gn} issues survive.</p>
      </div>
{gbody}
    </div>
  </section>

  <section class="section section--flush-top">
    <div class="wrap">
      <div class="panel">
        <div class="panel__cols">
          <div class="panel__col">
            <div class="eyebrow eyebrow--pale">Advertise &amp; Submit</div>
            <h2 class="h2 h2--sm h2--dark mb-20">Want to be in the next issue?</h2>
            <p class="lead lead--mist mb-30 measure-44">Display ads start at $7 and classified ads are free to the community. Deadlines are seven days before each issue.</p>
            <div class="btnrow">
              <a class="btn btn--white btn--sm" href="advertise.html">Rates &amp; how to submit <span class="btn__arrow">&#8594;</span></a>
              <a class="btn btn--hairline-light btn--sm" href="mailto:desertwhispers@yahoo.com">Email the editor</a>
            </div>
          </div>
          <div class="panel__col">
            <div class="eyebrow eyebrow--pale">The Basics</div>
            <div class="roster">
              <div class="roster__row">
                <div class="roster__name">Published</div>
                <div class="roster__role">The 1st and the 15th</div>
              </div>
              <div class="roster__row">
                <div class="roster__name">Ad deadline</div>
                <div class="roster__role">7 days prior, by 2 p.m.</div>
              </div>
              <div class="roster__row">
                <div class="roster__name">Free classifieds</div>
                <div class="roster__role">Up to 5 per issue, 35 words</div>
              </div>
              <div class="roster__row">
                <div class="roster__name">Editor</div>
                <div class="roster__role">desertwhispers@yahoo.com</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
"""
 + CLOSER + "\n</main>\n" + FOOTER)
open("whispers.html", "w").write(whis)
print("  wrote whispers.html  (%d Whispers + %d Gazette)" % (wn, gn))

# ------------------------------------------------------------------- MINUTES
mnav, mbody, mn = groups("minutes", "m", "meeting")
myears = [int(g["year"]) for g in A["minutes"]]

mins = (head("Board &amp; Minutes",
             f"Meeting minutes for the Christmas Valley Park and Recreation District Board, {min(myears)} to {max(myears)}. The Board meets the second Tuesday of every month and public comment is always welcome.",
             "images/community-hall.jpg")
 + header("minutes")
 + '\n<main id="main">\n'
 + subhero("community-hall.jpg", "The Community Hall, where the Board meets", "The District Board",
           "Every meeting, on the record.",
           "Five directors, elected by the district. The Board meets the second Tuesday of each month at 9 a.m. in the Community Hall, and anyone may speak.")
 + strip([("Next meeting", "2nd Tuesday", "9 a.m., Community Hall", False),
          ("Minutes on file", f"{mn}", f"{min(myears)} to {max(myears)}", True),
          ("Public comment", "Always", "No sign-up needed", False),
          ("Agendas", "At the office", "Posted before each meeting", False)])
 + f"""
  <section class="section section--tight-top">
    <div class="wrap">
      <div class="sec-head sec-head--tight">
        <div class="sec-head__main">
          <div class="eyebrow eyebrow--accent">The Board</div>
          <h2 class="h2 h2--sm">Five directors and an office manager.</h2>
        </div>
        <p class="sec-head__aside lead">Directors are elected by the district and serve without pay. If something on District property needs attention, these are the people to tell.</p>
      </div>
      <div class="split">
        <div class="split__body">
          <div class="ratelist">
            <!-- BUILD:roster -->
            <div class="rate"><div class="rate__main"><div class="rate__name">Scott Batson</div><div class="rate__note">Chairperson</div></div><div class="rate__price"><a href="tel:14582815925">(458) 281-5925</a></div></div>
            <div class="rate"><div class="rate__main"><div class="rate__name">David Uran</div><div class="rate__note">Vice Chairperson</div></div><div class="rate__price"><a href="tel:15415764177">(541) 576-4177</a></div></div>
            <div class="rate"><div class="rate__main"><div class="rate__name">Glenna Wade</div><div class="rate__note">Director</div></div></div>
            <div class="rate"><div class="rate__main"><div class="rate__name">Terry Crawford</div><div class="rate__note">Director</div></div></div>
            <div class="rate"><div class="rate__main"><div class="rate__name">Gari Merrifield</div><div class="rate__note">Director</div></div></div>
            <div class="rate"><div class="rate__main"><div class="rate__name">Ashley Anderson</div><div class="rate__note">Office Manager &middot; Editor, Desert Whispers</div></div></div>
            <!-- /BUILD:roster -->
          </div>
        </div>
        <div class="split__media">
          <div class="frame frame--short">
            <img src="images/sign.jpg" alt="The District sign in Christmas Valley" loading="lazy" />
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="section section--tint">
    <div class="wrap">
      <div class="sec-head sec-head--tight">
        <div class="sec-head__main">
          <div class="eyebrow eyebrow--accent">The record</div>
          <h2 class="h2">Minutes, by year.</h2>
        </div>
        <p class="sec-head__aside lead">Tap a year to open it, and tap again to close it. Every set of minutes the District holds in digital form. Anything older lives on paper at the office.</p>
      </div>
      <div class="yearnav">
{mnav}
      </div>
{mbody}
    </div>
  </section>
"""
 + CLOSER + "\n</main>\n" + FOOTER)
open("minutes.html", "w").write(mins)
print("  wrote minutes.html   (%d sets of minutes)" % mn)

if MISSING:
    print("\n  %d referenced files are not on disk and were marked 'Not available':" % len(MISSING))
    for m in MISSING: print("     -", m)
