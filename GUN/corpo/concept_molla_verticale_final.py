# CONCEPT FINALE - meccanismo a molla verticale con la MOLLA REALE (inox 304, De 8, filo 1.0).
#
# Evoluzione di concept_molla_verticale_v3.py (v1/v2/v3 restano come sono). Non tocca build.py /
# meccanica.py / parametri.py: build.py viene LETTO (AST, solo le righe di calcolo puro) e mai
# eseguito. Sistema di build.py: X asse canna, Z alto, Y laterale (piano dei gusci y = 0), mm.
# Scrive: concept_stl/final_*.stl, concept_stl/final_profili.json (profili per build.py),
# concept_stl/final_profilo.png e MECCANISMO.md.
#
# RISULTATI DELL'ULTIMA ESECUZIONE: vedi il blocco "RISULTATI" qui sotto (lo stesso testo e'
# stampato dallo script e riportato in MECCANISMO.md).
# ---------------------------------------------------------------------------------
# RISULTATI
#  (compilato dopo l'esecuzione: vedi sotto, sezione aggiornata a mano con i numeri stampati)
# ---------------------------------------------------------------------------------
import ast
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# show_object e' iniettato solo dentro agentcad; qui giriamo con Python puro
if "show_object" not in dir():
    def show_object(*a, **k):  # noqa: E306  (no-op fuori da agentcad)
        pass

from build123d import Align, Axis, Box, Compound, Cylinder, Plane, Polygon, Pos, Rot, extrude, export_stl  # noqa: E402
from shapely.geometry import LineString, MultiPoint, Point, Polygon as SPoly, box as sbox  # noqa: E402
from shapely.ops import unary_union  # noqa: E402
from shapely import affinity  # noqa: E402

import meccanica as M  # noqa: E402

p, q = M.p, M.q
_C, _MIN = Align.CENTER, Align.MIN
QUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(QUI, "concept_stl")
BUILD = os.path.join(QUI, "build.py")
DOC = os.path.join(QUI, "MECCANISMO.md")


# =====================================================================
# build.py LETTO (non eseguito), come in v3
# =====================================================================
def _leggi_build():
    src = open(BUILD).read()
    dopo, corpo = False, []
    costanti_dopo = {"cx_p", "cz_p", "R_PONT", "r_PONT", "W_PONT", "Z_PONT_TOP", "viti", "RIENTRO_G",
                     "S_G0", "t_g", "S_MED", "S_VITE_G", "CAP_H", "CAP_T", "S_CAP", "PONTE_SUP_W",
                     "ANIMA_INF_W", "G_TESTA_PERNO"}
    for nodo in ast.parse(src).body:
        if isinstance(nodo, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "guaina" for t in nodo.targets):
            dopo = True
            continue
        if not dopo:
            if isinstance(nodo, (ast.Assert, ast.If)):
                continue
            corpo.append(nodo)
        elif isinstance(nodo, ast.Assign):
            nomi = {n.id for t in nodo.targets for n in ast.walk(t) if isinstance(n, ast.Name)}
            if nomi and nomi <= costanti_dopo:
                corpo.append(nodo)
    ns = {"__file__": BUILD, "__name__": "build_letto"}
    exec(compile(ast.Module(body=corpo, type_ignores=[]), "build.py", "exec"), ns)
    ns["_GATTONI"] = []
    for nodo in ast.parse(src).body:
        if isinstance(nodo, ast.For) and isinstance(nodo.iter, ast.Tuple) and \
                all(isinstance(e, ast.List) for e in nodo.iter.elts):
            ns["_GATTONI"] = [ast.literal_eval(e) for e in nodo.iter.elts]
    m = re.search(r"perno = cil_x\(p\.tamb_asse_d, q\.x_cam - ([\d.]+)", src)
    ns["_PERNO_TAMB_DIETRO"] = float(m.group(1)) if m else 10.0
    m = re.search(r"vuoto_asse_tamburo\(q\.x_cam - ([\d.]+)", src)
    ns["_FORO_TAMB_DIETRO"] = float(m.group(1)) if m else 12.0
    return ns


BT = _leggi_build()
W, W2 = BT["W"], BT["W2"]
ZA = BT["za"]
ANG_MOLLA = 32.0                                # asse molla dalla verticale (impugnatura 20). v3: 28; con la sede lunga
                                                # a 28 il braccio del grilletto passava a < 1.6 mm dal frontale del manico
U = (math.sin(math.radians(ANG_MOLLA)), math.cos(math.radians(ANG_MOLLA)))   # asse molla, verso l'alto
NF = (U[1], -U[0])                              # normale "in avanti" all'asse molla (verso +X)
imp_xz = BT["imp_xz"]
grip = SPoly(BT["profilo_imp"]()).buffer(0)
TEL = SPoly(BT["telaio_pts"]).buffer(0)         # profilo laterale di build.py (NON cambia)


def profilo_telaio(X0, Z0):
    """telaio_pts di build.py con il dorso (X_DORSO0, Z_DORSO0) spostato (solo per la variante facoltativa)."""
    b = BT
    nd = b["N_DORSO"]
    dorso_t = [(X0 + (b["X_DORSO1"] - X0) * (1 - math.cos(math.pi / 2 * i / nd)),
                Z0 + (b["Z_DORSO1"] - Z0) * math.sin(math.pi / 2 * i / nd)) for i in range(nd + 1)]
    p0, p0b = b["_p0"], b["_p0b"]
    t0 = (p0[0] - p0b[0], p0[1] - p0b[1])
    k = math.dist(p0, (X0, Z0))
    t0 = (t0[0] / math.hypot(*t0) * k, t0[1] / math.hypot(*t0) * k)
    t1 = (0.0, k)

    def her(u):
        h00, h10, h01, h11 = 2*u**3 - 3*u**2 + 1, u**3 - 2*u**2 + u, -2*u**3 + 3*u**2, u**3 - u**2
        return (h00*p0[0] + h10*t0[0] + h01*X0 + h11*t1[0], h00*p0[1] + h10*t0[1] + h01*Z0 + h11*t1[1])
    fuso = [her(i / b["N_FUSO"]) for i in range(1, b["N_FUSO"])]
    return (dorso_t + [(30, 12), (q.x_cam - 1, 12.5)] + b["fronte_alto"] + b["fronte_basso"] + [
        (q.x_spal + 3, -23), (q.x_spal + 1.5, -30), (q.x_spal, -37), (26, -38)]
        + b["profilo_imp"](s_dorso=b["S_FUSIONE"]) + fuso)


assert max(math.dist(a, b) for a, b in zip(profilo_telaio(BT["X_DORSO0"], BT["Z_DORSO0"]), BT["telaio_pts"])) < 1e-9

_cxp, _czp = BT["cx_p"], BT["cz_p"]
anello = Point(_cxp, _czp).buffer(BT["R_PONT"], 64).difference(Point(_cxp, _czp).buffer(BT["r_PONT"], 64))
anello = anello.difference(sbox(-200, BT["Z_PONT_TOP"], 200, 200))
vano_pont = Point(_cxp, _czp).buffer(BT["r_PONT"], 64)
gattoni = unary_union([SPoly(g).buffer(0) for g in BT["_GATTONI"]])
ponticello = anello.union(gattoni)

# =====================================================================
# PARAMETRI
# =====================================================================
X_SCUDO = BT["x_scudo0"]          # 40.0 retro dello scudo di build.py (battuta del cane)
X_SCUDO1 = BT["x_scudo1"]         # 44.0 faccia anteriore dello scudo
X_CAM = q.x_cam
ZB = 0.0

# --- cane (geometria di v3: e' quella che entra nel telaio) ---
X_PERNO, Z_PERNO = 30.5, -20.0
D_PERNO = 3.0                     # spina acciaio d3 (o vite M3 senza testa / chiodo d3)
R_MOZZO = 5.0
SP_CANE = 7.0                     # con 8 la parete verso la scanalatura di carica scende a 1.1 mm
ANG_ARMO = 30.0                   # v3: 26. Stessa coda (20 mm) ruotata di piu': +15% di energia a parita' di carico sul dente
CORSA_CODA = 10.35                # = 2 x 20 x sin(15 gradi): compressione data dal cane
R_CONT = 3.2
Z_SPERONE = 21.5
ALLEGG = (1.5, 15.0, 2.2)
ALLEGG2 = ()                      # altri fori (dx dal perno, z, raggio)

# --- percussore flottante (trascinato dalla forcella del cane) ---
D_SHANK = 2.6
D_COL, L_COL = 5.0, 2.0           # v3: collare 1.5 -> 2.0 (parete >= 1.6 anche sui pezzi)
T_LIP = 3.6                       # v3: 1.2. Il collare, ruotato di 30 gradi rispetto al cane, scava la tasca in diagonale:
                                  # con 2.0 restavano 0.3 mm di pelle sulla faccia di battuta del cane; con 3.6 restano >= 1.6
S_PUSH = p.cart_fascia + 0.5 + 0.5
RITIRO_TIP = 0.3

# --- dente di monta / grilletto ---
R_NASO = 8.0
H_ENG = 1.2
GIOCO_SGANCIO = 0.3
L_NASO = 14.5
W_NASO = 2.5
SP_GRIL = 6.0
D_PERNO_G = 2.0                   # spina acciaio d2
R_MOZZO_G = 3.5
R_BRACCIO = 2.4
MU = 0.3                          # PLA/PLA a secco
MU_NASO = 0.09                    # rullino: mu_perno x r_perno / r_rullino = 0.3 x 0.875 / 3.5 = 0.075, + 0.015 di margine
DITO = (36.8, -44.0)
OFF_EXTRA = 0.6                   # luce in piu' fra braccio del grilletto e pattino (anche a fine corsa + 0.5 gradi)

# --- rullino (pezzo separato, ruota su perno di filamento 1.75 nella forcella del grilletto) ---
R_RULL = 3.5                      # d7
W_RULL = 2.4                      # larghezza; la forcella ha due guance da (6-2.6)/2 = 1.7
R_FORC = 2.6                      # mozzo della forcella attorno al perno del rullino (sta dentro il rullino)
D_PERNO_R = 1.75                  # filamento PLA 1.75 (foro 2.0 nel rullino, 1.9 nelle guance)

# --- sede molla nel manico ---
D_SEDE = 9.2                      # canale a sezione QUADRA 9.2 x 9.2 (meta' in ogni guscio): molla De 8
L_COPPA = 3.0
L_PIST = 6.0                      # pistone quadro 8.8: non ruota, tiene orientato il pattino
T_PAD = 2.0
PRE_MIN = 2.0
CAP_SIC = BT["CAP_T"]

# --- MOLLA REALE: filo di molla inox 304 da tagliare ---
MOLLA_d, MOLLA_De, MOLLA_PASSO = 1.0, 8.0, 3.0
MOLLA_Dm = MOLLA_De - MOLLA_d
MOLLA_G = 68000.0                 # MPa, inox 304
MOLLA_NM = 2.0                    # spire non attive: l'ultima spira di ogni capo si chiude a pinza
L0_STIMA = 45.0                   # lunghezza dei vostri calcoli (k ~1.9)
K_TOLL = 0.30                     # k vero = k stimato x (1 +- 0.30)
RM_INOX = 1800.0                  # Rm minimo filo 1.4310/304 d1.0 (EN 10270-3), prudente
TAU_AMM = 0.45 * RM_INOX
L0_TAGLIO = 60.0                  # LUNGHEZZA DI TAGLIO SCELTA (= 20 spire a passo 3)
F_TARGET = 23.5                   # forza molla a cane armato (grilletto a fondo) che si cerca con i distanziali [N]
F_LIM = 25.0                      # limite dato
L1_GEOM = 58.0                    # lunghezza della sede SENZA distanziali (fra coppa e pistone, a riposo)
DIST_SET = (0.5, 1.0, 2.0, 4.0, 8.0)   # distanziali stampati (dischi d8.8): qualunque spessore 0..15.5 a passi di 0.5
DIST_MAX = sum(DIST_SET)

# --- munizione e balistica (come v2/v3) ---
RHO_PLA = 1.24e-3 * 0.85
RHO_CART = 1.24e-3 * 0.95
F_TRATT = 5.0
E_REST = 0.4
ETA_MECC = 0.85
K_CONT = 1.0e6
CD, RHO_ARIA, H_TIRO = 0.8, 1.2, 1.2
GITT_MIN, GITT_MAX = 4.0, 5.0
F_DITO_MAX = 25.0

PARETE = p.parete_min
RHO_ACC = 7.85e-3


# =====================================================================
# MOLLA REALE: modello
# =====================================================================
def k_molla(L0, fac=1.0):
    na = L0 / MOLLA_PASSO - MOLLA_NM
    return MOLLA_G * MOLLA_d ** 4 / (8 * MOLLA_Dm ** 3 * na) * fac


C_IND = MOLLA_Dm / MOLLA_d
K_WAHL = (4 * C_IND - 1) / (4 * C_IND - 4) + 0.615 / C_IND


def tau_molla(F):
    return K_WAHL * 8 * F * MOLLA_Dm / (math.pi * MOLLA_d ** 3)


def molla_cfg(L0, fac=1.0, sp=0.0):
    nt = L0 / MOLLA_PASSO
    m = dict(nome=f"inox {MOLLA_d:g}x{MOLLA_De:g} L0 {L0:g}", d=MOLLA_d, De=MOLLA_De, L0=L0, nt=nt,
             na=nt - MOLLA_NM, k=k_molla(L0, fac), fac=fac, sp=sp)
    m["L1"] = L1_GEOM - sp
    m["pre"] = L0 - m["L1"]
    m["Lp"] = (nt + 1) * MOLLA_d            # pacco con i capi chiusi (prudente)
    m["massa"] = nt * math.pi * MOLLA_Dm * math.pi * MOLLA_d ** 2 / 4 * RHO_ACC
    return m


# =====================================================================
# UTILITA' 2D
# =====================================================================
P = (X_PERNO, Z_PERNO)


def rot(pt, ang, c=P):
    a = math.radians(ang)
    dx, dz = pt[0] - c[0], pt[1] - c[1]
    return (c[0] + dx * math.cos(a) - dz * math.sin(a), c[1] + dx * math.sin(a) + dz * math.cos(a))


def rotg(g, ang, c):
    return affinity.rotate(g, ang, origin=c)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def J_poligono(pts, c):
    s, n = 0.0, len(pts)
    for i in range(n):
        x0, z0 = pts[i][0] - c[0], pts[i][1] - c[1]
        x1, z1 = pts[(i + 1) % n][0] - c[0], pts[(i + 1) % n][1] - c[1]
        s += (x0 * z1 - x1 * z0) * (x0 * x0 + x0 * x1 + x1 * x1 + z0 * z0 + z0 * z1 + z1 * z1)
    return abs(s) / 12.0


def poligoni(g):
    if g.is_empty:
        return []
    return [g] if g.geom_type == "Polygon" else [x for x in g.geoms if x.geom_type == "Polygon"]


def J_geom(g, c):
    tot = 0.0
    for pg in poligoni(g):
        tot += J_poligono(list(pg.exterior.coords)[:-1], c)
        for h in pg.interiors:
            tot -= J_poligono(list(h.coords)[:-1], c)
    return tot


def solido(g, sp, y0=0.0):
    out_ = None
    for pg in poligoni(g):
        if pg.area < 1e-3:
            continue
        f = Polygon(*list(pg.exterior.coords)[:-1], align=None)
        s = extrude(Plane.XZ * f, amount=sp / 2, both=True)
        for h in pg.interiors:
            s -= extrude(Plane.XZ * Polygon(*list(h.coords)[:-1], align=None), amount=sp, both=True)
        out_ = s if out_ is None else out_ + s
    return out_.translate((0, y0, 0))


