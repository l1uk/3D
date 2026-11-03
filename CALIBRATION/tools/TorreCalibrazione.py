# =====================================================================
# TorreCalibrazione - script di post-processing per Cura (5.x)
# =====================================================================
# Cambia un parametro a blocchi lungo l'altezza di una torre:
#   - temperatura ugello        (M104)
#   - lunghezza di retrazione   (riscrive le righe di retrazione)
#   - velocita' di retrazione   (riscrive F di retrazione/ripristino)
#   - ventola                   (M106, sostituisce quelli di Cura)
#
# Installazione in Cura:
#   copia questo file in ~/.local/share/cura/<versione>/scripts/
#   riavvia Cura -> Estensioni > Post-elaborazione > Modifica G-code
#   > Aggiungi script > "Torre Calibrazione"
#
# Uso anche da terminale (stesso algoritmo, utile per test):
#   python3 TorreCalibrazione.py in.gcode out.gcode \
#       --modo temperatura --inizio 230 --passo -5 --z0 1 --blocco 8
#
# Regola dei blocchi: un layer appartiene al blocco i se la sua quota
# superiore Z sta in (z0 + i*blocco, z0 + (i+1)*blocco]. Sotto z0 (la
# base) vale il valore iniziale.
# =====================================================================

import math
import re

MODI = ("temperatura", "retrazione_lunghezza", "retrazione_velocita", "ventola")

_RE_Z = re.compile(r"\bZ(-?\d+\.?\d*)")
_RE_E = re.compile(r"\bE(-?\d+\.?\d*)")
_RE_F = re.compile(r"\bF(\d+\.?\d*)")
_RE_XYZ = re.compile(r"\b[XYZ]-?\d")
_EPS = 1e-4


def _codice(riga):
    """Restituisce la parte di comando della riga (senza commento), maiuscola."""
    return riga.split(";", 1)[0].strip().upper()


def _verifica(modo, valore):
    if modo == "temperatura" and not (170 <= valore <= 260):
        raise ValueError("Temperatura fuori range sicuro (170-260): %s" % valore)
    if modo == "retrazione_lunghezza" and not (0 <= valore <= 10):
        raise ValueError("Retrazione fuori range (0-10 mm): %s" % valore)
    if modo == "retrazione_velocita" and not (5 <= valore <= 100):
        raise ValueError("Velocita' retrazione fuori range (5-100 mm/s): %s" % valore)
    if modo == "ventola" and not (0 <= valore <= 100):
        raise ValueError("Ventola fuori range (0-100 %%): %s" % valore)


def _fmt(v, dec=5):
    s = ("%." + str(dec) + "f") % v
    return s.rstrip("0").rstrip(".") if "." in s else s


def _comando_valore(modo, v, retr_fw):
    if modo == "temperatura":
        return "M104 S%d ; TorreCalibrazione: temperatura %d" % (round(v), round(v))
    if modo == "ventola":
        return "M106 S%d ; TorreCalibrazione: ventola %s%%" % (round(v * 255 / 100), _fmt(v, 1))
    if modo == "retrazione_lunghezza":
        c = "; TorreCalibrazione: retrazione %s mm" % _fmt(v, 2)
        return c + ("\nM207 S%s" % _fmt(v, 2) if retr_fw else "")
    c = "; TorreCalibrazione: velocita' retrazione %s mm/s" % _fmt(v, 1)
    return c + ("\nM207 F%d\nM208 F%d" % (round(v * 60), round(v * 60)) if retr_fw else "")


