#!/usr/bin/env python3
"""Builds the static site from publications_master.json.
Run:  python3 build.py   (writes the HTML files next to this script)
"""
import json, html, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
pubs = json.load(open(os.path.join(HERE, "publications_master.json"), encoding="utf-8"))
E = html.escape

# ------------------------------------------------------------------ content
NAME = "Patrick Sharkey"
TAGLINE = "William S. Tod Professor of Sociology and Public Affairs, Princeton University"
EMAIL = "psharkey@princeton.edu"
CV_FILE = "Sharkey_CV.pdf"
ADDRESS = "Princeton School of Public and International Affairs<br>Wallace Hall<br>Princeton University<br>Princeton, NJ 08544"

HOME_PARA = ("Patrick Sharkey is the William S. Tod Professor of Sociology and Public Affairs at Princeton&rsquo;s School of Public and International Affairs. "
             "His research centers on the challenges created by urban inequality, with a particular focus on community violence.")

BIO_PARAS = [
    "Patrick Sharkey is the William S. Tod Professor of Sociology and Public Affairs at Princeton&rsquo;s School of Public and International Affairs. "
    "His research centers on the challenges created by urban inequality, with a particular focus on community violence. "
    "Sharkey leads the Violence and Inequality Project at Princeton, a multidisciplinary effort to build a research infrastructure more useful to "
    "policymakers and community organizations working to confront violence. He recently received the 2026 Faculty Teaching Award selected by the "
    "graduating class of Princeton Sociology undergraduates, and was named as one of the World&rsquo;s Top 50 Thinkers by Prospect Magazine. "
    "His most recent book is titled <em>Uneasy Peace: The Great Crime Decline, the Renewal of City Life, and the Next War on Violence</em>.",
]

FEATURED = [
    dict(img="assets/ph-nyt.jpg", title="How Charities Fight Crime", sub="Headway, New York Times", url="https://www.nytimes.com/2026/07/15/headway/newsletter-how-charities-fight-crime.html"),
    dict(img="assets/ezra.jpg", title="Why Is Murder Spiking? And Can Cities Address It Without Police?", sub="The Ezra Klein Show, New York Times", url="https://www.nytimes.com/2021/11/23/opinion/ezra-klein-podcast-patrick-sharkey.html"),
    dict(img="assets/hayes.jpg", title="A More Violent America", sub="Why Is This Happening? with Chris Hayes", url="https://podcasts.apple.com/us/podcast/a-more-violent-america-with-patrick-sharkey/id1382983397?i=1000522131955"),
    dict(img="assets/newyorker.jpg", title="The Great Crime Decline", sub="Adam Gopnik reviews Uneasy Peace, The New Yorker", url="https://www.newyorker.com/magazine/2018/02/12/the-great-crime-decline"),
    dict(img="assets/nature.jpg", title="Computational Approaches and the Future of Urban Crime Research", sub="Nature", url="https://doi.org/10.1038/s41586-026-10622-4"),
    dict(img="assets/nyt-homebodies.jpg", title="A Nation of Homebodies", sub="The Upshot, New York Times", url="https://www.nytimes.com/2024/10/05/upshot/americans-homebodies-alone-census.html"),
    dict(img="assets/nyt-gun.jpg", title="A Drop in American Gun Violence", sub="The Morning, New York Times", url="https://www.nytimes.com/2023/11/01/briefing/gun-violence.html"),
    dict(img="assets/nyt-lessons.jpg", title="Two Lessons of the Urban Crime Decline", sub="New York Times", url="https://www.nytimes.com/2018/01/13/opinion/sunday/two-lessons-of-the-urban-crime-decline.html"),
    dict(img="assets/wapo.jpg", title="Why Do We Need the Police?", sub="Washington Post", url="https://www.washingtonpost.com/outlook/2020/06/12/defund-police-violent-crime/"),
    dict(img="assets/prospect.jpg", title="The World's Top 50 Thinkers", sub="Prospect Magazine", url="https://www.prospectmagazine.co.uk/politics/37755/the-worlds-top-50-thinkers-2021"),
]

