#!/usr/bin/env python3
"""Zostaví web zo src/template.html, src/i18n/*.json a src/privacy/*.html:
index.html (angličtina), <jazyk>/index.html, privacy.html, <jazyk>/privacy.html a sitemap.xml.

Použitie:  python3 build.py
Text zmeníš v src/i18n/<jazyk>.json (rovnaký kľúč vo všetkých 11 jazykoch),
vzhľad a štruktúru v src/template.html. Vygenerované HTML súbory nikdy neupravuj ručne.
"""
import hashlib, html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ORDER = ["en", "sk", "cs", "pl", "de", "fr", "nl", "es", "it", "pt", "ro"]
DEFAULT = "en"
# Slová, ktoré sa na verejnom webe nesmú objaviť (uložené ako SHA-256, aby ich repozitár nezverejnil).
BANNED = {
    "21a91522f40e53f3746a0204679423ef532946fec1c405af5666a12b2f873ed5",
    "00e67fcbad7785c90ebf49d9611bb9bfb4c3373b1aada5011d268d4f1ddd73e9",
    "bbdefa2950f49882f295b1285d4fa9dec45fc4144bfb07ee6acc68762d12c2e3",
    "6f3573e11b64105f586ca9f9f1fbe2fb9f14f0f89cd99cf20b21e8097609fd98",
    "faf5748b85f02aa56dc0b396c27354dcb3eab4d0caf5b5c9022a7e7fc92f8c35",
}

def fail(msg):
    print("build: CHYBA –", msg); sys.exit(1)

def load():
    tr = {}
    for code in ORDER:
        f = ROOT / "src" / "i18n" / f"{code}.json"
        if not f.exists(): fail(f"chýba súbor {f.relative_to(ROOT)}")
        tr[code] = json.loads(f.read_text("utf-8"))
    keys = set(tr[DEFAULT])
    for code, d in tr.items():
        miss, extra = keys - set(d), set(d) - keys
        if miss: fail(f"{code}.json nemá kľúče: {', '.join(sorted(miss))}")
        if extra: fail(f"{code}.json má navyše kľúče: {', '.join(sorted(extra))}")
    return tr

def check_banned(text, where):
    for w in re.findall(r"[a-z0-9][a-z0-9\-]{2,}", text.lower()):
        if hashlib.sha256(w.encode()).hexdigest() in BANNED:
            fail(f"{where}: obsahuje slovo, ktoré nesmie byť verejne (pozri CLAUDE.md, časť Diskrétnosť)")

def esc(t): return html.escape(t, quote=False)

def prerender(s, t):
    def fill(m):
        open_tag, tag, key, inner, close = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
        v = t.get(key)
        return open_tag + (esc(v) if isinstance(v, str) else inner) + close
    s = re.sub(r'(<(\w+)\b[^>]*\bdata-t="(\w+)"[^>]*>)(.*?)(</\2>)', fill, s, flags=re.S)
    lines = t["heroHead"].split("\n")
    s = s.replace('<h1 id="h-hero"></h1>', '<h1 id="h-hero">' + " ".join(f"<span>{esc(l)}</span>" for l in lines) + "</h1>")
    s = s.replace('<ul class="subline caps" id="subline"></ul>', '<ul class="subline caps" id="subline">' + "".join(f"<li>{esc(t[k])}</li>" for k in ("service2", "service4", "service5", "service1")) + "</ul>")
    rows = "".join(
        f'<article class="row"><div><h3>{esc(t[f"offering{i}Title"])}</h3><p class="txt">{esc(t[f"offering{i}Text"])}</p></div>'
        f'<ul class="items">' + "".join(f"<li>{esc(t[f'offering{i}Item{j}'])}</li>" for j in (1, 2, 3, 4) if f'offering{i}Item{j}' in t) + "</ul></article>"
        for i in (1, 2, 3))
    s = s.replace('<div class="rows" id="offerings"></div>', f'<div class="rows" id="offerings">{rows}</div>')
    pics = [("img/cables.jpg", "35% 40%"), ("img/frames.jpg", "50% 60%"), ("img/crane.jpg", "50% 88%")]
    tiles = "".join(
        f'<article class="tile"><figure><img src="{pics[i-1][0]}" alt="" loading="lazy" style="object-position:{pics[i-1][1]}"></figure>'
        f'<h3>{esc(t[f"offering{i}Title"])}</h3><p>{esc(t[f"offering{i}Text"])}</p>'
        f'<ul class="items">' + "".join(f"<li>{esc(t[f'offering{i}Item{j}'])}</li>" for j in (1, 2, 3, 4) if f'offering{i}Item{j}' in t) + "</ul></article>"
        for i in (1, 2, 3))
    s = s.replace('<div class="tiles" id="offerings"></div>', f'<div class="tiles" id="offerings">{tiles}</div>')
    s = s.replace('alt="" fetchpriority="high"', f'alt="{esc(t["photoAlt"])}" fetchpriority="high"')
    s = s.replace('<ul class="values perks" id="perks"></ul>', '<ul class="values perks" id="perks">' + "".join(f"<li>{esc(t[f'perk{i}'])}</li>" for i in (1, 2, 3)) + "</ul>")
    s = s.replace('<ul class="values" id="values"></ul>', '<ul class="values" id="values">' + "".join(f"<li>{esc(t[f'value{i}'])}</li>" for i in (1, 2, 3, 4)) + "</ul>")
    s = s.replace('<ul class="roles" id="roles"></ul>', '<ul class="roles" id="roles">' + "".join(f"<li>{esc(r)}</li>" for r in t["roles"]) + "</ul>")
    return s.replace("{{metaDesc}}", html.escape(t["metaDesc"]))

