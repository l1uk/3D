#!/usr/bin/env bash
# Rigenera le due varianti di fianco: agentcad (STEP + preview + STL validato),
# STL separati in varianti/, controlli di stampa, slicing, render Blender.
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$(cd ../.. && pwd)
PY=$ROOT/.venv/bin/python
$ROOT/.venv/bin/agentcad run fianchi_varianti.py --label fianchi_AB --no-view --no-diff --export stl 2>/dev/null \
    | tail -1 > /tmp/agentcad_run.json
DIR=$($PY -c "
import json; d=json.load(open('/tmp/agentcad_run.json'))
assert d['status']=='success' and d['metrics']['is_valid'], d.get('message')
assert d['mesh_validation']['stl']['is_valid']
print(d['outputs']['step'].rsplit('/',1)[0])")
echo "agentcad: $DIR  is_valid=true, STL manifold"
mkdir -p varianti render
$PY - "$DIR" <<'EOF'
import sys, trimesh
m = trimesh.load(f"{sys.argv[1]}/output.stl")
parti = sorted(m.split(only_watertight=False), key=lambda p: p.bounds[0][1])
for nome, p in zip(["A_classica", "B_coup_de_fouet"], parti):
    p.apply_translation([0, -p.bounds[0][1], -p.bounds[0][2]])
    p.export(f"varianti/fianco_{nome}.stl")
EOF
(cd $ROOT && $PY tools/check_stampa.py BOMBONIERA/v8/varianti/fianco_*.stl \
  && $PY tools/slice_stima.py BOMBONIERA/v8/varianti/fianco_*.stl)
cp "$DIR/preview.png" render/fianchi_varianti_agentcad.png
blender -b --factory-startup -P blender/render_varianti.py >/dev/null 2>&1
echo "render: render/fianchi_varianti_AB.png"
