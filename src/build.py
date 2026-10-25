"""Assemble the static site.

src/pages/**/*.html  ->  site/**/*.html, wrapped in the shared header/footer.
Also writes sitemap.xml, robots.txt, _redirects (Netlify) and the share image reference.
Links use clean addresses (/about, /blog/<slug>) that match the original Hostinger site,
so existing Google results and shared links keep working after the move.
"""
import re, json, pathlib, shutil, sys, html as htmllib
sys.path.insert(0, str(pathlib.Path(__file__).parent))

SRC = pathlib.Path(__file__).parent
OUT = SRC.parent / "site"
DOMAIN = "https://k3professionalservices.com"
BUILT = "2026-10-25"  # last-modified date for pages without their own date

TOKENS = {
    "{{BOOK}}": "https://bookings.cloud.microsoft/book/ConsultingAppointments@k3professionalservices.com/",
    "{{ASSESS}}": "https://resumaire.com/career-discovery",
    "{{ATS}}": "https://resumaire.com/resume-checker",
    "{{PRICING}}": "https://resumaire.com/pricing",
    "{{RESUMAIRE}}": "https://www.resumaire.com",
    "{{LOGO}}": "/images/k3-logo-256.webp",
    "{{LIVE}}": DOMAIN,
}

# Add the business's real social profile URLs here (LinkedIn company page first).
# They appear in the footer and in the business markup Google reads.
SOCIAL = [
    ("LinkedIn", "https://www.linkedin.com/company/146724626"),
    ("Instagram", "https://www.instagram.com/k3professionalservices/"),
    ("TikTok", "https://www.tiktok.com/@k3professionalservices"),
    ("Threads", "https://www.threads.com/@k3professionalservices"),
    ("X", "https://x.com/K3Professional"),
]

NAV = [("/", "Home"), ("/about", "About"), ("{{RESUMAIRE}}", "Resumaire"),
       ("/certifications", "Certifications"), ("/remote-careers", "Remote Careers"),
       ("/blog", "Blog"), ("/contact", "Contact")]

SHARE_IMAGE = DOMAIN + "/images/share.png"


def header(path):
    links = []
    for href, label in NAV:
        active = href != "/" and path.startswith(href) or href == path
        cls = ' class="active"' if active else ""
        links.append(f'<a href="{href}"{cls}>{label}</a>')
    nav = "\n      ".join(links)
    return f'''<header class="site-header">
  <div class="container">
    <a class="brand" href="/"><img src="{{{{LOGO}}}}" alt="K3 Professional Services Logo" width="48" height="48"></a>
    <input type="checkbox" id="menu" class="menu-toggle" aria-label="Open menu">
    <label for="menu" class="menu-btn" aria-hidden="true">&#9776;</label>
    <nav class="nav" aria-label="Main">
      {nav}
      <a class="btn btn-gold btn-sm" href="{{{{BOOK}}}}">Book a Free Call</a>
    </nav>
  </div>
</header>'''