BOOKS = [
    dict(title="Uneasy Peace: The Great Crime Decline, the Renewal of City Life, and the Next War on Violence",
         pub="W.W. Norton, 2018", cover="assets/uneasy-peace.jpg", url="https://wwnorton.com/books/Uneasy-Peace/",
         links=[("Publisher", "https://wwnorton.com/books/Uneasy-Peace/")]),
    dict(title="Stuck in Place: Urban Neighborhoods and the End of Progress toward Racial Equality",
         pub="University of Chicago Press, 2013", cover="assets/stuck-in-place.jpg",
         url="https://press.uchicago.edu/ucp/books/book/chicago/S/bo14365260.html",
         links=[("Publisher", "https://press.uchicago.edu/ucp/books/book/chicago/S/bo14365260.html"),
                ("Awards", "https://press.uchicago.edu/ucp/books/book/chicago/S/bo14365260.html#anchor-awards")]),
    dict(title="Spatial Foundations of Inequality",
         pub="RSF: The Russell Sage Foundation Journal of the Social Sciences, 2017. Co-edited with George Galster.",
         cover="assets/spatial-foundations.jpg", url="https://www.rsfjournal.org/content/3/2",
         links=[("Journal issue", "https://www.rsfjournal.org/content/3/2")]),
    dict(title="A Sociology Experiment",
         pub="Fourth edition. Co-edited with Shamus Khan and Gwen Sharp.", cover="assets/sociology-experiment.jpg",
         url="https://www.sociologyexperiment.com/", links=[("Website", "https://www.sociologyexperiment.com/")]),
]

# Topic assignment for the papers page filter, by keyword in the title. First match wins.
TOPICS = [
    ("Violence and crime", r"violen|crime|homicid|shoot|gun|street efficacy|deterr|frisk|criminal justice|public safety|social fabric"),
    ("Neighborhoods and mobility", r"neighbo|mobility|residential|context|migration|metropolis|segmentation|isolat|homebound|redlin|spatial|stigma|integration|place"),
    ("Children and cognition", r"child|cognit|test score|attention|academic|school|verbal|sleep"),
    ("Welfare and labor policy", r"welfare|work|employ|temporary help|medicaid|homeless|summer scholar"),
    ("Methods", r"selection|computational|instrument|method"),
]
def topic(p):
    t = p["title"].lower()
    for name, rx in TOPICS:
        if re.search(rx, t): return name
    return "Other"

# ------------------------------------------------------------------ helpers
def coauthors(auth):
    """Return the list of coauthor names other than Sharkey, in natural order; None if unparseable."""
    s = re.sub(r"\s*\((eds?\.)\)", "", auth).replace(" with ", ", ")
    toks = [t.strip() for t in re.split(r",\s*(?:and\s+)?|\s+and\s+", s) if t.strip()]
    if len(toks) < 2: return None
    # first author is stored "Last, First"
    names = [toks[1] + " " + toks[0]] + toks[2:]
    others = [n for n in names if "sharkey" not in n.lower()]
    if len(others) != len(names) - 1: return None
    return others

def cite(p):
    """Chetty-style: title (linked), then (with coauthors), venue vol(issue): pages, year."""
    link = f"https://doi.org/{p['doi']}" if p["doi"] else p["url"]
    title = f'<a href="{E(link)}">{E(p["title"])}</a>' if link else E(p["title"])
    co = coauthors(p["authors"])
    if co is None:
        with_ = E(p["authors"])
    elif co:
        with_ = "with " + E(", ".join(co[:-1]) + (" and " if len(co) > 1 else "") + co[-1]) if len(co) > 1 else "with " + E(co[0])
        with_ = f"({with_})"
    else:
        with_ = ""
    venue = E(p["venue"])
    if p["type"] in ("Journal article", "Book review", "Essay / op-ed"): venue = f"<em>{venue}</em>"
    bits = [venue]
    if p["volume"]:
        bits.append(" " + E(p["volume"]) + (f"({E(p['issue'])})" if p["issue"] else ""))
    if p["pages"]: bits.append(": " + E(p["pages"]))
    if p["year"]: bits.append(", " + E(str(p["year"])))
    extra = ""
    if p["open_access_pdf"]: extra = f' <a class="pdf" href="{E(p["open_access_pdf"])}">PDF</a>'
    sub = (with_ + ", " if with_ else "") + "".join(bits) + extra
    return f'<div class="paper"><div class="ptitle">{title}</div><div class="psub">{sub}</div></div>'

NAV = [("home","index.html","home"),("bio","bio.html","cv"),("books","books.html","books"),
       ("papers","papers.html","papers and data"),("news","news.html","news")]

def page(title, body, active):
    nav = "".join(f'<a href="{h}"{" class=\"active\"" if k==active else ""}>{t}</a>' for k,h,t in NAV)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header>
  <a class="name" href="index.html">{NAME.upper()}</a>
  <nav>{nav}</nav>
