#!/usr/bin/env bash
# Esporta tutti gli STL della panchina Horta (v7) in BOMBONIERA/stl/.
# Uso: tools/esporta_stl.sh   (da qualsiasi cartella)
# Dopo aver tarato i giochi col provino, rilanciarlo per aggiornare gli STL.
set -euo pipefail
cd "$(dirname "$0")/.."
SCAD=phone_holder_v7_horta.scad
mkdir -p stl/pezzi stl/piatti stl/test

# controllo: i pezzi dei piatti incastrati restano ad almeno 2 mm
esito=$(openscad -o /tmp/check_piatti.stl -D 'modalita="check_piatti"' "$SCAD" 2>&1 || true)
if [[ "$esito" != *"object is empty"* ]]; then
    echo "ERRORE: pezzi troppo vicini nei piatti incastrati (modalita check_piatti)" >&2
    exit 1
fi
rm -f /tmp/check_piatti.stl

esporta() {   # $1 = modalita, $2 = file di destinazione
    echo "-> $2"
    openscad -q -o "$2" -D "modalita=\"$1\"" "$SCAD"
}

# pezzi singoli
esporta fianco               stl/pezzi/fianco.stl            # ne servono 2 (uguali)
esporta seduta               stl/pezzi/seduta.stl
esporta schienale            stl/pezzi/schienale.stl
esporta manneken             stl/pezzi/manneken_coppia.stl   # sx + dx, ugello 0.2

# piatti: una panchina intera
esporta piatto_panchina_x1   stl/piatti/panchina_x1_ugello04.stl

# piatti per la serie (pezzi uguali sullo stesso piatto)
esporta piatto_fianchi_x4    stl/piatti/fianchi_x4_ugello04.stl
esporta piatto_sedute_x8     stl/piatti/sedute_x8_ugello04.stl
esporta piatto_schienali_x6  stl/piatti/schienali_x6_ugello04.stl
esporta piatto_manneken      stl/piatti/manneken_x10_coppie_ugello02.stl

# provini
esporta test_giunti          stl/test/test_giunti_ugello04.stl

echo "Fatto."