def footer():
    social = ""
    if SOCIAL:
        items = "".join(f'<li><a href="{u}" rel="me noopener" target="_blank" aria-label="K3 Professional Services on {n}">{n}</a></li>' for n, u in SOCIAL)
        social = f'\n        <h4 style="margin-top:28px">Follow Us</h4>\n        <ul class="social">{items}</ul>'
    return f'''<footer class="site-footer">
  <div class="container">
    <div class="cols">
      <div>
        <a href="/"><img class="logo" src="{{{{LOGO}}}}" alt="K3 Logo"></a>
        <p>Delivering professional career development, resume, and coaching services directly to you.</p>{social}
      </div>
      <div>
        <h3>Quick Links</h3>
        <ul>
          <li><a href="/">Home</a></li>
          <li><a href="/about">About Us</a></li>
          <li><a href="/career-development">Career Development</a></li>
          <li><a href="/career-coaching">Career Coaching</a></li>
          <li><a href="/resume-writing">Resume Writing</a></li>
          <li><a href="/interview-coaching">Interview Coaching</a></li>
          <li><a href="/certifications">Certifications &amp; Resources</a></li>
          <li><a href="/remote-careers">Remote Careers</a></li>
          <li><a href="{{{{RESUMAIRE}}}}">Resumaire</a></li>
          <li><a href="/concierge">Concierge</a></li>
          <li><a href="/blog">Blog</a></li>
          <li><a href="/contact">Contact</a></li>
        </ul>
      </div>
      <div>
        <h4>Free Tools</h4>
        <ul>
          <li><a href="{{{{ASSESS}}}}">Free Career Assessment</a></li>
          <li><a href="{{{{ATS}}}}">Free ATS Check</a></li>
        </ul>
        <h3 style="margin-top:28px">Contact</h3>
        <ul>
          <li><a href="tel:+13219664940">321-966-4940</a></li>
          <li><a href="mailto:general@k3professionalservices.com">general@k3professionalservices.com</a></li>
          <li>Serving Florida and clients nationwide (virtual).</li>
        </ul>
      </div>
      <div>
        <h3>Ready to Book?</h3>
        <p>Start with a free 15-minute discovery call.</p>
        <a class="btn btn-gold" href="{{{{BOOK}}}}">Book a Free Call</a>
      </div>
    </div>
    <div class="bottom">
      <span>&copy; 2026 K3 Professional Services. All rights reserved.</span>
      <span><a href="/privacy">Privacy Policy</a><a href="/terms">Terms of Service</a></span>
    </div>
  </div>
</footer>'''


BUSINESS = {
    "@type": "ProfessionalService",
    "@id": DOMAIN + "/#business",
    "name": "K3 Professional Services",
    "legalName": "K3 Professional Services, LLC",
    "url": DOMAIN + "/",
    "logo": DOMAIN + "/images/k3-logo.webp",
    "image": SHARE_IMAGE,
    "description": "Career coaching, resume and LinkedIn writing, interview preparation, job-search planning and done-for-you concierge job search for professionals in Florida and nationwide.",
    "telephone": "+1-321-966-4940",
    "email": "general@k3professionalservices.com",
    "address": {"@type": "PostalAddress", "addressRegion": "FL", "addressCountry": "US"},
    "areaServed": [{"@type": "State", "name": "Florida"}, {"@type": "Country", "name": "United States"}],
    "founder": {"@type": "Person", "name": "Keiandra Gray", "jobTitle": "Founder & Career Coach",
                "sameAs": ["https://www.linkedin.com/in/keiandra-gray-14a315442"]},
    "employee": [{"@type": "Person", "name": "Jamillah", "jobTitle": "COO & Career Developer"}],
    "knowsAbout": ["Career coaching", "Resume writing", "LinkedIn profile optimization",
                   "Interview preparation", "Job search strategy", "Career change", "Cover letter writing"],
    "openingHours": "Mo-Fr 09:00-18:00",
    "priceRange": "$99-$1497",
    "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Career services", "itemListElement": [
        {"@type": "Offer", "price": p, "priceCurrency": "USD", "itemOffered": {"@type": "Service", "name": n}}
        for n, p in [("Strategy Session", "249"), ("Resume Tailored to One Job", "199"),
                     ("Cover Letter for One Job", "99"), ("Mock Interview", "199"),
                     ("Interview Cheat Sheet", "99"), ("Portfolio Page, Built for You", "349"),
                     ("Three Researched Openings", "449"), ("Concierge Job Search", "1497")]]},
}


