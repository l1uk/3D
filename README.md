# Progetti 3D

Pezzi parametrici per stampa FDM su Ender 3 V2 (PLA, Cura 5.12). Una cartella per progetto.
Convenzioni, setup completo e piano di migrazione sono in [`.kiro/steering/3d-printing.md`](.kiro/steering/3d-printing.md).
Calibrazione della stampante: [`CALIBRATION/README.md`](CALIBRATION/README.md).

## Strumenti

| Uso | Strumento |
|---|---|
| Progetti nuovi | build123d + agentcad (Python, B-rep, export STEP/STL/3MF) |
| Progetti esistenti `.scad` | OpenSCAD nightly (comando `openscad`, motore Manifold) |
| Stampabilità e interferenze | `tools/check_stampa.py` |
| Tempo di stampa, filamento, supporti | `tools/slice_stima.py` (CuraEngine 5.12) |
| Forme scultoree, render | Blender |
| Raffinamento automatico con agenti | [`tools/harness/`](tools/harness/README.md) |

## Ambiente Python

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements-cad.txt
```

Le versioni sono fissate: build123d resta a 0.10.x perché agentcad 0.7.1 richiede `build123d<0.11`.

## Verifica di un pezzo

```bash
.venv/bin/python tools/check_stampa.py pezzo.stl                 # manifold, piatto, sbalzi, pareti
.venv/bin/python tools/check_stampa.py --interf a.stl b.stl      # parti che si accoppiano
.venv/bin/python tools/slice_stima.py pezzo.stl [--supporti]     # tempo, grammi, supporti
```

Il file STL va orientato come si stampa (Z verso l'alto, piano a z = 0).
`slice_stima.py` usa il profilo PLA di `CALIBRATION/README.md` (dizionario `PROFILO_PLA` nello script): aggiornarlo dopo la calibrazione.

## Dipendenze esterne (fuori dal repository)

- OpenSCAD nightly: `~/.local/opt/openscad/`, link `~/.local/bin/openscad`
- CuraEngine: estratto da `~/.local/bin/cura.AppImage` in `~/.local/opt/curaengine/`, lanciato da `~/.local/bin/curaengine`
- Blender 4.0.2 di sistema
- Server MCP agentcad per Kiro: `.kiro/settings/mcp.json`
