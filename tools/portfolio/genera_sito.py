#!/usr/bin/env python3
"""Genera il sito portfolio statico da portfolio.yml.

Legge il manifest (tools/portfolio/portfolio.yml), copia le immagini referenziate
e produce in output/ una home con grid di card + una pagina per progetto.

Nessuna dipendenza CAD: solo PyYAML (gia' nel venv). Pensato per girare anche in CI.

Uso:
    python tools/portfolio/genera_sito.py [--manifest FILE] [--output DIR] [--base-url PREFIX]

--base-url serve su GitHub Pages di project (es. /nome-repo); default "" (root).
"""
from __future__ import annotations

import argparse
import hashlib
import html
import shutil
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Manca PyYAML. Installa con: .venv/bin/pip install pyyaml")

# Root del repo = due livelli sopra questo file (tools/portfolio/genera_sito.py)
REPO_ROOT = Path(__file__).resolve().parents[2]


# --------------------------------------------------------------------------- utils

def esc(testo) -> str:
    """Escape HTML, gestendo None."""
    return html.escape(str(testo)) if testo is not None else ""


def tonalita_da_id(progetto_id: str) -> int:
    """Hue 0-359 deterministico derivato dall'id, per l'accento di ogni progetto."""
    h = hashlib.sha1(progetto_id.encode("utf-8")).hexdigest()
    return int(h[:8], 16) % 360


def copia_immagine(src_rel: str, assets_dir: Path) -> str | None:
    """Copia un'immagine (path relativo alla root repo) in output/assets.

    Ritorna il path relativo usabile nell'HTML, oppure None se il file non esiste.
    """
    if not src_rel:
        return None
    src = (REPO_ROOT / src_rel).resolve()
    if not src.is_file():
        print(f"  ATTENZIONE: immagine mancante, saltata: {src_rel}", file=sys.stderr)
        return None
    # nome di destinazione: appiattito e univoco per evitare collisioni
    nome_dest = src_rel.replace("/", "__").replace(" ", "_")
    dest = assets_dir / nome_dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return f"assets/{nome_dest}"


# --------------------------------------------------------------------------- HTML

def head(titolo: str, base_url: str, hue: int | None = None, in_sottopagina: bool = False) -> str:
    accento = f"--hue: {hue};" if hue is not None else ""
    prefisso = base_url.rstrip("/")
    css_href = f"{prefisso}/style.css"
    return f"""<!DOCTYPE html>
<html lang="it" data-theme="dark"{f' style="{accento}"' if accento else ''}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(titolo)}</title>
<link rel="stylesheet" href="{css_href}">
</head>
<body>
<header class="topbar">
  <a class="brand" href="{prefisso}/index.html">◆ Progetti 3D</a>
  <button id="theme-toggle" class="theme-toggle" aria-label="Cambia tema">◐</button>
</header>
<main class="container">
"""


FOOT = """</main>
<footer class="footer">
  <span>Generato da portfolio.yml · stampa FDM</span>
</footer>
<script>
(function () {
  var key = "portfolio-theme";
  var root = document.documentElement;
  var saved = localStorage.getItem(key);
  if (saved) root.setAttribute("data-theme", saved);
  var btn = document.getElementById("theme-toggle");
  if (btn) btn.addEventListener("click", function () {
    var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    localStorage.setItem(key, next);
  });
})();
</script>
</body>
</html>
"""


def card_metriche(metriche: dict | None) -> str:
    if not metriche:
        return ""
    etichette = {
        "ingombro_mm": "Ingombro",
        "massa_g": "Massa",
        "tempo_stampa": "Stampa",
    }
    suffissi = {"ingombro_mm": " mm", "massa_g": " g", "tempo_stampa": ""}
    righe = []
    for chiave, etichetta in etichette.items():
        val = metriche.get(chiave)
        if val in (None, "", "null"):
            continue
        righe.append(
            f'<div class="metric"><span class="metric-k">{esc(etichetta)}</span>'
            f'<span class="metric-v">{esc(val)}{suffissi[chiave]}</span></div>'
        )
    if not righe:
        return ""
    return '<div class="metrics">' + "".join(righe) + "</div>"