def schema(meta, url):
    graph = []
    b = dict(BUSINESS)
    if SOCIAL:
        b["sameAs"] = [u for _, u in SOCIAL]
    if meta["path"] == "/":
        graph += [b, {"@type": "WebSite", "@id": DOMAIN + "/#website", "url": DOMAIN + "/",
                      "name": "K3 Professional Services", "publisher": {"@id": DOMAIN + "/#business"}}]
    if meta.get("date"):
        graph.append({"@type": "BlogPosting", "headline": meta["headline"], "description": meta["description"],
                      "image": meta["image"], "datePublished": meta["date"], "dateModified": meta["date"],
                      "author": {"@type": "Organization", "name": "K3 Professional Services", "url": DOMAIN + "/"},
                      "publisher": {"@id": DOMAIN + "/#business"}, "mainEntityOfPage": url})
    if meta.get("service"):
        # A service page: what it is, who provides it, where, and the real prices
        # listed on the page. "offers" in the page header is "Name=price; Name=price".
        offers = []
        for item in meta.get("offers", "").split(";"):
            if "=" in item:
                name, price = item.rsplit("=", 1)
                offers.append({"@type": "Offer", "price": price.strip(), "priceCurrency": "USD",
                               "url": url, "itemOffered": {"@type": "Service", "name": name.strip()}})
        node = {"@type": "Service", "name": meta["service"], "serviceType": meta["service"],
                "description": meta["description"], "url": url,
                "provider": {"@type": "ProfessionalService", "@id": DOMAIN + "/#business",
                             "name": "K3 Professional Services", "url": DOMAIN + "/"},
                "areaServed": [{"@type": "State", "name": "Florida"},
                               {"@type": "Country", "name": "United States"}]}
        if offers:
            node["offers"] = offers
        graph.append(node)
    if meta.get("faq"):
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in meta["faq"]]})
    crumbs = [("Home", "/")]
    parts = [p for p in meta["path"].split("/") if p]
    if parts:
        if parts[0] == "blog" and len(parts) > 1:
            crumbs.append(("Blog", "/blog"))
        crumbs.append((meta.get("crumb", meta["title"].split("|")[0].strip()), meta["path"]))
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": DOMAIN + p}
            for i, (n, p) in enumerate(crumbs)]})
    if not graph:
        return ""
    data = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)
    return f'<script type="application/ld+json">\n{data}\n</script>\n'


def faq_from_body(body):
    """Pull <details class="faq"><summary>Q</summary><p>A</p></details> pairs for FAQ markup."""
    out = []
    for q, a in re.findall(r'<details class="faq">\s*<summary>(.*?)</summary>\s*(.*?)</details>', body, re.S):
        clean = lambda s: htmllib.unescape(re.sub(r"<[^>]+>", "", s)).strip()
        out.append((clean(q), re.sub(r"\s+", " ", clean(a))))
    return out


def page(meta, body):
    title, desc = meta["title"], meta["description"]
    url = DOMAIN + meta["path"]
    robots = '<meta name="robots" content="noindex">\n' if meta.get("noindex") else ""
    canonical = "" if meta.get("noindex") else f'<link rel="canonical" href="{url}">\n'
    og_type = "article" if meta.get("date") else "website"
    image = meta.get("image", SHARE_IMAGE)
    article = f'<meta property="article:published_time" content="{meta["date"]}">\n' if meta.get("date") else ""
    return f'''<!DOCTYPE html>
<html lang="en-US">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
{robots}{canonical}<meta name="theme-color" content="#1b4b3d">
<meta name="google-site-verification" content="P0765nV-KGeStHcwXKXyxjnYqI9YFBxDpug5VeJAVyU">
<meta name="Impact-Site-Verification" content="ffafe3b1-1a64-4221-bc9c-3c3a5d7f47a3">
<meta property="og:site_name" content="K3 Professional Services">
<meta property="og:locale" content="en_US">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{image}">
<meta property="og:image:alt" content="{meta.get("image_alt", "K3 Professional Services — Real coaching for the career you want")}">
{article}<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{image}">
<link rel="icon" type="image/png" sizes="48x48" href="/images/favicon.png">
<link rel="apple-touch-icon" href="/images/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,600;1,700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/style.css">
{schema(meta, url)}</head>
<body>
{header(meta["path"])}
<main>
{body.strip()}
</main>
{footer()}
</body>
</html>
'''


def read_meta(raw):
    m = re.match(r"<!--(.*?)-->", raw, re.S)
    meta = {}
    for line in m.group(1).strip().splitlines():
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
    return meta, raw[m.end():]


# ---- blog posts (content/blog/*.md, written in the /admin editor) ----

CONTENT = SRC.parent / "content" / "blog"
STATIC = SRC.parent / "static"
CTA_DEFAULT = ("Prefer to talk it through with a person? "
               '<a href="{{BOOK}}">Book a free 15-minute call</a> with the K3 team, or try the '
               '<a href="{{ASSESS}}">free career assessment</a> and the '
               '<a href="{{ATS}}">free ATS resume check</a>.')


