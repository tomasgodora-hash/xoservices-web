#!/usr/bin/env python3
"""Zostaví index.html zo src/template.html a src/i18n/*.json.

Použitie:  python3 build.py
Text zmeníš v src/i18n/<jazyk>.json (rovnaký kľúč vo všetkých 11 jazykoch),
vzhľad a štruktúru v src/template.html. index.html nikdy neupravuj ručne.
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
    s = s.replace('<ul class="values perks" id="perks"></ul>', '<ul class="values perks" id="perks">' + "".join(f"<li>{esc(t[f'perk{i}'])}</li>" for i in (1, 2, 3)) + "</ul>")
    s = s.replace('<ul class="values" id="values"></ul>', '<ul class="values" id="values">' + "".join(f"<li>{esc(t[f'value{i}'])}</li>" for i in (1, 2, 3, 4)) + "</ul>")
    s = s.replace('<ul class="roles" id="roles"></ul>', '<ul class="roles" id="roles">' + "".join(f"<li>{esc(r)}</li>" for r in t["roles"]) + "</ul>")
    return s.replace("{{metaDesc}}", html.escape(t["metaDesc"]))

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Zostaví web zo šablóny a prekladov.")
    ap.add_argument("--template", default="src/template.html", help="šablóna (predvolene src/template.html)")
    ap.add_argument("--out", default="index.html", help="výstupný súbor (predvolene index.html)")
    args = ap.parse_args()
    tr = load()
    tpl = (ROOT / args.template).read_text("utf-8")
    for code, d in tr.items(): check_banned(json.dumps(d, ensure_ascii=False), f"{code}.json")
    check_banned(tpl, "template.html")
    out = prerender(tpl, tr[DEFAULT])
    out = out.replace("/*__I18N__*/null", json.dumps(tr, ensure_ascii=False, separators=(",", ":")))
    if "{{" in out or "__I18N__" in out: fail("v šablóne ostal nevyplnený zástupný text")
    page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n')
    i = out.index("</style>") + len("</style>")
    page += out[:i] + "\n</head>\n<body>\n" + out[i:] + "\n</body>\n</html>\n"
    (ROOT / args.out).write_text(page, "utf-8")
    print(f"build: {args.out} hotový ({len(page)//1024} kB, {len(tr)} jazykov, {len(tr[DEFAULT])} kľúčov)")

if __name__ == "__main__":
    main()