SITE = "https://xoservices.eu"
OG_LOCALE = {"en": "en_GB", "sk": "sk_SK", "cs": "cs_CZ", "pl": "pl_PL", "de": "de_DE", "fr": "fr_FR",
             "nl": "nl_NL", "es": "es_ES", "it": "it_IT", "pt": "pt_PT", "ro": "ro_RO"}

def url(code): return SITE + ("/" if code == DEFAULT else f"/{code}/")
def path(code): return "index.html" if code == DEFAULT else f"{code}/index.html"
def privacy_path(code): return "privacy.html" if code == DEFAULT else f"{code}/privacy.html"

def title(t): return "XO-SERVICES | " + t["pageTitle"]

def jsonld(t):
    org = {
        "@context": "https://schema.org", "@type": "Organization",
        "name": "XO-SERVICES s. r. o.", "alternateName": "XO-SERVICES", "url": SITE + "/",
        "logo": SITE + "/logo.png", "image": SITE + "/og.png", "description": t["metaDesc"],
        "email": "info@xoservices.eu", "telephone": "+421908975983",
        "vatID": "SK2122656217", "taxID": "2122656217",
        "identifier": {"@type": "PropertyValue", "propertyID": "IČO", "value": "57302880"},
        "address": {"@type": "PostalAddress", "streetAddress": "Jenisejská 45A", "postalCode": "040 12",
                    "addressLocality": "Košice", "addressCountry": "SK"},
        "areaServed": "Europe", "knowsLanguage": ["en", "sk", "pl"],
        "sameAs": ["https://www.instagram.com/xoservices_/"],
    }
    return json.dumps(org, ensure_ascii=False).replace("</", "<\\/")

def wrap(code, out):
    page = (f'<!doctype html>\n<html lang="{code}">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n')
    i = out.index("</style>") + len("</style>")
    return page + out[:i] + "\n</head>\n<body>\n" + out[i:] + "\n</body>\n</html>\n"

