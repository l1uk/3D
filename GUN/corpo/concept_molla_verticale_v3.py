# CONCEPT v3 - molla singola nel manico: QUALE molla comprare + INNESTO nel telaio vero.
#
# Evoluzione di concept_molla_verticale_v2.py (v1 e v2 restano come sono). Non tocca
# build.py / meccanica.py / parametri.py: build.py viene LETTO (AST, solo le righe di
# calcolo puro: profilo del telaio, impugnatura, sezioni della guaina, costanti) e mai
# eseguito come script. Sistema come build.py: X asse canna, Z alto, Y laterale (piano
# dei gusci y = 0), asse canna z = 0, mm.
#
# I RISULTATI (numeri dell'ultima esecuzione) sono riportati qui sotto e ristampati
# dallo script in due sezioni, OBIETTIVO 1 e OBIETTIVO 2.
# ---------------------------------------------------------------------------------
# OBIETTIVO 1 - MOLLA DA COMPRARE
#  Spazio: l'asse molla (inclinato 28 gradi, impugnatura 20) parte da (13.4,-9.5) sotto la coda del
#   cane; nel manico un foro fino a d13 (De 12) scenderebbe ~97 mm con parete 1.6 (cappetta 2.2
#   esclusa). In Y: De <= 17.8 (W 22); in XZ il limite vero e' il mozzo del grilletto accanto alla
#   cima della molla (De <= ~14) e il braccio che deve passarle davanti. La lunghezza NON la limita
#   il manico ma il grilletto: il naso piu' in basso striscia di piu' sul pistone (4 mm a 33 mm) e
#   l'attrito si mangia il ritorno -> naso con RULLINO, montaggio scelto L1_GEOM = 34 mm.
#  Perdite (simulazione 1D di v2, cane 4.1 g, massa efficace 4.4 g, e=0.4, fascia 5 N = 7.5 mJ):
#   molla -> cartuccia passa il 26-29%. Col modello d'aria (Cd 0.8) 4 m teso = 41 mJ, 6 m = 97 mJ:
#   l'intervallo 36-60 mJ vale ~4-4.7 m, non 6.
#  Candidati (L1 34, spire stimate col passo 0.45 Dm):  E molla -> cartuccia, tiro teso, dito
#   penna 0.6x5x29     59 mJ -> 14 mJ, 2.4 m, 10 N   POCA
#   A 0.7x6x40        99 mJ -> 26 mJ, 3.2 m, 15 N   POCA
#   B 0.8x7x45 arm.  154 mJ -> 43 mJ, 4.1 m, 21 N   OK  <- RACCOMANDATA
#   C 0.8x7x50 arm.  191 mJ -> 54 mJ, 4.6 m, 24 N   OK (tau 944/1012, al limite)
#   D 0.8x6x40 arm.  169 mJ -> 49 mJ, 4.4 m, 25 N   OK (k 1.7, grilletto duro)
#   E 0.8x7x50 inox  167 mJ -> 46 mJ, 4.2 m, 21 N   OK
#  RACCOMANDAZIONE: molla di compressione in acciaio armonico (EN 10270-1 DH), d 0.8, De 7, L0 45,
#   ~18 spire (16 attive), k ~1.07 N/mm, estremi chiusi. Montata a 34 (precarico 11 mm, 11.8 N),
#   24.6 armata (pacco 14.4), F max 22 N, tau 806/1012 MPa. Prova: da 45 a 35 mm ~1.1 kg sulla
#   bilancia. Grilletto ~21 N con rullino (26 N senza), pollice ~11 N. Se la gittata non basta:
#   C (0.8x7x50).
#  Spinta diretta: non serve; con la stessa molla il canale di oggi andrebbe allungato di ~7 mm.
#
# OBIETTIVO 2 - INNESTO NEL TELAIO DI build.py
#  Posizioni: perno cane M3 (30.5,-20) [v2 a x 35 tagliava la scanalatura di carica], perno grilletto
#   d2 (16,-28) = la finta vite di oggi, naso (30.5,-28), dito (36.8,-44) nel ponticello. Scudo
#   vero di build.py x 40..44 (v2 usava 41). Cane spesso 7 (con 8 restavano 1.1 mm verso la
#   scanalatura; con 7 restano 1.61). Sperone alzato a z 21.5 (v2 era 1 mm sopra la cinghia) e
#   alleggerito con un foro d4.4.
#  Verifiche: sede molla d8 dentro il manico (parete XZ >= 9 mm, Y 7 per lato, le guancette non sono
#   toccate); braccio del grilletto davanti alla molla con gancio sotto il pattino, a 1 mm dalle
#   spire, tutto dentro il telaio; lama nel vano del ponticello (luce 0.7); perni lunghi 23.8 / 22.3
#   sui fianchi bombati, a filo, infilabili dal fianco a gusci chiusi, fuori da guancette e cappetta.
#  INTERFERENZE CON build.py: il perno del tamburo (da x 34.3) passa nella feritoia del cane -> va
#   accorciato a x >= 39.6 (appoggio dietro 4.4 mm invece di 9.7); tre spine dei gusci (10,-10),
#   (30,-6), (4,-36) cadono nei vani -> nuove posizioni nel report.
#  Dorso: X_DORSO0/Z_DORSO0 da (-28,-12) a (-1,-23): dorso dietro il cane da x -28 a x -1 (-27 mm),
#   variante conservativa (3.5,-12) -25 mm. Lunghezza fuori tutto 143 -> 143: la fa il tallone.
#  Disegno: concept_stl/v3_profilo.png; STL v3_* (assieme a riposo/armato, guscio sinistro).
#  Lista delle modifiche a build.py: sezione 2f della stampa.
# ---------------------------------------------------------------------------------
import ast
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# show_object e' iniettato solo dentro agentcad; qui giriamo con Python puro
if "show_object" not in dir():
    def show_object(*a, **k):  # noqa: E306  (no-op fuori da agentcad)
        pass

from build123d import Align, Box, Compound, Cylinder, Plane, Polygon, Pos, Rot, extrude, export_stl  # noqa: E402
from shapely.geometry import LineString, MultiPoint, Point, Polygon as SPoly, box as sbox  # noqa: E402
from shapely.ops import unary_union  # noqa: E402
from shapely import affinity  # noqa: E402

import meccanica as M  # noqa: E402

p, q = M.p, M.q
_C, _MIN = Align.CENTER, Align.MIN
QUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(QUI, "concept_stl")
BUILD = os.path.join(QUI, "build.py")


# =====================================================================
# build.py LETTO (non eseguito): tutto quello che sta prima della guaina in loft
# (solo liste di punti e funzioni) + alcune costanti scalari successive.
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
ANG_MOLLA = 28.0                                # asse molla dalla verticale (impugnatura: 20). Piu' inclinato
                                                # porta il fondo della sede verso la pancia del dorso e il gancio
                                                # del grilletto lontano dall'incavo delle dita
U = (math.sin(math.radians(ANG_MOLLA)), math.cos(math.radians(ANG_MOLLA)))   # asse molla, verso l'alto
NF = (U[1], -U[0])                              # normale "in avanti" all'asse molla (verso +X)
imp_xz = BT["imp_xz"]
grip = SPoly(BT["profilo_imp"]()).buffer(0)
TEL_OLD = SPoly(BT["telaio_pts"]).buffer(0)


def profilo_telaio(X0, Z0):
    """telaio_pts di build.py con il dorso (X_DORSO0, Z_DORSO0) spostato.
    Stessa costruzione: quarto d'ellisse fino alla cinghia + Hermite dal dorso impugnatura."""
    b = BT
    nd = b["N_DORSO"]
    dorso_t = [(X0 + (b["X_DORSO1"] - X0) * (1 - math.cos(math.pi / 2 * i / nd)),
                Z0 + (b["Z_DORSO1"] - Z0) * math.sin(math.pi / 2 * i / nd)) for i in range(nd + 1)]
    p0 = b["_p0"]
    p0b = b["_p0b"]
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


_rif = profilo_telaio(BT["X_DORSO0"], BT["Z_DORSO0"])
assert max(math.dist(a, b) for a, b in zip(_rif, BT["telaio_pts"])) < 1e-9, "profilo_telaio non replica build.py"

# ponticello (2D): anello tagliato sopra Z_PONT_TOP + gattoni; il vano interno e' dove va il dito
_cxp, _czp = BT["cx_p"], BT["cz_p"]
anello = Point(_cxp, _czp).buffer(BT["R_PONT"], 64).difference(Point(_cxp, _czp).buffer(BT["r_PONT"], 64))
anello = anello.difference(sbox(-200, BT["Z_PONT_TOP"], 200, 200))
vano_pont = Point(_cxp, _czp).buffer(BT["r_PONT"], 64)
gattoni = unary_union([SPoly(g).buffer(0) for g in BT["_GATTONI"]])
ponticello = anello.union(gattoni)

# =====================================================================
# PARAMETRI DEL CONCEPT
# =====================================================================
X_SCUDO = BT["x_scudo0"]          # 40.0: retro dello scudo DI BUILD.PY (v2 usava q.x_sc = 41)
X_SCUDO1 = BT["x_scudo1"]         # 44.0: faccia anteriore dello scudo
X_CAM = q.x_cam
ZB = 0.0