</header>
<main>
{body}
</main>
<footer><p>&copy; {NAME}</p></footer>
</body>
</html>
"""
def write(fn, s): open(os.path.join(HERE, fn), "w", encoding="utf-8").write(s)
def yr(p):
    try: return int(p["year"])
    except: return 0

# ------------------------------------------------------------------ home
home = f"""
<section class="intro">
  <img class="portrait" src="assets/sharkey.jpg" alt="{NAME}">
  <div>
    {''.join(f'<p>{b}</p>' for b in BIO_PARAS)}
    <p>Email: <a href="mailto:{EMAIL}">{EMAIL}</a></p>
    <p><a href="{CV_FILE}">Curriculum vitae</a></p>
  </div>
</section>
<h2 class="center">Recent News</h2>
<section class="featured">
  {''.join(f'<a class="card" href="{E(f["url"])}"><img src="{f["img"]}" alt=""><div class="ctitle">{E(f["title"])}</div><div class="csub">{E(f["sub"])}</div></a>' for f in FEATURED)}
</section>
<script>
(function(){{const g=document.querySelector('.featured');const c=[...g.children];for(let i=c.length-1;i>0;i--){{const j=Math.floor(Math.random()*(i+1));[c[i],c[j]]=[c[j],c[i]];}}c.forEach(x=>g.appendChild(x));}})();
</script>
"""
write("index.html", page(NAME, home, "home"))

# ------------------------------------------------------------------ bio / cv
bio = f"""<h1>CV</h1>
<p><a href="{CV_FILE}">Download PDF</a></p>
<iframe class="cv" src="{CV_FILE}" title="Curriculum vitae"></iframe>
"""
write("bio.html", page(f"CV | {NAME}", bio, "bio"))

# ------------------------------------------------------------------ books
books = "<h1>Books</h1>" + "".join(f"""
<section class="book">
  <a href="{E(b['url'])}"><img src="{b['cover']}" alt="{E(b['title'])}"></a>
  <div>
    <div class="ptitle"><a href="{E(b['url'])}">{E(b['title'])}</a></div>
    <div class="psub">{E(b['pub'])}</div>
    <div class="psub">{' &middot; '.join(f'<a href="{E(u)}">{E(t)}</a>' for t,u in b['links'])}</div>
  </div>
