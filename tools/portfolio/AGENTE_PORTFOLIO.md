# Guida agente: censimento repo, render e manifest del portfolio

Questo documento dice a un agente (Kiro o equivalente) **come preparare i dati** che la
GitHub Action userà per pubblicare il portfolio su GitHub Pages. L'obiettivo di una
sessione guidata da questo file è arrivare a un `tools/portfolio/portfolio.yml` completo e
accurato, con render presenti per ogni progetto che ne vale la pena, descrizioni scritte e
metadati reali.

**Cosa NON fa questo documento:** non descrive la Action né il generatore HTML. La Action
si limita a leggere `portfolio.yml` e i PNG già committati (decisione presa: la CI non
rigenera nulla). La rigenerazione dei render è un compito **manuale, locale, dell'agente**,
guidato da questo file.

Lingua: italiano per tutto (descrizioni, commenti, titoli).

---

## 0. Principi

1. **La fonte di verità è l'agente, non la CI.** I render si generano in locale con la
   toolchain della macchina (OpenSCAD nightly, venv build123d/agentcad, Blender, CuraEngine)
   e si committano. La Action pubblica ciò che trova.
2. **Vetrina curata, non muro di immagini.** Il repo contiene molti PNG intermedi (varianti
   `v1..vN`, `diff_*`, singoli `parts/*`). Nel portfolio va solo ciò che è scelto
   esplicitamente nel manifest. In caso di dubbio, meno immagini ma buone.
3. **Niente invenzioni.** Dimensioni, massa, tempi di stampa vanno **misurati** con gli
   strumenti del repo, non stimati a mente. Se un dato non è verificabile, ometterlo e dirlo.
4. **Non rigenerare ciò che è già buono.** Se un render esiste, è recente rispetto al
   sorgente e rappresenta bene il pezzo, riusarlo. Rigenerare solo se manca o è obsoleto
   (sorgente modificato dopo il PNG).
5. **Rispettare le convenzioni del workspace** descritte in `.kiro/steering/3d-printing.md`
   (toolchain, tolleranze, flusso "linguaggio naturale → 3D", struttura cartelle).

---

## 1. Passo 1 — Censimento del repository

Produrre un quadro di ogni progetto (una cartella di primo livello = un progetto; escludere
`.git`, `.venv`, `.kiro`, `tools`, `CALIBRATION`).

Per ogni progetto raccogliere:

- **Tipo sorgente**: `.scad` (OpenSCAD), `.py` (build123d/agentcad), misto, o nessuno.
- **File sorgente principale**: quale script rappresenta il pezzo "buono/finale" (ignorare
  `archivio/`, varianti fallite, `concept/`).
- **Render esistenti**: PNG presenti e se sembrano attuali (confronto data PNG vs data
  sorgente con `git log`/`stat`).
- **Metadati disponibili**: STL già esportati, output di `stl_info.py`, note nei README/`.md`.
- **Stato**: `completo` (sorgente + render buoni), `da_render` (sorgente ok, render mancanti
  o vecchi), `incompleto` (sorgente non pronto), `vuoto` (cartella senza sorgente utile).

Comandi utili (eseguire dalla root del repo):

```bash
# progetti di primo livello
ls -d */ | grep -vE '^(\.git|\.venv|\.kiro|tools|CALIBRATION)/'

# sorgenti per progetto (esclude ambienti e cartelle di lavoro agentcad)
find "<PROGETTO>" -type d \( -name .agentcad -o -name __pycache__ -o -name archivio \) -prune \
  -o -type f \( -iname '*.scad' -o -iname '*.py' \) -print | sort

# render esistenti
find "<PROGETTO>" -type d -name .agentcad -prune -o -type f -iname '*.png' -print | sort

# il sorgente è più recente del render? (se sì, il PNG è obsoleto)
git log -1 --format=%ci -- "<sorgente>"
git log -1 --format=%ci -- "<render.png>"
```

Stato noto al 2026-11-03 (verificare, non fidarsi ciecamente):