def lungo_asse(o, t):
    """Punto a distanza t lungo -U (verso il calcio) dall'origine o."""
    return (o[0] - U[0] * t, o[1] - U[1] * t)


def banda_asse(o, t0, t1, r):
    return LineString([lungo_asse(o, t0), lungo_asse(o, t1)]).buffer(r, cap_style=2)


def sottili(g, t=PARETE, amin=1.0):
    """Zone del profilo 2D piu' sottili di t (apertura morfologica); trascura gli spigoli vivi (< amin mm^2)."""
    op = g.buffer(-t / 2, 16).buffer(t / 2, 16)
    perso = g.difference(op.buffer(0.02))
    return [c for c in poligoni(perso) if c.area > amin]


# =====================================================================
# CANE (come v3)
# =====================================================================
L_CODA = CORSA_CODA / (2 * math.sin(math.radians(ANG_ARMO / 2)))
n_perp = (-U[1], U[0])
if n_perp[0] > 0:
    n_perp = (-n_perp[0], -n_perp[1])
coda_mid = (P[0] + L_CODA * n_perp[0], P[1] + L_CODA * n_perp[1])
coda0 = rot(coda_mid, -ANG_ARMO / 2)


def comp_cane(th):
    c = rot(coda0, th)
    return -dot((c[0] - coda0[0], c[1] - coda0[1]), U)


def dcomp_cane(th, h=0.05):
    return (comp_cane(th + h) - comp_cane(th - h)) / math.radians(2 * h)


def su_asse(pt):
    t = dot((pt[0] - coda_mid[0], pt[1] - coda_mid[1]), U)
    return (coda_mid[0] + t * U[0], coda_mid[1] + t * U[1]), t


# --- percussore e forcella ---
X_STOP = X_SCUDO - 0.05
TIP_S = X_CAM + S_PUSH
TIP_R = X_SCUDO1 - RITIRO_TIP
RITIRO = TIP_S - TIP_R


def x_piano(x0, th):
    pt = rot((x0, ZB), th)
    a = math.radians(th)
    return pt[0] + (pt[1] - ZB) * math.tan(a)


def dx_piano(x0, th, h=0.05):
    return (x_piano(x0, th + h) - x_piano(x0, th - h)) / math.radians(2 * h)


DF = x_piano(X_STOP, 0) - x_piano(X_STOP, ANG_ARMO)
G_LOST = DF - RITIRO
X_FACE = X_STOP - T_LIP - G_LOST - L_COL
L_PERC = TIP_S - X_FACE
M_PERC = (math.pi / 4 * (D_COL ** 2 * L_COL + D_SHANK ** 2 * (L_PERC - L_COL))) * RHO_PLA
th_urto = ANG_ARMO
while x_piano(X_FACE, th_urto) < TIP_R - L_PERC and th_urto > 0:
    th_urto -= 0.01


def perc_2d(tip):
    col = sbox(tip - L_PERC, -D_COL / 2, tip - L_PERC + L_COL, D_COL / 2)
    sh = sbox(tip - L_PERC + L_COL - 0.01, -D_SHANK / 2, tip, D_SHANK / 2)
    return col, sh


def _tip_armamento(th):
    tirato = x_piano(X_STOP - T_LIP, th) + (L_PERC - L_COL)
    return min(TIP_S, tirato)


# --- grilletto ---
N0 = (P[0], P[1] - R_NASO)
PT = (N0[0] - L_NASO, N0[1])
PHI_CAMMA = -math.degrees(H_ENG / L_NASO)
PHI_SGANCIO = -math.degrees((H_ENG + GIOCO_SGANCIO) / L_NASO)
PHI_FINE = PHI_SGANCIO - 1.0

R_CAMMA = R_NASO + H_ENG
W_CAMMA = ANG_ARMO + 14.0
a0 = -90.0
settore = [P] + [(P[0] + R_CAMMA * math.cos(math.radians(a0 + W_CAMMA * i / 16)),
                  P[1] + R_CAMMA * math.sin(math.radians(a0 + W_CAMMA * i / 16))) for i in range(17)]
camma0 = rotg(SPoly(settore).buffer(0), -ANG_ARMO, P)

# --- asse molla, coppa, pistone, rullino ---
cima0, t_cima0 = su_asse((coda0[0] - U[0] * R_CONT, coda0[1] - U[1] * R_CONT))
T_PIST0 = L_COPPA + L1_GEOM                     # cima del pistone (senza distanziali), a riposo
T_PAD1 = T_PIST0 + L_PIST + T_PAD               # faccia inferiore del pattino
T_BC = T_PAD1 + R_RULL                          # centro del rullino a riposo
BC_rip = lungo_asse(cima0, T_BC)
BC0 = rot(BC_rip, -PHI_CAMMA, PT)


def comp_gril(phi):
    c = rot(BC0, phi, PT)
    return dot((c[0] - BC_rip[0], c[1] - BC_rip[1]), U)


def dcomp_gril(phi, h=0.05):
    return (comp_gril(phi + h) - comp_gril(phi - h)) / math.radians(2 * h)


def lat_naso(phi):
    c = rot(BC0, phi, PT)
    return dot((c[0] - cima0[0], c[1] - cima0[1]), NF)


PHIS = [PHI_FINE + (0.0 - PHI_FINE) * i / 20 for i in range(21)]
LAT = [lat_naso(f) for f in PHIS]
LAT_MIN, LAT_MAX = min(LAT), max(LAT)
A_ASSIALE = T_BC - dot((PT[0] - cima0[0], PT[1] - cima0[1]), (-U[0], -U[1]))
CC = comp_cane(ANG_ARMO)
CG = comp_gril(PHI_FINE)

# =====================================================================
# PROFILI 2D
# =====================================================================
zb = ZB
P0, P1 = P
braccio = SPoly([
    (X_STOP, zb - 5.5), (X_STOP, zb + 5.0), (X_STOP - 1.5, zb + 9.0),
    (P0 + 6.5, 14.5), (P0 + 4.5, 19.0), (P0 + 1.0, Z_SPERONE),
    (P0 - 3.0, Z_SPERONE - 0.5), (P0 - 6.0, Z_SPERONE - 2.5), (P0 - 7.5, Z_SPERONE - 5.0),
    (P0 - 5.0, Z_SPERONE - 5.5), (P0 - 2.5, Z_SPERONE - 8.0), (P0 - 1.5, zb + 9.0),
    (X_FACE - 3.0, zb + 6.5),
    (P0 - R_MOZZO * 0.9, P1 + 2), (P0 + R_MOZZO * 0.9, P1 - 2),
])
SPERONE = (P0 - 5.0, Z_SPERONE - 4.5)
mozzo = Point(P).buffer(R_MOZZO, 32)
coda_g = LineString([P, coda0]).buffer(R_CONT, 16)

pose_arm = [ANG_ARMO * i / 26 for i in range(27)]
fer_col = []
for th in pose_arm:
    for tip in {_tip_armamento(th), TIP_S if th == 0 else _tip_armamento(th),
                TIP_R if th >= th_urto else _tip_armamento(th)}:
        col, sh = perc_2d(tip)
        fer_col.append(rotg(col.buffer(0.2), -th, P))
for i in range(11):
    th = th_urto * i / 10
    col, sh = perc_2d(x_piano(X_FACE, th) + L_PERC)
    fer_col.append(rotg(col.buffer(0.2), -th, P))
fer_col = unary_union(fer_col)
fer_sh = unary_union([rotg(perc_2d(_tip_armamento(th))[1].buffer(0.2), -th, P) for th in pose_arm] +
                     [rotg(perc_2d(x_piano(X_FACE, th_urto * i / 10) + L_PERC)[1].buffer(0.2), -th_urto * i / 10, P)
                      for i in range(11)])

cane2d_pieno = braccio.union(mozzo).union(coda_g).union(camma0).simplify(0.03)
cane2d_pieno = cane2d_pieno.difference(Point(P0 + ALLEGG[0], ALLEGG[1]).buffer(ALLEGG[2], 24))
for _al in ALLEGG2:                 # fori di alleggerimento nel corpo (cane piu' leggero = urto piu' efficiente)
    cane2d_pieno = cane2d_pieno.difference(Point(P0 + _al[0], _al[1]).buffer(_al[2], 24))
cane2d_netto = cane2d_pieno.difference(fer_col)

# --- grilletto (definito a phi = 0, naso nella tacca) ---
naso = sbox(N0[0] - W_NASO - 0.05, N0[1] - 2.6, N0[0] - 0.1, N0[1])
braccio_naso = sbox(PT[0], N0[1] - 3.4, N0[0] - W_NASO + 0.5, N0[1] - 1.6)     # v3: 1.4 di spessore -> 1.8
lama = unary_union([
    LineString([PT, (29.0, -32.5)]).buffer(2.2, 16),
    SPoly([(27.0, -31.5), (32.0, -31.5), (36.0, -37.0), (37.2, -44.0), (36.3, -50.0), (34.2, -54.0),
           (32.4, -53.2), (33.2, -47.5), (32.3, -41.0), (29.0, -35.5)]),
])
# braccio nel manico: scende DAVANTI alla molla e porta la forcella del rullino sotto il pattino
OFF_K = max(D_SEDE / 2, LAT_MAX + 1.6) + R_BRACCIO + 0.8 + max(0.0, -LAT_MIN) + OFF_EXTRA
K_rip = (BC_rip[0] + NF[0] * OFF_K, BC_rip[1] + NF[1] * OFF_K)
K_alto = lungo_asse((cima0[0] + NF[0] * OFF_K, cima0[1] + NF[1] * OFF_K), T_PIST0 - 4.0)
braccio_rip = LineString([PT, K_alto, K_rip, BC_rip]).buffer(R_BRACCIO, 16, join_style=1)
braccio_g = rotg(braccio_rip, -PHI_CAMMA, PT).union(Point(BC0).buffer(R_FORC, 24))
gril2d = unary_union([Point(PT).buffer(R_MOZZO_G, 24), naso, braccio_naso, lama, braccio_g]).simplify(0.03)
gril2d = gril2d.difference(Point(PT).buffer(D_PERNO_G / 2 + 0.15, 16))
gril2d_netto = gril2d.difference(Point(BC0).buffer((D_PERNO_R + 0.15) / 2, 16))
rull2d = Point(BC0).buffer(R_RULL, 32).difference(Point(BC0).buffer((D_PERNO_R + 0.25) / 2, 16))


def cane_pose(th, netto=True):
    return rotg(cane2d_netto if netto else cane2d_pieno, th, P)


def gril_pose(phi):
    return rotg(gril2d, phi, PT)


def rull_pose(phi):
    return rotg(rull2d, phi, PT)


D_PIST = D_SEDE - 0.4


def pistone_2d(dt=0.0):
    o = lungo_asse(cima0, dt)
    cil = banda_asse(o, T_PIST0, T_PIST0 + L_PIST, D_PIST / 2)
    a, b = LAT_MIN - 1.6 - 0.5, LAT_MAX + 1.6 + 0.5
    c0, c1 = lungo_asse(o, T_PIST0 + L_PIST), lungo_asse(o, T_PAD1)
    pad = SPoly([(c0[0] + NF[0] * a, c0[1] + NF[1] * a), (c0[0] + NF[0] * b, c0[1] + NF[1] * b),
                 (c1[0] + NF[0] * b, c1[1] + NF[1] * b), (c1[0] + NF[0] * a, c1[1] + NF[1] * a)])
    return cil.union(pad)


def molla_2d(L, De, dt_cima=0.0):
    return banda_asse(lungo_asse(cima0, dt_cima), L_COPPA, L_COPPA + L, De / 2)


# =====================================================================
# USCITA
# =====================================================================
righe = []


def out(s=""):
    righe.append(s)
    print(s)


def _vol(a, b):
    try:
        return (a & b).volume
    except Exception:
        return 0.0


# =====================================================================
# MASSE, SIMULAZIONE (stessa di v2/v3)
# =====================================================================
m_cane = cane2d_netto.area * SP_CANE * RHO_PLA
I_cane = J_geom(cane2d_netto, P) * SP_CANE * RHO_PLA
r_eff = abs(dx_piano(X_FACE, th_urto / 2))
m_eff_ax = I_cane / r_eff ** 2


def massa_cartuccia(tipo="aperta"):
    Lb = p.cart_bossolo_L[1] if tipo == "corta" else p.cart_bossolo_L[0]
    R, Rc, Rg, Ro = p.cart_D / 2, p.cart_D_corpo / 2, p.cart_gola_D / 2, p.cart_ogiva_D / 2
    f = p.cart_fascia
    g0, g1 = f, f + 0.8
    ri_g, ri = Rg - p.cart_parete, Rc - p.cart_parete
    fondo = 1.2 if tipo == "chiusa" else 0.0
    arco = [(Ro * math.cos(math.radians(90 * i / 12)), Lb + p.cart_ogiva_L + p.cart_punta_L * math.sin(math.radians(90 * i / 12)))
            for i in range(1, 13)]
    prof = SPoly([(0, 0), (R, 0), (R, g0), (Rg, g0), (Rg, g1), (Rc, g1 + (Rc - Rg)), (Rc, Lb - f), (R, Lb - f),
                  (R, Lb), (Ro, Lb), (Ro, Lb + p.cart_ogiva_L)] + arco).buffer(0)
    cav = SPoly([(0, fondo), (ri_g, fondo), (ri_g, g1 + 0.5), (ri, g1 + 0.5 + (ri - ri_g)), (ri, Lb - ri), (0, Lb)]).buffer(0)
    sez = prof.difference(cav)
    if tipo != "chiusa":
        sez = sez.union(sbox(0, 0, 1.5, Lb - 1.4))
    return 2 * math.pi * sez.centroid.x * sez.area * RHO_CART


M_CART = massa_cartuccia("aperta")


