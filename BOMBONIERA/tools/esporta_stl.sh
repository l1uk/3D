#!/usr/bin/env bash
# Esporta tutti gli STL della panchina Horta (v7) in BOMBONIERA/stl/.
# Uso: tools/esporta_stl.sh   (da qualsiasi cartella)
# Dopo aver tarato i giochi col provino, rilanciarlo per aggiornare gli STL.
set -euo pipefail
cd "$(dirname "$0")/.."
SCAD=phone_holder_v7_horta.scad

esporta() {   # $1 = modalita, $2 = file di destinazione
    echo "-> $2"
    openscad -q -o "$2" -D "modalita=\"$1\"" "$SCAD"
}

# pezzi singoli
esporta fianco                   stl/pezzi/fianco_x2.stl          # stampane 2 (sono uguali)
esporta seduta                   stl/pezzi/seduta.stl
esporta schienale                stl/pezzi/schienale.stl
esporta manneken                 stl/pezzi/manneken_sx_dx.stl     # coppia speculare

# piatti di stampa
esporta piatto1_fianchi          stl/piatti/piatto1_fianchi_ugello04.stl
esporta piatto2_seduta_schienale stl/piatti/piatto2_seduta_schienale_ugello04.stl
esporta manneken                 stl/piatti/piatto3_manneken_ugello02.stl

# provini
esporta test_giunti              stl/test/test_giunti_ugello04.stl

echo "Fatto."