# --- cane ---
X_PERNO, Z_PERNO = 30.5, -20.0    # v2: 35. Arretrato: il perno a x=35 attraversava la scanalatura di carica
D_PERNO = 3.0                     # vite/spina M3 acciaio
R_MOZZO = 5.0
SP_CANE = 7.0                     # v2: 8. Con 8 tra feritoia e scanalatura di carica restavano 1.25 mm
ANG_ARMO = 26.0
CORSA_CODA = 9.0
R_CONT = 3.2
Z_SPERONE = 21.5                  # cima dello sperone a riposo (v2: 13.5, solo 1 mm sopra la cinghia)
ALLEGG = (1.5, 15.0, 2.2)         # foro di alleggerimento nello sperone (dx da perno, z, raggio)

# --- percussore trascinato (come v2) ---
D_SHANK = 2.6
D_COL, L_COL = 5.0, 1.5
T_LIP = 1.2
S_PUSH = p.cart_fascia + 0.5 + 0.5
RITIRO_TIP = 0.3

# --- dente di monta / grilletto ---
R_NASO = 8.0
H_ENG = 1.2
GIOCO_SGANCIO = 0.3
L_NASO = 14.5                     # v2: 9. Perno grilletto a (16,-28) = posto della finta vite di build.py;
                                  # meno rotazione (strisciamento sul pistone) e piu' braccio per il dito
W_NASO = 2.5
SP_GRIL = 6.0
D_PERNO_G = 2.0                   # spina acciaio d2 (o chiodo d2)
R_MOZZO_G = 3.5
R_BRACCIO = 2.4                   # semi-spessore (XZ) del braccio che scende nel manico
MU = 0.3                          # PLA/PLA a secco
MU_NASO = 0.10                    # naso del grilletto con RULLINO (PLA d6.4 su perno filamento 1.75)
DITO = (36.8, -44.0)              # dove preme il dito (faccia anteriore della lama, a grilletto in avanti)

# --- sede molla nel manico ---
L1_GEOM = 34.0                    # lunghezza di montaggio a riposo (fra coppa e pistone) del telaio
L_COPPA = 3.0                     # coppa superiore (sotto la coda del cane)
L_PIST = 6.0                      # pistone guidato nel foro
T_PAD = 2.0                       # pattino sotto il pistone, su cui rotola il naso del grilletto
PRE_MIN = 2.0                     # precarico minimo che si accetta [mm]
CAP_SIC = BT["CAP_T"]             # in fondo al manico la cappetta d'ottone si sovrappone per 2.2 mm

# --- munizione e balistica (come v2) ---
RHO_PLA = 1.24e-3 * 0.85
RHO_CART = 1.24e-3 * 0.95
F_TRATT = 5.0
E_REST = 0.4
ETA_MECC = 0.85
K_CONT = 1.0e6
CD, RHO_ARIA, H_TIRO = 0.8, 1.2, 1.2
E_CART_MIN, E_CART_MAX = 36.0, 60.0   # obiettivo nella cartuccia DOPO le perdite [mJ]
F_DITO_MAX = 25.0                 # oltre, il grilletto e' troppo duro per un giocattolo [N]

PARETE = p.parete_min
RHO_ACC = 7.85e-3

# =====================================================================
# MOLLE: misure REALI da listino (d x De x L0). Le spire NON sono scritte nei listini
# economici: si stimano col passo tipico (~0.45 Dm) e si VERIFICANO con la bilancia
# (vedi "prova" nel report). Acciaio armonico = EN 10270-1 (DH), "Federstahl";
# inox = 1.4310 / AISI 302-304 (G piu' basso, carico ammesso piu' basso).
# =====================================================================
MAT = {"armonico": dict(G=80000.0, Rm={0.6: 2350, 0.7: 2300, 0.8: 2250, 0.9: 2200, 1.0: 2150}),
       "inox":     dict(G=70000.0, Rm={0.6: 2000, 0.7: 1950, 0.8: 1900, 0.9: 1850, 1.0: 1800})}
TAU_FRAZ = 0.45                   # tau ammessa = 0.45 Rm (statico con margine, molla compressa spesso)


def _nt_stima(d, De, L0):
    Dm = De - d
    passo = 0.45 * Dm
    na = round((L0 - 1.5 * d) / passo)
    return na + 2, 2                # 2 spire morte (estremi chiusi)


def _molla(nome, d, De, L0, mat="armonico", nt=None, nm=None, nota=""):
    if nt is None:
        nt, nm = _nt_stima(d, De, L0)
    return dict(nome=nome, d=d, De=De, L0=L0, nt=nt, nm=nm, mat=mat, nota=nota)


MOLLE = [
    _molla("penna", p.molla_d, p.molla_De, p.molla_L0, nt=p.molla_n_tot, nm=p.molla_n_morte,
           nota="molla da penna di oggi (riferimento)"),
    _molla("A 0.7x6x40", 0.7, 6.0, 40, nota="kit assortito / sfusa da listino (eBay 'Druckfeder 0,7x6x40')"),
    _molla("B 0.8x7x45", 0.8, 7.0, 45, nota="sfusa da listino o catalogo molle (Gutekunst/Sodemann, serie D)"),
    _molla("C 0.8x7x50", 0.8, 7.0, 50, nota="sfusa da listino (eBay 'Druckfeder 0,8x7x50')"),
    _molla("D 0.8x6x40", 0.8, 6.0, 40, nota="sfusa da listino: corta e dura"),
    _molla("E 0.8x7x50 inox", 0.8, 7.0, 50, mat="inox", nota="stessa misura in inox 304 (molle 'Edelstahl')"),
]


def molla(m):
    m = dict(m)
    G = MAT[m["mat"]]["G"]
    D = m["De"] - m["d"]
    na = m["nt"] - m["nm"]
    m["Dm"], m["na"] = D, na
    m["k"] = M.molla_k(m["d"], m["De"], na, G)
    m["Lp"] = m["nt"] * m["d"]
    m["L1"] = min(L1_GEOM, m["L0"] - PRE_MIN)
    m["spessore"] = L1_GEOM - m["L1"]           # distanziale sotto la molla se L0 e' corta
    m["pre"] = m["L0"] - m["L1"]
    C = D / m["d"]
    m["C"] = C
    m["Kw"] = (4 * C - 1) / (4 * C - 4) + 0.615 / C
    m["tau"] = lambda F, D=D, d=m["d"], Kw=m["Kw"]: Kw * 8 * F * D / (math.pi * d ** 3)
    rm = MAT[m["mat"]]["Rm"]
    m["tau_amm"] = TAU_FRAZ * rm[min(rm, key=lambda dd: abs(dd - m["d"]))]
    m["massa"] = m["nt"] * math.pi * D * math.pi * m["d"] ** 2 / 4 * RHO_ACC
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


def J_geom(g, c):
    gs = [g] if g.geom_type == "Polygon" else list(g.geoms)
    tot = 0.0
    for pg in gs:
        tot += J_poligono(list(pg.exterior.coords)[:-1], c)
        for h in pg.interiors:
            tot -= J_poligono(list(h.coords)[:-1], c)
    return tot


def solido(g, sp, y0=0.0):
    gs = [g] if g.geom_type == "Polygon" else list(g.geoms)
    out_ = None
    for pg in gs:
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


# =====================================================================
# CANE
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


# --- percussore e forcella (come v2, scudo di build.py) ---
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


# --- grilletto: naso sotto il perno del cane ---
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

# --- asse molla, coppa, pistone, punto di contatto del naso ---
cima0, t_cima0 = su_asse((coda0[0] - U[0] * R_CONT, coda0[1] - U[1] * R_CONT))   # cima della coppa sup.
T_PIST0 = L_COPPA + L1_GEOM                     # cima del pistone (lungo -U da cima0), a riposo
T_PAD1 = T_PIST0 + L_PIST + T_PAD               # faccia inferiore del pattino
T_BC = T_PAD1 + R_CONT                          # centro del naso (rullino) a riposo
BC_rip = lungo_asse(cima0, T_BC)
BC0 = rot(BC_rip, -PHI_CAMMA, PT)


def comp_gril(phi):
    c = rot(BC0, phi, PT)
    return dot((c[0] - BC_rip[0], c[1] - BC_rip[1]), U)


def dcomp_gril(phi, h=0.05):
    return (comp_gril(phi + h) - comp_gril(phi - h)) / math.radians(2 * h)


def lat_naso(phi):
    """Posizione laterale (lungo NF) del naso rispetto all'asse molla."""
    c = rot(BC0, phi, PT)
    return dot((c[0] - cima0[0], c[1] - cima0[1]), NF)


PHIS = [PHI_FINE + (0.0 - PHI_FINE) * i / 20 for i in range(21)]
LAT = [lat_naso(f) for f in PHIS]
LAT_MIN, LAT_MAX = min(LAT), max(LAT)
A_ASSIALE = T_BC - dot((PT[0] - cima0[0], PT[1] - cima0[1]), (-U[0], -U[1]))   # distanza assiale perno-naso


# =====================================================================
# PROFILI 2D
# =====================================================================
zb = ZB
P0, P1 = P
braccio = SPoly([
    (X_STOP, zb - 5.5), (X_STOP, zb + 5.0), (X_STOP - 1.5, zb + 9.0),
    (P0 + 6.5, 14.5), (P0 + 4.5, 19.0), (P0 + 1.0, Z_SPERONE),                  # collo e cima dello sperone
    (P0 - 3.0, Z_SPERONE - 0.5), (P0 - 6.0, Z_SPERONE - 2.5), (P0 - 7.5, Z_SPERONE - 5.0),   # uncino
    (P0 - 5.0, Z_SPERONE - 5.5), (P0 - 2.5, Z_SPERONE - 8.0), (P0 - 1.5, zb + 9.0),
    (X_FACE - 3.0, zb + 6.5),
    (P0 - R_MOZZO * 0.9, P1 + 2), (P0 + R_MOZZO * 0.9, P1 - 2),
])
SPERONE = (P0 - 5.0, Z_SPERONE - 4.5)           # dove spinge il pollice
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
cane2d_netto = cane2d_pieno.difference(fer_col)

