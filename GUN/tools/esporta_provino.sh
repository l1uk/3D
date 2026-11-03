#!/usr/bin/env bash
# Esporta tutti gli STL del provino, controlla le collisioni e rigenera i render.
# Uso: tools/esporta_provino.sh   (dalla cartella GUN)
set -euo pipefail
cd "$(dirname "$0")/.."
SCAD=provino_balistico.scad
mkdir -p stl/provino png

parti=(telaio camera percussore pomolo tappo canna_8 canna_6 volata
       proiettile_diabolo proiettile_volano proiettile_ogiva
       canna_c cartuccia_chiusa cartuccia_aperta cartuccia_corta)
for p in "${parti[@]}"; do
  openscad -q -o "stl/provino/$p.stl" -D modalita=\"parte\" -D parte=\"$p\" "$SCAD"
done
# bossoli e camera_c: una variante per ogni interferenza (tacche = indice+1)
for b in bossolo_8 bossolo_6 camera_c; do
  for v in 0 1 2; do
    openscad -q -o "stl/provino/${b}_v$((v+1)).stl" -D modalita=\"parte\" \
      -D parte=\"$b\" -D variante=$v "$SCAD"
  done
done

echo "== Controllo collisioni (deve essere vuoto)"
esito=0
for m in diabolo volano ogiva bb cart_chiusa cart_aperta cart_corta; do
  for s in armato sparato; do
    out=$(mktemp --suffix=.stl); rm -f "$out"
    openscad -o "$out" -D modalita=\"check\" -D stato=\"$s\" -D munizione=\"$m\" "$SCAD" >/dev/null 2>&1 || true
    # contatti a volume nullo (battute, spinta del percussore) non contano
    vol=0
    [ -f "$out" ] && vol=$(python3 -c "import sys; sys.path.insert(0,'tools'); import stl_info as t; print('%.3f' % t.volume(t.leggi_triangoli('$out')))")
    if awk "BEGIN{exit !($vol > 0.001)}"; then
      echo "COLLISIONE: $m $s (volume $vol mm3)"; esito=1
    else
      echo "ok: $m $s"
    fi
    rm -f "$out"
  done
done

echo "== Render"
R() { xvfb-run -a openscad -q -o "png/$1.png" --imgsize=1600,700 --viewall --autocenter \
        --colorscheme=Tomorrow --camera="$2" -D modalita=\"$3\" -D stato=\"$4\" \
        -D munizione=\"$5\" "$SCAD"; }
R provino_3q              0,0,0,62,0,215,0 assemblato armato diabolo
R provino_sezione_armato  0,0,0,90,0,0,0   sezione    armato diabolo
R provino_sezione_sparato 0,0,0,90,0,0,0   sezione    sparato diabolo
R provino_sezione_bb      0,0,0,90,0,0,0   sezione    armato bb
R provino_sezione_cart    0,0,0,90,0,0,0   sezione    armato cart_aperta
R provino_sezione_cart_sparato 0,0,0,90,0,0,0 sezione sparato cart_aperta
exit $esito