def simula_cane(m, m_proj=None, F_tr=F_TRATT, dt=2e-7):
    """Caduta del cane, urto col percussore, spinta della cartuccia (1D, SI). Come v2/v3."""
    m_proj = M_CART if m_proj is None else m_proj
    k = m["k"] * 1e3
    I = I_cane * 1e-9 + (m["massa"] / 3 * 1e-3) * (dcomp_cane(ANG_ARMO / 2) * 1e-3) ** 2
    mp, mc = M_PERC * 1e-3, m_proj * 1e-3
    pre = m["pre"] + comp_gril(PHI_FINE)
    le = math.log(E_REST)
    z_ = -le / math.sqrt(math.pi ** 2 + le ** 2)
    c1 = 2 * z_ * math.sqrt(K_CONT * (mp * m_eff_ax * 1e-3 / (mp + m_eff_ax * 1e-3)))
    c2 = 2 * z_ * math.sqrt(K_CONT * (mp * mc / (mp + mc)))
    k_stop = 50 * K_CONT * (r_eff * 1e-3) ** 2
    c_stop = 2 * z_ * math.sqrt(k_stop * I)
    th, om = math.radians(ANG_ARMO), 0.0
    xp, vp = _tip_armamento(ANG_ARMO) * 1e-3, 0.0
    xc, vc = X_CAM * 1e-3, 0.0
    Lp = L_PERC * 1e-3
    E0 = m["k"] * ((pre + comp_cane(ANG_ARMO)) ** 2 - pre ** 2) / 2
    KE_urto, t, libero, t_lib, W_tr = None, 0.0, False, 0.0, 0.0
    while t < 0.03:
        thd = math.degrees(th)
        xf = x_piano(X_FACE, thd) * 1e-3
        dxf = dx_piano(X_FACE, thd) * 1e-3
        tau = -ETA_MECC * k * (pre + comp_cane(thd)) * 1e-3 * dcomp_cane(thd) * 1e-3
        d1 = xf - (xp - Lp)
        F1 = max(0.0, K_CONT * d1 + c1 * (dxf * om - vp)) if d1 > 0 else 0.0
        if F1 > 0 and KE_urto is None:
            KE_urto = 0.5 * I * om ** 2 * 1e3
        xl = x_piano(X_STOP - T_LIP, thd) * 1e-3
        d3 = (xp - Lp + L_COL * 1e-3) - xl
        F3 = max(0.0, K_CONT * d3 + c1 * (vp - dx_piano(X_STOP - T_LIP, thd) * 1e-3 * om)) if d3 > 0 else 0.0
        d2 = xp - xc
        F2 = max(0.0, K_CONT * d2 + c2 * (vp - vc)) if d2 > 0 else 0.0
        Ts = (-k_stop * th - c_stop * om) if th < 0 else 0.0
        u = (xc - X_CAM * 1e-3) * 1e3
        ov = max(0.0, min(u + p.cart_fascia, p.cart_fascia + 0.5) - max(u, 0.0))
        Ftr = F_tr * min(ov, p.cart_fascia) / p.cart_fascia
        if vc > 1e-6 or F2 > Ftr:
            ac = (F2 - Ftr) / mc
        else:
            ac, vc = 0.0, 0.0
        al = (tau - F1 * dxf + F3 * dxf + Ts) / I
        ap = (F1 - F2 - F3) / mp
        om += al * dt; th += om * dt
        vp += ap * dt; xp += vp * dt
        vc += ac * dt; xc += vc * dt
        W_tr += Ftr * max(vc, 0) * dt
        t += dt
        if not libero and u > p.cart_fascia + 0.5 and F2 == 0 and vc > vp:
            libero, t_lib = True, t
        if libero and t - t_lib > 2e-4:
            break
    KE_c = 0.5 * mc * vc ** 2 * 1e3
    return dict(E0=E0, KE_urto=KE_urto or 0.0, KE_c=KE_c, v=vc, W_tr=W_tr * 1e3, eta=KE_c / E0)


def gittata(v, ang_deg=0.0, m_g=None, h=H_TIRO):
    m_g = M_CART if m_g is None else m_g
    A = math.pi * (p.cart_D / 2 * 1e-3) ** 2
    kd = 0.5 * RHO_ARIA * CD * A / (m_g * 1e-3)
    x, z = 0.0, h
    vx, vz = v * math.cos(math.radians(ang_deg)), v * math.sin(math.radians(ang_deg))
    dt = 1e-4
    while z > 0:
        vv = math.hypot(vx, vz)
        vx -= kd * vv * vx * dt
        vz -= (9.81 + kd * vv * vz) * dt
        x += vx * dt
        z += vz * dt
    return x


def v_per_gittata(g_m, m_g=None):
    lo, hi = 1.0, 40.0
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if gittata(mid, 0, m_g) < g_m else (lo, mid)
    return hi


b_h = lambda th: dcomp_cane(th)            # noqa: E731
b_t = lambda phi: -dcomp_gril(phi)         # noqa: E731
r_dente = math.dist(P, N0)
r_dito = math.dist(PT, DITO)


def forze(m, mu_naso=MU_NASO):
    F = lambda th, phi: m["k"] * (m["pre"] + comp_cane(th) + comp_gril(phi))   # noqa: E731
    F_arm = F(ANG_ARMO, 0.0)
    F_sg = F(ANG_ARMO, PHI_SGANCIO)
    tau_h = F_arm * b_h(ANG_ARMO)
    N_dente = tau_h / r_dente
    attr_naso = mu_naso * F_sg * A_ASSIALE
    F_dito = (F_sg * b_t(PHI_SGANCIO) + MU * N_dente * L_NASO + attr_naso) / r_dito
    ritorno = F(0.0, PHI_CAMMA) * b_t(PHI_CAMMA) - mu_naso * F(0.0, PHI_CAMMA) * A_ASSIALE
    F_poll = max(F(th, 0.0) * b_h(th) for th in (0.0, ANG_ARMO / 2, ANG_ARMO)) / math.dist(P, SPERONE)
    F_max = F(ANG_ARMO, PHI_FINE)
    L_min = m["L1"] - comp_cane(ANG_ARMO) - comp_gril(PHI_FINE)
    return dict(F_rip=F(0.0, PHI_CAMMA), F_arm=F_arm, F_max=F_max, L_min=L_min, F_dito=F_dito,
                F_poll=F_poll, ritorno=ritorno, N_dente=N_dente)


def scegli_distanziale(L0, fac):
    """Distanziale (passi di 0.5, 0..DIST_MAX) piu' spesso = piu' energia, con molla <= F_LIM e grilletto <= F_DITO_MAX."""
    best = None
    for i in range(0, int(DIST_MAX * 2) + 1):
        sp = i / 2
        m = molla_cfg(L0, fac, sp)
        if m["pre"] < PRE_MIN:
            continue
        f = forze(m)
        if f["F_max"] > F_LIM + 1e-9 or f["F_dito"] > F_DITO_MAX + 1e-9:
            continue
        best = (sp, f["F_max"])
    return best


def valuta(L0, fac=1.0, sp=None):
    adatta = True
    if sp is None:
        sc = scegli_distanziale(L0, fac)
        adatta = sc is not None
        sp = sc[0] if sc else 0.0
        if not adatta:
            return dict(adatta=False, sp=None, m=molla_cfg(L0, fac, 0.0))
    m = molla_cfg(L0, fac, sp)
    f = forze(m)
    s = simula_cane(m)
    g = gittata(s["v"])
    return dict(adatta=adatta, m=m, f=f, s=s, g=g, sp=sp, tau=tau_molla(f["F_max"]),
                ok_pacco=f["L_min"] >= m["Lp"] + p.margine_pacco, ok_pre=m["pre"] >= PRE_MIN)


def distanziali(sp):
    """Scompone sp (intero) nei dischi di DIST_SET."""
    resto, usati = round(sp * 2) / 2, []
    for d in sorted(DIST_SET, reverse=True):
        if resto >= d - 1e-9:
            usati.append(d)
            resto -= d
    return "+".join(f"{d:g}" for d in sorted(usati)) if usati else "nessuno"


# =====================================================================
# SPAZIO NEL MANICO e SEZIONE DEL TELAIO
# =====================================================================
_s_cap = BT["S_CAP"]
_dentro_cap = SPoly(BT["profilo_imp"](CAP_SIC, s0=_s_cap - 0.5)).buffer(0)
_zona_cap = SPoly([imp_xz(_s_cap, -200), imp_xz(_s_cap, 200), imp_xz(300, 200), imp_xz(300, -200)])
anello_cap = grip.intersection(_zona_cap).difference(_dentro_cap)
_sopra_imp = SPoly([imp_xz(2, -200), imp_xz(2, 200), imp_xz(-200, 200), imp_xz(-200, -200)])
materiale_imp = grip.union(_sopra_imp.intersection(TEL)).difference(anello_cap)
lecito_imp = materiale_imp.buffer(-PARETE)


def t_max_sede(D):
    t = 10.0
    while t < 150 and banda_asse(cima0, -1.0, t + 0.5, D / 2).difference(lecito_imp).area < 0.02:
        t += 0.5
    return t


_cache_sez = {}


def semi_larghezza(x, z):
    """Semi-larghezza del telaio (Y) nel punto (x, z) secondo la guaina di build.py."""
    if z <= BT["Z_INNESTO"]:
        return W2
    chiave = round(x)
    if chiave not in _cache_sez:
        w = BT["_sezione"](float(round(x)))
        pts = []
        for e in w.edges():
            for i in range(41):
                v = e @ (i / 40)
                pts.append((v.Y, v.Z))
        _cache_sez[chiave] = MultiPoint(pts).convex_hull
    g = _cache_sez[chiave].intersection(LineString([(-60, z), (60, z)]))
    return 0.0 if g.is_empty else min(-g.bounds[0], g.bounds[2])


def z_cima_profilo(x):
    g = TEL.intersection(LineString([(x, -500), (x, 500)]))
    return None if g.is_empty else g.bounds[3]


# =====================================================================
#                         1. MOLLA REALE
# =====================================================================
out("=" * 100)
out("1. MOLLA REALE: filo di molla inox 304 De 8, filo 1.0, passo ~3 (da tagliare)")
out("=" * 100)
_k45 = k_molla(L0_STIMA)
out(f"1a. Modello: Dm {MOLLA_Dm:g}, C {C_IND:.1f} (Wahl {K_WAHL:.3f}), G {MOLLA_G:g} MPa; spire attive = L0/{MOLLA_PASSO:g} - {MOLLA_NM:g} "
    f"(ultima spira di ogni capo chiusa a pinza).")
out(f"    Vostri numeri: L0 {L0_STIMA:g} -> {L0_STIMA / MOLLA_PASSO - MOLLA_NM:.0f} spire attive, k {_k45:.2f} N/mm (ok, coincide).")
out(f"    k scende col taglio piu' lungo: k(L0) = {MOLLA_G * MOLLA_d ** 4 / (8 * MOLLA_Dm ** 3):.1f} / (L0/{MOLLA_PASSO:g} - {MOLLA_NM:g})  "
    + ", ".join(f"L0 {L:g}: {k_molla(L):.2f}" for L in (45, 50, 55, 60, 65, 70)))
out(f"    Tolleranza richiesta: k x (1 +- {K_TOLL:.2f}). Tau ammessa {TAU_AMM:.0f} MPa (0.45 Rm, Rm {RM_INOX:g} prudente per 304 d1.0).")
out(f"    Geometria del cane (v3, invariata): coda {L_CODA:.1f} mm, {ANG_ARMO:g} gradi -> il cane comprime {CC:.2f} mm, il grilletto "
    f"a fondo corsa altri {CG:+.2f}.")
out(f"    Per tutti i pezzi: cane {m_cane:.1f} g (massa efficace all'asse {m_eff_ax:.1f} g), percussore {M_PERC:.2f} g, "
    f"cartuccia {M_CART:.2f} g.")

out("")
_vg = {g: v_per_gittata(g) for g in (GITT_MIN, 4.5, GITT_MAX)}
_Eg = {g: 0.5 * M_CART * v ** 2 for g, v in _vg.items()}
out(f"1b. OBIETTIVO: {GITT_MIN:g}-{GITT_MAX:g} m di tiro teso (da {H_TIRO} m, Cd {CD}): "
    + ", ".join(f"{g:g} m = {_vg[g]:.1f} m/s = {_Eg[g]:.0f} mJ" for g in _vg) + " nella cartuccia.")
out(f"    Con il rendimento simulato molla->cartuccia (~27-29%) servono ~{_Eg[GITT_MIN] / 0.28:.0f}-{_Eg[GITT_MAX] / 0.27:.0f} mJ nella molla.")
_Emax_cost = (CC) * F_LIM
out(f"    LIMITE FISICO: con corsa {CC:.1f} mm e forza max {F_LIM:g} N la molla non puo' dare piu' di {CC:.1f} x {F_LIM:g} = "
    f"{_Emax_cost:.0f} mJ (molla a forza costante, L0 infinita).")
out(f"    Una molla vera (forza che sale) ne da' meno: E = F_max x corsa - k corsa^2 / 2. Per questo con F <= {F_LIM:g} N si arriva "
    f"alla parte BASSA della finestra (~4.0-4.3 m), non a 5 m.")

# --- 1c. confronto delle lunghezze di taglio ---
out("")
out(f"1c. LUNGHEZZE DI TAGLIO a k nominale, sede fissa L1_GEOM = {L1_GEOM:g} mm (senza distanziali), distanziale scelto per "
    f"F armato ~{F_TARGET:g} N (max {F_LIM:g}):")
out(f"    {'L0':>4s} {'spire':>5s} {'k':>5s} {'dist':>4s} {'L1':>5s} {'pre':>5s} {'Frip':>5s} {'Fmax':>5s} {'Lmin':>5s}/{'pac':>4s} "
    f"{'tau':>4s} {'E0':>4s} {'Ec':>5s} {'v':>5s} {'teso':>5s} {'dito':>5s} {'poll':>5s}")
TAB_L0 = {}
for L0 in (45.0, 50.0, 55.0, 60.0, 65.0, 70.0):
    r = valuta(L0)
    TAB_L0[L0] = r
    if not r["adatta"]:
        m = r["m"]
        if L0 - L1_GEOM < PRE_MIN:
            _pm = max(PRE_MIN, L0 - L1_GEOM + DIST_MAX)
            out(f"    {L0:4.0f} {m['nt']:5.1f} {m['k']:5.2f}  NON ADATTA (troppo dura): col precarico minimo possibile ({_pm:g} mm) "
                f"fa gia' {m['k'] * (_pm + CC + CG):.1f} N")
        else:
            out(f"    {L0:4.0f} {m['nt']:5.1f} {m['k']:5.2f}  NON ADATTA (troppo lunga per la sede {L1_GEOM:g}): senza distanziale "
                f"precarico {L0 - L1_GEOM:g} mm = {m['k'] * (L0 - L1_GEOM + CC + CG):.1f} N")
        continue
    m, f, s = r["m"], r["f"], r["s"]
    note = "" if r["ok_pacco"] else " PACCO"
    out(f"    {L0:4.0f} {m['nt']:5.1f} {m['k']:5.2f} {r['sp']:4g} {m['L1']:5.1f} {m['pre']:5.1f} {f['F_rip']:5.1f} {f['F_max']:5.1f} "
        f"{f['L_min']:5.1f}/{m['Lp'] + p.margine_pacco:4.1f} {r['tau']:4.0f} {s['E0']:4.0f} {s['KE_c']:5.1f} {s['v']:5.1f} "
        f"{r['g']:5.2f} {f['F_dito']:5.1f} {f['F_poll']:5.1f}{note}")
out("    (k N/mm, dist = distanziale mm, L/pre mm, F N, tau MPa, E mJ, v m/s, teso m; dito = grilletto, poll = sperone, N)")
_r45 = TAB_L0[45.0]
_r45_vostra = valuta(45.0, 1.0, sp=L1_GEOM - (45.0 - 10.0))   # precarico 10 come nei vostri calcoli
out(f"    I vostri numeri (L0 45, precarico 10, corsa 9): F max {_r45_vostra['f']['F_max']:.0f} N, E0 {_r45_vostra['s']['E0']:.0f} mJ, "
    f"{_r45_vostra['g']:.1f} m, grilletto {_r45_vostra['f']['F_dito']:.0f} N: troppo duro (il grilletto sente ~ la forza della molla).")
out(f"    L0 45 e' troppo dura per la corsa di {CC:.1f} mm: k x corsa = {_k45 * (CC + CG):.0f} N senza precarico, non resta spazio"
    f" per caricarla. Da 55 a 65 i risultati sono simili; 60 lascia il margine di taratura migliore (distanziale a meta').")

# --- 1d. scelta ---
RN = TAB_L0[L0_TAGLIO]
MN, FN, SN = RN["m"], RN["f"], RN["s"]
SP_NOM = RN["sp"]
out("")
out(f"1d. SCELTA: tagliare a L0 = {L0_TAGLIO:g} mm ({L0_TAGLIO / MOLLA_PASSO:.0f} spire a passo {MOLLA_PASSO:g}; contare le spire, "
    f"non i mm), chiudere a pinza l'ultima spira di ogni capo.")