# --- grilletto (definito a phi = 0, naso nella tacca) ---
naso = sbox(N0[0] - W_NASO - 0.05, N0[1] - 2.6, N0[0] - 0.1, N0[1])
braccio_naso = sbox(PT[0], N0[1] - 3.0, N0[0] - W_NASO + 0.5, N0[1] - 1.6)
lama = unary_union([
    LineString([PT, (29.0, -32.5)]).buffer(2.2, 16),
    SPoly([(27.0, -31.5), (32.0, -31.5), (36.0, -37.0), (37.2, -44.0), (36.3, -50.0), (34.2, -54.0),
           (32.4, -53.2), (33.2, -47.5), (32.3, -41.0), (29.0, -35.5)]),
])
# braccio nel manico: scende DAVANTI alla molla e si aggancia sotto il pattino (gancio), cosi'
# non attraversa le spire. Costruito a riposo e riportato a phi = 0.
D_SEDE_REF = 8.0                                 # sede per molle fino a De 7 (si verifica sotto)
OFF_K = D_SEDE_REF / 2 + R_BRACCIO + 0.8 + max(0.0, -(LAT_MIN - 0.0))
K_rip = (BC_rip[0] + NF[0] * OFF_K, BC_rip[1] + NF[1] * OFF_K)
K_alto = lungo_asse((cima0[0] + NF[0] * OFF_K, cima0[1] + NF[1] * OFF_K), T_PIST0 - 4.0)
braccio_rip = LineString([PT, K_alto, K_rip, BC_rip]).buffer(R_BRACCIO, 16, join_style=1)
braccio_g = rotg(braccio_rip, -PHI_CAMMA, PT).union(Point(BC0).buffer(R_CONT, 24))
gril2d = unary_union([Point(PT).buffer(R_MOZZO_G, 24), naso, braccio_naso, lama, braccio_g]).simplify(0.03)
gril2d = gril2d.difference(Point(PT).buffer(D_PERNO_G / 2 + 0.15, 16))


def cane_pose(th, netto=True):
    return rotg(cane2d_netto if netto else cane2d_pieno, th, P)


def gril_pose(phi):
    return rotg(gril2d, phi, PT)


# --- pistone + pattino (si muove lungo l'asse con comp_gril) ---
D_PIST = D_SEDE_REF - 0.4


def pistone_2d(dt=0.0):
    o = lungo_asse(cima0, dt)
    cil = banda_asse(o, T_PIST0, T_PIST0 + L_PIST, D_PIST / 2)
    a, b = LAT_MIN - 1.6, LAT_MAX + 1.6
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
# MASSA DEL CANE, ENERGIA (simulazione 1D di v2)
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


def simula_cane(m, m_proj, F_tr, dt=2e-7):
    """Caduta del cane, urto col percussore, spinta della cartuccia (1D, SI). Come v2."""
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


def gittata(v, ang_deg, m_g, h=H_TIRO):
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


def miglior_gittata(v, m_g):
    return max((gittata(v, a, m_g), a) for a in range(0, 50, 5))


def v_per_gittata(g_m, m_g):
    lo, hi = 1.0, 40.0
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if gittata(mid, 0, m_g) < g_m else (lo, mid)
    return hi


# --- leve e forze (dipendono dalla molla) ---
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
    attr_naso = mu_naso * F_sg * A_ASSIALE            # il rullino striscia/rotola sul pattino
    F_dito = (F_sg * b_t(PHI_SGANCIO) + MU * N_dente * L_NASO + attr_naso) / r_dito
    ritorno = F(0.0, PHI_CAMMA) * b_t(PHI_CAMMA) - mu_naso * F(0.0, PHI_CAMMA) * A_ASSIALE
    F_poll = max(F(th, 0.0) * b_h(th) for th in (0.0, ANG_ARMO / 2, ANG_ARMO)) / math.dist(P, SPERONE)
    F_max = F(ANG_ARMO, PHI_FINE)
    L_min = m["L1"] - comp_cane(ANG_ARMO) - comp_gril(PHI_FINE)
    return dict(F_rip=F(0.0, PHI_CAMMA), F_arm=F_arm, F_max=F_max, L_min=L_min, F_dito=F_dito,
                F_poll=F_poll, ritorno=ritorno, N_dente=N_dente)


# =====================================================================
# SPAZIO NEL MANICO (quote vere dell'impugnatura di build.py)
# =====================================================================
_s_cap = BT["S_CAP"]
_dentro_cap = SPoly(BT["profilo_imp"](CAP_SIC, s0=_s_cap - 0.5)).buffer(0)
_zona_cap = SPoly([imp_xz(_s_cap, -200), imp_xz(_s_cap, 200), imp_xz(300, 200), imp_xz(300, -200)])
anello_cap = grip.intersection(_zona_cap).difference(_dentro_cap)        # dove c'e' la cappetta
_sopra_imp = SPoly([imp_xz(2, -200), imp_xz(2, 200), imp_xz(-200, 200), imp_xz(-200, -200)])
materiale_imp = grip.union(_sopra_imp.intersection(TEL_OLD)).difference(anello_cap)
lecito_imp = materiale_imp.buffer(-PARETE)


def t_max_sede(D):
    """Fin dove (t lungo -U da cima0) puo' scendere un foro di diametro D con parete min."""
    t = 10.0
    while t < 150 and banda_asse(cima0, -1.0, t + 0.5, D / 2).difference(lecito_imp).area < 0.02:
        t += 0.5
    return t


def s_imp(pt):
    return dot((pt[0] - BT["X_IMP0"], pt[1] - BT["Z_IMP0"]), BT["_dir"])


# =====================================================================
# SEZIONE TRASVERSALE DEL TELAIO (guaina di build.py) -> larghezza locale
# =====================================================================
_cache_sez = {}


def semi_larghezza(x, z, X0=None):
    """Semi-larghezza del telaio (Y) nel punto (x, z) secondo la guaina di build.py."""
    if z <= BT["Z_INNESTO"]:
        return W2
    chiave = (round(x), X0)
    if chiave not in _cache_sez:
        if X0 is not None:
            vecchi = BT["X_STRETTO"], BT["_sagoma"]
            BT["X_STRETTO"], BT["_sagoma"] = X0, SPoly(profilo_telaio(X0, Z0_NEW)).buffer(0)
        w = BT["_sezione"](float(round(x)))
        if X0 is not None:
            BT["X_STRETTO"], BT["_sagoma"] = vecchi
        pts = []
        for e in w.edges():
            for i in range(41):
                v = e @ (i / 40)
                pts.append((v.Y, v.Z))
        _cache_sez[chiave] = MultiPoint(pts).convex_hull
    g = _cache_sez[chiave].intersection(LineString([(-60, z), (60, z)]))
    return 0.0 if g.is_empty else min(-g.bounds[0], g.bounds[2])


# =====================================================================
#                              OBIETTIVO 1
# =====================================================================
out("=" * 100)
out("OBIETTIVO 1 - QUALE MOLLA COMPRARE")
out("=" * 100)
out(f"Geometria: cane imperniato in ({P0:g}, {P1:g}), coda L={L_CODA:.1f} -> la coda comprime {CORSA_CODA:g} mm in "
    f"{ANG_ARMO:g} gradi; il grilletto (perno {PT[0]:.0f},{PT[1]:.0f}) aggiunge {comp_gril(PHI_FINE):+.2f} mm a fondo corsa.")
out(f"Asse molla inclinato {ANG_MOLLA:g} gradi (impugnatura {BT['ANG_IMP']:g}), la cima passa a {dot((cima0[0]-BT['X_IMP0'], cima0[1]-BT['Z_IMP0']), BT['_nrm']):.1f} mm "
    f"davanti all'asse del manico; cima della coppa a ({cima0[0]:.1f}, {cima0[1]:.1f}), s={s_imp(cima0):.0f} sull'asse manico.")

# --- 1a. spazio ---
out("")
out("1a. SPAZIO REALE NEL MANICO (impugnatura di build.py, parete min 1.6, cappetta 2.2 in fondo)")
_ingombro = [("coppa sup.", L_COPPA), ("pistone", L_PIST), ("pattino", T_PAD), ("naso/rullino sotto", 2 * R_CONT)]
_extra = sum(v for _, v in _ingombro)
tab_spazio = {}
for De in (5, 6, 7, 8, 10, 12):
    tm = t_max_sede(De + 1.0)
    tab_spazio[De] = tm
    out(f"   De {De:>2} (foro d{De + 1}): il foro puo' scendere fino a t={tm:5.1f} mm (s={s_imp(lungo_asse(cima0, tm)):.0f} "
        f"sul manico lungo {BT['L_IMP']:g}+{BT['H_TALL']:g}) -> molla montata fino a L1 ~{tm - _extra:.0f} mm")
De_Y = W - 2 * PARETE - 1.0
d_hub = abs(dot((PT[0] - cima0[0], PT[1] - cima0[1]), NF)) - R_MOZZO_G - 0.5
out(f"   De MAX: in Y il manico e' largo {W:g} -> De <= {De_Y:.1f}; in XZ il limite vero e' il mozzo del grilletto "
    f"accanto alla cima della molla (a {d_hub + 0.5 + R_MOZZO_G:.1f} mm dall'asse) -> De <= {2 * d_hub:.1f}; "
    f"e davanti alla molla deve passare il braccio del grilletto.")