def tag_html(tag: list | None) -> str:
    if not tag:
        return ""
    chip = "".join(f'<span class="tag">{esc(t)}</span>' for t in tag)
    return f'<div class="tags">{chip}</div>'


def genera_home(sito: dict, progetti: list[dict], base_url: str) -> str:
    prefisso = base_url.rstrip("/")
    titolo = sito.get("titolo", "Progetti 3D")
    out = [head(titolo, base_url)]
    out.append('<section class="hero">')
    out.append(f'<h1>{esc(titolo)}</h1>')
    if sito.get("sottotitolo"):
        out.append(f'<p class="hero-sub">{esc(sito["sottotitolo"])}</p>')
    if sito.get("descrizione"):
        out.append(f'<p class="hero-desc">{esc(sito["descrizione"])}</p>')
    out.append("</section>")

    out.append('<section class="grid">')
    for p in progetti:
        hue = tonalita_da_id(p["id"])
        cover = p.get("_cover_web")
        link = f'{prefisso}/progetti/{p["id"]}.html'
        out.append(f'<a class="card" href="{link}" style="--hue: {hue};">')
        if cover:
            out.append(f'<div class="card-media"><img loading="lazy" src="{prefisso}/{cover}" alt="{esc(p.get("titolo",""))}"></div>')
        else:
            out.append('<div class="card-media card-media--empty">nessun render</div>')
        out.append('<div class="card-body">')
        out.append(f'<h2 class="card-title">{esc(p.get("titolo", p["id"]))}</h2>')
        if p.get("descrizione"):
            out.append(f'<p class="card-desc">{esc(p["descrizione"])}</p>')
        out.append(tag_html(p.get("tag")))
        out.append("</div>")
        out.append("</a>")
    out.append("</section>")
    out.append(FOOT)
    return "".join(out)


def genera_pagina_progetto(p: dict, base_url: str) -> str:
    prefisso = base_url.rstrip("/")
    hue = tonalita_da_id(p["id"])
    titolo = p.get("titolo", p["id"])
    out = [head(f"{titolo} · Progetti 3D", base_url, hue=hue, in_sottopagina=True)]
    out.append(f'<a class="back" href="{prefisso}/index.html">← tutti i progetti</a>')
    out.append('<article class="progetto">')
    out.append(f'<h1 class="progetto-titolo">{esc(titolo)}</h1>')
    out.append(tag_html(p.get("tag")))
    if p.get("descrizione"):
        out.append(f'<p class="progetto-desc">{esc(p["descrizione"])}</p>')

    # scheda info laterale
    info = []
    for chiave, etichetta in (("materiale", "Materiale"), ("ugello", "Ugello"), ("stato", "Stato")):
        if p.get(chiave):
            info.append(f'<div class="info-row"><span>{etichetta}</span><strong>{esc(p[chiave])}</strong></div>')
    info.append(card_metriche(p.get("metriche")).replace("metrics", "metrics info-metrics"))
    if any(i for i in info if i):
        out.append('<aside class="info-card">' + "".join(info) + "</aside>")

    # galleria
    immagini = p.get("_img_web", [])
    if immagini:
        out.append('<section class="gallery">')
        for img in immagini:
            cap = f'<figcaption>{esc(img["didascalia"])}</figcaption>' if img.get("didascalia") else ""
            out.append(
                f'<figure class="shot"><img loading="lazy" src="{prefisso}/{img["src"]}" '
                f'alt="{esc(img.get("didascalia", titolo))}">{cap}</figure>'
            )
        out.append("</section>")
    else:
        out.append('<p class="vuoto">Nessun render disponibile per questo progetto.</p>')

    if p.get("sorgente"):
        out.append(f'<p class="sorgente">Sorgente: <code>{esc(p["sorgente"])}</code></p>')
    out.append("</article>")
    out.append(FOOT)
    return "".join(out)


