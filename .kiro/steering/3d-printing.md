---
inclusion: always
---

# Workspace 3D: setup, convenzioni e piani

Workspace di progetti 3D parametrici per stampa FDM. Una cartella per progetto (BOMBONIERA, KORG SP 200, PRACTICE MUTE, GUN, ...). Lingua: italiano per codice, commenti e risposte.

## Stampante e slicer

- Creality Ender 3 V2: piatto in vetro, estrusore Bowden, Professional Firmware (mriscoc), slicer Cura 5.12.
- Filamento principale: PLA Bambu Lab. Alcuni progetti vecchi (BOMBONIERA v2/v4/v5) erano pensati per ABS.
- Volume utile: considerare circa 220 × 220 × 250 mm. Pezzi più grandi vanno divisi con un incastro (es. leggio KORG in metà).
- Calibrazione e profilo Cura: vedi `CALIBRATION/README.md` e `CALIBRATION/GUIDA_FILE.md`. Line width 0.42 mm, layer 0.2 mm.
- Tolleranze: convenzione `diametro_foro = diametro_perno + gioco` (gioco diametrale). Valori in uso: 0.25–0.30 mm per incastri a pressione o linguette, 0.5 mm per rotazione libera o sedi. Il valore misurato per questa macchina si ricava da `CALIBRATION/stl/02_tolleranze.stl`; se l'utente lo comunica, aggiornare questa sezione.

## OpenSCAD (strumento attuale)

- Installata la nightly **2026.10.31** come AppImage, senza sudo:
  - binario: `~/.local/opt/openscad/OpenSCAD-2026.10.31-x86_64.AppImage` (SHA-256 verificato)
  - comandi: `openscad` e `openscad-nightly`, symlink in `~/.local/bin` (già nel PATH)
  - menu: `~/.local/share/applications/openscad-nightly.desktop`; i file `.scad` (MIME `application/x-openscad`, definito in `~/.local/share/mime/packages/openscad.xml`) si aprono con la nightly
  - il pacchetto apt 2021.01 è stato rimosso dall'utente
- Backend predefinito: **Manifold**. Su `phone_holder_v7_horta.scad` il render scende da 31,6 s (2021.01, CGAL) a 0,76 s, con geometria identica (stesse dimensioni e massa).
- Compatibilità verificata su tutti i 41 `.scad` del workspace: nessun errore o warning. Restituiscono "top level object is empty" solo `GUN/lib.scad` e `GUN/params.scad` (librerie) e `KORG SP 200/leggio_korg_sp200.scad` (riga 44, `part = "left    "` con spazi finali; versione superata dalla v2).
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
2. Scrivere il `.scad` parametrico secondo le convenzioni sopra.
3. Verificare prima di consegnare: export STL senza errori, solido manifold, render PNG da più viste (3/4, lato, orientamento di stampa), ingombro e massa con `stl_info.py`. Controllare sbalzi oltre ~55°, ponti oltre ~35 mm, pareti sotto 2 × line width (0.84 mm).
4. Mostrare render e metriche, poi iterare sulle richieste dell'utente.
5. Dopo la stampa, se un accoppiamento non funziona, correggere il parametro di tolleranza (non la geometria a mano).

## build123d + agentcad (strumento per i progetti nuovi)

Decisione dell'utente (31/10/2026): i **progetti nuovi** si fanno in build123d. OpenSCAD resta per mantenere i file `.scad` esistenti e i loro script; non convertire in blocco. Si migra un progetto esistente solo quando va riprogettato in modo sostanziale (es. corpo del revolver GUN).

Setup installato:
- virtualenv `.venv/` nella root del workspace (Python 3.12, creato con `uv`), ignorato da git
- versioni fissate in `requirements-cad.txt`; ricreare con `uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements-cad.txt`
- `build123d 0.10.0` (non 0.11+: agentcad 0.7.1 richiede `build123d<0.11`), `cadquery-ocp 7.8.1`, `agentcad 0.7.1`, `ocp-vscode 4.2.0`
- agentcad non invia dati all'esterno, salvo i comandi `cloud`, `feedback`, `subscribe`: **non usarli**. Nel MCP sono disabilitati i tool `cloud_*`
- server MCP in `.kiro/settings/mcp.json` (`.venv/bin/python -m agentcad.mcp`); va creato a mano dall'utente perché l'agente non può scrivere in `.kiro/settings/`. Se il server MCP non è disponibile, usare la CLI `.venv/bin/agentcad`, che fa le stesse cose

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
3. Pilota: riscrivere un progetto piccolo (TAPPO FLACONE o MORSETTO_MICROFONO) in build123d e confrontarlo con la versione OpenSCAD (leggibilità, tempo di sviluppo, qualità dei raccordi, stampa).
4. Decidere in base al pilota. Migrare un progetto esistente solo quando va modificato in modo sostanziale; non convertire in blocco.

Passi 1 e 2 completati il 31/10/2026 (il `mcp.json` va aggiunto dall'utente). Dopo il pilota, aggiornare questa sezione con l'esito e le motivazioni.