def elabora(chunks, modo, inizio, passo, z0, blocco):
    """Elabora una lista di blocchi di G-code (come 'data' di Cura) e la restituisce modificata."""
    if modo not in MODI:
        raise ValueError("Modo sconosciuto: %s" % modo)
    if blocco <= 0:
        raise ValueError("Altezza blocco deve essere > 0")

    righe = [c.split("\n") for c in chunks]
    piatte = [(ci, li) for ci in range(len(righe)) for li in range(len(righe[ci]))]

    def quota_layer(k, z_attuale):
        # Quota alla PRIMA ESTRUSIONE del layer (Cura 5.x muove Z prima del
        # marcatore ;LAYER:, e con lo Z-hop la quota del viaggio non e' quella
        # di stampa): parto dalla Z corrente e seguo le Z fino a un G1 X/Y con E.
        z = z_attuale
        for ci, li in piatte[k + 1:]:
            r = righe[ci][li]
            if r.startswith(";LAYER:"):
                break
            c = _codice(r)
            if c.startswith(("G0", "G1")):
                m = _RE_Z.search(c)
                if m:
                    z = float(m.group(1))
                if c.startswith("G1") and _RE_E.search(c) and re.search(r"\b[XY]-?\d", c):
                    return z
        return z

    def indice(z):
        if z is None or z <= z0 + _EPS:
            return 0
        return max(0, int(math.ceil((z - z0) / blocco - _EPS)) - 1)

    usa_retr_fw = any(_codice(r).startswith(("G10", "G11")) for ch in righe for r in ch)

    # stato
    nei_layer = False
    idx_corr = None
    valore = inizio
    z_corr = 0.0           # ultima Z vista
    relativo = False       # M83
    e_corr = 0.0           # E assoluta tracciata (valore ORIGINALE del file)
    in_retr = False        # (assoluto) siamo tra retrazione e ripristino
    retr_orig = None       # (relativo) lunghezza della retrazione originale in sospeso
    modifiche = 0

    for k, (ci, li) in enumerate(piatte):
        r = righe[ci][li]

        if r.startswith(";LAYER:"):
            nei_layer = True
            idx = indice(quota_layer(k, z_corr))
            if idx != idx_corr:
                idx_corr = idx
                valore = inizio + idx * passo
                _verifica(modo, valore)
                righe[ci][li] = r + "\n" + _comando_valore(modo, valore, usa_retr_fw)
                modifiche += 1
            continue

        c = _codice(r)
        if not c:
            continue
        if c.startswith("M82"):
            relativo = False
            continue
        if c.startswith("M83"):
            relativo = True
            continue
        if c.startswith("G92"):
            m = _RE_E.search(c)
            if m:
                e_corr = float(m.group(1))
            continue

        if (nei_layer and modo == "temperatura" and c.startswith(("M104", "M109"))
                and not re.search(r"\bS0\b", c)):
            # Cura cambia temperatura dopo il primo layer: la decide la torre
            righe[ci][li] = "; (TorreCalibrazione) rimosso: " + r
            continue

        if nei_layer and modo == "ventola" and c.startswith(("M106", "M107")):
            # la ventola la decide la torre
            righe[ci][li] = "; (TorreCalibrazione) rimosso: " + r
            continue

        if not c.startswith(("G0", "G1")):
            continue
        m_z = _RE_Z.search(c)
        if m_z:
            z_corr = float(m_z.group(1))
        m_e = _RE_E.search(c)
        if not m_e:
            continue
        e_val = float(m_e.group(1))
        solo_e = not _RE_XYZ.search(c)

        if relativo:
            if nei_layer and solo_e and modo.startswith("retrazione") and not usa_retr_fw:
                if e_val < 0:                       # retrazione
                    retr_orig = -e_val
                    if modo == "retrazione_lunghezza":
                        r = _RE_E.sub("E-" + _fmt(valore), r, count=1)
                    else:
                        r = _RE_F.sub("F%d" % round(valore * 60), r, count=1)
                    righe[ci][li] = r
                elif e_val > 0 and retr_orig is not None:   # ripristino
                    if modo == "retrazione_lunghezza":
                        extra = e_val - retr_orig
                        r = _RE_E.sub("E" + _fmt(valore + extra), r, count=1)
                    else:
                        r = _RE_F.sub("F%d" % round(valore * 60), r, count=1)
                    righe[ci][li] = r
                    retr_orig = None
            continue

        # ---- estrusione assoluta (default Cura) ----
        # Retrazione: E scende senza muovere XYZ -> riscrivo la E come (E_prima - valore).
        # Ripristino: E risale al valore assoluto ORIGINALE, quindi non va toccata
        # (tutte le estrusioni successive restano coerenti); cambio solo la F se serve.
        prima = e_corr
        e_corr = e_val
        if nei_layer and solo_e and modo.startswith("retrazione") and not usa_retr_fw:
            if e_val < prima - _EPS:                     # retrazione
                if modo == "retrazione_lunghezza":
                    r = _RE_E.sub("E" + _fmt(prima - valore), r, count=1)
                else:
                    r = _RE_F.sub("F%d" % round(valore * 60), r, count=1)
                righe[ci][li] = r
                in_retr = True
            elif e_val > prima + _EPS and in_retr:       # ripristino
                if modo == "retrazione_velocita":
                    righe[ci][li] = _RE_F.sub("F%d" % round(valore * 60), r, count=1)
                in_retr = False
        elif not solo_e:
            in_retr = False

    out = ["\n".join(ch) for ch in righe]
    if out:
        intest = ";TorreCalibrazione modo=%s inizio=%s passo=%s z0=%s blocco=%s cambi=%d\n" % (
            modo, _fmt(inizio), _fmt(passo), _fmt(z0), _fmt(blocco), modifiche)
        out[0] = intest + out[0]
    return out


