---
inclusion: always
---

# Workspace 3D: setup, convenzioni e piani

Workspace di progetti 3D parametrici per stampa FDM. Una cartella per progetto (BOMBONIERA, KORG SP 200, PRACTICE MUTE, GUN, ...). Lingua: italiano per codice, commenti e risposte.

## Stampante e slicer

- Creality Ender 3 V2: piatto in vetro, estrusore Bowden, Professional Firmware (mriscoc), slicer Cura 5.12.
- Filamento principale: PLA Bambu Lab. Ugello 0.4 di serie; ugello 0.2 per dettagli fini (es. Manneken della BOMBONIERA, layer 0.08–0.12).
- Volume utile: considerare circa 220 × 220 × 250 mm. Pezzi più grandi vanno divisi con un incastro (es. leggio KORG in metà).
- Calibrazione e profilo Cura: vedi `CALIBRATION/README.md` e `CALIBRATION/GUIDA_FILE.md`. Line width 0.42 mm, layer 0.2 mm.
- Tolleranze: convenzione `diametro_foro = diametro_perno + gioco` (gioco diametrale). Valori in uso: 0.25–0.30 mm per incastri a pressione o linguette, 0.5 mm per rotazione libera o sedi. Il valore misurato per questa macchina si ricava da `CALIBRATION/stl/02_tolleranze.stl`; se l'utente lo comunica, aggiornare questa sezione.

## Setup in breve

| Uso | Strumento |
|---|---|
| Progetti nuovi (es. corpo revolver GUN/corpo) | build123d + agentcad (MCP o CLI) |
| Manutenzione dei `.scad` esistenti (provino GUN, BOMBONIERA v7, ...) | OpenSCAD nightly |
| Stampabilità e interferenze tra STL | `tools/check_stampa.py` (trimesh + manifold3d) |
| Tempo di stampa, filamento, supporti | `tools/slice_stima.py` (CuraEngine 5.12 da CLI) |
| Parti scultoree, render fotografici | Blender 4.0.2 (`blender -b -P script.py`) |
| Metriche STL rapide (ingombro, massa) | `GUN/tools/stl_info.py` |

## OpenSCAD (manutenzione dei progetti esistenti)

- Installata la nightly **2026.10.31** come AppImage, senza sudo:
  - binario: `~/.local/opt/openscad/OpenSCAD-2026.10.31-x86_64.AppImage` (SHA-256 verificato)
  - comandi: `openscad` e `openscad-nightly`, symlink in `~/.local/bin` (già nel PATH)
  - menu: `~/.local/share/applications/openscad-nightly.desktop`; i file `.scad` (MIME `application/x-openscad`, definito in `~/.local/share/mime/packages/openscad.xml`) si aprono con la nightly
  - il pacchetto apt 2021.01 è stato rimosso dall'utente
- Backend predefinito: **Manifold**. Su `phone_holder_v7_horta.scad` il render scende da 31,6 s (2021.01, CGAL) a 0,76 s, con geometria identica (stesse dimensioni e massa).
- Compatibilità verificata il 31/10/2026 su tutti i `.scad` allora presenti (41; dopo il riordino di BOMBONIERA, che ha tenuto solo la v7 Horta, sono 33): nessun errore o warning. Restituiscono "top level object is empty" solo `GUN/lib.scad` e `GUN/params.scad` (librerie) e `KORG SP 200/leggio_korg_sp200.scad` (riga 44, `part = "left    "` con spazi finali; versione superata dalla v2).
- Aggiornamento: scaricare il nuovo AppImage da `https://files.openscad.org/snapshots/`, verificare il `.sha256`, `chmod +x`, poi rifare `ln -sf <nuovo file> ~/.local/bin/openscad` (e `openscad-nightly`). Aggiornare `Exec`/versione qui. La nightly non si aggiorna da sola.

### Comandi utili

```bash
openscad -o out.stl file.scad                              # export STL
openscad -o out.stl -D parte=\"perno\" file.scad           # parametro da riga di comando
openscad -o out.png --render --autocenter --viewall \
  --imgsize=1200,900 --colorscheme=Tomorrow file.scad      # render PNG headless
openscad -o out.stl --summary all --summary-file s.json file.scad  # metriche JSON
python3 GUN/tools/stl_info.py file.stl                     # ingombro (mm) e massa (g)
```

## Strumenti di verifica (root `tools/`, venv CAD)

```bash
.venv/bin/python tools/check_stampa.py pezzo.stl [...]            # stampabilita'
.venv/bin/python tools/check_stampa.py --interf a.stl b.stl c.stl # volume di intersezione per coppia
.venv/bin/python tools/slice_stima.py pezzo.stl [--supporti] [-s infill_sparse_density=30]
```