out(f"   La lunghezza NON e' limitata dal manico (~{tab_spazio[7] - _extra:.0f} mm per De 7) ma dal GRILLETTO: il naso sta "
    f"{A_ASSIALE:.0f} mm (assiali) sotto il perno e,")
out(f"   ruotando di {abs(PHI_FINE):.1f} gradi, striscia di {LAT_MAX - LAT_MIN:.1f} mm sul pattino. Il naso a {A_ASSIALE:.0f} mm "
    f"con attrito a secco (mu {MU}) darebbe coppia d'attrito {MU * A_ASSIALE:.1f} mm*F contro")
out(f"   {b_t(PHI_CAMMA):.1f} mm*F di ritorno: per questo il naso ha un RULLINO (mu eff ~{MU_NASO}). Scelta: L1_GEOM = {L1_GEOM:g} mm "
    f"(foro fino a t={T_PAD1 + 2 * R_CONT:.0f}, s={s_imp(lungo_asse(cima0, T_PAD1 + 2 * R_CONT)):.0f}).")
out(f"   => SPAZIO: molla montata L1 <= {L1_GEOM:g} mm, L0 = L1 + precarico (fino a ~{L1_GEOM + 20:.0f} se il filo lo regge), "
    f"De <= 7 con la sede d8 del concept (fino a ~{min(De_Y, 2 * d_hub):.0f} spostando il braccio).")

# --- 1b. perdite ---
out("")
s_rif = simula_cane(molla(MOLLE[0]), M_CART, F_TRATT)
out(f"1b. PERDITE (cane {m_cane:.1f} g, massa efficace all'asse {m_eff_ax:.1f} g, percussore {M_PERC:.2f} g, cartuccia {M_CART:.2f} g):")
out(f"   molla -> cane all'urto: rendimento {ETA_MECC} (attriti coda/coppe/perno); urto cane->percussore->cartuccia e={E_REST};")
out(f"   fascia di trattenuta {F_TRATT:g} N su {p.cart_fascia:g} mm = {F_TRATT * p.cart_fascia:.1f} mJ da pagare. "
    f"Con la molla da penna: {s_rif['E0']:.0f} mJ -> {s_rif['KE_urto']:.0f} -> {s_rif['KE_c']:.0f} mJ "
    f"(passa il {s_rif['eta'] * 100:.0f}%, perde {100 - s_rif['eta'] * 100:.0f}%).")
v_lo, v_hi = v_per_gittata(4.0, M_CART), v_per_gittata(6.0, M_CART)
E_lo, E_hi = 0.5 * M_CART * v_lo ** 2, 0.5 * M_CART * v_hi ** 2
out(f"   Gittata (tiro teso da {H_TIRO} m, Cd {CD}): 4 m -> {v_lo:.1f} m/s = {E_lo:.0f} mJ, 6 m -> {v_hi:.1f} m/s = {E_hi:.0f} mJ "
    f"nella cartuccia da {M_CART:.2f} g. (Obiettivo dato: {E_CART_MIN:g}-{E_CART_MAX:g} mJ.)")
out(f"   NB: col mio modello d'aria l'intervallo dato 36-60 mJ vale ~4-4.7 m, non 6: 6 m teso chiedono ~{E_hi:.0f} mJ.")

# --- 1c. candidati ---
out("")
out(f"1c. CANDIDATI (L1 di montaggio = min({L1_GEOM:g}, L0-{PRE_MIN:g}); spire attive STIMATE col passo ~0.45 Dm, k da verificare)")
out(f"   {'molla':16s} {'mat':8s} {'na':>3s} {'k':>5s} {'pre':>5s} {'Frip':>5s} {'Fmax':>5s} {'Lmin':>5s}/{'pac':>4s} "
    f"{'tau':>5s}/{'amm':>4s} {'E0':>4s} {'Ecart':>5s} {'v':>5s} {'teso':>5s} {'alz':>5s} {'dito':>5s} {'poll':>4s}  esito")
ris = []
for mm in MOLLE:
    m = molla(mm)
    f = forze(m)
    s = simula_cane(m, M_CART, F_TRATT)
    g0 = gittata(s["v"], 0, M_CART)
    gb, ab = miglior_gittata(s["v"], M_CART)
    tau = m["tau"](f["F_max"])
    ok_pacco = f["L_min"] >= m["Lp"] + p.margine_pacco - 0.05
    ok_tau = tau <= m["tau_amm"]
    ok_De = m["De"] <= D_SEDE_REF - 1.0 + 1e-6
    ok_E = s["KE_c"] >= E_CART_MIN
    ok_dito = f["F_dito"] <= F_DITO_MAX
    ok_rit = f["ritorno"] > 0
    probl = [n for n, o in (("PACCO", ok_pacco), ("TAU", ok_tau), ("De", ok_De), ("POCA E", ok_E),
                            ("DITO DURO", ok_dito), ("NO RITORNO", ok_rit)) if not o]
    if s["KE_c"] > E_CART_MAX:
        probl.append("oltre 60 mJ")
    esito = "OK" if not probl else ", ".join(probl)
    ris.append((m, f, s, g0, gb, ab, tau, probl))
    out(f"   {m['nome']:16s} {m['mat']:8s} {m['na']:3d} {m['k']:5.2f} {m['pre']:5.1f} {f['F_rip']:5.1f} {f['F_max']:5.1f} "
        f"{f['L_min']:5.1f}/{m['Lp'] + p.margine_pacco:4.1f} {tau:5.0f}/{m['tau_amm']:4.0f} {s['E0']:4.0f} {s['KE_c']:5.1f} "
        f"{s['v']:5.1f} {g0:5.1f} {gb:5.1f} {f['F_dito']:5.1f} {f['F_poll']:4.1f}  {esito}")
out("   (k N/mm, pre = precarico a riposo mm, F N, L mm, tau MPa, E mJ, v m/s, gittate m: teso = 0 gradi, alz = angolo migliore;"
    " dito/poll = forza al grilletto/sperone N)")

_eta = [r[2]["eta"] for r in ris if r[0]["nome"] != "penna"]
out(f"   Rendimento simulato molla->cartuccia {min(_eta) * 100:.0f}-{max(_eta) * 100:.0f}% (dopo urto e fascia): per {E_CART_MIN:g} mJ "
    f"servono ~{E_CART_MIN / max(_eta):.0f}-{E_CART_MIN / min(_eta):.0f} mJ nella molla, per {E_CART_MAX:g} mJ ~{E_CART_MAX / max(_eta):.0f}-"
    f"{E_CART_MAX / min(_eta):.0f}.")
# --- 1d. raccomandazione ---
validi = [r for r in ris if not [x for x in r[7] if x != "oltre 60 mJ"]]
if validi:
    # la piu' dolce sul dito fra quelle che stanno nella finestra 36-60 mJ; se nessuna, la piu' vicina
    nella = [r for r in validi if r[2]["KE_c"] <= E_CART_MAX] or validi
    REC = min(nella, key=lambda r: (r[1]["F_dito"], -r[2]["KE_c"]))
else:
    REC = max(ris, key=lambda r: r[2]["KE_c"])
mR, fR, sR, g0R, gbR, abR, tauR, prR = REC
ML = mR
out("")
out(f"1d. RACCOMANDAZIONE: molla '{mR['nome']}' ({mR['nota']})")
out(f"   ACQUISTO: molla di compressione {mR['mat']}{' (EN 10270-1 DH, Federstahl)' if mR['mat'] == 'armonico' else ' 1.4310'}, "
    f"filo d {mR['d']:g} mm, De {mR['De']:g} mm (Di {mR['De'] - 2 * mR['d']:.1f}), L0 {mR['L0']:g} mm, estremi chiusi "
    f"(meglio se molati), {mR['nt']} spire totali circa ({mR['na']} attive), k ~{mR['k']:.2f} N/mm.")
out(f"   Montaggio: L1 {mR['L1']:g} a riposo (precarico {mR['pre']:.1f} mm, {fR['F_rip']:.1f} N), {fR['L_min']:.1f} mm armato col "
    f"grilletto a fondo (pacco {mR['Lp']:.1f}+{p.margine_pacco:g}), F max {fR['F_max']:.1f} N, tau {tauR:.0f}/{mR['tau_amm']:.0f} MPa."
    + (f" Distanziale {mR['spessore']:.1f} mm sopra il pistone." if mR["spessore"] > 0.05 else ""))
out(f"   Resa: molla {sR['E0']:.0f} mJ -> cartuccia {sR['KE_c']:.0f} mJ ({sR['eta'] * 100:.0f}%), {sR['v']:.1f} m/s, "
    f"~{g0R:.1f} m tiro teso, ~{gbR:.0f} m alzando ({abR} gradi). Dito ~{fR['F_dito']:.0f} N, pollice ~{fR['F_poll']:.0f} N.")
_Lprova = mR["L0"] - 10.0
out(f"   PROVA PRIMA DI MONTARLA (le spire dei listini sono una stima): compressa da {mR['L0']:g} a {_Lprova:g} mm deve "
    f"reggere ~{mR['k'] * 10:.0f} N = {mR['k'] * 10 / 9.81 * 1000:.0f} g sulla bilancia da cucina.")
out(f"   Se pesa meno del 20% -> prendere la misura con filo superiore; se pesa di piu' del 20% -> controllare tau e grilletto.")
_alt = sorted([r for r in ris if r is not REC and r[0]["nome"] != "penna"], key=lambda r: len(r[7]))
for r in _alt[:2]:
    out(f"   alternativa '{r[0]['nome']}': cartuccia {r[2]['KE_c']:.0f} mJ, {r[3]:.1f} m teso, dito {r[1]['F_dito']:.0f} N"
        f" -> {'OK' if not r[7] else ', '.join(r[7])}")