# --------------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description="Genera il sito portfolio da portfolio.yml")
    ap.add_argument("--manifest", default=str(Path(__file__).with_name("portfolio.yml")))
    ap.add_argument("--output", default=str(Path(__file__).with_name("output")))
    ap.add_argument("--base-url", default="", help="Prefisso path per Pages di project (es. /3D)")
    args = ap.parse_args()

    manifest = Path(args.manifest)
    if not manifest.is_file():
        sys.exit(f"Manifest non trovato: {manifest}\n"
                 f"Compilalo seguendo tools/portfolio/AGENTE_PORTFOLIO.md")

    with manifest.open(encoding="utf-8") as f:
        dati = yaml.safe_load(f) or {}

    sito = dati.get("sito", {})
    progetti = dati.get("progetti", []) or []

    output = Path(args.output)
    if output.exists():
        shutil.rmtree(output)
    assets = output / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    (output / "progetti").mkdir(parents=True, exist_ok=True)

    # copia immagini e annota i path web risolti su ogni progetto
    for p in progetti:
        p["_cover_web"] = copia_immagine(p.get("copertina", ""), assets)
        imgs = []
        for img in p.get("immagini", []) or []:
            web = copia_immagine(img.get("src", ""), assets)
            if web:
                imgs.append({"src": web, "didascalia": img.get("didascalia")})
        # se non c'e' copertina esplicita ma ci sono immagini, usa la prima
        if not p["_cover_web"] and imgs:
            p["_cover_web"] = imgs[0]["src"]
        p["_img_web"] = imgs

    # scrivi CSS
    (output / "style.css").write_text(CSS, encoding="utf-8")

    # home
    (output / "index.html").write_text(
        genera_home(sito, progetti, args.base_url), encoding="utf-8"
    )

    # pagine progetto
    for p in progetti:
        pagina = genera_pagina_progetto(p, args.base_url)
        (output / "progetti" / f'{p["id"]}.html').write_text(pagina, encoding="utf-8")

    print(f"Sito generato in {output}")
    print(f"  progetti: {len(progetti)}")
    tot_img = sum(len(p.get('_img_web', [])) for p in progetti)
    print(f"  immagini copiate: {tot_img}")
    return 0


# --------------------------------------------------------------------------- CSS

