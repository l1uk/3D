#!/usr/bin/env bash
# Esporta il copritasto clacson in STL stampabile.
#   1. agentcad run  -> genera lo STEP e la preview
#   2. agentcad export -> STL grezzo
#   3. trimesh salda i vertici ai bordi delle calotte (STL watertight)
# Uso:  bash tools/esporta_stl.sh
set -euo pipefail
cd "$(dirname "$0")/.."                 # cartella PULSANTE
VENV=../.venv/bin

LABEL=${1:-finale}
$VENV/agentcad run tasto.py --label "$LABEL" --no-view >/dev/null
# individua l'ultima cartella vN_LABEL generata
DIR=$(ls -dt v*_"$LABEL" | head -1)
$VENV/agentcad export "$DIR/output.step" --format stl >/dev/null

# riparazione: salda i vertici duplicati ai bordi dei bollini
$VENV/python - "$DIR/output.stl" <<'PY'
import sys, trimesh
m = trimesh.load(sys.argv[1])
m.merge_vertices()
m.update_faces(m.nondegenerate_faces())
m.update_faces(m.unique_faces())
m.remove_unreferenced_vertices()
m.fix_normals()
assert m.is_watertight, "STL non watertight dopo la riparazione"
m.export("tasto_clacson.stl")
print(f"OK  tasto_clacson.stl  volume {m.volume/1000:.3f} cm3  watertight={m.is_watertight}")
PY