# sensibilita'
s_tr2 = simula_cane(ML, M_CART, 2.0)
s_tr10 = simula_cane(ML, M_CART, 10.0)
fR_secco = forze(ML, MU)
out(f"   Sensibilita': trattenuta 2 N -> {s_tr2['KE_c']:.0f} mJ / {gittata(s_tr2['v'], 0, M_CART):.1f} m; "
    f"10 N -> {s_tr10['KE_c']:.0f} mJ / {gittata(s_tr10['v'], 0, M_CART):.1f} m. "
    f"Naso SENZA rullino (mu {MU}): dito {fR_secco['F_dito']:.0f} N, ritorno "
    f"{'ok' if fR_secco['ritorno'] > 0 else 'NON torna'} ({fR_secco['ritorno']:.0f} N*mm).")
ssp_L = q.L1 - ML["L1"]
out(f"   Spinta diretta (alternativa, NON serve): la stessa molla nel canale orizzontale di oggi vorrebbe il canale "
    f"{ML['L1'] - q.L1:+.0f} mm piu' lungo (L1 {ML['L1']:g} contro {q.L1:g}) -> corpo ~{ML['L1'] - q.L1:.0f} mm piu' lungo dietro.")

# =====================================================================
#                              OBIETTIVO 2
# =====================================================================
D_SEDE = D_SEDE_REF
out("")
out("=" * 100)
out("OBIETTIVO 2 - INNESTO NEL TELAIO DI build.py")
out("=" * 100)

# --- inviluppi (vani) nel piano XZ, tutti centrati su y = 0 ---
TH_ALL = [ANG_ARMO * i / 26 for i in range(27)]
sweep_cane = unary_union([cane_pose(th, netto=False) for th in TH_ALL])
PHI_ALL = [PHI_FINE - 0.5 + (0.5 - PHI_FINE + 0.5) * i / 14 for i in range(15)]
sweep_gril = unary_union([gril_pose(f) for f in PHI_ALL])
cg_min, cg_max = min(comp_gril(f) for f in PHI_ALL), max(comp_gril(f) for f in PHI_ALL)
sweep_pist = unary_union([pistone_2d(-cg_min), pistone_2d(-cg_max), pistone_2d(0.0)])
vano_cane = sweep_cane.buffer(0.3)
vano_gril = sweep_gril.buffer(0.3)
vano_molla = unary_union([banda_asse(cima0, -1.0, T_PIST0 + L_PIST + 0.5, D_SEDE / 2), sweep_pist.buffer(0.3)])
foro_pc = Point(P).buffer(D_PERNO / 2 + 0.15, 24)
foro_pg = Point(PT).buffer(D_PERNO_G / 2 + 0.15, 24)

# --- profilo dorsale suggerito (calcolato qui, riportato in 2e) ---
Z_APERTO = 5.0                                  # sopra questa quota la feritoia del cane e' aperta (sperone fuori)
racchiudere = unary_union([vano_molla, vano_gril.difference(Point(_cxp, _czp).buffer(BT["R_PONT"] + 1.0)),
                           vano_cane.intersection(sbox(-100, -100, 100, Z_APERTO)),
                           foro_pc.buffer(PARETE), foro_pg.buffer(PARETE)])


def violazione(tel):
    return racchiudere.difference(tel.buffer(-PARETE)).area


viol_old = violazione(TEL_OLD)
Z0_NEW = BT["Z_DORSO0"]
best = None
for X0 in [BT["X_DORSO0"] + 1.0 * i for i in range(0, 46)]:
    for Z0 in [-30.0 + 1.0 * j for j in range(0, 36)]:
        pg = SPoly(profilo_telaio(X0, Z0))
        if not pg.is_valid:
            continue
        if violazione(pg) > viol_old + 0.05:
            continue
        xr = pg.intersection(sbox(-200, -25.0, 200, 200)).bounds[0]     # dorso piu' arretrato sopra z=-25
        chiave = (-round(xr, 1), pg.area)
        if best is None or chiave < best[2]:
            best = (X0, Z0, chiave)
X0_NEW, Z0_NEW, _ = best
X0_CONS = max(X0 for X0 in [BT["X_DORSO0"] + 0.5 * i for i in range(0, 90)]
              if SPoly(profilo_telaio(X0, BT["Z_DORSO0"])).is_valid
              and violazione(SPoly(profilo_telaio(X0, BT["Z_DORSO0"]))) <= viol_old + 0.05)
TEL_CONS = SPoly(profilo_telaio(X0_CONS, BT["Z_DORSO0"])).buffer(0)
TEL_NEW = SPoly(profilo_telaio(X0_NEW, Z0_NEW)).buffer(0)



# 2a. posizioni
out("2a. POSIZIONI (coordinate di build.py; scudo di build.py x %.0f..%.0f, asse tamburo z %.2f)" % (X_SCUDO, X_SCUDO1, ZA))
out(f"   perno cane M3     ({P0:6.1f}, {P1:6.1f})   [v2 (35,-20): passava nella scanalatura di carica]")
out(f"   perno grilletto d2 ({PT[0]:6.1f}, {PT[1]:6.1f})   = posto della finta vite (16,-28) di build.py")
out(f"   naso/dente         ({N0[0]:6.1f}, {N0[1]:6.1f});  dito a ({DITO[0]:g}, {DITO[1]:g}) nel ponticello")
out(f"   sede molla d{D_SEDE:g}: da ({cima0[0]:.1f}, {cima0[1]:.1f}) giu' lungo il manico fino a "
    f"({lungo_asse(cima0, T_PAD1)[0]:.1f}, {lungo_asse(cima0, T_PAD1)[1]:.1f}) (+ vano del gancio e del rullino)")
out(f"   percussore: foro d{D_SHANK + 0.3:.1f} nello scudo a z=0, collare nella forcella del cane (x {X_FACE:.1f}..{X_STOP:.1f})")
_bb = sweep_cane.bounds
out(f"   feritoia del cane (inviluppo 0-{ANG_ARMO:g} gradi): x {_bb[0]:.1f}..{_bb[2]:.1f}, z {_bb[1]:.1f}..{_bb[3]:.1f}, larga "
    f"{SP_CANE + p.gioco_rot:g}; feritoia del grilletto: x {sweep_gril.bounds[0]:.1f}..{sweep_gril.bounds[2]:.1f}, "
    f"z {sweep_gril.bounds[1]:.1f}..{sweep_gril.bounds[3]:.1f}, larga {SP_GRIL + p.gioco_rot:g}")

# 2b. molla e braccio dentro il manico
out("")
out("2b. SEDE MOLLA NEL MANICO")
_viol = vano_molla.difference(lecito_imp).area
_dmin = materiale_imp.exterior.distance(vano_molla) if materiale_imp.geom_type == "Polygon" else \
    min(g.exterior.distance(vano_molla) for g in materiale_imp.geoms)
out(f"   parete XZ: vano molla+pistone fuori dalla parete minima {_viol:.2f} mm^2 -> "
    f"{'OK' if _viol < 0.05 else 'BUCA'}; parete minima {_dmin:.1f} mm (cappetta 2.2 gia' tolta)")
sl_m = min(semi_larghezza(x, z) for x, z in [lungo_asse(cima0, t) for t in range(0, int(T_PAD1) + 1, 3)])
out(f"   parete Y: manico largo {2 * sl_m:.1f} nel tratto della molla, foro d{D_SEDE:g} -> {sl_m - D_SEDE / 2:.1f} mm per lato "
    f"({'OK' if sl_m - D_SEDE / 2 >= PARETE else 'SOTTILE'}); le guancette ({BT['t_g']:g} mm) stanno FUORI dai fianchi y=+-{W2:g}: "
    f"nessuna tasca le tocca")
_gu = SPoly(BT["profilo_imp"](BT["RIENTRO_G"], BT["S_G0"], BT["L_IMP"] - BT["RIENTRO_G"])).buffer(0)
_vg = imp_xz(BT["S_VITE_G"], 0)
_dvg = Point(_vg).distance(vano_molla.union(vano_gril))
out(f"   vite della guancetta (s={BT['S_VITE_G']:g}, ({_vg[0]:.1f},{_vg[1]:.1f})): oggi e' finta; se diventa vera e passante "
    f"dista {_dvg:.1f} mm dai vani -> {'OK con foro d2' if _dvg >= 1.0 + PARETE else 'va spostata'}")
arm_alto = gril_pose(0.0).difference(banda_asse(cima0, T_PIST0 + L_PIST - 0.5, 200, 30))
_dsp = min(rotg(arm_alto, f, PT).distance(molla_2d(L1_GEOM, ML["De"]).union(pistone_2d())) for f in PHI_ALL)
_dsp_rip = gril_pose(PHI_CAMMA).difference(banda_asse(cima0, T_PIST0 + L_PIST - 0.5, 200, 30)).distance(
    molla_2d(L1_GEOM, ML["De"]).union(pistone_2d()))
out(f"   braccio del grilletto: scende davanti alla molla e si aggancia sotto il pattino; luce minima dalle spire "
    f"{_dsp:.1f} mm (a riposo {_dsp_rip:.1f}) -> {'non le tocca' if _dsp > 0.1 else 'TOCCA'}")