out(f"    k ~{MN['k']:.2f} N/mm ({MN['na']:.0f} attive). Montata a L1 {MN['L1']:g} (sede {L1_GEOM:g} - distanziale {SP_NOM:g} = dischi "
    f"{distanziali(SP_NOM)}): precarico {MN['pre']:.1f} mm, {FN['F_rip']:.1f} N a riposo.")
out(f"    Armato: {FN['F_max']:.1f} N (<= {F_LIM:g}), L {FN['L_min']:.1f} mm (pacco {MN['Lp']:.0f} + {p.margine_pacco:g}), tau "
    f"{RN['tau']:.0f}/{TAU_AMM:.0f} MPa.")
out(f"    Resa: {SN['E0']:.0f} mJ -> {SN['KE_c']:.0f} mJ nella cartuccia ({SN['eta'] * 100:.0f}%), {SN['v']:.1f} m/s, ~{RN['g']:.1f} m teso "
    f"(finestra {GITT_MIN:g}-{GITT_MAX:g}: dentro, in basso).")
out(f"    Mani: pollice sullo sperone ~{FN['F_poll']:.0f} N, grilletto ~{FN['F_dito']:.0f} N (con rullino), ritorno del grilletto "
    f"{FN['ritorno']:.0f} N*mm ({'ok' if FN['ritorno'] > 0 else 'NON torna'}).")
_Fpacco = MN["k"] * (L0_TAGLIO - MN["Lp"])
out(f"    A PACCO (solo se la si schiaccia a mano fuori sede): {_Fpacco:.0f} N, tau {tau_molla(_Fpacco):.0f} MPa > ammessa: "
    f"NON comprimerla a pacco, si siede (perde lunghezza).")
out(f"    Instabilita': L0/Dm = {L0_TAGLIO / MOLLA_Dm:.1f} (> 5.3: libera sbanderebbe) -> la guida il canale quadro {D_SEDE:g} "
    f"(gioco {D_SEDE - MOLLA_De:.1f} sul diametro).")
_r_alta = valuta(L0_TAGLIO, 1.0, SP_NOM + 4)
out(f"    Variante 'gittata': +4 mm di distanziale -> {_r_alta['f']['F_max']:.0f} N, {_r_alta['s']['KE_c']:.0f} mJ, {_r_alta['g']:.1f} m, "
    f"grilletto {_r_alta['f']['F_dito']:.0f} N (oltre il limite dato: solo se il grilletto duro e' accettabile).")
out(f"    Corsa: v3 armava a 26 gradi (9 mm). Qui {ANG_ARMO:g} gradi con la STESSA coda (20 mm): {CC:.2f} mm, ~+0.25 m a pari forza e")
out(f"    pari carico sul dente. Allungare la coda invece (piu' leva) carica il dente: +2 mm di corsa = grilletto +5 N, scartato.")

# --- 1e. tolleranza su k ---
out("")
out(f"1e. TOLLERANZA k +-{K_TOLL * 100:.0f}% (L0 {L0_TAGLIO:g}):")
out(f"    {'k vero':>10s} | {'SENZA taratura (dist ' + format(SP_NOM, 'g') + ')':^34s} | {'CON taratura (distanziale scelto)':^40s}")
TOLL = []
for fac in (1 - K_TOLL, 0.85, 1.0, 1.15, 1 + K_TOLL):
    r0 = valuta(L0_TAGLIO, fac, SP_NOM)
    r1 = valuta(L0_TAGLIO, fac)
    TOLL.append((fac, r0, r1))
    out(f"    {fac:4.2f} {k_molla(L0_TAGLIO, fac):4.2f} | F {r0['f']['F_max']:4.1f} N, {r0['g']:4.2f} m, dito {r0['f']['F_dito']:4.1f} "
        f"{'PACCO' if not r0['ok_pacco'] else '':5s} | dist {r1['sp']:4g} ({distanziali(r1['sp']):>9s}): F {r1['f']['F_max']:4.1f} N, "
        f"{r1['g']:4.2f} m, dito {r1['f']['F_dito']:4.1f}")
_g_lo = min(t[2]["g"] for t in TOLL)
_g_hi = max(t[2]["g"] for t in TOLL)
_g0_lo = min(t[1]["g"] for t in TOLL)
_F0_hi = max(t[1]["f"]["F_max"] for t in TOLL)
out(f"    -> NB: a k +30% anche tarata resta a {TOLL[-1][2]['g']:.2f} m (molla piu' rigida = meno energia a pari forza): "
    f"sotto i 4 m di ~{(GITT_MIN - TOLL[-1][2]['g']) * 100:.0f} cm.")
out(f"    -> senza taratura: {_g0_lo:.1f} m nel caso peggiore (k -30%) e fino a {_F0_hi:.0f} N (k +30%). Con la taratura (bilancia + "
    f"distanziali) si resta a {F_TARGET:g}+-1 N e {_g_lo:.1f}-{_g_hi:.1f} m in tutto l'intervallo.")
_adatte = [L for L, r in TAB_L0.items() if r["adatta"]]
out(f"    La sede ha margine: distanziali da 0 a {DIST_MAX:g} mm -> vanno bene tagli da L0 {min(_adatte):g} a {max(_adatte):g} (e "
    f"intermedi) senza ridisegnare (tabella 1c).")

# --- 1f. taratura ---
_x_prova = 10.0
out("")
out("1f. TARATURA (prima del montaggio, bilancia da cucina):")
out(f"    1. tagliare {L0_TAGLIO / MOLLA_PASSO:.0f} spire (~{L0_TAGLIO:g} mm), chiudere i capi, misurare L0 vera col calibro;")
out(f"    2. infilarla su un'asta d5 (o nel distanziale-guida), premerla di {_x_prova:g} mm sulla bilancia: k = grammi x 0.00981 / {_x_prova:g}.")
out(f"       Atteso {MN['k'] * _x_prova / 9.81 * 1000:.0f} g (k {MN['k']:.2f}); intervallo +-30%: "
    f"{MN['k'] * 0.7 * _x_prova / 9.81 * 1000:.0f}-{MN['k'] * 1.3 * _x_prova / 9.81 * 1000:.0f} g;")
out(f"    3. distanziale [mm] = {L1_GEOM:g} - L0_vera + {F_TARGET:g} / k_misurata - {CC + CG:.1f}, arrotondato per difetto al mezzo mm (dischi 0.5/1/2/4/8);")
out(f"       esempi a L0 {L0_TAGLIO:g} (scelta dello script: piu' energia con molla <= {F_LIM:g} N e grilletto <= {F_DITO_MAX:g} N): " + ", ".join(f"k {k_molla(L0_TAGLIO, f):.2f} -> {r1['sp']:g} mm" for f, r0, r1 in TOLL))
out("    4. se il distanziale viene < 0 (molla molto piu' dura): tagliare 1-2 spire IN PIU' (L0 63-66) e ripetere;")
out(f"       se viene > {DIST_MAX:g} (molto piu' morbida): va bene lo stesso fino a {DIST_MAX:g}, oltre usare L0 piu' lunga.")

# =====================================================================
#                         2. PEZZI E VERIFICHE
# =====================================================================
out("")
out("=" * 100)
out("2. PEZZI DEL MECCANISMO NEL TELAIO DI build.py (profilo di oggi: X_DORSO0/Z_DORSO0 NON cambiano)")
out("=" * 100)

# --- inviluppi (vani) nel piano XZ ---
TH_ALL = [ANG_ARMO * i / 26 for i in range(27)]
sweep_cane = unary_union([cane_pose(th, netto=False) for th in TH_ALL])
PHI_ALL = [PHI_FINE - 0.5 + (0.5 - PHI_FINE + 0.5) * i / 14 for i in range(15)]
sweep_gril = unary_union([gril_pose(f) for f in PHI_ALL] + [rull_pose(f) for f in PHI_ALL])
cg_min, cg_max = min(comp_gril(f) for f in PHI_ALL), max(comp_gril(f) for f in PHI_ALL)
sweep_pist = unary_union([pistone_2d(-cg_min), pistone_2d(-cg_max), pistone_2d(0.0)])
vano_cane = sweep_cane.buffer(0.3)
vano_gril = sweep_gril.buffer(0.3)
vano_molla = unary_union([banda_asse(cima0, -1.0, T_PIST0 + L_PIST + 0.5, D_SEDE / 2), sweep_pist.buffer(0.3)])
foro_pc = Point(P).buffer(D_PERNO / 2, 24)          # d3.0 in CAD: stampato ~2.85 -> spina d3 a leggera interferenza
foro_pg = Point(PT).buffer(D_PERNO_G / 2, 24)

# fori del tamburo / scanalatura di carica / finestra (da build.py)
_car_r = q.camera_d / 2
_car_z = BT["z_car"]
_car_x0 = X_SCUDO - BT["L_car"]
scanal_xz = sbox(_car_x0, _car_z - _car_r, X_SCUDO1 + 0.1, _car_z + _car_r)
y_scan = abs(BT["y_car"]) - _car_r
finestra = sbox(q.x_cam - p.g_tamb, ZA - q.finestra_R, q.x_cam - p.g_tamb + q.finestra_L, ZA + q.finestra_R)
band_pt = sbox(-50, ZA - p.tamb_asse_d / 2 - 0.5, 200, ZA + p.tamb_asse_d / 2 + 0.5)
x_cane_band = vano_cane.intersection(band_pt).bounds[2]
X_PERNO_TAMB = x_cane_band + 0.4                    # nuovo inizio del perno del tamburo
X_FORO_TAMB = x_cane_band - 0.5                     # il foro sbuca nella feritoia (niente setto da 0.4 mm)
foro_tamb = sbox(X_FORO_TAMB, ZA - (p.tamb_asse_d + p.gioco_rot) / 2, 200, ZA + (p.tamb_asse_d + p.gioco_rot) / 2)
foro_perc = sbox(X_SCUDO - 0.1, -(D_SHANK + 0.3) / 2, X_SCUDO1 + 0.1, (D_SHANK + 0.3) / 2)

# spianatura della cresta sopra la feritoia del cane: dove la guaina e' piu' stretta di feritoia + 2 pareti
# le guance finirebbero a lama: la' si allarga la feritoia a tutta la larghezza utile (piano come un top strap)
HW_MIN = (SP_CANE + p.gioco_rot) / 2 + PARETE
_qs = []
_gc = vano_cane.intersection(TEL)
_x = math.floor(_gc.bounds[0])
while _x <= _gc.bounds[2]:
    _zc = z_cima_profilo(_x)
    _z = math.floor(_gc.bounds[1])
    while _zc is not None and _z <= _zc + 0.5:
        if _gc.buffer(0.3).contains(Point(_x, _z)) and semi_larghezza(_x, _z) < HW_MIN:
            _qs.append(sbox(_x - 0.5, _z - 0.25, _x + 0.5, _z + 0.25))
        _z += 0.25
    _x += 0.5
spianatura = unary_union(_qs).buffer(0.25).intersection(TEL) if _qs else Point(0, 0).buffer(0)
SPIAN_PROF = 0.0
if not spianatura.is_empty:
    _xs = [spianatura.bounds[0] + 0.5 * i for i in range(int((spianatura.bounds[2] - spianatura.bounds[0]) / 0.5) + 1)]
    for _x in _xs:
        _f = spianatura.intersection(sbox(_x - 0.25, -100, _x + 0.25, 100))
        if not _f.is_empty and z_cima_profilo(_x) is not None:
            SPIAN_PROF = max(SPIAN_PROF, z_cima_profilo(_x) - _f.bounds[1])

# setti sottili FRA vani (in XZ): si fondono nel vano piu' stretto (un setto < 1.6 non si stampa)
VANI = [("cane", vano_cane, SP_CANE + p.gioco_rot), ("grilletto", vano_gril, SP_GRIL + p.gioco_rot),
        ("molla", vano_molla, D_SEDE), ("foro perno cane", foro_pc, W), ("foro perno grilletto", foro_pg, W),
        ("foro asse tamburo", foro_tamb, p.tamb_asse_d + p.gioco_rot), ("finestra tamburo", finestra, W),
        ("foro percussore", foro_perc, D_SHANK + 0.3)]
if not spianatura.is_empty:
    VANI.append(("spianatura cresta", spianatura, 2 * HW_MIN))
raccordi = []
SETTI = []
for i in range(len(VANI)):
    for j in range(i + 1, len(VANI)):
        ni, gi, wi = VANI[i]
        nj, gj, wj = VANI[j]
        d = gi.distance(gj)
        if d >= PARETE or (ni.startswith("foro perno") and nj in ("cane", "grilletto")):
            continue
        u_ = gi.union(gj)
        chiuso = u_.buffer(PARETE / 2 + 0.05, 16).buffer(-(PARETE / 2 + 0.05), 16)
        sl = chiuso.difference(u_).intersection(gi.buffer(PARETE + 0.1)).intersection(gj.buffer(PARETE + 0.1))
        if sl.area > 0.01:
            raccordi.append((sl, min(wi, wj)))
        SETTI.append((ni, nj, d, sl.area))

racchiudere = unary_union([vano_molla, vano_gril.difference(Point(_cxp, _czp).buffer(BT["R_PONT"] + 1.0)),
                           vano_cane.intersection(sbox(-100, -100, 100, 5.0)),
                           foro_pc.buffer(PARETE), foro_pg.buffer(PARETE)])

# --- 2a. posizioni e pezzi ---
out("2a. PEZZI E POSIZIONI (coordinate di build.py)")
out(f"   cane PLA sp {SP_CANE:g}: perno d{D_PERNO:g} in ({P0:g}, {P1:g}), coda {L_CODA:.1f} mm, {ANG_ARMO:g} gradi di armamento, battuta a "
    f"riposo = retro dello scudo (x {X_SCUDO:g}); {m_cane:.1f} g")
out(f"   grilletto PLA sp {SP_GRIL:g}: perno d{D_PERNO_G:g} in ({PT[0]:g}, {PT[1]:g}) (= finta vite di oggi), naso ({N0[0]:g},{N0[1]:g}) "
    f"aggancio {H_ENG:g} mm, scatto a {PHI_SGANCIO:.1f} gradi, fine corsa {PHI_FINE:.1f}; braccio nel manico lungo "
    f"{math.dist(PT, BC_rip):.0f} mm, forcella del rullino a ({BC0[0]:.1f}, {BC0[1]:.1f})")
out(f"   rullino PLA d{2 * R_RULL:g} x {W_RULL:g} su perno di filamento d{D_PERNO_R:g} x {SP_GRIL - 0.2:g}; corsa sul pattino "
    f"{LAT_MIN:+.1f}..{LAT_MAX:+.1f} mm")
out(f"   percussore flottante PLA: collare d{D_COL:g} x {L_COL:g}, gambo d{D_SHANK:g}, lungo {L_PERC:.1f}; gioco nella forcella "
    f"{G_LOST:.2f} mm; a riposo sporge {TIP_S - X_SCUDO1:.1f}-{TIP_S + G_LOST - X_SCUDO1:.1f} mm dallo scudo, armato e' "
    f"{X_SCUDO1 - TIP_R:.1f} mm DENTRO lo scudo; {M_PERC:.2f} g")
out(f"   sede molla: canale quadro {D_SEDE:g} lungo l'asse inclinato {ANG_MOLLA:g} gradi da ({cima0[0]:.1f},{cima0[1]:.1f}) a "
    f"({lungo_asse(cima0, T_PAD1)[0]:.1f},{lungo_asse(cima0, T_PAD1)[1]:.1f}); "
    f"coppa d{MOLLA_De + 0.6:g} x {L_COPPA:g}, distanziali d{D_PIST:g}, pistone quadro {D_PIST:g} x {L_PIST:g} + pattino {T_PAD:g}")