- `check_stampa.py`: Z del file = verso di stampa. Esce con 1 se non manifold, fuori piatto (220×220×250) o con interferenze; sbalzi, pareti sottili e corpi separati sono avvisi. Lo spessore pareti si misura con raggi tra facce quasi parallele, quindi ignora smussi e spigoli. Validato su casi noti e sugli STL del provino: ha trovato le pareti da 0.8 mm delle cartucce (`cart_parete = 0.8` < 0.84) e il `tappo` fatto di 2 corpi separati da 0.05 mm (flangia a `-L_tappo-1.55` con `h=1.5` in `provino_balistico.scad`).
- `slice_stima.py`: usa il profilo PLA di `CALIBRATION/README.md` (dizionario `PROFILO_PLA` nello script, da aggiornare dopo la calibrazione) sulla definizione `creality_ender3` con piatto 220×220. Risolve le formule delle definizioni Cura perché CuraEngine da solo non le valuta. Tempo e grammi vengono dal log del motore (l'intestazione del G-code in CLI ha segnaposto). Indica se servono supporti. Le stime sono quelle di Cura, indicative.
- CuraEngine 5.12: estratto da `~/.local/bin/cura.AppImage` in `~/.local/opt/curaengine/` (motore, librerie, definizioni, 31 MB), lanciato da `~/.local/bin/curaengine`, che usa il loader dell'AppImage con glibc/libstdc++ di sistema. Se si aggiorna Cura, rifare l'estrazione.
- Il profilo attuale salvato in Cura (`~/.local/share/cura/5.12`) è ancora quello ABS (245 °C, piatto 100 °C, layer 0.28, ventola spenta, materiale ABS generico): non usarlo come riferimento per il PLA.
- Blender 4.0.2 è installato di sistema: in background con `blender -b --factory-startup -P script.py`; import STL con `bpy.ops.wm.stl_import(filepath=...)` (verificato). Serve per forme scultoree (es. figure come i Manneken della BOMBONIERA, da importare poi come mesh) e render con materiali.
- Visualizzazione dal vivo dei modelli build123d: estensione "OCP CAD Viewer" di Kiro (pacchetto `ocp-vscode` già nel venv); va installata dall'utente dal pannello Extensions. Senza, usare `preview.png` di agentcad o `agentcad view`.

## Convenzioni per i file .scad

- Intestazione con commento: cosa fa il pezzo, materiale, orientamento di stampa, note di montaggio.
- Parametri in testa, raggruppati con sezioni Customizer (`/* [Sezione] */`) e range (`// [min:passo:max]`).
- Variabile di selezione `parte = "tutto"; // [tutto, a, b]` per esportare i singoli pezzi con `-D`.
- `$fn` globale tra 48 e 120 a seconda delle dimensioni.
- Tolleranze come parametri espliciti (`clearance`, `gioco_*`), mai numeri nascosti nel codice.
- Versioni successive come nuovo file (`_v2`, `_v3`) o in `archivio/`; render in `render_vN/` o `png/`; STL esportati in `stl/`.
- Script di export ripetuti in `tools/` del progetto (esempio: `GUN/tools/esporta_provino.sh`).

## Flusso di lavoro "linguaggio naturale → 3D"

1. Raccogliere i requisiti: misure reali (calibro o foto con righello), materiale, orientamento di stampa, dove agiscono le forze, priorità (estetica, robustezza, tempo di stampa). Chiedere le quote mancanti invece di inventarle; se si deve stimare, dichiararlo.
2. Scrivere lo script parametrico: build123d per i pezzi nuovi, `.scad` solo se si modifica un progetto OpenSCAD esistente. Stesse convenzioni (intestazione, parametri in testa, tolleranze esplicite, selezione della parte).
3. Verificare prima di consegnare: export STL senza errori, render PNG da più viste (3/4, lato, orientamento di stampa), poi `tools/check_stampa.py` (manifold, piatto, corpi separati, sbalzi > 55°, pareti < 0.84 mm; `--interf` per i pezzi che si accoppiano) e `tools/slice_stima.py` (tempo, grammi, supporti necessari). Ponti oltre ~35 mm vanno ancora controllati a vista.
4. Mostrare render e metriche, poi iterare sulle richieste dell'utente.
5. Dopo la stampa, se un accoppiamento non funziona, correggere il parametro di tolleranza (non la geometria a mano).

## build123d + agentcad (strumento per i progetti nuovi)

Decisione dell'utente (31/10/2026): i **progetti nuovi** si fanno in build123d. OpenSCAD resta per mantenere i file `.scad` esistenti e i loro script; non convertire in blocco. Si migra un progetto esistente solo quando va riprogettato in modo sostanziale (es. corpo del revolver GUN).

Setup installato:
- virtualenv `.venv/` nella root del workspace (Python 3.12, creato con `uv`), ignorato da git
- versioni fissate in `requirements-cad.txt`; ricreare con `uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements-cad.txt`
- `build123d 0.10.0` (non 0.11+: agentcad 0.7.1 richiede `build123d<0.11`), `cadquery-ocp 7.8.1`, `agentcad 0.7.1`, `ocp-vscode 4.2.0`, `trimesh 5.2.0`, `manifold3d 3.5.4`, `rtree 1.4.1` (ray casting di trimesh), `shapely 2.2.0` + `networkx 3.7` (geometria 2D: sezioni di mesh con `mesh.section(...).to_2D()`, offset/buffer, unioni e semplificazione di profili, controllo ponti e dettagli layer per layer)
- Export verificati da build123d: STEP, STL, 3MF (`Mesher`), testo 3D, import SVG
- agentcad non invia dati all'esterno, salvo i comandi `cloud`, `feedback`, `subscribe`: **non usarli**. Nel MCP sono disabilitati i tool `cloud_*`
- server MCP attivo, configurato in `.kiro/settings/mcp.json` (`.venv/bin/python -m agentcad.mcp`, `AGENTCAD_NO_LOG=1`, tool `cloud_*` disabilitati). L'agente non può modificare `.kiro/settings/`: eventuali cambi li fa l'utente. Tool disponibili: `run`, `render`, `measure`, `inspect`, `diff`, `export`, `check_spec`, `context`, `docs`, `import_cad`, `recover`, `view`. Se il server non risponde, usare la CLI `.venv/bin/agentcad`, che fa le stesse cose

Ciclo di lavoro (verificato con un pezzo di prova):

```bash
cd <cartella progetto>                       # es. GUN/corpo
../../.venv/bin/agentcad init --name corpo   # una volta: crea agentcad.json, .agentcad/, AGENTS.md, .claude/
../../.venv/bin/agentcad docs quickstart     # guida dell'agente; docs preamble per i nomi disponibili
../../.venv/bin/agentcad run corpo.py --label v1 --dry-run
../../.venv/bin/agentcad run corpo.py --label v1 --no-view   # -> v1_<label>/output.step + preview.png (4 viste)
../../.venv/bin/agentcad measure v1_v1/output.step           # dimensioni, volume, is_valid
../../.venv/bin/agentcad export v1_v1/output.step --format stl
```

- Negli script agentcad l'API build123d è già importata: niente `import`, `show_object(...)` per ogni parte.
- Leggere sempre `preview.png` e `metrics.is_valid: true` prima di consegnare; l'STL esportato viene verificato manifold da agentcad. Poi `GUN/tools/stl_info.py` per ingombro e massa.
- Raccordi: selezionare gli spigoli (es. `edges().group_by(Axis.Z)[-1]` = spigoli superiori). Se `fillet` fallisce, ridurre il raggio o raccordare prima delle booleane.
- Stampa in piano: raccordare gli spigoli superiori, non quelli sul piatto (sbalzo); sotto usare smussi a 45° o niente.
- Parametri condivisi con progetti OpenSCAD: non duplicarli a mano, leggerli dal `.scad` (es. `GUN/params.scad`) con un piccolo parser, così la fonte resta unica.

## Piano di migrazione

Stato: setup completato (passi 1 e 2); pilota in corso sul corpo del revolver GUN.

Motivazioni:
- OpenSCAD è vivo ma rilascia poco: l'ultima stable è 2021.01, è in preparazione una release 2026.xx (tag di test `openscad-2026.10-TEST4`). Con la nightly i problemi di velocità sono risolti, quindi non c'è urgenza.
- Limite strutturale di OpenSCAD: lavora con mesh, non B-rep. Raccordi e smussi selettivi richiedono `minkowski()`/`hull()` o costruzioni a mano; niente selezione di facce o spigoli; niente `shell` a parete costante; niente export STEP.
- build123d (Python, kernel OpenCASCADE, B-rep): `fillet`/`chamfer` su spigoli scelti, selettori di facce/spigoli, `shell`, curve esatte (risoluzione scelta all'export), export STEP/STL/3MF, tutto l'ecosistema Python. API ancora prima della 1.0, quindi fissare la versione.
- Alternative valutate e scartate come strumento principale: CadQuery (stesso kernel, API a catena meno leggibile); Zoo Design Studio/KCL (agente integrato ma cloud e linguaggio proprietario); FreeCAD o Fusion via MCP (pilotare una GUI è più fragile del codice versionato).
- Per il ciclo agentico: **agentcad** (open source, Apache-2.0, MCP + CLI, build123d) esegue lo script, restituisce metriche e render PNG ed esporta STEP/STL in locale, così l'agente verifica il proprio lavoro. Il suo benchmark (v0.7.0, punteggio 0,245) indica che i pezzi complessi richiedono ancora quote esplicite e iterazioni.

Passi previsti:
1. Creare un virtualenv nel workspace (Python 3.12) con `build123d` e `agentcad[mcp]` a versioni fissate.
2. Configurare agentcad in `.kiro/settings/mcp.json`.
3. Pilota: corpo finito del revolver in `GUN/corpo/` (build123d), con meccanica guidata da `GUN/params.scad` perché i test balistici non sono ancora fatti. Il provino OpenSCAD resta invariato. Valutare leggibilità, tempo di sviluppo, qualità dei raccordi, stampa. (In origine si pensava a TAPPO FLACONE o MORSETTO_MICROFONO; l'utente ha scelto GUN.)
4. Decidere in base al pilota. Migrare un progetto esistente solo quando va modificato in modo sostanziale; non convertire in blocco.

Passi 1 e 2 completati il 31/10/2026. Passo 3 in corso. Dopo il pilota, aggiornare questa sezione con l'esito e le motivazioni.