out(f"   rullino sul pattino: corsa laterale {LAT_MIN:+.1f}..{LAT_MAX:+.1f} mm, pattino largo {LAT_MAX - LAT_MIN + 3.2:.1f}; "
    f"il pistone (d{D_PIST:.1f} x {L_PIST:g}) e' guidato nel foro e regge la coppia del carico eccentrico")
_fuori = sweep_gril.difference(materiale_imp.union(TEL_NEW).union(vano_pont).union(ponticello).buffer(0.01))
_out_gr = _fuori.area
out(f"   grilletto fuori dal telaio, dal manico e dal ponticello: {_out_gr:.2f} mm^2"
    + (f" (in x {_fuori.bounds[0]:.1f}..{_fuori.bounds[2]:.1f}, z {_fuori.bounds[1]:.1f}..{_fuori.bounds[3]:.1f})" if _out_gr > 0.01 else ""))

# 2c. ponticello
_lama_basso = [gril_pose(f).intersection(sbox(22.0, -80, 80, _czp + 4.0)) for f in (0.0, PHI_CAMMA, PHI_FINE)]
_gap_p = min(Point(_cxp, _czp).buffer(BT["r_PONT"], 96).exterior.distance(g) for g in _lama_basso)
_in_p = all(g.within(vano_pont) for g in _lama_basso)
_pas = sweep_gril.intersection(anello)
out("")
out(f"2c. PONTICELLO di build.py (anello r{BT['r_PONT']:g}/{BT['R_PONT']:g} in ({_cxp},{_czp}), largo {BT['W_PONT']:g}): lama "
    f"{'dentro il vano' if _in_p else 'FUORI'} sotto z={_czp + 4:g}, luce minima {_gap_p:.1f} mm a riposo/armato/fondo corsa (v2: usciva)")
out(f"   in alto la lama passa nella feritoia attraverso la testa dell'anello (x {_pas.bounds[0]:.0f}..{_pas.bounds[2]:.0f}) come oggi: "
    f"restano {(BT['W_PONT'] - SP_GRIL - p.gioco_rot) / 2:.2f} mm per lato ({'OK' if (BT['W_PONT'] - SP_GRIL - p.gioco_rot) / 2 >= PARETE else 'SOTTILE'})")
# 2d. perni
out("")
out("2d. PERNI ATTRAVERSO IL TELAIO (gusci in due meta' su y=0)")
_car_r = q.camera_d / 2
_car_z = BT["z_car"]
_car_x0 = X_SCUDO - BT["L_car"]
scanal_xz = sbox(_car_x0, _car_z - _car_r, X_SCUDO1 + 0.1, _car_z + _car_r)       # scanalatura di carica (lato destro)
y_scan = abs(BT["y_car"]) - _car_r                   # |y| del bordo interno della scanalatura (a z = z_car)
foro_tamb = sbox(q.x_cam - BT["_FORO_TAMB_DIETRO"], ZA - (p.tamb_asse_d + p.gioco_rot) / 2, 200,
                 ZA + (p.tamb_asse_d + p.gioco_rot) / 2)
finestra = sbox(q.x_cam - p.g_tamb, ZA - q.finestra_R, q.x_cam - p.g_tamb + q.finestra_L, ZA + q.finestra_R)
for nome, c, foro, dpin, vano_suo in (("cane", P, foro_pc, D_PERNO, vano_cane), ("grilletto", PT, foro_pg, D_PERNO_G, vano_gril)):
    hw = semi_larghezza(c[0], c[1], X0_NEW)
    d_est = TEL_NEW.exterior.distance(foro)
    altri = {"scanalatura carica": scanal_xz, "foro asse tamburo": foro_tamb, "finestra tamburo": finestra,
             "vano molla": vano_molla, ("vano grilletto" if nome == "cane" else "vano cane"): (vano_gril if nome == "cane" else vano_cane)}
    dd = {k: v.distance(foro) for k, v in altri.items()}
    peggio = min(dd, key=dd.get)
    coperto = _gu.contains(Point(c))
    out(f"   {nome:9s} d{dpin:g}: telaio largo {2 * hw:.1f} in quel punto -> spina lunga {2 * hw - 0.4:.1f} (a filo, 0.2 sotto ogni "
        f"fianco): NON esce; parete XZ verso l'esterno {d_est:.1f} mm, verso '{peggio}' {dd[peggio]:.1f} mm "
        f"({'OK' if min(d_est, dd[peggio]) >= PARETE else 'SOTTILE'}); "
        f"{'sotto la guancetta' if coperto else 'fuori dalle guancette: si infila dal fianco a gusci chiusi'}")
# scanalatura di carica: parete in Y verso la feritoia del cane dove si sovrappongono in XZ
_sov = vano_cane.intersection(scanal_xz)
if _sov.is_empty:
    out("   scanalatura di carica: il cane non la sovrappone in XZ")
else:
    zs = [_sov.bounds[1] + (_sov.bounds[3] - _sov.bounds[1]) * i / 20 for i in range(21)]
    yin = min(abs(BT["y_car"]) - math.sqrt(max(_car_r ** 2 - (z - _car_z) ** 2, 0.0)) for z in zs)
    out(f"   scanalatura di carica (lato destro, y<-{y_scan:.1f}): si sovrappone in XZ alla feritoia del cane "
        f"(x {_sov.bounds[0]:.1f}..{_sov.bounds[2]:.1f}); parete in Y = {yin:.2f} - {(SP_CANE + p.gioco_rot) / 2:.2f} = "
        f"{yin - (SP_CANE + p.gioco_rot) / 2:.2f} mm ({'OK' if yin - (SP_CANE + p.gioco_rot) / 2 >= PARETE - 1e-3 else 'SOTTILE'}; "
        f"con cane da 8 sarebbe {yin - (8 + p.gioco_rot) / 2:.2f})")
# perno del tamburo
band_pt = sbox(-50, ZA - p.tamb_asse_d / 2 - 0.5, 200, ZA + p.tamb_asse_d / 2 + 0.5)
x_cane_band = vano_cane.intersection(band_pt).bounds[2]
x_pt_old = q.x_cam - BT["_PERNO_TAMB_DIETRO"]
out(f"   PERNO DEL TAMBURO: in build.py parte da x={x_pt_old:.1f} (foro da {q.x_cam - BT['_FORO_TAMB_DIETRO']:.1f}) e "
    f"{'ATTRAVERSA' if x_cane_band > x_pt_old else 'non tocca'} la feritoia del cane (che arriva a x={x_cane_band:.1f} "
    f"alla sua quota): va accorciato a x>={x_cane_band + 0.4:.1f}, appoggio dietro {X_SCUDO1 - x_cane_band - 0.4:.1f} mm "
    f"(oggi {X_SCUDO1 - x_pt_old:.1f}), quasi tutto nello scudo")
# finte viti / spine dei gusci
out("   SPINE DEI GUSCI (finte viti di build.py, filamento d1.75 passante):")
vani_tutti = unary_union([vano_cane, vano_gril, vano_molla, foro_pc.buffer(0.5), foro_pg.buffer(0.5)])
viti_nuove = []
for (vx, vz) in BT["viti"]:
    d = Point(vx, vz).distance(vani_tutti)
    ok = d >= 0.95 + PARETE
    if (vx, vz) == (round(PT[0]), round(PT[1])) or math.dist((vx, vz), PT) < 0.6:
        out(f"     ({vx:5.1f},{vz:6.1f}): DIVENTA il perno del grilletto (la testa finta copre la spina d2)")
        viti_nuove.append((vx, vz))
        continue
    if ok:
        out(f"     ({vx:5.1f},{vz:6.1f}): libera ({d:.1f} mm dai vani) -> resta")
        viti_nuove.append((vx, vz))
        continue
    best = None
    for r in [0.5 * i for i in range(1, 60)]:
        for k in range(24):
            a = 2 * math.pi * k / 24
            c = (vx + r * math.cos(a), vz + r * math.sin(a))
            pc = Point(c)
            if pc.distance(vani_tutti) >= 0.95 + PARETE and TEL_NEW.buffer(-(0.95 + PARETE + 1.0)).contains(pc) \
                    and pc.distance(finestra) >= 2.6 and pc.distance(scanal_xz) >= 2.6 and pc.distance(foro_tamb) >= 2.6:
                best = c
                break
        if best:
            break
    out(f"     ({vx:5.1f},{vz:6.1f}): BUCA un vano (a {d:.1f} mm) -> spostarla in ({best[0]:.1f},{best[1]:.1f})")
    viti_nuove.append(best)
out(f"   + perno del cane ({P0:g},{P1:g}) come sesta 'vite' a vista (testa finta sopra la M3).")
out("   MONTAGGIO: guscio sinistro steso; dentro: cane (con percussore nella forcella), grilletto, coppa, molla,")
out("   distanziale/pistone (la molla si monta precaricata: si arma il cane a mano e si infila il pistone dal vano del")
out("   rullino), si chiude il guscio destro e si infilano DAL FIANCO M3 e spina d2 attraverso entrambe le meta'.")
out("   Tutti gli assi sono fuori dalle guancette e dalla cappetta: si smonta senza togliere le guancette.")

# 2e. profilo dorsale
out("")
out("2e. NUOVO PROFILO DORSALE")
def x_retro(tel, z_min):
    g = tel.intersection(sbox(-200, z_min, 200, 200))
    return g.bounds[0]