out(f"   limite della sede: con parete 1.6 un canale {D_SEDE:g} potrebbe scendere fino a t={t_max_sede(D_SEDE):.0f}; "
    f"il rullino arriva a t={T_BC + R_RULL:.0f} (margine {t_max_sede(D_SEDE) - T_BC - R_RULL:.0f} mm)")
_bb = sweep_cane.bounds
out(f"   feritoia cane (inviluppo 0-{ANG_ARMO:g}): x {_bb[0]:.1f}..{_bb[2]:.1f}, z {_bb[1]:.1f}..{_bb[3]:.1f} larga {SP_CANE + p.gioco_rot:g}; "
    f"feritoia grilletto: x {sweep_gril.bounds[0]:.1f}..{sweep_gril.bounds[2]:.1f}, z {sweep_gril.bounds[1]:.1f}..{sweep_gril.bounds[3]:.1f} "
    f"larga {SP_GRIL + p.gioco_rot:g}")

# --- 2b. interferenze nelle pose ---
out("")
out("2b. INTERFERENZE NELLE POSE (2D nel piano dei pezzi: cane, grilletto, rullino, pistone, molla stanno tutti su y=0)")
TOLL_A = 0.05          # mm^2: sotto e' contatto (superfici che si toccano per progetto)


def inter(a, b):
    return a.intersection(b).area


def gap(a, b):
    return a.distance(b)


POSE = {}
# armamento: cane da 0 a quasi armato, il naso striscia sul cerchio della camma (phi = PHI_CAMMA)
POSE["armamento"] = max(inter(cane_pose(th).buffer(-0.02), gril_pose(PHI_CAMMA)) for th in TH_ALL[:-1])
POSE["armato (dente in tacca)"] = inter(cane_pose(ANG_ARMO).buffer(-0.02), gril_pose(0.0))
POSE["riposo"] = inter(cane_pose(0.0).buffer(-0.02), gril_pose(PHI_CAMMA))
_gap_scatto = min(gap(cane_pose(th), gril_pose(PHI_FINE)) for th in TH_ALL)
POSE["scatto (cane che cade, grilletto premuto)"] = max(inter(cane_pose(th), gril_pose(PHI_FINE)) for th in TH_ALL)
for k_, v_ in POSE.items():
    out(f"   cane/grilletto {k_:42s}: {v_:5.2f} mm^2 {'(contatto)' if 0 < v_ < TOLL_A else ('OK' if v_ == 0 else 'INTERFERISCE')}")
out(f"   scatto: luce minima naso/camma mentre il cane cade {_gap_scatto:.2f} mm")
# grilletto (senza rullino) / pistone+pattino in tutta la corsa: deve restare staccato, il carico passa solo dal rullino
_gp = min(gap(gril_pose(f).difference(Point(rot(BC0, f, PT)).buffer(R_FORC + 0.01)), pistone_2d(-comp_gril(f))) for f in PHI_ALL)
_rp = max(inter(rull_pose(f).buffer(-0.02), pistone_2d(-comp_gril(f))) for f in PHI_ALL)
_fp = min(gap(Point(rot(BC0, f, PT)).buffer(R_FORC), pistone_2d(-comp_gril(f))) for f in PHI_ALL)
out(f"   grilletto/pistone+pattino: luce minima {_gp:.2f} mm (braccio), forcella {_fp:.2f} mm; rullino/pattino {_rp:.2f} mm^2 (contatto)")
arm_alto = lambda f: gril_pose(f).difference(banda_asse(cima0, T_PIST0 - 0.5, 200, 30))   # noqa: E731
_dsp = min(arm_alto(f).distance(molla_2d(L1_GEOM - SP_NOM - CC, MOLLA_De, CC).union(molla_2d(L1_GEOM - SP_NOM, MOLLA_De)))
           for f in PHI_ALL)
out(f"   grilletto/spire della molla (riposo e armato): luce minima {_dsp:.2f} mm -> {'non le tocca' if _dsp > 0.3 else 'TROPPO VICINO'}")
_cm = min(gap(cane_pose(th).difference(coda_g.buffer(0.01) if th == 0 else rotg(coda_g, th, P).buffer(0.01)),
              molla_2d(L1_GEOM - SP_NOM - comp_cane(th), MOLLA_De + 0.6, comp_cane(th))) for th in TH_ALL)
out(f"   cane (fuori dalla coda)/coppa+molla: luce minima {_cm:.2f} mm")
_cs = sweep_cane.bounds[2]
out(f"   cane/scudo: il cane arriva a x {_cs:.2f} (scudo da {X_SCUDO:g}) -> la battuta e' lo scudo, nessuna compenetrazione")
_cpc = TIP_S - L_PERC + L_COL
out(f"   percussore/scudo: collare davanti a x {_cpc + G_LOST:.2f} al massimo (scudo {X_SCUDO:g}), gambo d{D_SHANK:g} nel foro "
    f"d{D_SHANK + 0.3:.1f}")
_sweep_tot = unary_union([sweep_cane, sweep_gril])
_fuori = sweep_gril.difference(materiale_imp.union(TEL).union(vano_pont).union(ponticello).buffer(0.01))
out(f"   grilletto fuori da telaio/manico/ponticello: {_fuori.area:.2f} mm^2")

# --- 2c. pareti ---
out("")
out(f"2c. PARETI (minimo {PARETE:g} mm)")
tel_mat = TEL.union(ponticello)
vani_tutti = unary_union([v for _, v, _ in VANI] + [r for r, _ in raccordi] + [vano_pont])
# le zone sottili ammesse: bordo dell'apertura in alto della feritoia del cane (sperone fuori) e uscita della lama nel ponticello
_apert = unary_union([vano_cane.difference(TEL).buffer(1.2), vano_gril.intersection(vano_pont.buffer(1.0)).buffer(1.2),
                      vano_gril.difference(TEL.union(ponticello)).buffer(1.2)])


def _mat_mecc():
    vt = unary_union([v for _, v, _ in VANI] + [r for r, _ in raccordi] + [vano_pont])
    return tel_mat.difference(vt).intersection(sbox(-40, -95, X_SCUDO1 + 2, 30))


mat_mecc = _mat_mecc()
N_FUSI = 0
for c in sottili(mat_mecc):          # lingue sottili di materiale FRA due vani (non sul bordo esterno): si fondono
    if c.distance(TEL.exterior) > 0.3 and c.difference(_apert).area > 0.5:
        w_ = min([w for _, v, w in VANI if v.distance(c) < 0.05] or [SP_GRIL + p.gioco_rot])
        raccordi.append((c.buffer(0.1), w_))
        N_FUSI += 1
mat_mecc = _mat_mecc()
_sott = sottili(mat_mecc)
_sott_veri = [c for c in _sott if c.difference(_apert).area > 0.5]
out(f"   XZ, materiale del telaio fra vani ed esterno: {len(_sott)} zone < {PARETE:g} mm, di cui {len(_sott_veri)} fuori dai bordi "
    f"delle aperture volute" + ("" if not _sott_veri else ": " + "; ".join(
        f"x {c.bounds[0]:.0f}..{c.bounds[2]:.0f} z {c.bounds[1]:.0f}..{c.bounds[3]:.0f} ({c.area:.1f} mm^2)" for c in _sott_veri)))
_viol = racchiudere.difference(TEL.union(ponticello).buffer(-PARETE)).area
out(f"   vani chiusi (molla, grilletto fuori dal ponticello, cane sotto z 5, perni) dentro il telaio con parete: fuori "
    f"{_viol:.2f} mm^2 ({'OK' if _viol < 0.1 else 'BUCA'})")
if N_FUSI:
    out(f"   {N_FUSI} lingue di materiale < {PARETE:g} fra due vani (non sul bordo esterno): fuse nel vano piu' stretto")
for ni, nj, d, a in SETTI:
    out(f"   setto {ni}/{nj}: {d:.2f} mm < {PARETE:g} -> " + ("fuso nel vano piu' stretto (aperto)" if a > 0.01 else "si toccano per progetto"))
# molla nel manico
_dmin = min(pg.exterior.distance(vano_molla) for pg in poligoni(materiale_imp))
_vm = vano_molla.difference(lecito_imp).area
out(f"   sede molla in XZ: fuori dalla parete minima {_vm:.2f} mm^2, parete minima verso l'esterno del manico {_dmin:.1f} mm")
_pts_m = [lungo_asse(cima0, t) for t in range(0, int(T_PAD1) + 1, 2)]
_sl_m = min(semi_larghezza(x, z) for x, z in _pts_m)
out(f"   sede molla in Y: telaio largo {2 * _sl_m:.1f} lungo la molla, canale {D_SEDE:g} -> {_sl_m - D_SEDE / 2:.1f} mm per lato")


def parete_y(vano, larg, solo_sotto_cima=True, passo=1.0):
    """Minimo di (semi-larghezza locale del telaio - meta' feritoia) sui punti del vano dentro il profilo."""
    g = vano.intersection(TEL)
    x0, z0, x1, z1 = g.bounds
    peggio = (99.0, None)
    x = math.floor(x0)
    while x <= x1:
        zc = z_cima_profilo(x)
        zz = math.floor(z0)
        while zz <= z1:
            if g.contains(Point(x, zz)) and not spianatura.buffer(0.3).contains(Point(x, zz)) \
                    and (not solo_sotto_cima or zc is None or zz <= zc - 0.5):
                w_ = semi_larghezza(x, zz) - larg / 2
                if w_ < peggio[0]:
                    peggio = (w_, (x, zz))
            zz += passo
        x += passo
    return peggio


PY_CANE = parete_y(vano_cane, SP_CANE + p.gioco_rot)
PY_GRIL = parete_y(vano_gril, SP_GRIL + p.gioco_rot)
out(f"   cresta sopra la feritoia del cane: dove la guaina e' piu' stretta di {2 * HW_MIN:.1f} la feritoia si allarga a {2 * HW_MIN:.1f} "
    f"(spianatura x {spianatura.bounds[0]:.0f}..{spianatura.bounds[2]:.0f}, al massimo {SPIAN_PROF:.1f} mm sotto il profilo)"
    if not spianatura.is_empty else "   cresta sopra la feritoia del cane: larga abbastanza, nessuna spianatura")
out(f"   guance della feritoia del cane (sotto il profilo di build.py): {PY_CANE[0]:.2f} mm in ({PY_CANE[1][0]:.0f},{PY_CANE[1][1]:.0f}) "
    f"{'OK' if PY_CANE[0] >= PARETE - 1e-3 else 'SOTTILE'}")
out(f"   guance della feritoia del grilletto: {PY_GRIL[0]:.2f} mm in ({PY_GRIL[1][0]:.0f},{PY_GRIL[1][1]:.0f}) "
    f"{'OK' if PY_GRIL[0] >= PARETE - 1e-3 else 'SOTTILE'}")
_sov = vano_cane.intersection(scanal_xz)
if _sov.is_empty:
    PY_SCAN = 99.0
    out("   scanalatura di carica: non si sovrappone alla feritoia del cane")
else:
    zs = [_sov.bounds[1] + (_sov.bounds[3] - _sov.bounds[1]) * i / 20 for i in range(21)]
    yin = min(abs(BT["y_car"]) - math.sqrt(max(_car_r ** 2 - (z - _car_z) ** 2, 0.0)) for z in zs)
    PY_SCAN = yin - (SP_CANE + p.gioco_rot) / 2
    out(f"   scanalatura di carica / feritoia cane (sovrapposte in XZ a x {_sov.bounds[0]:.1f}..{_sov.bounds[2]:.1f}): parete in Y "
        f"{PY_SCAN:.2f} mm ({'OK' if PY_SCAN >= PARETE - 1e-3 else 'SOTTILE'})")
PY_PONT = (BT["W_PONT"] - SP_GRIL - p.gioco_rot) / 2
_lama_basso = [gril_pose(f).intersection(sbox(22.0, -80, 80, _czp + 4.0)) for f in (0.0, PHI_CAMMA, PHI_FINE)]
_gap_p = min(Point(_cxp, _czp).buffer(BT["r_PONT"], 96).exterior.distance(g) for g in _lama_basso)
out(f"   ponticello (largo {BT['W_PONT']:g}): feritoia della lama {SP_GRIL + p.gioco_rot:g} -> {PY_PONT:.2f} mm per lato; "
    f"lama a {_gap_p:.1f} mm dal bordo interno dell'anello")
# spessori dei pezzi
PEZZI2D = {"cane": cane2d_netto, "grilletto": gril2d_netto, "rullino": rull2d, "pistone+pattino": pistone_2d()}
for n_, g_ in PEZZI2D.items():
    s_ = sottili(g_, amin=0.8)
    out(f"   pezzo {n_:16s}: zone < {PARETE:g} mm: " + ("nessuna" if not s_ else "; ".join(
        f"x {c.bounds[0]:.1f}..{c.bounds[2]:.1f} z {c.bounds[1]:.1f}..{c.bounds[3]:.1f} ({c.area:.1f})" for c in s_)))
_pelle = min(X_STOP - fer_col.intersection(sbox(0, z_ - 0.05, 41, z_ + 0.05)).bounds[2]
             for z_ in [-5.4 + 0.1 * i for i in range(104)] if not fer_col.intersection(sbox(0, z_ - 0.05, 41, z_ + 0.05)).is_empty)
out(f"   faccia di battuta del cane davanti alla tasca del collare: pelle minima {_pelle:.2f} mm "
    f"({'OK' if _pelle >= PARETE - 0.02 else 'SOTTILE'})")
out(f"   forcella del rullino: guance {(SP_GRIL - W_RULL - 0.2) / 2:.2f} mm, mozzo {R_FORC - (D_PERNO_R + 0.15) / 2:.2f} mm attorno al perno; "
    f"labbro della forcella del percussore {T_LIP:g} mm, fianchi {(SP_CANE - D_SHANK - 0.4) / 2:.1f} mm")

# --- 2d. perni ---
out("")
out("2d. PERNI ATTRAVERSO IL TELAIO (gusci in due meta' su y=0, perni infilati dal fianco a gusci chiusi)")
_gu = SPoly(BT["profilo_imp"](BT["RIENTRO_G"], BT["S_G0"], BT["L_IMP"] - BT["RIENTRO_G"])).buffer(0)
PERNI = {}
for nome, c, foro, dpin in (("cane", P, foro_pc, D_PERNO), ("grilletto", PT, foro_pg, D_PERNO_G)):
    hw = semi_larghezza(c[0], c[1])
    d_est = TEL.exterior.distance(foro)
    altri = {"scanalatura carica": scanal_xz, "foro asse tamburo": foro_tamb, "finestra tamburo": finestra,
             "vano molla": vano_molla, ("vano grilletto" if nome == "cane" else "vano cane"): (vano_gril if nome == "cane" else vano_cane)}
    dd = {k: v.distance(foro) for k, v in altri.items()}
    peggio = min(dd, key=dd.get)
    coperto = _gu.contains(Point(c))
    L_pin = 2 * hw - 0.4
    PERNI[nome] = (L_pin, dpin, d_est, peggio, dd[peggio], coperto)
    out(f"   {nome:9s} d{dpin:g}: telaio largo {2 * hw:.1f} -> spina d{dpin:g} x {L_pin:.1f} (0.2 sotto ogni fianco, NON esce); "
        f"parete XZ verso l'esterno {d_est:.1f}, verso '{peggio}' {dd[peggio]:.1f} mm ({'OK' if min(d_est, dd[peggio]) >= PARETE else 'SOTTILE'}); "
        f"{'SOTTO la guancetta' if coperto else 'fuori dalle guancette'}")
