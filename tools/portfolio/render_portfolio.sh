#!/usr/bin/env bash
# Render PNG per il portfolio dei progetti OpenSCAD (vedi AGENTE_PORTFOLIO.md, passo 2a).
# Uso, dalla root del repo:   tools/portfolio/render_portfolio.sh
# Per ogni voce: progetto | file .scad | nome PNG | opzioni -D (facoltative).
# Ogni voce produce <progetto>/png/<nome>_3q.png e <nome>_lato.png.
set -uo pipefail
cd "$(dirname "$0")/../.."

VOCI=(
  "KORG SP 200|leggio_korg_sp200_v2.scad|leggio|"
  "KORG SP 200|copri_fader_korg_sp200.scad|copri_fader|"
  "PRACTICE MUTE|sordina_tromba.scad|sordina|mode=\"assembly\""
  "PRACTICE MUTE|sordina_tromba.scad|sordina_sezione|mode=\"cross_section\""
  "TRUMPET STAND|supporto_tromba_con_sordina.scad|supporto|mode=\"assembly\""
  "MORSETTO_MICROFONO|morsetto_completo.scad|morsetto|"
  "TAPPO FLACONE|tappo_flacone.scad|tappo|mode=\"full\""
  "MAPPAMONDO|boccola_mappamondo.scad|boccola|"
  "dosatore_lavastoviglie|dosatore_lavastoviglie.scad|dosatore|part=\"assembly\""
  "dosatore_lavastoviglie|dosatore_lavastoviglie.scad|dosatore_sezione|part=\"section\""
  "TOOTHPASTE SQUEEZER|LUCHIX/ratchet_squeezer.scad|squeezer|part=\"assembly\""
)

for voce in "${VOCI[@]}"; do
  IFS='|' read -r prog file nome def <<< "$voce"
  mkdir -p "$prog/png"
  opt=(); [[ -n "$def" ]] && opt=(-D "$def")
  for vista in "3q|55,0,25" "lato|90,0,0"; do
    IFS='|' read -r suff rot <<< "$vista"
    out="$prog/png/${nome}_${suff}.png"
    if openscad -q -o "$out" --render --autocenter --viewall --imgsize=1600,1200 \
         --colorscheme=Tomorrow --camera=0,0,0,${rot},0 "${opt[@]}" "$prog/$file" 2>/tmp/render_err.txt; then
      echo "ok   $out"
    else
      echo "ERR  $out: $(tail -2 /tmp/render_err.txt | tr '\n' ' ')"
    fi
  done
done