Z_DORSO_ZONA = -25.0
xo, xn = x_retro(TEL_OLD, Z_DORSO_ZONA), x_retro(TEL_NEW, Z_DORSO_ZONA)
d_mezzo = [x_retro(TEL_OLD, z) for z in (-10, 0, 8)], [x_retro(TEL_NEW, z) for z in (-10, 0, 8)]
area_tolta = TEL_OLD.area - TEL_NEW.area
L_tot_old = q.L_tel + BT["CANNA_VISTA"] - TEL_OLD.bounds[0]
L_tot_new = q.L_tel + BT["CANNA_VISTA"] - TEL_NEW.bounds[0]
_wd = 2 * semi_larghezza(xo + 6, 0.0)
out(f"   ricerca sui due parametri di build.py (X_DORSO0, Z_DORSO0), stessa ellisse + raccordo di Hermite, "
    f"vincolo: tutti i vani con parete >= {PARETE:g}; obiettivo: dorso piu' avanti possibile, poi meno materiale")
out(f"   build.py oggi: X_DORSO0={BT['X_DORSO0']:g}, Z_DORSO0={BT['Z_DORSO0']:g}  ->  suggerito: X_DORSO0={X0_NEW:g}, Z_DORSO0={Z0_NEW:g}")
out(f"   dorso dietro il cane (punto piu' arretrato sopra z={Z_DORSO_ZONA:g}): x {xo:.1f} -> {xn:.1f} = {xn - xo:.0f} mm piu' corto")
xc_ = x_retro(TEL_CONS, Z_DORSO_ZONA)
out(f"   variante CONSERVATIVA (Z_DORSO0={BT['Z_DORSO0']:g} come oggi, solo X avanti): X_DORSO0={X0_CONS:g} -> dorso a x {xc_:.1f} "
    f"({xc_ - xo:.0f} mm piu' corto), gobba alta di oggi, meno incavo per la mano")
out(f"   (la soluzione piu' corta ({X0_NEW:g},{Z0_NEW:g}) puo' scavare un incavo sopra il dorso del manico, tipo revolver moderno;"
    f" la conservativa tiene la gobba alta, piu' 'western')")
out(f"   alle quote z=-10/0/+8: x {d_mezzo[0][0]:.0f}/{d_mezzo[0][1]:.0f}/{d_mezzo[0][2]:.0f} -> "
    f"{d_mezzo[1][0]:.0f}/{d_mezzo[1][1]:.0f}/{d_mezzo[1][2]:.0f}")
out(f"   profilo laterale: -{area_tolta:.0f} mm^2 (~{area_tolta * 18 * 1e-3 * 1.24 * 0.5:.0f} g di PLA al 50%)")
out(f"   LUNGHEZZA FUORI TUTTO: {L_tot_old:.0f} -> {L_tot_new:.0f} mm. Il punto piu' arretrato e' il TALLONE "
    f"dell'impugnatura (x={TEL_OLD.bounds[0]:.1f}), che non cambia:")
out(f"   la pistola si accorcia SOLO in alto (sparisce la gobba dietro il cane), non nell'ingombro totale.")
pts_new = [(round(x, 1), round(z, 1)) for x, z in profilo_telaio(X0_NEW, Z0_NEW)[:BT["N_DORSO"] + 1]]
out(f"   nuovo dorso (ellisse, da build.dorso_telaio): {pts_new}")
_sbuca = sweep_cane.difference(TEL_NEW).intersection(sbox(-100, -100, X_SCUDO - 8, 100))
if not _sbuca.is_empty:
    out(f"   la feritoia del cane sbuca sul dorso dietro (x {_sbuca.bounds[0]:.0f}..{_sbuca.bounds[2]:.0f}, da z {_sbuca.bounds[1]:.0f}): "
        f"da armato lo sperone esce all'indietro, come la finestra del cane di un revolver d'epoca")
_sp_ar = cane_pose(ANG_ARMO).bounds
out(f"   sperone: a riposo cima z={Z_SPERONE:g} ({Z_SPERONE - 12.3:.0f} mm sopra la cinghia), armato arriva a "
    f"x={_sp_ar[0]:.1f}, z max {_sp_ar[3]:.1f}: resta fuori dal dorso nuovo")

# 2f. lista modifiche a build.py
out("")
out("2f. COSA CAMBIARE IN build.py PER ADOTTARE IL MECCANISMO (solo elenco, build.py NON e' toccato)")
modifiche = [
    "TELAIO: togliere M.vuoto_canale() (canale percussore+molla d8 da x=-1 a 41 e tappo): resta solo il foro "
    f"d{D_SHANK + 0.3:.1f} del percussore nello scudo a z=0.",
    f"TELAIO: X_DORSO0/Z_DORSO0 da ({BT['X_DORSO0']:g},{BT['Z_DORSO0']:g}) a ({X0_NEW:g},{Z0_NEW:g}); X_STRETTO segue "
    "(e' = X_DORSO0) -> il restringimento W_DIETRO si sposta in avanti; controllare l'assert della cresta.",
    f"TELAIO: feritoia del cane: non piu' Box(34, 8.5, 40) da (-18, z 5.6) ma l'inviluppo del cane ruotato 0-{ANG_ARMO:g} "
    f"gradi (x {_bb[0]:.0f}..{_bb[2]:.0f}, z {_bb[1]:.0f}..aperta in alto), larga {SP_CANE + p.gioco_rot:g}.",
    f"TELAIO: feritoia del grilletto: non piu' Box(15, 6.5, 20) da (28,-42) ma l'inviluppo del grilletto "
    f"(x {sweep_gril.bounds[0]:.0f}..{sweep_gril.bounds[2]:.0f}, z {sweep_gril.bounds[1]:.0f}..{sweep_gril.bounds[3]:.0f}), "
    "compreso il braccio che scende nel manico.",
    f"TELAIO: aggiungere la sede molla d{D_SEDE:g} lungo il manico (asse per ({cima0[0]:.1f},{cima0[1]:.1f}), "
    f"inclinato {ANG_MOLLA:g} gradi) fino a t={T_PIST0 + L_PIST:.0f} + il vano del pattino e del rullino.",
    f"TELAIO: fori passanti per il perno M3 del cane ({P0:g},{P1:g}) e per la spina d2 del grilletto ({PT[0]:g},{PT[1]:g}).",
    "TELAIO: spostare le finte viti/spine dei gusci come in 2d (" +
    ", ".join(f"({a:.0f},{b:.0f})" for a, b in viti_nuove) + ").",
    f"PERNO TAMBURO: da x={x_pt_old:.1f} a x>={x_cane_band + 0.4:.1f} (e il foro vuoto_asse_tamburo idem).",
    "CANE: il profilo di oggi (sperone fisso sopra il canale) diventa il cane imperniato di questo file: mozzo M3, "
    f"coda per la molla, camma col dente di monta, forcella del percussore, spessore {SP_CANE:g} (non 8).",
    "GRILLETTO: da sagoma estetica a pezzo funzionale: mozzo d2, naso nella tacca, lama nel ponticello, "
    "braccio nel manico con rullino.",
    "NUOVI PEZZI: percussore PLA con collare, coppa superiore, pistone con pattino (+ distanziale se serve), "
    f"rullino PLA, molla acciaio '{ML['nome']}', vite M3x{2 * semi_larghezza(P0, P1, X0_NEW) - 0.4:.0f} (o spina), "
    f"spina d2x{2 * semi_larghezza(PT[0], PT[1], X0_NEW) - 0.4:.0f}.",
    "SCANALATURA DI CARICA: invariata (con cane 7 e perno a x 30.5 non c'e' piu' interferenza).",
]
for i, s in enumerate(modifiche, 1):
    out(f"   {i:2d}. {s}")

# =====================================================================
# VERDETTO
# =====================================================================
out("")
out("=" * 100)
out("VERDETTO")
out("=" * 100)
out(f"(a) Molla: '{mR['nome']}' {mR['mat']} d{mR['d']:g} De{mR['De']:g} L0 {mR['L0']:g}, ~{mR['na']} spire attive, k~{mR['k']:.2f} N/mm "
    f"(si verifica con la bilancia: -10 mm = ~{mR['k'] * 10 / 9.81 * 1000:.0f} g).")
out(f"    Montata a L1 {mR['L1']:g} con {mR['pre']:.0f} mm di precarico: {sR['E0']:.0f} mJ -> {sR['KE_c']:.0f} mJ nella cartuccia, "
    f"~{g0R:.1f} m teso. Il prezzo e' il grilletto: ~{fR['F_dito']:.0f} N (con rullino).")
out(f"(b) Si innesta: perni nel telaio largo 22 senza uscire, sede molla dentro il manico con parete, ponticello e")
out(f"    scanalatura di carica rispettati - MA solo spostando il perno del cane a x {P0:g}, il cane a 7 mm, accorciando il perno")
out(f"    del tamburo e spostando le spine dei gusci che cadono nei vani. Lo sperone e' stato alzato a z {Z_SPERONE:g}.")
out(f"(c) Il telaio si accorcia SOLO in alto: dorso dietro il cane da x {xo:.0f} a x {xn:.0f} ({xn - xo:.0f} mm; {xc_ - xo:.0f} mm nella "
    f"variante che tiene la gobba alta).")
out(f"    La lunghezza fuori tutto resta {L_tot_new:.0f} mm: la fa il tallone del manico, che non si sposta.")

# =====================================================================
# SOLIDI, DISEGNO, EXPORT
# =====================================================================
TH_A, PHI_A = ANG_ARMO, 0.0
TH_R, PHI_R = 0.0, PHI_CAMMA


def solido_cane(th):
    s = solido(cane_pose(th), SP_CANE)
    s -= solido(rotg(fer_sh, th, P), D_SHANK + 0.4)
    return s - Pos(P[0], 0, P[1]) * Rot(90, 0, 0) * Cylinder(D_PERNO / 2 + 0.15, SP_CANE + 2)