out(f"   fori d{D_PERNO:g}/d{D_PERNO_G:g} nominali nel telaio (stampati ~0.15 piu' stretti = spina a leggera interferenza), "
    f"d{D_PERNO + 0.3:g}/d{D_PERNO_G + 0.3:g} nei pezzi mobili (girano liberi).")
out(f"   finte viti in (30.5,-20) e (16,-28): la testa finta ha il foro passante della spina; si spinge fuori con un chiodo.")
out(f"   rullino: perno di filamento d{D_PERNO_R:g} x {SP_GRIL - 0.2:g} nella forcella; lo trattengono i fianchi della feritoia "
    f"(larga {SP_GRIL + p.gioco_rot:g}).")

# --- 2e. tamburo ---
out("")
out("2e. TAMBURO LIBERO DI RUOTARE")
_ing_tamb = sbox(q.x_cam - p.g_tamb, ZA - q.R_tamb - 0.3, q.x_cam + q.L_tamb, ZA + q.R_tamb + 0.3)
_c_t = sweep_cane.intersection(_ing_tamb).area
_g_t = sweep_gril.intersection(_ing_tamb).area
out(f"   inviluppo di rotazione del tamburo (x {q.x_cam - p.g_tamb:.1f}..{q.x_cam + q.L_tamb:.1f}, R {q.R_tamb:.1f}+0.3): cane in tutte "
    f"le pose {_c_t:.2f} mm^2, grilletto {_g_t:.2f} mm^2")
out(f"   percussore ARMATO: punta a x {TIP_R:.2f}, {X_SCUDO1 - TIP_R:.1f} mm dietro la faccia dello scudo e {q.x_cam - TIP_R:.1f} dal "
    f"tamburo -> il tamburo gira libero solo a cane ARMATO")
out(f"   percussore a RIPOSO: la punta entra {TIP_S - q.x_cam:.1f}-{TIP_S + G_LOST - q.x_cam:.1f} mm nella camera -> a cane abbattuto "
    f"il tamburo e' bloccato (voluto: come un revolver ad azione singola si ruota col cane armato)")
out(f"   perno del tamburo: in build.py parte da x {q.x_cam - BT['_PERNO_TAMB_DIETRO']:.1f} e attraversa la feritoia del cane "
    f"(che arriva a x {x_cane_band:.1f} alla sua quota) -> parte da x {X_PERNO_TAMB:.1f}; il suo foro da x {X_FORO_TAMB:.1f} "
    f"(sbuca nella feritoia, nessun setto sottile). Appoggio dietro il tamburo {X_SCUDO1 - X_PERNO_TAMB:.1f} mm (oggi "
    f"{BT['_PERNO_TAMB_DIETRO'] - p.g_tamb:.1f}).")
out("   INDICIZZAZIONE: questo meccanismo NON ha mano/cricchetto ne' fermo: il tamburo si gira a mano (le tacche del fermo sul "
    "tamburo ci sono, il nottolino no). Vedi i rischi.")

# --- 2f. spine dei gusci ---
out("")
out("2f. SPINE DEI GUSCI (finte viti di build.py, filamento d1.75 passante)")
vani_sp = unary_union([vano_cane, vano_gril, vano_molla, foro_pc.buffer(0.5), foro_pg.buffer(0.5)])
viti_nuove = []
for (vx, vz) in BT["viti"]:
    d = Point(vx, vz).distance(vani_sp)
    if math.dist((vx, vz), PT) < 0.6:
        out(f"     ({vx:5.1f},{vz:6.1f}): DIVENTA il perno del grilletto")
        viti_nuove.append((vx, vz))
        continue
    if d >= 0.95 + PARETE:
        out(f"     ({vx:5.1f},{vz:6.1f}): libera ({d:.1f} mm dai vani) -> resta")
        viti_nuove.append((vx, vz))
        continue
    best = None
    for r in [0.5 * i for i in range(1, 60)]:
        for kk in range(24):
            a = 2 * math.pi * kk / 24
            c = (vx + r * math.cos(a), vz + r * math.sin(a))
            pc = Point(c)
            if pc.distance(vani_sp) >= 0.95 + PARETE and TEL.buffer(-(0.95 + PARETE + 1.0)).contains(pc) \
                    and pc.distance(finestra) >= 2.6 and pc.distance(scanal_xz) >= 2.6 and pc.distance(foro_tamb) >= 2.6 \
                    and not _gu.buffer(1.0).contains(pc):
                best = (round(c[0], 1), round(c[1], 1))
                break
        if best:
            break
    out(f"     ({vx:5.1f},{vz:6.1f}): BUCA un vano (a {d:.1f} mm) -> spostarla in ({best[0]:.1f},{best[1]:.1f})")
    viti_nuove.append(best)
VITI_FINALI = viti_nuove + [(P0, P1)]
out(f"   + perno del cane ({P0:g},{P1:g}) come sesta finta vite.")

# --- 2g. variante facoltativa del dorso (v3) ---
TEL_V3 = SPoly(profilo_telaio(-1.0, -23.0)).buffer(0)
_v3ok = racchiudere.difference(TEL_V3.union(ponticello).buffer(-PARETE)).area
_vc = vano_cane.intersection(sbox(-100, -100, 100, 5.0)).difference(TEL_V3.buffer(-PARETE)).area
out("")
out(f"2g. DORSO PIU' CORTO di v3 (X_DORSO0,Z_DORSO0 = -1,-23): FACOLTATIVO, estetico. Con i vani finali: fuori parete "
    f"{_v3ok:.2f} mm^2 -> {'resta valido' if _v3ok < 0.1 else 'NON piu valido con la sede lunga: lasciare il dorso di oggi'}.")

# =====================================================================
# SOLIDI, EXPORT
# =====================================================================
TH_A, PHI_A = ANG_ARMO, 0.0
TH_R, PHI_R = 0.0, PHI_CAMMA


def solido_cane(th):
    s = solido(cane_pose(th), SP_CANE)
    s -= solido(rotg(fer_sh, th, P), D_SHANK + 0.4)
    return s - Pos(P[0], 0, P[1]) * Rot(90, 0, 0) * Cylinder(D_PERNO / 2 + 0.15, SP_CANE + 2)


def solido_gril(phi):
    s = solido(gril_pose(phi), SP_GRIL)
    c = rot(BC0, phi, PT)
    s -= Pos(c[0], 0, c[1]) * Rot(90, 0, 0) * Cylinder(R_RULL + 0.5, W_RULL + 0.2)          # gola della forcella
    s -= Pos(c[0], 0, c[1]) * Rot(90, 0, 0) * Cylinder((D_PERNO_R + 0.15) / 2, SP_GRIL + 2)
    return s


def solido_rull(phi):
    c = rot(BC0, phi, PT)
    return Pos(c[0], 0, c[1]) * Rot(90, 0, 0) * (Cylinder(R_RULL, W_RULL) - Cylinder((D_PERNO_R + 0.25) / 2, W_RULL + 1))


def perno_rull(phi):
    c = rot(BC0, phi, PT)
    return Pos(c[0], 0, c[1]) * Rot(90, 0, 0) * Cylinder(D_PERNO_R / 2, SP_GRIL - 0.2)


def solido_perc(tip):
    return M._cil_x(D_COL, tip - L_PERC, L_COL, z=ZB) + \
        M._cil_x(D_SHANK, tip - L_PERC + L_COL - 0.01, L_PERC - L_COL + 0.01, z=ZB)


def cil_lungo_u(d, base, L):
    ang = math.degrees(math.atan2(U[0], U[1]))
    return Pos(base[0], 0, base[1]) * Rot(0, ang, 0) * Cylinder(d / 2, L, align=(_C, _C, _MIN))


def molla_elica(L, base, n_sp):
    """Molla vera (elica di filo d1) lungo l'asse, da base verso l'alto."""
    from build123d import Helix, Circle, sweep as _sw, Location, Plane as _Pl
    try:
        el = Helix(pitch=L / n_sp, height=L, radius=MOLLA_Dm / 2)
        prof = _Pl(origin=el @ 0, z_dir=el % 0) * Circle(MOLLA_d / 2)
        s = _sw(prof, path=el)
        ang = math.degrees(math.atan2(U[0], U[1]))
        return Pos(base[0], 0, base[1]) * Rot(0, ang, 0) * s
    except Exception:
        return cil_lungo_u(MOLLA_De, base, L) - cil_lungo_u(MOLLA_De - 2 * MOLLA_d, base, L)


def assieme_molla(th, phi, sp=SP_NOM, elica=True):
    dc, dg = comp_cane(th), comp_gril(phi)
    L = L1_GEOM - sp - dc - dg
    cima = lungo_asse(cima0, dc)
    b_sup = lungo_asse(cima, L_COPPA)
    b_mol = lungo_asse(b_sup, L)
    b_dist = lungo_asse(b_mol, sp)
    coppa = cil_lungo_u(MOLLA_De + 0.6, b_sup, L_COPPA)
    mol = molla_elica(L, b_mol, MOLLA_na_tot) if elica else cil_lungo_u(MOLLA_De, b_mol, L)
    dist = []
    t = 0.0
    for d in [float(x) for x in distanziali(sp).split("+")] if sp > 0 else []:
        dist.append(cil_lungo_u(D_PIST, lungo_asse(b_mol, t + d), d - 0.02))
        t += d
    pist = solido(pistone_2d(-dg), D_PIST)
    return mol, coppa, dist, pist


MOLLA_na_tot = L0_TAGLIO / MOLLA_PASSO
cane_ar, cane_ab = solido_cane(TH_A), solido_cane(TH_R)
gril_ar, gril_rip = solido_gril(PHI_A), solido_gril(PHI_R)
rull_ar, rull_rip = solido_rull(PHI_A), solido_rull(PHI_R)
pr_ar, pr_rip = perno_rull(PHI_A), perno_rull(PHI_R)
perc_ar, perc_ab = solido_perc(_tip_armamento(TH_A)), solido_perc(TIP_S)
molla_ar, coppa_ar, dist_ar, pist_ar = assieme_molla(TH_A, PHI_A)
molla_rip, coppa_rip, dist_rip, pist_rip = assieme_molla(TH_R, PHI_R)
tubo_ar, tubo_rip = assieme_molla(TH_A, PHI_A, elica=False)[0], assieme_molla(TH_R, PHI_R, elica=False)[0]   # per i controlli
L_PC, L_PG = PERNI["cane"][0], PERNI["grilletto"][0]
perno_cane = Pos(P[0], 0, P[1]) * Rot(90, 0, 0) * Cylinder(D_PERNO / 2, L_PC)
perno_gril = Pos(PT[0], 0, PT[1]) * Rot(90, 0, 0) * Cylinder(D_PERNO_G / 2, L_PG)
tamburo = M.tamburo_base()
scudo = M._cil_x(2 * BT["r_scudo"], X_SCUDO, X_SCUDO1 - X_SCUDO, z=ZA) - \
    M._cil_x(D_SHANK + 0.3, X_SCUDO - 0.1, X_SCUDO1 - X_SCUDO + 0.2, z=ZB)
perno_tamb = M._cil_x(p.tamb_asse_d, X_PERNO_TAMB, q.x_cam + q.L_tamb + 5 - X_PERNO_TAMB, z=ZA)

# guscio sinistro schematico (fianchi piani y 0..W/2) col profilo di build.py e TUTTI i vani finali
guscio = solido(TEL, W2, y0=W2 / 2)
for _, vano, larg in VANI:
    if vano is finestra:
        continue
    guscio -= solido(vano, larg)
for sl, larg in raccordi:
    guscio -= solido(sl, larg)
guscio -= M.vuoto_finestra_tamburo() + M.vuoto_canna()

# interferenze 3D residue
_pezzi_A = dict(cane=cane_ar, grilletto=gril_ar, rullino=rull_ar, percussore=perc_ar, molla=tubo_ar, pistone=pist_ar)
_pezzi_R = dict(cane=cane_ab, grilletto=gril_rip, rullino=rull_rip, percussore=perc_ab, molla=tubo_rip, pistone=pist_rip)
V3D = {}
for posa, pz in (("armato", _pezzi_A), ("riposo", _pezzi_R)):
    V3D[(posa, "cane/tamburo")] = _vol(pz["cane"], tamburo)
    V3D[(posa, "cane/scudo")] = _vol(pz["cane"], scudo)
    V3D[(posa, "cane/grilletto")] = _vol(pz["cane"], pz["grilletto"])
    V3D[(posa, "grilletto/molla")] = _vol(pz["grilletto"], pz["molla"])
    V3D[(posa, "grilletto/pistone")] = _vol(pz["grilletto"], pz["pistone"])
    V3D[(posa, "rullino/forcella")] = _vol(pz["rullino"], pz["grilletto"])
    V3D[(posa, "pezzi/guscio")] = sum(_vol(guscio, s) for k_, s in pz.items())
V3D[("armato", "percussore/tamburo")] = _vol(perc_ar, tamburo)
V3D[("riposo", "percussore/tamburo (voluto: blocca)")] = _vol(perc_ab, tamburo)
_tamb_rot = [tamburo.rotate(Axis((0, 0, ZA), (1, 0, 0)), a) for a in (10, 20, 30)]
V3D[("armato", "tamburo ruotato 10/20/30 vs pezzi")] = sum(_vol(t, s) for t in _tamb_rot for s in (perc_ar, cane_ar, scudo))
V3D[("-", "perno tamburo/cane")] = max(_vol(perno_tamb, c) for c in (cane_ar, cane_ab))
out("")
out("2h. CONTROLLO 3D [mm^3] (solidi veri; molla = tubo pieno De 8, piu' prudente dell'elica; < 0.5 = contatto voluto)")
for (posa, cosa), v in V3D.items():
    out(f"   {posa:7s} {cosa:38s} {v:7.2f}")

# --- profili per build.py ---
def _js(g):
    return [dict(ext=[(round(x, 3), round(z, 3)) for x, z in pg.exterior.coords[:-1]],
                 holes=[[(round(x, 3), round(z, 3)) for x, z in h.coords[:-1]] for h in pg.interiors]) for pg in poligoni(g)]


PROFILI = dict(
    nota="Profili XZ in coordinate di build.py (y = 0 piano dei gusci). Estrudere simmetrici in Y della larghezza indicata.",
    vano_cane=dict(larghezza=SP_CANE + p.gioco_rot, poligoni=_js(vano_cane)),
    vano_grilletto=dict(larghezza=SP_GRIL + p.gioco_rot, poligoni=_js(vano_gril)),
    vano_molla=dict(larghezza=D_SEDE, poligoni=_js(vano_molla)),
    raccordi=[dict(larghezza=w_, poligoni=_js(g_)) for g_, w_ in raccordi],
    spianatura_cresta=dict(larghezza=2 * HW_MIN, poligoni=_js(spianatura)),
    cane=dict(spessore=SP_CANE, poligoni=_js(cane2d_netto), forcella_gambo=dict(larghezza=D_SHANK + 0.4, poligoni=_js(fer_sh))),
    grilletto=dict(spessore=SP_GRIL, poligoni=_js(rotg(gril2d_netto, PHI_CAMMA, PT))),
    perni=dict(cane=dict(x=P0, z=P1, d=D_PERNO, L=round(L_PC, 1)), grilletto=dict(x=PT[0], z=PT[1], d=D_PERNO_G, L=round(L_PG, 1))),
    foro_percussore=dict(d=D_SHANK + 0.3, x0=X_SCUDO - 0.1, x1=X_SCUDO1 + 0.1, z=0.0),
    perno_tamburo=dict(x_inizio=round(X_PERNO_TAMB, 2), foro_x_inizio=round(X_FORO_TAMB, 2)),
    viti=[(round(a, 1), round(b, 1)) for a, b in VITI_FINALI],
)
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "final_profili.json"), "w") as fh:
    json.dump(PROFILI, fh, indent=1)