# ---------------------------------------------------------------------
# Integrazione Cura
# ---------------------------------------------------------------------
try:
    from ..Script import Script  # type: ignore

    class TorreCalibrazione(Script):
        def getSettingDataString(self):
            return """{
                "name": "Torre Calibrazione",
                "key": "TorreCalibrazione",
                "metadata": {},
                "version": 2,
                "settings": {
                    "modo": {
                        "label": "Modalita'",
                        "description": "Parametro da variare a blocchi",
                        "type": "enum",
                        "options": {
                            "temperatura": "Temperatura ugello",
                            "retrazione_lunghezza": "Retrazione lunghezza",
                            "retrazione_velocita": "Retrazione velocita'",
                            "ventola": "Ventola %"
                        },
                        "default_value": "temperatura"
                    },
                    "inizio": {
                        "label": "Valore iniziale",
                        "description": "Valore del primo blocco (e della base)",
                        "type": "float",
                        "default_value": 230
                    },
                    "passo": {
                        "label": "Passo",
                        "description": "Variazione per ogni blocco (negativo per scendere)",
                        "type": "float",
                        "default_value": -5
                    },
                    "z0": {
                        "label": "Altezza inizio (mm)",
                        "description": "Spessore della base: sopra questa quota iniziano i blocchi",
                        "type": "float",
                        "default_value": 1.0
                    },
                    "blocco": {
                        "label": "Altezza blocco (mm)",
                        "description": "Altezza di ogni blocco della torre",
                        "type": "float",
                        "default_value": 8.0,
                        "minimum_value": 0.5
                    }
                }
            }"""

        def execute(self, data):
            return elabora(
                data,
                self.getSettingValueByKey("modo"),
                float(self.getSettingValueByKey("inizio")),
                float(self.getSettingValueByKey("passo")),
                float(self.getSettingValueByKey("z0")),
                float(self.getSettingValueByKey("blocco")),
            )

except (ImportError, ValueError):
    # eseguito fuori da Cura
    pass


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Torre di calibrazione: post-processing G-code Cura")
    p.add_argument("ingresso")
    p.add_argument("uscita")
    p.add_argument("--modo", choices=MODI, required=True)
    p.add_argument("--inizio", type=float, required=True)
    p.add_argument("--passo", type=float, required=True)
    p.add_argument("--z0", type=float, default=1.0)
    p.add_argument("--blocco", type=float, default=8.0)
    a = p.parse_args()

    with open(a.ingresso, encoding="utf-8") as f:
        testo = f.read()
    # stessa divisione che fa Cura: un blocco per layer
    parti = re.split(r"(?=^;LAYER:)", testo, flags=re.M)
    risultato = elabora(parti, a.modo, a.inizio, a.passo, a.z0, a.blocco)
    with open(a.uscita, "w", encoding="utf-8") as f:
        f.write("".join(risultato))
    print("Scritto", a.uscita)