def solido_perc(tip):
    return M._cil_x(D_COL, tip - L_PERC, L_COL, z=ZB) + \
        M._cil_x(D_SHANK, tip - L_PERC + L_COL - 0.01, L_PERC - L_COL + 0.01, z=ZB)


def cil_lungo_u(d, base, L):
    ang = math.degrees(math.atan2(U[0], U[1]))
    return Pos(base[0], 0, base[1]) * Rot(0, ang, 0) * Cylinder(d / 2, L, align=(_C, _C, _MIN))


def assieme_molla(th, phi):
    dc, dg = comp_cane(th), comp_gril(phi)
    L = ML["L1"] - dc - dg
    cima = lungo_asse(cima0, dc)
    b_sup = lungo_asse(cima, L_COPPA)
    b_mol = lungo_asse(b_sup, L)
    pist = solido(pistone_2d(-dg), D_PIST)
    return (cil_lungo_u(ML["De"], b_mol, L), cil_lungo_u(ML["De"] + 0.6, b_sup, L_COPPA), pist)


cane_ar, cane_ab = solido_cane(TH_A), solido_cane(TH_R)
gril_ar, gril_rip = solido(gril_pose(PHI_A), SP_GRIL), solido(gril_pose(PHI_R), SP_GRIL)
perc_ar, perc_ab = solido_perc(_tip_armamento(TH_A)), solido_perc(TIP_S)
molla_ar, coppa_ar, pist_ar = assieme_molla(TH_A, PHI_A)
molla_rip, coppa_rip, pist_rip = assieme_molla(TH_R, PHI_R)
hw_c, hw_g = semi_larghezza(P0, P1, X0_NEW), semi_larghezza(PT[0], PT[1], X0_NEW)
perno_cane = Pos(P[0], 0, P[1]) * Rot(90, 0, 0) * Cylinder(D_PERNO / 2, 2 * hw_c - 0.4)
perno_gril = Pos(PT[0], 0, PT[1]) * Rot(90, 0, 0) * Cylinder(D_PERNO_G / 2, 2 * hw_g - 0.4)
tamburo = M.tamburo_base()
scudo = M._cil_x(2 * BT["r_scudo"], X_SCUDO, X_SCUDO1 - X_SCUDO, z=ZA) - \
    M._cil_x(D_SHANK + 0.3, X_SCUDO - 0.1, X_SCUDO1 - X_SCUDO + 0.2, z=ZB)
cartuccia = M._cil_x(p.cart_D, X_CAM, max(q.cart_L_tot), z=ZB)

# guscio sinistro schematico (fianchi piani, y 0..W/2) col profilo NUOVO e le tasche dei vani
guscio = solido(TEL_NEW, W2, y0=W2 / 2)
for vano, larg in ((vano_cane, SP_CANE + p.gioco_rot), (vano_gril, SP_GRIL + p.gioco_rot), (vano_molla, D_SEDE)):
    guscio -= solido(vano, larg)
guscio -= solido(foro_pc, W + 2) + solido(foro_pg, W + 2)
guscio -= M.vuoto_finestra_tamburo() + M.vuoto_asse_tamburo(x_cane_band + 0.4, q.L_tel + 1) + M.vuoto_canna()
guscio -= M._cil_x(D_SHANK + 0.3, X_SCUDO - 1, X_SCUDO1 - X_SCUDO + 2, z=ZB)

# interferenze 3D residue (a riposo e armato)
v_ct = max(_vol(c, tamburo) for c in (cane_ab, cane_ar))
v_cs = max(_vol(c, scudo) for c in (cane_ab, cane_ar))
v_gc = _vol(gril_ar, cane_ar) + _vol(gril_rip, cane_ab)
v_mg = _vol(molla_rip, gril_rip) + _vol(molla_ar, gril_ar)
v_guscio = sum(_vol(guscio, s) for s in (cane_ab, cane_ar, gril_rip, gril_ar, molla_rip, molla_ar, pist_rip))
out("")
out(f"controllo 3D [mm^3]: cane/tamburo {v_ct:.2f}, cane/scudo {v_cs:.2f}, grilletto/cane {v_gc:.2f}, molla/grilletto {v_mg:.2f}, "
    f"pezzi/guscio sinistro {v_guscio:.2f}")

# disegno laterale: profilo vecchio e nuovo + meccanismo
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(11, 9))
    x, z = TEL_OLD.exterior.xy
    ax.plot(x, z, color="#999999", lw=1.2, ls="--", label=f"telaio build.py (dorso {BT['X_DORSO0']:g},{BT['Z_DORSO0']:g})")
    x, z = TEL_NEW.exterior.xy
    ax.plot(x, z, color="#1f6f63", lw=2.0, label=f"telaio suggerito, piu' corto (dorso {X0_NEW:g},{Z0_NEW:g})")
    x, z = TEL_CONS.exterior.xy
    ax.plot(x, z, color="#8a5cc2", lw=1.2, ls="-.", label=f"variante conservativa (dorso {X0_CONS:g},{BT['Z_DORSO0']:g})")
    for g, c, lab in ((ponticello.difference(vano_pont), "#4fa89a", "ponticello"), (vano_molla, "#3060ff", "sede molla/pistone"),
                      (cane_pose(0.0), "#ff7a00", "cane a riposo"), (gril_pose(PHI_CAMMA), "#b08030", "grilletto a riposo")):
        gs = [g] if g.geom_type == "Polygon" else list(g.geoms)
        for i, pg in enumerate(gs):
            xx, zz = pg.exterior.xy
            ax.fill(xx, zz, color=c, alpha=0.45, label=lab if i == 0 else None)
            for h in pg.interiors:
                xx, zz = h.xy
                ax.fill(xx, zz, color="white")
    xx, zz = cane_pose(ANG_ARMO).exterior.xy
    ax.plot(xx, zz, color="#ff7a00", lw=0.8, ls=":", label="cane armato")
    xx, zz = molla_2d(ML["L1"], ML["De"]).exterior.xy
    ax.plot(xx, zz, color="#0020a0", lw=1.0)
    ax.add_patch(plt.Rectangle((q.x_cam, ZA - q.R_tamb), q.L_tamb, 2 * q.R_tamb, fc="#d9a441", alpha=0.25, label="tamburo"))
    ax.add_patch(plt.Rectangle((X_SCUDO, ZA - BT["r_scudo"]), X_SCUDO1 - X_SCUDO, 2 * BT["r_scudo"], fc="#4fa89a", alpha=0.4))
    for (vx, vz) in BT["viti"]:
        ax.plot(vx, vz, "x", color="red", ms=7)
    for (vx, vz) in viti_nuove:
        ax.plot(vx, vz, "o", mfc="none", color="green", ms=7)
    ax.plot(*P, "k+", ms=10)
    ax.plot(*PT, "k+", ms=10)
    ax.set_aspect("equal")
    ax.grid(alpha=0.3)
    ax.set_title(f"v3: molla '{ML['nome']}' nel manico, profilo dorsale suggerito (x rosse = viti di oggi, o verdi = nuove)")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_xlim(-45, 100)
    ax.set_ylim(-115, 30)
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(os.path.join(OUT, "v3_profilo.png"), dpi=110, bbox_inches="tight")
    out(f"disegno: {os.path.relpath(os.path.join(OUT, 'v3_profilo.png'), os.getcwd())}")
except Exception as err:  # il disegno e' un di piu'
    out(f"disegno saltato: {err}")

COL_A, COL_S, COL_G = "#d9a441", "#ff7a00", "#b08030"
show_object(guscio, id="guscio_sx", name="Guscio sinistro schematico (profilo nuovo)", options={"color": "#4fa89a", "alpha": 0.35})
show_object(cane_ab, id="cane_abbattuto", name="Cane abbattuto", options={"color": COL_S})
show_object(cane_ar, id="cane_armato", name="Cane armato", options={"color": COL_A, "alpha": 0.5})
show_object(gril_rip, id="grilletto_riposo", name="Grilletto a riposo", options={"color": COL_G})
show_object(perc_ab, id="percussore", name="Percussore", options={"color": "#eeeeee"})
show_object(molla_rip, id="molla", name=f"Molla {ML['nome']}", options={"color": "#3060ff"})
show_object(pist_rip, id="pistone", name="Pistone + pattino", options={"color": "#88aaff"})
show_object(tamburo, id="tamburo", name="Tamburo", options={"color": "#d9a441", "alpha": 0.4})

os.makedirs(OUT, exist_ok=True)
comuni = [perno_cane, perno_gril, tamburo, scudo, cartuccia]
export_stl(Compound([cane_ab, gril_rip, perc_ab, molla_rip, coppa_rip, pist_rip] + comuni),
           os.path.join(OUT, "v3_assieme_riposo.stl"))
export_stl(Compound([cane_ar, gril_ar, perc_ar, molla_ar, coppa_ar, pist_ar] + comuni),
           os.path.join(OUT, "v3_assieme_armato.stl"))
export_stl(Compound([guscio, cane_ab, gril_rip, perc_ab, molla_rip, coppa_rip, pist_rip] + comuni),
           os.path.join(OUT, "v3_guscio_sx_assieme.stl"))
for nome, s in {"cane": cane_ab, "grilletto": gril_rip, "percussore": perc_ab, "molla": molla_rip, "coppa": coppa_rip,
                "pistone": pist_rip, "guscio_sx": guscio}.items():
    export_stl(s, os.path.join(OUT, f"v3_{nome}.stl"))
print(f"export: {os.path.relpath(OUT, os.getcwd())}/v3_*.stl")