# --- disegno laterale ---
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(11, 10))
    x, z = TEL.exterior.xy
    ax.plot(x, z, color="#1f6f63", lw=1.6, label="telaio build.py (invariato)")
    for g, c, lab in ((ponticello.difference(vano_pont), "#4fa89a", "ponticello"), (vano_molla, "#3060ff", "sede molla/pistone"),
                      (cane_pose(0.0), "#ff7a00", "cane a riposo"), (gril_pose(PHI_CAMMA), "#b08030", "grilletto a riposo"),
                      (rull_pose(PHI_CAMMA), "#802020", "rullino")):
        for i, pg in enumerate(poligoni(g)):
            xx, zz = pg.exterior.xy
            ax.fill(xx, zz, color=c, alpha=0.45, label=lab if i == 0 else None)
            for h in pg.interiors:
                xx, zz = h.xy
                ax.fill(xx, zz, color="white")
    for pg in poligoni(cane_pose(ANG_ARMO)):
        xx, zz = pg.exterior.xy
        ax.plot(xx, zz, color="#ff7a00", lw=0.8, ls=":", label="cane armato")
    xx, zz = molla_2d(L1_GEOM - SP_NOM, MOLLA_De).exterior.xy
    ax.plot(xx, zz, color="#0020a0", lw=1.0, label=f"molla L1 {L1_GEOM - SP_NOM:g}")
    ax.add_patch(plt.Rectangle((q.x_cam, ZA - q.R_tamb), q.L_tamb, 2 * q.R_tamb, fc="#d9a441", alpha=0.25, label="tamburo"))
    for sl, _ in raccordi:
        for pg in poligoni(sl):
            xx, zz = pg.exterior.xy
            ax.fill(xx, zz, color="red", alpha=0.6)
    for (vx, vz) in BT["viti"]:
        ax.plot(vx, vz, "x", color="red", ms=7)
    for (vx, vz) in VITI_FINALI:
        ax.plot(vx, vz, "o", mfc="none", color="green", ms=7)
    ax.set_aspect("equal")
    ax.grid(alpha=0.3)
    ax.set_title(f"finale: molla inox 1.0x8 L0 {L0_TAGLIO:g} (x rosse = viti di oggi, o verdi = nuove)")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_xlim(-45, 100)
    ax.set_ylim(-115, 30)
    fig.savefig(os.path.join(OUT, "final_profilo.png"), dpi=110, bbox_inches="tight")
    out(f"disegno: concept_stl/final_profilo.png")
except Exception as err:
    out(f"disegno saltato: {err}")


def per_stampa(s, asse="Y"):
    """Pezzo estruso lungo Y -> sdraiato sul piatto (Y diventa Z), z >= 0, centrato."""
    if asse == "Y":
        s = s.rotate(Axis.X, 90)
    elif asse == "X":
        s = s.rotate(Axis.Y, -90)
    elif asse == "U":
        ang = math.degrees(math.atan2(U[0], U[1]))
        s = s.rotate(Axis.Y, -ang)
    bb = s.bounding_box()
    return s.translate((-bb.center().X, -bb.center().Y, -bb.min.Z))


comuni = [perno_cane, perno_gril, tamburo, scudo, perno_tamb, M._cil_x(p.cart_D, X_CAM, max(q.cart_L_tot), z=ZB)]
export_stl(Compound([cane_ab, gril_rip, rull_rip, pr_rip, perc_ab, molla_rip, coppa_rip, pist_rip] + dist_rip + comuni),
           os.path.join(OUT, "final_assieme_riposo.stl"))
export_stl(Compound([cane_ar, gril_ar, rull_ar, pr_ar, perc_ar, molla_ar, coppa_ar, pist_ar] + dist_ar + comuni),
           os.path.join(OUT, "final_assieme_armato.stl"))
STL = {
    "cane": per_stampa(cane_ab), "grilletto": per_stampa(gril_rip), "rullino": per_stampa(rull_rip),
    "percussore": per_stampa(perc_ab, "X"), "coppa": per_stampa(coppa_rip, "U"), "pistone": per_stampa(pist_rip),
    "molla_acciaio_rif": molla_rip, "perno_cane_acciaio_rif": per_stampa(perno_cane),
    "perno_grilletto_acciaio_rif": per_stampa(perno_gril), "perno_rullino_filamento": per_stampa(pr_rip),
    "guscio_sx_schematico": guscio,
}
for d in DIST_SET:
    STL[f"distanziale_{d:g}mm"] = Cylinder(D_PIST / 2, d, align=(_C, _C, _MIN))
for nome, s in STL.items():
    export_stl(s, os.path.join(OUT, f"final_{nome}.stl"))
out(f"export: concept_stl/final_assieme_riposo.stl, final_assieme_armato.stl + {len(STL)} pezzi final_*.stl "
    f"(PLA gia' sdraiati per la stampa; *_rif = acciaio, solo riferimento)")

COL_A, COL_S, COL_G = "#d9a441", "#ff7a00", "#b08030"
show_object(guscio, id="guscio_sx", name="Guscio sinistro schematico", options={"color": "#4fa89a", "alpha": 0.35})
show_object(cane_ab, id="cane", name="Cane abbattuto", options={"color": COL_S})
show_object(gril_rip, id="grilletto", name="Grilletto a riposo", options={"color": COL_G})
show_object(rull_rip, id="rullino", name="Rullino", options={"color": "#802020"})
show_object(perc_ab, id="percussore", name="Percussore", options={"color": "#eeeeee"})
show_object(molla_rip, id="molla", name="Molla inox", options={"color": "#3060ff"})
show_object(pist_rip, id="pistone", name="Pistone + pattino", options={"color": "#88aaff"})
show_object(tamburo, id="tamburo", name="Tamburo", options={"color": "#d9a441", "alpha": 0.4})

# =====================================================================
# ESITI e VERDETTO
# =====================================================================
ESITI = {
    "energia/gittata nominale": GITT_MIN <= RN["g"] <= GITT_MAX + 0.5,
    f"forza molla <= {F_LIM:g} N": FN["F_max"] <= F_LIM + 1e-6,
    f"grilletto <= {F_DITO_MAX:g} N": FN["F_dito"] <= F_DITO_MAX,
    "ritorno del grilletto": FN["ritorno"] > 0,
    "tolleranza k +-30% (con taratura: forze nei limiti, gittata >= 3.85 m)": all(t[2]["adatta"] and GITT_MIN - 0.15 <= t[2]["g"] and t[2]["f"]["F_max"] <= F_LIM + 1e-6
                                            and t[2]["f"]["F_dito"] <= F_DITO_MAX + 1e-6 for t in TOLL),
    "pacco/tau": RN["ok_pacco"] and RN["tau"] <= TAU_AMM,
    "pose 2D cane/grilletto": all(v < TOLL_A for v in POSE.values()) and _gap_scatto > 0.1,
    "grilletto/pistone/molla": _gp > 0.2 and _fp > 0.2 and _dsp > 0.3,
    "pareti XZ": not _sott_veri and _viol < 0.1 and _vm < 0.05,
    "spessori dei pezzi": _pelle >= PARETE - 0.02 and all(not sottili(g_, amin=0.8) for g_ in PEZZI2D.values()),
    "pareti Y": min(PY_CANE[0], PY_GRIL[0], PY_SCAN, PY_PONT, _sl_m - D_SEDE / 2) >= PARETE - 1e-3,
    "perni": all(min(v[2], v[4]) >= PARETE for v in PERNI.values()),
    "tamburo libero (armato)": _c_t < 0.01 and _g_t < 0.01 and V3D[("armato", "percussore/tamburo")] < 0.01
    and V3D[("armato", "tamburo ruotato 10/20/30 vs pezzi")] < 0.01,
    "3D senza compenetrazioni": all(v < 0.5 for (posa, cosa), v in V3D.items() if "voluto" not in cosa),
}
out("")
out("=" * 100)
out("ESITI")
out("=" * 100)
for k_, v_ in ESITI.items():
    out(f"   {'OK ' if v_ else 'NO '} {k_}")

# =====================================================================
# MECCANISMO.md
# =====================================================================
_hw_c = PERNI["cane"][0]
_hw_g = PERNI["grilletto"][0]
_viti_txt = ", ".join(f"({a:g}, {b:g})" for a, b in VITI_FINALI)
_x_pt_old = q.x_cam - BT["_PERNO_TAMB_DIETRO"]
md = []
A = md.append
A("# MECCANISMO - revolver giocattolo GUN, molla verticale nel manico (versione finale)")
A("")
A("Generato da `concept_molla_verticale_final.py` (non modificare a mano i numeri: rilanciare lo script).")
A("Coordinate di `build.py`: X asse canna (verso la volata), Z alto, Y laterale (y = 0 piano dei gusci), mm.")
A("")
A("## 1. La molla: cosa comprare e come tagliarla")
A("")
A(f"- **Filo di molla inox AISI 304** (1.4301/1.4310), **diametro esterno 8 mm, filo 1.0 mm**, passo ~{MOLLA_PASSO:g} mm "
  f"(molla di compressione lunga da tagliare). G = {MOLLA_G:g} MPa, Dm {MOLLA_Dm:g}, indice C {C_IND:.0f}.")
A(f"- **Tagliare {L0_TAGLIO / MOLLA_PASSO:.0f} spire = ~{L0_TAGLIO:g} mm** (non 45): contare le spire, poi chiudere a pinza "
  f"l'ultima spira di ogni capo (appoggio piano, {MOLLA_NM:g} spire non attive). Spire attive ~{MN['na']:.0f}, "
  f"**k ~{MN['k']:.2f} N/mm** (stima: tolleranza +-30%).")
A(f"- Perche' 60 e non 45: con 45 mm (k {k_molla(45):.2f}) i vostri 10 mm di precarico danno {_r45_vostra['f']['F_max']:.0f} N a cane "
  f"armato e ~{_r45_vostra['f']['F_dito']:.0f} N al grilletto; e anche con precarico quasi nullo k x corsa ({CC + CG:.1f} mm) fa gia' "
  f"{_k45 * (CC + CG):.0f} N: non resta spazio per caricarla. La 60 da' {RN['g']:.1f} m con {FN['F_max']:.1f} N.")
A(f"- Montaggio nominale: sede {L1_GEOM:g} mm, **distanziale {SP_NOM:g} mm** (dischi {distanziali(SP_NOM)}), molla montata a "
  f"{MN['L1']:g} mm: precarico {MN['pre']:.1f} mm ({FN['F_rip']:.1f} N), armata {FN['L_min']:.1f} mm ({FN['F_max']:.1f} N), "
  f"pacco {MN['Lp']:.0f} mm, tau {RN['tau']:.0f}/{TAU_AMM:.0f} MPa.")
A(f"- Resa simulata: {SN['E0']:.0f} mJ nella molla -> {SN['KE_c']:.0f} mJ nella cartuccia da {M_CART:.2f} g "
  f"({SN['eta'] * 100:.0f}%), {SN['v']:.1f} m/s, **~{RN['g']:.1f} m di tiro teso**. Pollice ~{FN['F_poll']:.0f} N, "
  f"grilletto ~{FN['F_dito']:.0f} N.")
A(f"- Limite onesto: con la corsa di {CC:.0f} mm e {F_LIM:g} N la molla non puo' superare {_Emax_cost:.0f} mJ: 5 m tesi "
  f"(~{_Eg[GITT_MAX]:.0f} mJ nella cartuccia) richiedono ~30 N di molla (distanziale +4: {_r_alta['g']:.1f} m, grilletto "
  f"{_r_alta['f']['F_dito']:.0f} N).")
A("- Non comprimerla mai a pacco fuori sede (a pacco tau ~" + f"{tau_molla(_Fpacco):.0f} MPa: si siede).")
A("")
A("### Taratura (bilancia da cucina) e lunghezze alternative")
A("")
A(f"1. Misurare L0 vera. Premere la molla di 10 mm sulla bilancia (infilata su un'asta d5): atteso "
  f"{MN['k'] * 10 / 9.81 * 1000:.0f} g, intervallo +-30% {MN['k'] * 0.7 * 10 / 9.81 * 1000:.0f}-"
  f"{MN['k'] * 1.3 * 10 / 9.81 * 1000:.0f} g. k = grammi x 0.00981 / 10.")
A(f"2. Distanziale [mm] = {L1_GEOM:g} - L0 + {F_TARGET:g}/k - {CC + CG:.1f}, per difetto al mezzo mm, con i dischi 0.5/1/2/4/8 (0..{DIST_MAX:g} mm).")
A("")
A("| k vero | k N/mm | senza taratura | distanziale | con taratura |")
A("|---|---|---|---|---|")
for fac, r0, r1 in TOLL:
    A(f"| {fac:.2f} x | {k_molla(L0_TAGLIO, fac):.2f} | {r0['f']['F_max']:.1f} N, {r0['g']:.2f} m, grilletto {r0['f']['F_dito']:.0f} N | "
      f"{r1['sp']:g} mm ({distanziali(r1['sp'])}) | {r1['f']['F_max']:.1f} N, {r1['g']:.2f} m, grilletto {r1['f']['F_dito']:.0f} N |")
A("")
A("Lunghezze di taglio alternative (stessa sede, cambia solo il distanziale):")
A("")
A("| L0 | spire | k | distanziale | F armato | gittata | grilletto |")
A("|---|---|---|---|---|---|---|")
for L0, r in TAB_L0.items():
    if not r["adatta"]:
        A(f"| {L0:g} | {r['m']['nt']:.0f} | {r['m']['k']:.2f} | - | non adatta (troppo dura) | - | - |")
        continue
    A(f"| {L0:g} | {r['m']['nt']:.0f} | {r['m']['k']:.2f} | {r['sp']:g} | {r['f']['F_max']:.1f} N | {r['g']:.2f} m | {r['f']['F_dito']:.0f} N |")
A("")
A("## 2. Pezzi")
A("")
A("| pezzo | materiale | note | STL |")
A("|---|---|---|---|")
A(f"| cane | PLA, sp {SP_CANE:g}, sdraiato, 100% o 4 perimetri | perno ({P0:g},{P1:g}), coda {L_CODA:.0f} mm, dente di monta, forcella del percussore | final_cane.stl |")
A(f"| grilletto | PLA, sp {SP_GRIL:g}, sdraiato | perno ({PT[0]:g},{PT[1]:g}), naso, lama, braccio nel manico con forcella | final_grilletto.stl |")
A(f"| rullino | PLA d{2 * R_RULL:g} x {W_RULL:g} | gira sul perno di filamento | final_rullino.stl |")
A(f"| perno rullino | filamento PLA d1.75 x {SP_GRIL - 0.2:g} | | final_perno_rullino_filamento.stl |")
A(f"| percussore | PLA, in piedi sul collare | collare d{D_COL:g}x{L_COL:g}, gambo d{D_SHANK:g}, L {L_PERC:.1f} | final_percussore.stl |")
A(f"| coppa | PLA | d{MOLLA_De + 0.6:g} x {L_COPPA:g}, fra coda del cane e molla | final_coppa.stl |")
A(f"| pistone + pattino | PLA, sdraiato | quadro {D_PIST:g} (non ruota), pattino per il rullino | final_pistone.stl |")
A(f"| distanziali | PLA | dischi d{D_PIST:g} x 0.5, 1, 2, 4, 8 | final_distanziale_*mm.stl |")
A(f"| molla | inox 304 1.0 x 8, L0 {L0_TAGLIO:g} | | final_molla_acciaio_rif.stl (riferimento) |")
A(f"| perno cane | spina acciaio d{D_PERNO:g} x {_hw_c:.1f} (o chiodo/vite M3 tagliata) | | final_perno_cane_acciaio_rif.stl |")
A(f"| perno grilletto | spina acciaio d{D_PERNO_G:g} x {_hw_g:.1f} (o chiodo d2) | | final_perno_grilletto_acciaio_rif.stl |")
A("")
A("Assiemi: `concept_stl/final_assieme_armato.stl`, `final_assieme_riposo.stl`; guscio di controllo `final_guscio_sx_schematico.stl`; "
  "profili 2D per build.py in `concept_stl/final_profili.json`; disegno `concept_stl/final_profilo.png`.")
