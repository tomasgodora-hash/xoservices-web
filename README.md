# xoservices.eu

Firemný web XO-SERVICES s. r. o. Statická stránka na GitHub Pages, 11 jazykov, štýl XO (biela, čierna, vodoznak XO).

## Kde je čo

| Čo | Kde |
|---|---|
| Kód webu | tento repozitár (`tomasgodora-hash/xoservices-web`) |
| Hosting | GitHub Pages, vetva `main`, koreň repozitára |
| Doména a DNS | Websupport (admin.websupport.sk) |
| Pošta info@xoservices.eu | Websupport |
| Certifikát HTTPS | GitHub Pages (Let's Encrypt), obnovuje sa sám |

## Ako zmeniť text

1. Uprav `src/i18n/<jazyk>.json`. Každý kľúč musí byť vo všetkých 11 jazykoch.
2. Spusti `python3 build.py`. Skontroluje preklady a vygeneruje `index.html`.
3. Commit + push do `main`. Web sa zmení do 1–2 minút.

Vzhľad a štruktúra sú v `src/template.html`. **`index.html` nikdy neupravuj ručne**, pri ďalšom builde by sa zmena stratila.

## Súbory

- `src/template.html` – šablóna stránky (HTML, CSS, JS)
- `src/i18n/*.json` – texty (en, sk, cs, pl, de, fr, nl, es, it, pt, ro)
- `build.py` – zostavenie a kontroly
- `index.html` – vygenerovaná stránka (needitovať)
- `privacy.html` – ochrana osobných údajov (SK + EN)
- `404.html`, `robots.txt`, `sitemap.xml`, `og.png` (náhľad pri zdieľaní), `logo.png`
- `fonts/` – písmo Inter (licencia SIL OFL 1.1, `fonts/LICENSE-Inter.txt`)
- `CNAME` – doména. **Doménu nemeň v nastaveniach GitHubu, len tento súbor.**