def summary(markdown_text, limit):
    """The first real paragraph of a post as plain text, cut at a word boundary."""
    for block in re.split(r"\n\s*\n", markdown_text):
        b = block.strip()
        if not b or b[0] in "#>-*|!<" or re.match(r"^\d+[.)]\s", b):
            continue
        b = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", b)
        b = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", b)
        b = re.sub(r"[*_`]", "", b)
        b = re.sub(r"\s+", " ", b).strip()
        if len(b) <= limit:
            return b
        cut = b[:limit - 1].rsplit(" ", 1)[0].rstrip(",;:.")
        return cut + "…"
    return ""


def read_post(path):
    """A post file: JSON front matter (what the editor writes), then Markdown."""
    text = path.read_text(encoding="utf-8").lstrip("﻿")
    stripped = text.lstrip()
    if stripped.startswith("{"):
        data, end = json.JSONDecoder().raw_decode(stripped)
        body = stripped[end:]
    elif stripped.startswith("---"):
        # Simple YAML front matter, in case a post was written by hand.
        _, fm, body = stripped.split("---", 2)
        data = {}
        for line in fm.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip().strip('"').strip("'")
    else:
        raise ValueError(f"{path.name}: no front matter")
    data["body"] = body.strip()
    # New posts are saved as "YYYY-MM-DD-title.md": the date is the day the post
    # was created in the editor, and the web address is the title part only.
    named = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)$", path.stem)
    data["slug"] = named.group(2) if named else path.stem
    data["date"] = str(data.get("date") or (named.group(1) if named else ""))[:10]
    if not data.get("title") or not data["date"]:
        raise ValueError(f"{path.name}: needs a title and a date")
    # Everything else fills itself in when the editor leaves it out.
    data["category"] = data.get("category") or "Career Development"
    data["image"] = data.get("image") or "/images/hero-blog.webp"
    data["image_alt"] = data.get("image_alt") or data["title"]
    data["description"] = data.get("description") or summary(data["body"], 155)
    data["excerpt"] = data.get("excerpt") or summary(data["body"], 220)
    return data


def nice_date(iso):
    import datetime
    d = datetime.date.fromisoformat(iso)
    return f"{d.strftime('%B')} {d.day}, {d.year}"


def esc(s):
    return htmllib.escape(str(s), quote=True)


def post_card(p, featured=False):
    if featured:
        return f"""<a class="card featured-post" href="/blog/{p['slug']}" style="padding:24px">
      <img src="{esc(p['image'])}" alt="{esc(p['image_alt'])}">
      <div>
        <span class="tag">Featured · {esc(p['category'])}</span>
        <h2 style="font-size:1.9rem">{esc(p['title'])}</h2>
        <p>{esc(p['excerpt'])}</p>
        <p class="byline">K3 Professional Services · {nice_date(p['date'])}</p>
        <span class="btn btn-green btn-sm">Read Article</span>
      </div>
    </a>"""
    return f"""<a class="card post-card" href="/blog/{p['slug']}">
        <img src="{esc(p['image'])}" alt="{esc(p['image_alt'])}" loading="lazy">
        <span class="tag">{esc(p['category'])}</span>
        <h3>{esc(p['title'])}</h3>
        <p>{esc(p['excerpt'])}</p>
        <p class="byline">{nice_date(p['date'])} · <strong>Read →</strong></p>
      </a>"""