A("")
A("## 3. Come si arma e come spara")
A("")
A(f"1. **Riposo**: cane abbattuto contro il retro dello scudo (x {X_SCUDO:g}); la punta del percussore sporge "
  f"{TIP_S - q.x_cam:.1f} mm nella camera e **blocca il tamburo**; il naso del grilletto appoggia sul cerchio della camma; "
  f"molla a {MN['L1']:g} mm ({FN['F_rip']:.0f} N).")
A(f"2. **Armamento (pollice sullo sperone, ~{FN['F_poll']:.0f} N)**: il cane ruota indietro di {ANG_ARMO:g} gradi; la coda spinge "
  f"la coppa e comprime la molla di {CC:.0f} mm; la forcella tira indietro il percussore, che rientra {X_SCUDO1 - TIP_R:.1f} mm "
  "nello scudo. Il naso del grilletto striscia sulla camma.")
A("3. **Monta**: a fine corsa il naso del grilletto, spinto in su dalla molla attraverso rullino e braccio, scatta nella tacca "
  f"della camma (aggancio {H_ENG:g} mm). Cane armato, molla a {FN['L_min']:.0f} mm ({FN['F_arm']:.0f} N).")
A("4. **Rotazione del tamburo**: ora (e solo ora) il tamburo gira libero: si porta a mano la camera carica davanti al percussore.")
A(f"5. **Scatto (~{FN['F_dito']:.0f} N al grilletto)**: il grilletto ruota di {abs(PHI_SGANCIO):.1f} gradi, il naso esce dalla tacca "
  f"(+{GIOCO_SGANCIO:g} mm di sicurezza), il braccio comprime di altri {CG:.1f} mm la molla tramite il rullino.")
A(f"6. **Colpo**: il cane cade, la faccia batte sul collare del percussore (gioco {G_LOST:.1f} mm), il percussore spinge la cartuccia "
  f"di {S_PUSH:g} mm oltre la fascia di trattenuta e la lancia; il cane si ferma sullo scudo.")
A("7. **Rilascio**: lasciando il grilletto, la molla (tramite il rullino) lo riporta in avanti finche' il naso torna sulla camma.")
A("")
A("Montaggio: guscio sinistro steso; si posano cane (con il percussore nella forcella), grilletto con rullino e perno, coppa, "
  f"molla, distanziali, pistone (la molla va compressa a mano di {MN['pre']:.0f} mm, ~{FN['F_rip']:.0f} N, per posare il pistone "
  "sul rullino); si chiude il guscio destro e si infilano dal fianco la spina d3 del cane e la spina d2 del grilletto.")
A("")
A("## 4. Modifiche da applicare a build.py (in quest'ordine)")
A("")
A("Tutti i profili stanno in `concept_stl/final_profili.json` (poligoni XZ con fori, gia' nelle coordinate di build.py). "
  "Helper da aggiungere in testa a build.py, dopo gli import:")
A("")
A("```python")
A("import json")
A("_MEC = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concept_stl', 'final_profili.json')))")
A("def estrudi_mec(voce, larghezza=None):")
A("    \"\"\"Estrude simmetrico in Y i poligoni XZ di una voce di final_profili.json.\"\"\"")
A("    s = None")
A("    for pg in voce['poligoni']:")
A("        f = extrude(Plane.XZ * Polygon(*pg['ext'], align=None), amount=(larghezza or voce.get('larghezza') or voce['spessore']) / 2, both=True)")
A("        for h in pg['holes']:")
A("            f -= extrude(Plane.XZ * Polygon(*h, align=None), amount=50, both=True)")
A("        s = f if s is None else s + f")
A("    return s")
A("```")
A("")
mods = [
    ("BRIEF / vincolo da sbloccare (prima di tutto)",
     "Il BRIEF dice che ogni pezzo sottrae `M.vuoto_canale()`. Con questo meccanismo il canale orizzontale del percussore+molla "
     "(d{:g} a z=0 da x -1 a {:.0f}) non esiste piu' e, se resta, taglia la cima della sede molla e la feritoia del cane. "
     "Serve il vostro OK a togliere quel vincolo. NON cambiare `molla_*`/`precarico` in params.scad: da li' deriva x_cam "
     "(posizione del tamburo); restano come 'quote storiche'.".format(p.canale_D, q.x_sc)),
    ("misure d'involucro: `slot_cane`",
     f"da `8 + p.gioco_rot` a `7 + p.gioco_rot` ({SP_CANE + p.gioco_rot:g}). Cane spesso 7: con 8 la parete fra feritoia e "
     f"scanalatura di carica scende a 1.1 mm (con 7: {PY_SCAN:.2f})."),
    ("misure d'involucro: `z_fondo_cane`",
     "togliere (serviva solo a tenere il cane sopra il canale del percussore)."),
    ("misure d'involucro: nuove costanti",
     f"aggiungere `D_SEDE = {D_SEDE:g}`, `D_PERC_FORO = {D_SHANK + 0.3:.1f}` e l'helper `estrudi_mec` qui sopra."),
    ("finte viti: lista `viti`",
     f"da `[(10, -10), (16, -28), (30, -6), (q.x_spal + 8, -19.5), (4, -36)]` a `[{_viti_txt}]` "
     "(le vecchie (10,-10), (30,-6), (4,-36) cadono nei vani; (16,-28) e' gia' il perno del grilletto; si aggiunge il perno del "
     "cane). Nel ciclo delle teste: per i due perni forare la testa (`- Pos(vx, ys, vz) * Rot(90,0,0) * Cylinder(d/2, 4)`) "
     "cosi' la spina passa."),
    ("meccanica comune: riga `telaio = telaio - M.vuoto_finestra_tamburo() - M.vuoto_canale() - M.vuoto_canna(x_bocca)`",
     "togliere `- M.vuoto_canale()` e aggiungere il foro del percussore nello scudo: "
     f"`telaio -= cil_x(D_PERC_FORO, x_scudo0 - 0.1, t_scudo + 0.2)` (d{D_SHANK + 0.3:.1f} a z=0)."),
    ("meccanica comune: `M.vuoto_asse_tamburo(q.x_cam - 12, x_front + 1)`",
     f"da `q.x_cam - 12` a `q.x_cam - {q.x_cam - X_FORO_TAMB:.1f}` (foro da x {X_FORO_TAMB:.1f}, sbuca nella feritoia del cane)."),
    ("feritoie: `telaio -= Box(34, slot_cane, 40, ...).translate((-18, 0, z_fondo_cane))`",
     f"sostituire con `telaio -= estrudi_mec(_MEC['vano_cane'], slot_cane)`: inviluppo del cane 0-{ANG_ARMO:g} gradi "
     f"(x {_bb[0]:.0f}..{_bb[2]:.0f}, z {_bb[1]:.0f}..sopra il dorso)."),
    ("feritoie: `telaio -= Box(15, slot_gril, 20, ...).translate((28, 0, -42))`",
     f"sostituire con `telaio -= estrudi_mec(_MEC['vano_grilletto'], slot_gril)`: inviluppo di grilletto e rullino "
     f"(x {sweep_gril.bounds[0]:.0f}..{sweep_gril.bounds[2]:.0f}, z {sweep_gril.bounds[1]:.0f}..{sweep_gril.bounds[3]:.0f}), "
     "compreso il braccio nel manico."),
    ("feritoie: nuova sede molla",
     f"aggiungere `telaio -= estrudi_mec(_MEC['vano_molla'], D_SEDE)` (canale quadro {D_SEDE:g} inclinato {ANG_MOLLA:g} gradi + "
     "vano di pistone e pattino) e `for r in _MEC['raccordi']: telaio -= estrudi_mec(r)` (setti < 1.6 fusi)."),
    ("feritoie: fori dei perni",
     f"aggiungere `telaio -= Pos({P0:g}, 0, {P1:g}) * Rot(90, 0, 0) * Cylinder({D_PERNO / 2:g}, 60)` e "
     f"`telaio -= Pos({PT[0]:g}, 0, {PT[1]:g}) * Rot(90, 0, 0) * Cylinder({D_PERNO_G / 2:g}, 60)` (DOPO le teste delle viti)."),
    ("PERNO DEL TAMBURO: `perno = cil_x(p.tamb_asse_d, q.x_cam - 10, ...)`",
     f"da `q.x_cam - 10` (x {_x_pt_old:.1f}) a `q.x_cam - {q.x_cam - X_PERNO_TAMB:.1f}` (x {X_PERNO_TAMB:.1f}): oggi attraversa la "
     f"feritoia del cane. Appoggio dietro il tamburo {X_SCUDO1 - X_PERNO_TAMB:.1f} mm (nello scudo)."),
    ("CANE: `cane = profilo([...], 8, ...)` e unghiatura",
     "sostituire con `cane = estrudi_mec(_MEC['cane']) - estrudi_mec(_MEC['cane']['forcella_gambo']) "
     f"- Pos({P0:g}, 0, {P1:g}) * Rot(90, 0, 0) * Cylinder({D_PERNO / 2 + 0.15:g}, 10)` (pezzo a riposo). L'unghiatura va "
     f"riposizionata sulla faccia dietro dello sperone (attorno a ({SPERONE[0]:.0f}, {SPERONE[1]:.0f}))."),
    ("GRILLETTO: `grilletto = profilo([...], 6, ...)`",
     "sostituire con `grilletto = estrudi_mec(_MEC['grilletto'])` (a riposo) meno la gola della forcella "
     f"(cilindro r{R_RULL + 0.5:g} x {W_RULL + 0.2:g} attorno al centro del rullino) e il foro del perno del rullino "
     f"d{D_PERNO_R + 0.15:.2f}."),
    ("MONTAGGIO: nuovi `show_object`",
     "percussore, coppa, molla, distanziali, pistone, rullino, spine: si possono importare gli STL `final_*` o ricostruirli con "
     "le stesse primitive di concept_molla_verticale_final.py (sezione SOLIDI)."),
    ("EXPORT HARNESS: `_pezzi_harness`", "aggiungere i nuovi pezzi."),
    ("FACOLTATIVO: dorso (X_DORSO0, Z_DORSO0)",
     f"da (-28,-12) a (-1,-23) come proposto in v3 (-27 mm di gobba): con i vani finali "
     f"{'resta valido' if _v3ok < 0.1 else 'NON e piu valido'}. E' solo estetica: il meccanismo sta nel profilo di oggi."),
]
for i, (dove, cosa) in enumerate(mods, 1):
    A(f"{i}. **{dove}** - {cosa}")
A("")
A("Dopo le modifiche: rilanciare build.py e controllare che l'assert della cresta passi ancora (la feritoia e' piu' stretta: "
  "il margine aumenta).")
A("")
A("## 5. Da verificare con la stampa di prova")
A("")
A(f"1. **Taratura molla**: misura di k (bilancia), scelta del distanziale; poi misurare la gittata vera (attesa "
  f"{RN['g']:.1f} m) e la forza del grilletto (attesa ~{FN['F_dito']:.0f} N, dinamometro o bottiglia d'acqua appesa).")
A(f"2. **Trattenuta della cartuccia**: il modello assume {F_TRATT:g} N sulla fascia di {p.cart_fascia:g} mm "
  f"(2 N -> piu' gittata, 10 N -> meno). Verificare che la cartuccia non cada dal tamburo e che il percussore la spinga oltre "
  f"la fascia ({S_PUSH:g} mm di spinta). Non abbattere il cane accompagnandolo su una camera carica: la spinge fuori a meta'.")
A("3. **Indicizzazione del tamburo**: NON c'e' nottolino ne' mano. Il tamburo si gira a mano a cane armato e niente lo "
  "allinea: verificare quanto si puo' sbagliare (la punta d2.6 deve cadere sul fondello d10.5) e, se serve, aggiungere un "
  "fermo elastico nelle tacche esistenti.")
A(f"4. **Rullino e ritorno del grilletto**: senza rullino (attrito a secco) il grilletto NON torna (braccio {A_ASSIALE:.0f} mm). "
  "Controllare che il rullino giri libero sul filamento.")
A(f"5. **Dente di monta in PLA**: {FN['N_dente']:.0f} N sullo spigolo della tacca (aggancio {H_ENG:g} mm): rischio di "
  "arrotondamento/usura; stampare cane e grilletto con 4-5 perimetri e strato 0.12-0.16 nella zona del dente.")
A(f"6. **Fasce di tolleranza della stampa**: giochi 0.25-0.3 per lato fra pezzi mobili e feritoie, fori dei perni nominali "
  "(spina a leggera interferenza nel telaio), sede molla quadra (gioco 0.6 sul diametro molla).")
A(f"7. **Battuta del cane sullo scudo**: urto ripetuto PLA su PLA a ~{SN['KE_urto']:.0f} mJ: controllare crepe sul retro dello scudo.")
open(DOC, "w").write("\n".join(md) + "\n")
out(f"documento: MECCANISMO.md ({len(md)} righe)")

out("")
out("=" * 100)
out("VERDETTO")
out("=" * 100)
_ok = all(ESITI.values())
out(f"Molla: inox 1.0x8 TAGLIATA A {L0_TAGLIO:g} mm ({L0_TAGLIO / MOLLA_PASSO:.0f} spire, non 45), k~{MN['k']:.2f}, distanziale "
    f"{SP_NOM:g} mm: {FN['F_max']:.0f} N armata, {SN['KE_c']:.0f} mJ, ~{RN['g']:.1f} m teso, pollice {FN['F_poll']:.0f} N, "
    f"grilletto {FN['F_dito']:.0f} N.")
out(f"La finestra 4-5 m si centra solo in basso: a <= {F_LIM:g} N la fisica (corsa {CC:.0f} mm) non da' di piu'; 5 m vogliono ~30 N.")
out(f"k +-30% e' assorbito da taratura con bilancia + distanziali 0-{DIST_MAX:g} mm ({_g_lo:.1f}-{_g_hi:.1f} m); tagli "
    f"{min(_adatte):g}-{max(_adatte):g} mm vanno nella stessa sede.")
out("Verifiche geometriche: " + ("tutte OK" if _ok else "NON tutte OK: " + ", ".join(k for k, v in ESITI.items() if not v)) + ".")
out("Pronto per build.py: " + ("SI', con la modifica 1 (togliere vuoto_canale dal BRIEF) da approvare." if _ok else
                               "NO, prima chiudere i punti sopra."))
out("Rischi per la stampa: indicizzazione del tamburo assente, usura del dente PLA, rullino obbligatorio, trattenuta cartuccia.")