def main():
    import argparse, datetime
    ap = argparse.ArgumentParser(description="Zostaví web zo šablóny a prekladov.")
    ap.add_argument("--template", default="src/template.html", help="šablóna (predvolene src/template.html)")
    args = ap.parse_args()
    tr = load()
    tpl = (ROOT / args.template).read_text("utf-8")
    for code, d in tr.items(): check_banned(json.dumps(d, ensure_ascii=False), f"{code}.json")
    check_banned(tpl, "template.html")
    alts = "\n".join(f'<link rel="alternate" hreflang="{c}" href="{url(c)}">' for c in ORDER) + \
           f'\n<link rel="alternate" hreflang="x-default" href="{url(DEFAULT)}">'
    for code in ORDER:
        t = tr[code]
        out = prerender(tpl, t)
        out = out.replace("/*__I18N__*/null", json.dumps({code: t}, ensure_ascii=False, separators=(",", ":")))
        out = (out.replace("{{title}}", html.escape(title(t))).replace("{{url}}", url(code))
                  .replace("{{hreflang}}", alts).replace("{{ogLocale}}", OG_LOCALE[code])
                  .replace("{{jsonld}}", jsonld(t)).replace("{{lang}}", code)
                  .replace("{{privacyUrl}}", "/" + privacy_path(code)))
        if "{{" in out or "__I18N__" in out: fail(f"{code}: v šablóne ostal nevyplnený zástupný text")
        page = wrap(code, out)
        f = ROOT / path(code); f.parent.mkdir(exist_ok=True); f.write_text(page, "utf-8")
    build_privacy(tr)
    today = datetime.date.today().isoformat()
    links = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{c}" href="{url(c)}"/>' for c in ORDER) + \
            f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{url(DEFAULT)}"/>'
    sm = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
          'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' +
          "".join(f"  <url>\n    <loc>{url(c)}</loc>\n    <lastmod>{today}</lastmod>{links}\n  </url>\n" for c in ORDER) +
          "</urlset>\n")
    (ROOT / "sitemap.xml").write_text(sm, "utf-8")
    print(f"build: {len(ORDER)} jazykových stránok + ochrana údajov + sitemap.xml hotové ({len(tr[DEFAULT])} kľúčov)")

PRIV_SHELL = """<!doctype html>
<html lang="{code}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | XO-SERVICES</title>
<meta name="robots" content="noindex">
<link rel="icon" href="/logo.png">
<style>
@font-face{{font-family:"Inter";font-weight:400;font-display:swap;src:url(/fonts/inter-400.woff) format("woff")}}
@font-face{{font-family:"Inter";font-weight:700;font-display:swap;src:url(/fonts/inter-700.woff) format("woff")}}
@font-face{{font-family:"Inter";font-weight:900;font-display:swap;src:url(/fonts/inter-900.woff) format("woff")}}
:root{{--paper:#fff;--ink:#111;--grey:#666;--line:#dedede;color-scheme:light}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);font:400 1.0625rem/1.65 "Inter","Helvetica Neue",Arial,sans-serif}}
::selection{{background:var(--ink);color:var(--paper)}}
a{{color:inherit;text-underline-offset:.2em}}
:focus-visible{{outline:2px solid var(--ink);outline-offset:3px}}
.wrap{{max-width:46rem;margin:0 auto;padding:2.5rem max(16px,env(safe-area-inset-left,0px)) 4rem}}
header{{display:flex;align-items:center;justify-content:space-between;gap:1rem;border-bottom:1px solid var(--line);padding-bottom:1.25rem;margin-bottom:2.5rem}}
header img{{height:2.6rem;width:auto}}
header a{{font-weight:700;display:inline-flex;align-items:center;min-height:44px}}
h1{{font-weight:900;text-transform:uppercase;letter-spacing:-.03em;line-height:1;font-size:clamp(1.75rem,6vw,3.2rem);margin:0 0 1.5rem;text-wrap:balance;hyphens:auto;-webkit-hyphens:auto;overflow-wrap:break-word}}
h2{{font-size:1.25rem;font-weight:700;margin:2.2rem 0 .5rem}}
p,ul{{margin:.5rem 0}}
li{{margin:.35rem 0}}
.muted{{color:var(--grey);font-size:.9375rem}}
</style>
</head>
<body>
<div class="wrap">
<header><a href="{home}"><img src="/logo-sm.png" alt="XO-SERVICES" width="180" height="113"></a><a href="{home}">← xoservices.eu</a></header>
<main>
{body}
</main>
</div>
</body>
</html>
"""

def build_privacy(tr):
    for code in ORDER:
        src = ROOT / "src" / "privacy" / f"{code}.html"
        if not src.exists(): fail(f"chýba {src.relative_to(ROOT)}")
        body = src.read_text("utf-8")
        check_banned(body, src.name)
        m = re.search(r"<h1>(.*?)</h1>", body)
        f = ROOT / privacy_path(code); f.parent.mkdir(exist_ok=True)
        f.write_text(PRIV_SHELL.format(code=code, title=m.group(1) if m else "Privacy", home=url(code).replace(SITE, ""), body=body), "utf-8")

if __name__ == "__main__":
    main()