CSS = """\
:root {
  --hue: 210;
  --radius: 14px;
  --maxw: 1100px;
  --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* tema scuro (default) */
html[data-theme="dark"] {
  --bg: #0e1116;
  --bg-elev: #161b22;
  --bg-elev-2: #1c232d;
  --fg: #e6edf3;
  --fg-dim: #9aa7b4;
  --border: #2a333d;
  --accent: hsl(var(--hue) 70% 62%);
  --accent-soft: hsl(var(--hue) 55% 62% / 0.14);
  --shadow: 0 10px 30px rgba(0,0,0,0.45);
}
/* tema chiaro */
html[data-theme="light"] {
  --bg: #f6f7f9;
  --bg-elev: #ffffff;
  --bg-elev-2: #eef1f4;
  --fg: #16202b;
  --fg-dim: #5a6b7b;
  --border: #dce1e7;
  --accent: hsl(var(--hue) 62% 44%);
  --accent-soft: hsl(var(--hue) 62% 44% / 0.10);
  --shadow: 0 8px 24px rgba(20,30,45,0.10);
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  font-family: var(--font);
  background: var(--bg);
  color: var(--fg);
  line-height: 1.55;
  transition: background .25s ease, color .25s ease;
}

.topbar {
  position: sticky; top: 0; z-index: 10;
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 22px;
  background: color-mix(in srgb, var(--bg) 82%, transparent);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border);
}
.brand { font-weight: 700; color: var(--fg); text-decoration: none; letter-spacing: .3px; }
.brand:hover { color: var(--accent); }
.theme-toggle {
  border: 1px solid var(--border); background: var(--bg-elev); color: var(--fg);
  width: 38px; height: 38px; border-radius: 10px; cursor: pointer; font-size: 18px;
  transition: background .2s, border-color .2s;
}
.theme-toggle:hover { border-color: var(--accent); }

.container { max-width: var(--maxw); margin: 0 auto; padding: 36px 22px 64px; }

.hero { margin-bottom: 40px; }
.hero h1 { font-size: clamp(28px, 5vw, 46px); margin: 0 0 8px; letter-spacing: -0.5px; }
.hero-sub { font-size: 18px; color: var(--accent); margin: 0 0 10px; font-weight: 600; }
.hero-desc { color: var(--fg-dim); max-width: 60ch; margin: 0; }

.grid {
  display: grid; gap: 22px;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
}
.card {
  display: flex; flex-direction: column;
  background: var(--bg-elev); border: 1px solid var(--border);
  border-radius: var(--radius); overflow: hidden; text-decoration: none; color: inherit;
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.card:hover { transform: translateY(-4px); box-shadow: var(--shadow); border-color: var(--accent); }
.card-media { aspect-ratio: 4/3; background: var(--bg-elev-2); overflow: hidden; }
.card-media img { width: 100%; height: 100%; object-fit: cover; display: block; }
.card-media--empty {
  display: flex; align-items: center; justify-content: center;
  color: var(--fg-dim); font-size: 14px;
}
.card-body { padding: 16px 18px 20px; border-top: 3px solid var(--accent); }
.card-title { margin: 0 0 6px; font-size: 19px; }
.card-desc { margin: 0 0 12px; color: var(--fg-dim); font-size: 14px;
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }

.tags { display: flex; flex-wrap: wrap; gap: 6px; }
.tag {
  font-size: 12px; padding: 3px 10px; border-radius: 999px;
  background: var(--accent-soft); color: var(--accent); font-weight: 600;
}

/* pagina progetto */
.back { display: inline-block; margin-bottom: 20px; color: var(--fg-dim); text-decoration: none; font-size: 14px; }
.back:hover { color: var(--accent); }
.progetto-titolo { font-size: clamp(26px, 4vw, 40px); margin: 0 0 12px; letter-spacing: -0.5px;
  border-left: 5px solid var(--accent); padding-left: 16px; }
.progetto-desc { color: var(--fg-dim); max-width: 65ch; font-size: 17px; margin: 14px 0 24px; }

.info-card {
  display: flex; flex-wrap: wrap; gap: 10px 26px;
  background: var(--bg-elev); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 16px 20px; margin-bottom: 28px;
}
.info-row { display: flex; flex-direction: column; font-size: 14px; }
.info-row span { color: var(--fg-dim); font-size: 12px; text-transform: uppercase; letter-spacing: .5px; }
.info-metrics { display: flex; gap: 22px; }
.metric { display: flex; flex-direction: column; }
.metric-k { color: var(--fg-dim); font-size: 12px; text-transform: uppercase; letter-spacing: .5px; }
.metric-v { font-weight: 600; }

.gallery { display: grid; gap: 18px; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }
.shot { margin: 0; background: var(--bg-elev); border: 1px solid var(--border);
  border-radius: var(--radius); overflow: hidden; }
.shot img { width: 100%; display: block; background: var(--bg-elev-2); }
.shot figcaption { padding: 10px 14px; font-size: 13px; color: var(--fg-dim); }

.vuoto { color: var(--fg-dim); }
.sorgente { margin-top: 30px; color: var(--fg-dim); font-size: 14px; }
.sorgente code { background: var(--bg-elev-2); padding: 2px 7px; border-radius: 6px; }

.footer { border-top: 1px solid var(--border); color: var(--fg-dim);
  text-align: center; padding: 24px; font-size: 13px; }
"""


if __name__ == "__main__":
    raise SystemExit(main())