| Progetto | Sorgente | Render | Note |
|---|---|---|---|
| BOMBONIERA | `phone_holder_v7_horta.scad` (+ v8 build123d in corso) | sì, `render_v7/` | pezzo finale = v7 Horta; v8 è esplorazione |
| GUN | `provino_balistico.scad`, `corpo/` (build123d) | sì, `png/` e `corpo/png/` | molti PNG intermedi da NON pubblicare |
| KORG SP 200 | `leggio_korg_sp200_v2.scad`, `copri_fader_korg_sp200.scad` | no | da rendere |
| PRACTICE MUTE | `sordina_tromba.scad` | no | ha README e transcript |
| TRUMPET STAND | `supporto_tromba_con_sordina.scad` | no | da rendere |
| MORSETTO_MICROFONO | `morsetto_completo.scad` (+ pressore, tappo) | no | da rendere |
| TAPPO FLACONE | `tappo_flacone.scad` | no | da rendere |
| MAPPAMONDO | `boccola_mappamondo.scad` | no | pezzo piccolo |
| dosatore_lavastoviglie | `dosatore_lavastoviglie.scad` | no | da rendere |
| TOOTHPASTE SQUEEZER | `LUCHIX/ratchet_squeezer.scad` | no | da rendere |
| CALZASCARPE | nessuno | no | cartella vuota: escludere dal portfolio |

---

## 2. Passo 2 — Rigenerare i render mancanti o obsoleti

Rigenerare **solo** i progetti in stato `da_render`. Scegliere lo strumento in base al
sorgente. Convenzione cartelle: PNG in `png/` o `render_vN/` dentro il progetto; STL in `stl/`.

### 2a. Progetti OpenSCAD (`.scad`)

Render PNG headless da una vista 3/4 (preferita per copertina) e una laterale:

```bash
openscad -o "<PROGETTO>/png/<nome>_3q.png" --render --autocenter --viewall \
  --imgsize=1600,1200 --colorscheme=Tomorrow \
  --camera=0,0,0,55,0,25,0 "<PROGETTO>/<file>.scad"

openscad -o "<PROGETTO>/png/<nome>_lato.png" --render --autocenter --viewall \
  --imgsize=1600,1200 --colorscheme=Tomorrow \
  --camera=0,0,0,90,0,0,0 "<PROGETTO>/<file>.scad"
```

Se il file ha una variabile `parte`/`part` per selezionare il pezzo, rendere la vista
d'assieme (`parte="tutto"` o equivalente) per la copertina:

```bash
openscad -o out.png -D 'parte="tutto"' ... "<file>.scad"
```

### 2b. Progetti build123d/agentcad (`.py`)

Usare agentcad, che produce già `preview.png` (4 viste):

```bash
cd "<PROGETTO>"
../../.venv/bin/agentcad run <script>.py --label portfolio --no-view
# -> portfolio_<label>/output.step + preview.png
```

La `preview.png` di agentcad va bene come copertina. Per render curati usare lo script
Blender del progetto se presente (es. `BOMBONIERA/v8/blender/render_varianti.py`).

### 2c. Render fotografici (Blender)

Solo per i pezzi scultorei o quando serve qualità da vetrina. Partire dallo STL esportato:

```bash
blender -b --factory-startup -P "<PROGETTO>/blender/<script>.py"
```

### Verifica dopo ogni render

- Aprire il PNG e controllare che inquadri bene il pezzo (non tagliato, non minuscolo).
- Per gli STL generati lungo il percorso, passare da `tools/check_stampa.py` e annotare se
  risultano problemi (serve per la descrizione, non blocca il portfolio).

---

## 3. Passo 3 — Misurare i metadati (opzionali ma consigliati)

Per ogni progetto in vetrina, raccogliere dati **reali** da mostrare nelle card. Ometterli se
non misurabili (non inventarli).

```bash
# ingombro (mm) e massa stimata (g) da uno STL orientato come si stampa
.venv/bin/python GUN/tools/stl_info.py "<PROGETTO>/stl/<pezzo>.stl"

# tempo di stampa, grammi di filamento, se servono supporti (stime Cura, indicative)
.venv/bin/python tools/slice_stima.py "<PROGETTO>/stl/<pezzo>.stl" [--supporti]
```