</section>""" for b in BOOKS)
write("books.html", page(f"Books | {NAME}", books, "books"))

# ------------------------------------------------------------------ papers and data
sections = [
    ("ARTICLES AND REPORTS", {"Journal article", "Book chapter", "Report", "Working paper / preprint", "Book review"}),
    ("BOOKS AND EDITED VOLUMES", {"Book", "Edited volume", "Textbook"}),
    ("ESSAYS AND OP-EDS", {"Essay / op-ed"}),
]
topic_names = [t for t,_ in TOPICS] + ["Other"]
used = [t for t in sorted({topic(p) for p in pubs if p["type"] not in ("Data / replication",)}, key=topic_names.index) if t not in ("Welfare and labor policy", "Other")]
papers = '<h1>Papers and Data</h1><div class="filter"><span>Subset by topic</span>' + "".join(
    f'<button data-topic="{E(t)}">{E(t)}</button>' for t in used) + '<button data-topic="">Reset</button></div>'
for head, types in sections:
    items = sorted([p for p in pubs if p["type"] in types], key=yr, reverse=True)
    if not items: continue
    papers += f'<h2>{head}</h2>' + "".join(f'<div class="pwrap" data-topic="{E(topic(p))}">{cite(p)}</div>' for p in items)
repl = sorted([p for p in pubs if p["type"]=="Data / replication" and p["doi"]], key=yr, reverse=True)
papers += '<h2>DATA</h2><div class="pwrap"><div class="paper"><div class="ptitle"><a href="https://www.americanviolence.org/">American Violence</a></div><div class="psub">Neighborhood-level data on shootings and homicides in U.S. cities</div></div></div>'
papers += "".join(f'<div class="pwrap"><div class="paper"><div class="ptitle"><a href="https://doi.org/{E(p["doi"])}">{E(p["title"])}</a></div><div class="psub">{E(p["venue"])}, {E(str(p["year"]))}</div></div></div>' for p in repl)
papers += """
<script>
document.querySelectorAll('.filter button').forEach(b=>b.addEventListener('click',()=>{
  const t=b.dataset.topic;
  document.querySelectorAll('.filter button').forEach(x=>x.classList.toggle('on',x===b&&t!==''));
  document.querySelectorAll('.pwrap').forEach(w=>{w.style.display=(!t||w.dataset.topic===t)?'':'none';});
  document.querySelectorAll('main h2').forEach(h=>{let n=h.nextElementSibling,vis=false;while(n&&n.tagName!=='H2'){if(n.style.display!=='none')vis=true;n=n.nextElementSibling;}h.style.display=vis?'':'none';});
}));
</script>"""
write("papers.html", page(f"Papers and Data | {NAME}", papers, "papers"))

# ------------------------------------------------------------------ news
news_path = os.path.join(HERE, "news.json")
news = json.load(open(news_path, encoding="utf-8")) if os.path.exists(news_path) else []
body = "<h1>News</h1>"
if not news:
    body += "<p>Coverage list in preparation.</p>"
for n in sorted(news, key=lambda n: n.get("date",""), reverse=True):
    body += f'<div class="pwrap"><div class="paper"><div class="ptitle"><a href="{E(n["url"])}">{E(n["headline"])}</a></div><div class="psub">{E(n["outlet"])}, {E(n["date"])}</div></div></div>'
write("news.html", page(f"News | {NAME}", body, "news"))

# ------------------------------------------------------------------ css
write("style.css", """
:root { --text:#444; --dark:#111; --muted:#777; --rule:#e5e5e5; --max:60rem; }
* { box-sizing:border-box; }
html { font-size:15px; }
body { margin:0; color:var(--text); background:#fff; font-family: "Helvetica Neue", Helvetica, Arial, system-ui, sans-serif; line-height:1.6; }
a { color:var(--dark); text-decoration:none; }
a:hover { text-decoration:underline; }
header { text-align:center; padding:2.25rem 1rem 1.25rem; }
header .name { display:block; font-size:1.5rem; letter-spacing:.18em; color:var(--dark); margin-bottom:.75rem; }
nav a { margin:0 .9rem; color:var(--muted); font-size:.85rem; letter-spacing:.04em; }
nav a.active, nav a:hover { color:var(--dark); text-decoration:none; }
main { max-width:var(--max); margin:0 auto; padding:1.5rem 1.25rem 3rem; }
h1 { font-size:1.25rem; font-weight:normal; letter-spacing:.08em; text-transform:uppercase; color:var(--dark); margin:0 0 1.25rem; }
h2 { font-size:.85rem; font-weight:600; letter-spacing:.12em; color:var(--dark); margin:2.5rem 0 1rem; }
h2.center { text-align:center; margin-top:3rem; }
.intro { display:grid; grid-template-columns: 260px 1fr; gap:2.5rem; align-items:start; max-width:52rem; margin:0 auto; }
.portrait { width:100%; height:auto; display:block; }
.featured { display:grid; grid-template-columns: repeat(5, 1fr); gap:1.25rem; margin:0 auto; }
.card img { width:100%; aspect-ratio: 4/3; object-fit:cover; display:block; margin-bottom:.6rem; }
.card { color:var(--text); }
.card:hover { text-decoration:none; }
.card:hover .ctitle { text-decoration:underline; }
.ctitle { color:var(--dark); font-weight:600; font-size:.85rem; line-height:1.3; }
.csub { font-size:.75rem; color:var(--muted); margin-top:.2rem; }
.paper { margin:0 0 1rem; }
.ptitle { color:var(--dark); font-weight:600; line-height:1.35; }
.psub { font-size:.9rem; color:var(--muted); }
.psub a { color:var(--muted); }
a.pdf { font-size:.75rem; letter-spacing:.05em; border:1px solid var(--rule); padding:0 .35rem; margin-left:.4rem; color:var(--muted); }
.filter { font-size:.85rem; margin-bottom:.5rem; }
.filter span { color:var(--muted); margin-right:.5rem; }
.filter button { background:none; border:1px solid var(--rule); color:var(--text); font:inherit; padding:.15rem .6rem; margin:.15rem .25rem .15rem 0; cursor:pointer; border-radius:3px; }
.filter button.on { background:var(--dark); color:#fff; border-color:var(--dark); }
.book { display:grid; grid-template-columns: 120px 1fr; gap:1.5rem; margin:1.25rem 0 2rem; align-items:start; }
.book img { width:100%; height:auto; box-shadow:0 1px 4px rgba(0,0,0,.2); }
.address { line-height:1.5; }
iframe.cv { width:100%; height:80vh; border:1px solid var(--rule); margin-top:1.5rem; }
footer { text-align:center; color:var(--muted); font-size:.75rem; padding:2rem 1rem; border-top:1px solid var(--rule); }
@media (max-width:640px) {
  .intro { grid-template-columns:1fr; text-align:center; }
  .portrait { max-width:240px; margin:0 auto; }
  .featured { grid-template-columns:1fr 1fr; }
  .book { grid-template-columns:90px 1fr; gap:1rem; }
  nav a { margin:0 .5rem; display:inline-block; }
}
""")
print("built", len(pubs), "publications;", len(news), "news items")
