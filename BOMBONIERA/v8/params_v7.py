"""Quote funzionali della v7, lette da ../phone_holder_v7_horta.scad.

La v7 resta la fonte unica: qui si leggono i parametri numerici (assegnazioni
semplici "nome = valore;") e si ricalcolano le grandezze derivate con le stesse
formule del .scad. Se una quota cambia nella v7, cambia anche nella v8.
"""
import math
import re
from pathlib import Path

SCAD = Path(__file__).resolve().parent.parent / "phone_holder_v7_horta.scad"


def leggi_scad(percorso=SCAD):
    """Assegnazioni numeriche/booleane/stringa di primo livello del .scad."""
    p = {}
    for riga in percorso.read_text().splitlines():
        m = re.match(r'^([A-Za-z_]\w*)\s*=\s*([^;]+);', riga)
        if not m:
            continue
        nome, val = m.group(1), m.group(2).strip()
        if re.fullmatch(r'-?\d+(\.\d+)?', val):
            p[nome] = float(val)
        elif val in ("true", "false"):
            p[nome] = val == "true"
        elif val.startswith('"') and val.endswith('"'):
            p[nome] = val[1:-1]
        elif val.startswith('[') and re.fullmatch(r'\[[-\d.,\s]+\]', val):
            p[nome] = [float(x) for x in val[1:-1].split(',')]
    return p


P = leggi_scad()
rad = math.radians
alpha, beta, sp = P["alpha"], P["beta"], P["sp"]

# direzioni (piano del fianco: u orizzontale verso il retro, z verticale)
d = (math.cos(rad(alpha)), math.sin(rad(alpha)))     # lungo lo schienale
n = (-math.sin(rad(alpha)), math.cos(rad(alpha)))    # normale schienale, verso il davanti
g = (math.cos(rad(beta)), -math.sin(rad(beta)))      # lungo la seduta, verso il retro
m = (math.sin(rad(beta)), math.cos(rad(beta)))       # normale seduta, verso l'alto

tratto = P["spazio_cavo"] - P["inserzione"]
z_E = P["margine"] + tratto * math.sin(rad(alpha)) - P["asse"] * math.cos(rad(alpha))
E = (0.0, z_E)


def Pb(a, b):   # punto nel piano schienale (P(a, b) della v7)
    return (E[0] + a * d[0] + b * n[0], E[1] + a * d[1] + b * n[1])


def S(w, h):    # punto nel piano seduta (S(w, h) della v7)
    return (E[0] + w * g[0] + h * m[0], E[1] + w * g[1] + h * m[1])


x_in = P["L_in"] / 2
x_out = x_in + sp
xi = x_in - 0.15
lt = 9.0                                  # lunghezza linguette (costante nella v7)
ling_seduta = [-26.0, -4.0]
ling_schienale = [8.0, 52.0]
z_arm = z_E + P["bracciolo"]
a_arm = (z_arm - z_E + (sp / 2) * n[1]) / d[1]
u_attacco = 66.0
rs = 2.6
r_band = sp / 2 + 3.6
gap_s, n_s = 1.6, 5
doga_s = (P["w_back"] - P["w_front"] - (n_s - 1) * gap_s) / n_s
gap_b = 2.4
doghe_b = [(0, 16), (18.4, 35), (37.4, P["h_back"])]
w_fermo_in = -(P["spessore_max_tel"] / math.sin(rad(180 - alpha - beta)) + 0.4)


def F_crit(L, mt, frac=0.85, u_coda=None, m_panca=None, u_cg_panca=None):
    """Forza (N) di un dito sullo schermo che ribalta la panchina (stessa formula v7)."""
    u_coda = P["u_coda"] if u_coda is None else u_coda
    m_panca = P["m_panca"] if m_panca is None else m_panca
    u_cg_panca = P["u_cg_panca"] if u_cg_panca is None else u_cg_panca
    t = P["t_tel"]
    up = L / 2 * d[0] + t / 2 * n[0]
    uc = (mt * up + m_panca * u_cg_panca) / (mt + m_panca)
    Mr = (mt + m_panca) / 1000 * 9.81 * (u_coda - uc)
    Pp = Pb(frac * L, t)
    braccio = math.sin(rad(alpha)) * Pp[1] - math.cos(rad(alpha)) * (u_coda - Pp[0])
    return Mr / braccio


TELEFONI = [(140, 150), (150, 170), (165, 200), (175, 170), (185, 250)]

if __name__ == "__main__":
    chiavi = ["alpha", "beta", "sp", "L_in", "w_front", "w_back", "h_back", "bracciolo",
              "u_coda", "spessore_max_tel", "clearance", "gioco_manneken", "x_manneken",
              "t_tenone", "h_manneken", "spazio_cavo", "inserzione", "asse", "margine",
              "luce_fermo", "L_tel", "m_tel", "t_tel", "F_minima", "m_panca", "u_cg_panca"]
    for k in chiavi:
        print(f"{k:18s} {P[k]}")
    print(f"{'z_E':18s} {z_E:.2f}   (angolo seduta/schienale, dal tavolo)")
    print(f"{'z_arm':18s} {z_arm:.2f}")
    print(f"{'w_fermo_in':18s} {w_fermo_in:.2f}")
    print(f"{'doga_s':18s} {doga_s:.2f}")
    for L, mt in TELEFONI:
        print(f"F_crit {L} mm/{mt} g: {F_crit(L, mt):.2f} N in alto, {F_crit(L, mt, 0.5):.2f} N al centro")
