# Portfolio (GitHub Pages)

Sito statico che mostra i progetti 3D del repo. Una home con grid di card + una
pagina per progetto. Tema dark/light con toggle, accento di colore per progetto.

## Pezzi

| File | Ruolo |
|---|---|
| `portfolio.yml` | Manifest: fonte unica di cosa va in vetrina (titoli, descrizioni, immagini, metriche) |
| `genera_sito.py` | Generatore statico: legge il manifest, copia le immagini, scrive `output/` |
| `AGENTE_PORTFOLIO.md` | Guida per l'agente: censire il repo, rigenerare i render mancanti, compilare il manifest |
| `../../.github/workflows/portfolio.yml` | Action: a ogni push genera e pubblica su Pages |

## Flusso

1. **Preparare i dati** (manuale, locale): seguire `AGENTE_PORTFOLIO.md` per generare i
   render mancanti e compilare/estendere `portfolio.yml`. I render si committano nel repo.
2. **Generare in locale** per anteprima:
   ```bash
   .venv/bin/python tools/portfolio/genera_sito.py
   python3 -m http.server -d tools/portfolio/output 8000   # http://localhost:8000
   ```
3. **Pubblicare**: push su `main`. La Action rigenera il sito e lo mette su Pages.
   La CI **non** rigenera i render CAD: usa i PNG gia' committati.

## Base URL

Su Pages di project l'URL e' `https://<utente>.github.io/<repo>/`, quindi gli asset
vanno sotto `/<repo>`. La Action passa `--base-url /<repo>` in automatico. In locale il
default `""` va bene con `http.server` servito dalla cartella `output/`.

## Attivare Pages (una volta, sul sito GitHub)

Settings → Pages → Source: **GitHub Actions**. Poi il primo push su `main` pubblica.

## Dipendenze

Solo `pyyaml` (gia' nel venv; in CI `pip install pyyaml`). Nessuna dipendenza CAD.