def post_page_body(p, others):
    from markdown import to_html
    # Posts that already end with their own call to action don't get a second one.
    cta = "" if "bookings.cloud.microsoft" in p["body"] else (
        f'    <div class="card" style="margin-top:40px;border:2px solid var(--gold)"><p style="margin:0">{CTA_DEFAULT}</p></div>')
    related = [o for o in others if o["category"] == p["category"]][:2] or others[:2]
    more = ""
    if related:
        heading = f"More in {esc(p['category'])}" if related[0]["category"] == p["category"] else "More From the Blog"
        cards = "\n".join(post_card(o) for o in related)
        more = f"""
<section class="tint">
  <div class="container narrow">
    <h2>{heading}</h2>
    <div class="grid g2">{cards}</div>
  </div>
</section>"""
    return f"""<article class="article">
  <div class="container narrow">
    <a href="/blog" class="small">← Back to all articles</a>
    <span class="eyebrow" style="display:block;margin-top:24px">{esc(p['category'])}</span>
    <h1 style="font-size:clamp(2rem,4.4vw,3rem)">{esc(p['title'])}</h1>
    <p class="byline">K3 Professional Services · {nice_date(p['date'])}</p>
    <img class="cover" src="{esc(p['image'])}" alt="{esc(p['image_alt'])}">
{to_html(p['body'])}
{cta}
    <p style="margin-top:40px"><a class="btn btn-outline btn-sm" href="/blog">← Back to all articles</a></p>
  </div>
</article>{more}"""


def blog_index_body(posts):
    tpl = SRC / "templates"
    # A post marked featured leads only until a newer post is published.
    marked = next((p for p in posts if str(p.get("featured")).lower() == "true"), None)
    featured = marked if marked and posts and marked["date"] >= posts[0]["date"] else (posts[0] if posts else None)
    rest = [p for p in posts if p is not featured]
    grid = "\n".join(post_card(p) for p in rest)
    feat = post_card(featured, featured=True) if featured else "<p>New articles are on the way.</p>"
    return (tpl / "blog-hero.html").read_text() + f"""
<section>
  <div class="container">
    {feat}
    <div class="grid g2" style="margin-top:32px">
{grid}
    </div>
  </div>
</section>
""" + (tpl / "blog-suggest.html").read_text()


def write_page(rel, meta, body):
    html = page(meta, body)
    for k, v in TOKENS.items():
        html = html.replace(k, v)
    assert "{{" not in html, rel
    out = OUT / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print("built", meta["path"])


# ---- build ----
if OUT.exists():
    shutil.rmtree(OUT)
shutil.copytree(STATIC, OUT)  # css, images, admin editor, redirects, verification file

sitemap = []
for f in sorted((SRC / "pages").glob("*.html")):
    meta, body = read_meta(f.read_text())
    stem = f.stem
    meta["path"] = "/" if stem == "index" else "/" + stem
    if stem == "404":
        meta["path"], meta["noindex"] = "/404", True
    faq = faq_from_body(body)
    if faq:
        meta["faq"] = faq
    write_page(f.name, meta, body)
    if not meta.get("noindex"):
        sitemap.append((DOMAIN + meta["path"], meta.get("date", BUILT)))

# Newest first; on the same day, the most recently created file first.
posts = sorted((read_post(f) for f in CONTENT.glob("*.md")), key=lambda p: (p["date"], p["slug"]), reverse=True)
posts = [p for p in posts if str(p.get("draft", "")).lower() != "true"]
for p in posts:
    meta = {"title": f"{p['title']} | K3 Professional Services", "description": p["description"],
            "active": "blog", "date": p["date"], "headline": p["title"],
            "image": DOMAIN + p["image"] if p["image"].startswith("/") else p["image"],
            "image_alt": p["image_alt"], "path": f"/blog/{p['slug']}", "crumb": p["title"]}
    write_page(f"blog/{p['slug']}.html", meta, post_page_body(p, [o for o in posts if o is not p]))
    sitemap.append((DOMAIN + meta["path"], p["date"]))

index_meta = {"title": "Career Advice Blog | K3 Professional Services",
              "description": "Practical guidance on resumes, interviews and changing direction, written by people who have sat on the hiring side of the table.",
              "active": "blog", "path": "/blog"}
write_page("blog.html", index_meta, blog_index_body(posts))
sitemap.append((DOMAIN + "/blog", posts[0]["date"] if posts else BUILT))

sitemap.sort()
(OUT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in sitemap)
    + "</urlset>\n")
(OUT / "robots.txt").write_text(
    f"User-agent: *\nAllow: /\nDisallow: /admin/\n\nSitemap: {DOMAIN}/sitemap.xml\n")
print(len(posts), "blog posts,", len(sitemap), "pages in sitemap")
