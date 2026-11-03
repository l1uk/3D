"""Lettore dei parametri OpenSCAD: fonte unica = GUN/params.scad.

Legge le assegnazioni numeriche (`nome = espressione;`) e le valuta in
ordine, cosi' funzionano anche espressioni che usano parametri gia' letti.
Vettori `[a, b]` diventano liste. Stringhe, chiamate di funzione e
variabili speciali ($fn) vengono ignorate.

Alcune quote costruttive vivono solo nel provino (t_sc, g_tamb, L_tappo,
t_sp, L_sede, cam_L): si leggono in sola lettura da provino_balistico.scad,
sezione "Telaio provino". Se lo stesso nome compare in params.scad, vince
params.scad.
"""
from __future__ import annotations

import math
import re
from pathlib import Path

GUN = Path(__file__).resolve().parent.parent
PARAMS = GUN / "params.scad"
PROVINO = GUN / "provino_balistico.scad"

# quote del provino che il corpo deve riprodurre identiche
DAL_PROVINO = ("L_tappo", "t_sc", "g_tamb", "t_sp", "L_sede", "cam_L")

_ASSEGNAZIONE = re.compile(r"^\s*([A-Za-z_]\w*)\s*=\s*([^;]+);")


def _togli_commenti(testo: str) -> str:
    testo = re.sub(r"/\*.*?\*/", "", testo, flags=re.S)
    return re.sub(r"//.*", "", testo)


def leggi_scad(path: Path, solo: tuple[str, ...] | None = None,
               base: dict | None = None) -> dict:
    """Ritorna {nome: valore} per le assegnazioni numeriche del file."""
    ns: dict = {"PI": math.pi}
    if base:
        ns.update(base)
    out: dict = {}
    for riga in _togli_commenti(path.read_text()).splitlines():
        m = _ASSEGNAZIONE.match(riga)
        if not m:
            continue
        nome, expr = m.group(1), m.group(2).strip()
        if solo is not None and nome not in solo:
            continue
        if '"' in expr or "(" in expr:      # stringhe e funzioni: non numeriche
            continue
        try:
            val = eval(expr, {"__builtins__": {}}, ns)   # solo aritmetica e liste
        except Exception:
            continue
        if isinstance(val, bool) or not isinstance(val, (int, float, list)):
            continue
        ns[nome] = out[nome] = val
    return out


def carica() -> dict:
    p = leggi_scad(PROVINO, solo=DAL_PROVINO)
    p.update(leggi_scad(PARAMS))
    mancanti = [n for n in DAL_PROVINO if n not in p]
    if mancanti:
        raise ValueError(f"quote del provino non trovate: {mancanti}")
    return p


if __name__ == "__main__":
    for k, v in carica().items():
        print(f"{k:16s} = {v}")
