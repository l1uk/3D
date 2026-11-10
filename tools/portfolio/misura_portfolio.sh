#!/usr/bin/env bash
# Metriche per il portfolio (AGENTE_PORTFOLIO.md, passo 3), misurate su STL
# riesportati dal sorgente attuale in /tmp/portfolio_stl:
#   - "assieme": ingombro del pezzo montato (stl_info.py)
#   - "stampa":  pezzi da stampare, affettati con CuraEngine (slice_stima.py)
# Uso, dalla root del repo:   tools/portfolio/misura_portfolio.sh
set -uo pipefail
cd "$(dirname "$0")/../.."
T=/tmp/portfolio_stl; rm -rf "$T"; mkdir -p "$T"
PY=.venv/bin/python

# id | file .scad | tipo (assieme/stampa) | nome | -D
VOCI=(
  "korg-leggio|KORG SP 200/leggio_korg_sp200_v2.scad|assieme|leggio|part=\"both\""
  "korg-leggio|KORG SP 200/leggio_korg_sp200_v2.scad|stampa|centro|part=\"center\""
  "korg-leggio|KORG SP 200/leggio_korg_sp200_v2.scad|stampa|ala_sx|part=\"left\""
  "korg-leggio|KORG SP 200/leggio_korg_sp200_v2.scad|stampa|ala_dx|part=\"right\""
  "korg-leggio|KORG SP 200/leggio_korg_sp200_v2.scad|stampa|spine|part=\"pins\""
  "korg-copri-fader|KORG SP 200/copri_fader_korg_sp200.scad|assieme|copri_fader|"
  "korg-copri-fader|KORG SP 200/copri_fader_korg_sp200.scad|stampa|copri_fader|"
  "practice-mute|PRACTICE MUTE/sordina_tromba.scad|assieme|sordina|mode=\"assembly\""
  "practice-mute|PRACTICE MUTE/sordina_tromba.scad|stampa|corpo|mode=\"body_only\""
  "practice-mute|PRACTICE MUTE/sordina_tromba.scad|stampa|fondello|mode=\"cap_only\""
  "trumpet-stand|TRUMPET STAND/supporto_tromba_con_sordina.scad|assieme|supporto|mode=\"assembly\""
  "trumpet-stand|TRUMPET STAND/supporto_tromba_con_sordina.scad|stampa|base|mode=\"base\""
  "trumpet-stand|TRUMPET STAND/supporto_tromba_con_sordina.scad|stampa|clip|mode=\"clip\""
  "trumpet-stand|TRUMPET STAND/supporto_tromba_con_sordina.scad|stampa|pin|mode=\"pin\""
  "morsetto|MORSETTO_MICROFONO/morsetto_completo.scad|assieme|morsetto|"
  "morsetto|MORSETTO_MICROFONO/morsetto_completo.scad|stampa|morsetto|"
  "tappo-flacone|TAPPO FLACONE/tappo_flacone.scad|assieme|tappo|mode=\"full\""
  "tappo-flacone|TAPPO FLACONE/tappo_flacone.scad|stampa|tappo|mode=\"full\""
  "mappamondo|MAPPAMONDO/boccola_mappamondo.scad|assieme|boccola|"
  "mappamondo|MAPPAMONDO/boccola_mappamondo.scad|stampa|boccola|"
  "dosatore|dosatore_lavastoviglie/dosatore_lavastoviglie.scad|assieme|dosatore|part=\"assembly\""
  "dosatore|dosatore_lavastoviglie/dosatore_lavastoviglie.scad|stampa|piatto|part=\"print_plate\""
  "squeezer|TOOTHPASTE SQUEEZER/LUCHIX/ratchet_squeezer.scad|assieme|squeezer|part=\"assembly\""
  "squeezer|TOOTHPASTE SQUEEZER/LUCHIX/ratchet_squeezer.scad|stampa|piatto|part=\"print_plate\""
  "bomboniera|BOMBONIERA/phone_holder_v7_horta.scad|assieme|panchina|telefono=false"
  "passagatto|PASSAGATTO/porta_gattaiola.scad|assieme|porta|modo=\"intera\""
  "passagatto|PASSAGATTO/porta_gattaiola.scad|stampa|mezza_porta|modo=\"meta\""
)

for v in "${VOCI[@]}"; do
  IFS='|' read -r id file tipo nome def <<< "$v"
  out="$T/${id}__${tipo}__${nome}.stl"
  opt=(); [[ -n "$def" ]] && opt=(-D "$def")
  openscad -q -o "$out" "${opt[@]}" "$file" 2>/dev/null || echo "ERR export $out"
done
# la panchina si stampa dai piatti gia' esportati e verificati
cp BOMBONIERA/stl/piatti/panchina_x1_ugello04.stl "$T/bomboniera__stampa__panchina_x1.stl"

echo "### INGOMBRO (assieme)"
for f in "$T"/*__assieme__*.stl; do $PY GUN/tools/stl_info.py "$f" | tail -1; done
echo "### STAMPA ugello 0.4"
$PY tools/slice_stima.py "$T"/*__stampa__*.stl
echo "### STAMPA ugello 0.2 (Manneken BOMBONIERA)"
$PY tools/slice_stima.py -s machine_nozzle_size=0.2 -s line_width=0.22 -s layer_height=0.08 \
    -s layer_height_0=0.12 BOMBONIERA/stl/pezzi/manneken_coppia.stl