Metadati da proporre per card: ingombro `X×Y×Z mm`, massa `g`, tempo stampa `h:mm`,
materiale (default PLA), ugello (0.4 salvo note), stato (`stampato`/`da stampare`).

---

## 4. Passo 4 — Compilare/aggiornare `portfolio.yml`

Il manifest è la **fonte unica** di cosa va in vetrina. Schema proposto (YAML in
`tools/portfolio/portfolio.yml`; i percorsi immagine sono relativi alla root del repo):

```yaml
sito:
  titolo: "Progetti 3D — Luc"
  sottotitolo: "Pezzi parametrici per stampa FDM"
  descrizione: "Portfolio di progetti stampati in 3D, da OpenSCAD e build123d."

progetti:
  - id: bomboniera
    titolo: "Bomboniera panchina"
    descrizione: >
      Panchina in stile Art Nouveau (variante Horta) con figure Manneken Pis.
      Modulare, stampata a pezzi e incastrata.
    tag: [decorativo, art-nouveau, modulare]
    materiale: PLA
    ugello: "0.4 / 0.2 per i dettagli"
    stato: stampato
    copertina: BOMBONIERA/render_v7/2_vuota.png
    immagini:
      - { src: BOMBONIERA/render_v7/1_con_telefono.png, didascalia: "In uso" }
      - { src: BOMBONIERA/render_v7/5_fermo.png,        didascalia: "Fermo" }
    metriche:
      ingombro_mm: null      # compilare con stl_info.py se disponibile
      massa_g: null
      tempo_stampa: null
    sorgente: BOMBONIERA/phone_holder_v7_horta.scad

  # ... un blocco per progetto in vetrina ...

escludi:
  - CALZASCARPE        # cartella vuota
  - CALIBRATION        # utility di calibrazione, non un progetto
```

Regole di compilazione:

- **Un blocco per progetto** con stato `completo`. I progetti `da_render` entrano solo dopo
  aver generato i render (passo 2). Gli `incompleto`/`vuoto` vanno in `escludi` con motivo.
- **Copertina**: preferire una vista 3/4 d'assieme. Mai una `diff_*` o un singolo `parts/*`.
- **immagini**: massimo ~4-6 per progetto, scelte, con didascalia breve.
- **Non referenziare PNG dentro `.agentcad/`** (cartelle di lavoro): sono intermedi.
- **descrizione**: 1-3 frasi, concrete (a cosa serve il pezzo, com'è fatto/stampato).
  Attingere ai README dei progetti dove esistono (`PRACTICE MUTE/README.md`, ecc.).
- **metriche**: valorizzare solo i campi misurati; lasciare `null` gli altri.
- Mantenere l'ordine dei progetti dal più rappresentativo al meno.

---

## 5. Passo 5 — Igiene del repository (fare una volta)

- Verificare se `.agentcad/` è tracciato da git. Contiene artefatti di lavoro (candidate,
  geometry, preview intermedie) che **non** dovrebbero stare nel repo né nel portfolio.
  Se tracciato, proporre all'utente di aggiungerlo a `.gitignore` e rimuoverlo dall'indice
  (`git rm -r --cached`). **Non** rimuovere file senza conferma dell'utente.
- Assicurarsi che i PNG scelti per il portfolio siano effettivamente committati (la Action
  vede solo ciò che è nel repo).

---

## 6. Risultato atteso di una sessione

1. `tools/portfolio/portfolio.yml` presente e completo, validabile (`python -c "import yaml,sys;
   yaml.safe_load(open('tools/portfolio/portfolio.yml'))"`).
2. Ogni progetto in `progetti:` ha copertina e immagini che esistono su disco e sono committate.
3. Render mancanti generati e salvati nelle cartelle del progetto.
4. Metadati reali dove misurabili; `null` dove no.
5. Un riassunto all'utente: cosa è stato reso, cosa escluso e perché, quali dati mancano.

Dopo questo, la GitHub Action + il generatore HTML possono essere scritti sapendo che
`portfolio.yml` è la loro unica sorgente.
