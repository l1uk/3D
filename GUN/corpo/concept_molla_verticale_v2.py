# CONCEPT v2 - UNA SOLA molla (acciaio, nel manico) + cartuccia PLA intera.
#
# Evoluzione di concept_molla_verticale.py (v1 resta com'e'). Non tocca
# build.py / meccanica.py / parametri.py / concetti.py: le quote arrivano da
# meccanica.py (-> params.scad), l'impugnatura si legge da build.py via AST.
# Sistema: X = asse canna, Z = alto, asse canna z = 0, mm. Angoli nel piano
# XZ positivi = antiorari (per il cane: positivo = si arma, va indietro).
#
# ---------------------------------------------------------------------
# CINEMATISMO (una molla, tre funzioni)
#   La molla NON appoggia sul telaio: e' FLOTTANTE nel foro dell'impugnatura,
#   compressa tra la coda del cane (coppa in alto) e la coda del grilletto
#   (coppa in basso, il grilletto ha un braccio che scende nel manico).
#   Ogni estremo usa come reazione l'altro pezzo (come le due gambe della
#   molla a V di un Colt, ma con una molla a elica):
#     - in alto spinge la coda del cane -> coppia "in avanti" = SPARO, e a
#       colpo partito tiene il cane abbattuto (= ritorno/riposo del cane);
#     - in basso spinge il braccio del grilletto -> coppia "in avanti" =
#       RITORNO DEL GRILLETTO e tiene il naso del grilletto premuto contro la
#       camma del cane = SCATTO IN MONTA (la tacca entra da sola, "clic").
#   Monta in singola azione: il pollice arma il cane (comprime dall'alto); il
#   grilletto premuto comprime ancora un poco dal basso e libera la tacca.
#   La doppia azione NON e' fatta: il dente DA sul grilletto deve
#   ripassare sotto il cane dopo lo sparo e nei revolver lo fa una seconda
#   molla. Anche la manina che ruota il tamburo ha la sua molla: qui il
#   tamburo si ruota a mano col fermo a scatto, come nel corpo attuale.
#
# PERCUSSIONE: percussore corto in PLA guidato nello scudo, TRASCINATO dal
#   cane con una forcella a corsa a vuoto (non flottante libero):
#   - il cane va ad arco (~20 gradi sull'asse al bersaglio): diretto sul
#     fondello striscerebbe e servirebbe un'asola nello scudo; il percussore
#     va dritto in un foro tondo;
#   - lo scudo resta pieno (ci appoggia la cartuccia);
#   - la forcella lo ritira quando si arma: tamburo libero da armato;
#   - la sua corsa (S_PUSH) porta la fascia posteriore della cartuccia FUORI
#     dalla zona stretta della camera: non e' un colpo secco sul fondello ma
#     urto + spinta corta. Quando la fascia e' libera, la cartuccia vola.
#
# RISULTATI (parametri di default; il file li ristampa tutti):
#  1. Molla penna (De 5, L0 29) flottante: L1=27 a riposo, L2 18.5 da armato,
#     16.8 armato + grilletto premuto (pacco+margine 17.1: AL LIMITE,
#     ci arriva quasi). Cane 26 gradi, grilletto 9.4 gradi (riposo sulla camma) /
#     10.6 gradi (sgancio). Pollice ~6 N, grilletto ~9 N (dente neutro + attrito).
#     Il grilletto vince sempre: coppia in avanti con qualunque cane.
#  2. Percussore PLA d2.6 L~13.7, ~0.1 g. Corsa 3.1: 0.6 di aria + 2.5 di
#     spinta (la zona stretta e' lunga cart_fascia + 0.5 = 2.0). Cane ~5 g,
#     massa efficace all'asse ~3.5 g.
#  3. Cartuccia "aperta" calcolata dal profilo SCAD: ~0.85 g. Trattenuta
#     in camera stimata 5 N su 1.5 mm (~7 mJ da pagare prima di volare).
#  4. Energia (simulazione 1D a contatti elastici, e=0.4):
#       molla penna    56 mJ  -> cartuccia ~5 m/s  (~11 mJ, 20%)
#       molla lunga   151 mJ  -> cartuccia ~10 m/s (~42 mJ, 28%)
#     Gittata (da 1.2 m, attrito dell'aria): penna ~2.5 m tiro teso /
#     ~3.1 m alzando; lunga ~4.8 / ~9 m. A parita' di tutto un BB da 0.12 g
#     prenderebbe MENO energia (~4%): il cane pesante si adatta meglio alla
#     massa della cartuccia. Spinta diretta di oggi (molla nel corpo, corsa
#     8.2 a contatto): ~6.8 m/s con la stessa molla da penna.
#  5. Il canale dietro lo scudo sparisce: dorso del telaio da x=-28 a x~10
#     (-38 mm in alto); lunghezza totale invariata (~143 mm) finche' resta
#     il tallone dell'impugnatura.
#  DOVE SI ROMPE: vedi VERDETTO in fondo all'esecuzione.
# ---------------------------------------------------------------------
import ast
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# show_object e' iniettato solo dentro agentcad; qui giriamo con Python puro
if "show_object" not in dir():
    def show_object(*a, **k):  # noqa: E306  (no-op fuori da agentcad)
        pass

from build123d import Align, Box, Compound, Cylinder, Plane, Polygon, Pos, Rot, extrude, export_stl  # noqa: E402
from shapely.geometry import LineString, Point, Polygon as SPoly, box as sbox  # noqa: E402
from shapely.ops import unary_union  # noqa: E402
from shapely import affinity  # noqa: E402

import meccanica as M  # noqa: E402

p, q = M.p, M.q
_C, _MIN = Align.CENTER, Align.MIN
QUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(QUI, "concept_stl")

# =====================================================================
# PARAMETRI DEL CONCEPT
# =====================================================================
X_SCUDO = q.x_sc                 # 41: retro dello scudo
X_CAM = q.x_cam                  # 44.3: fondo della cartuccia
ZB = 0.0                         # camera in linea con la canna (asse tamburo + r_passo)

# --- cane (come v1) ---
X_PERNO, Z_PERNO = 35.0, -20.0   # perno del cane, sotto la canna, 6 mm dietro lo scudo
D_PERNO = 3.0                    # M3 acciaio
R_MOZZO = 5.0
SP_CANE = 8.0
ANG_ARMO = 26.0                  # rotazione abbattuto -> armato [gradi]
CORSA_CODA = 9.0                 # compressione data dalla coda del cane (come oggi)
R_CONT = 3.2                     # naso tondo delle code sulle coppe

# --- percussore trascinato ---
D_SHANK = 2.6                    # gambo nello scudo
D_COL, L_COL = 5.0, 1.5          # collare preso nella forcella del cane
T_LIP = 1.2                      # labbro anteriore della forcella (tira indietro il collare)
S_PUSH = p.cart_fascia + 0.5 + 0.5   # spinta dentro la camera: zona stretta (2.0) + 0.5
RITIRO_TIP = 0.3                 # da armato la punta resta 0.3 dentro lo scudo

# --- dente di monta / grilletto ---
R_NASO = 8.0                     # raggio (dal perno del cane) della cima del naso del grilletto
H_ENG = 1.2                      # impegno del dente
GIOCO_SGANCIO = 0.3              # il naso scende H_ENG + questo per liberare
L_NASO = 9.0                     # perno grilletto 9 mm dietro il naso: il naso scende RADIALE
W_NASO = 2.5
SP_GRIL = 6.0
D_PERNO_G = 2.0                  # perno grilletto (filamento 1.75 o chiodino)
R_MOZZO_G = 3.5
MU = 0.3                         # attrito PLA/PLA

# --- molla: si sceglie quella da modellare (la tabella energia le prova tutte) ---
MOLLE = {
    # molla da penna di oggi (params.scad)
    "penna": dict(d=p.molla_d, De=p.molla_De, L0=p.molla_L0, nt=p.molla_n_tot, nm=p.molla_n_morte,
                  pre=p.precarico, nota="molla da penna di oggi"),
    # molla commerciale piu' lunga, stesso diametro (De 5): filo 0.7, L0 45
    "lunga": dict(d=0.7, De=5.0, L0=45.0, nt=30, nm=4, pre=10.0,
                  nota="commerciale De5 filo 0.7 L0 45 (non da penna)"),
}
MOLLA = "penna"
TAU_AMM = 1000.0                 # tensione tangenziale ammessa filo armonico 0.6-0.7 [MPa]
RHO_ACC = 7.85e-3                # g/mm^3
L_COPPA = 3.0                    # coppe in alto e in basso

# --- munizione e balistica ---
RHO_PLA = 1.24e-3 * 0.85         # pezzi stampati (cane, percussore)
RHO_CART = 1.24e-3 * 0.95        # cartuccia: quasi tutta perimetri
F_TRATT = 5.0                    # N, forza della fascia in camera (STIMA: da misurare col provino camera_c)
E_REST = 0.4                     # restituzione PLA/PLA
ETA_MECC = 0.85                  # attriti code/coppe e perni durante la caduta del cane
K_CONT = 1.0e6                   # N/m rigidezza di contatto (PLA, pezzi corti)
CD, RHO_ARIA, H_TIRO = 0.8, 1.2, 1.2   # cartuccia che sbanda, aria, altezza di sparo [m]
M_BB = 0.12                      # g, pallino 6 mm per confronto

PARETE = p.parete_min

# =====================================================================
# IMPUGNATURA da build.py (solo costanti e funzioni del profilo)
# =====================================================================
def _impugnatura_da_build():
    src = open(os.path.join(QUI, "build.py")).read()
    servono = {"ANG_IMP", "X_IMP0", "Z_IMP0", "L_IMP", "F_IMP", "B_IMP", "PANCIA",
               "PICCO_PANCIA", "H_TALL", "R_PUNTA", "R_TALL", "CONC_DITA", "PICCO_CONC",
               "R_MIN", "N_IMP", "N_ARCO", "_a", "_dir", "_nrm", "X_DORSO0", "Z_DORSO0",
               "cx_p", "cz_p", "R_PONT", "r_PONT", "CANNA_VISTA"}
    funzioni = {"imp_xz", "dorso", "arco_imp", "profilo_imp"}
    corpo = []
    for nodo in ast.parse(src).body:
        if isinstance(nodo, ast.Assign):
            nomi = {n.id for t in nodo.targets for n in ast.walk(t) if isinstance(n, ast.Name)}
            if nomi & servono:
                corpo.append(nodo)
        elif isinstance(nodo, ast.FunctionDef) and nodo.name in funzioni:
            corpo.append(nodo)
    ns = {"math": math}
    exec(compile(ast.Module(body=corpo, type_ignores=[]), "build.py", "exec"), ns)
    return ns


B = _impugnatura_da_build()
U = (-B["_dir"][0], -B["_dir"][1])          # asse impugnatura verso l'alto
grip = SPoly(B["profilo_imp"]()).buffer(0)

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
    """Momento polare d'area (mm^4) di un poligono rispetto a c."""
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


def solido(g, sp):
    """Poligono shapely (piano XZ) estruso simmetrico in Y."""
    gs = [g] if g.geom_type == "Polygon" else list(g.geoms)
    out = None
    for pg in gs:
        f = Polygon(*list(pg.exterior.coords)[:-1], align=None)
        s = extrude(Plane.XZ * f, amount=sp / 2, both=True)
        for h in pg.interiors:
            s -= extrude(Plane.XZ * Polygon(*list(h.coords)[:-1], align=None), amount=sp, both=True)
        out = s if out is None else out + s
    return out


# =====================================================================
# MOLLA
# =====================================================================
def molla(nome):
    m = dict(MOLLE[nome])
    D = m["De"] - m["d"]
    na = m["nt"] - m["nm"]
    m["k"] = M.molla_k(m["d"], m["De"], na, p.molla_G)
    m["Lp"] = m["nt"] * m["d"]
    m["L1"] = m["L0"] - m["pre"]
    C = D / m["d"]
    m["Kw"] = (4 * C - 1) / (4 * C - 4) + 0.615 / C
    m["tau"] = lambda F, D=D, d=m["d"], Kw=m["Kw"]: Kw * 8 * F * D / (math.pi * d ** 3)
    m["massa"] = m["nt"] * math.pi * D * math.pi * m["d"] ** 2 / 4 * RHO_ACC
    return m


ML = molla(MOLLA)

# =====================================================================
# CANE: coda e molla (cinematica come v1, ma la molla ora e' flottante)
# =====================================================================
L_CODA = CORSA_CODA / (2 * math.sin(math.radians(ANG_ARMO / 2)))
n_perp = (-U[1], U[0])
if n_perp[0] > 0:
    n_perp = (-n_perp[0], -n_perp[1])
coda_mid = (P[0] + L_CODA * n_perp[0], P[1] + L_CODA * n_perp[1])
coda0 = rot(coda_mid, -ANG_ARMO / 2)            # coda a cane abbattuto


def comp_cane(th):
    """Compressione data dal cane (mm) all'angolo th rispetto all'abbattuto."""
    c = rot(coda0, th)
    return -dot((c[0] - coda0[0], c[1] - coda0[1]), U)


def dcomp_cane(th, h=0.05):
    return (comp_cane(th + h) - comp_cane(th - h)) / math.radians(2 * h)   # mm/rad


# asse molla: retta per coda_mid parallela a U
def su_asse(pt):
    t = dot((pt[0] - coda_mid[0], pt[1] - coda_mid[1]), U)
    return (coda_mid[0] + t * U[0], coda_mid[1] + t * U[1]), t


# =====================================================================
# PERCUSSORE e forcella
# =====================================================================
# faccia della forcella (spinge il collare) e labbro (lo tira): piani verticali a cane abbattuto
X_STOP = X_SCUDO - 0.05                         # il labbro batte sullo scudo: fine corsa del cane
TIP_S = X_CAM + S_PUSH                          # punta a cane abbattuto
TIP_R = X_SCUDO + p.t_sc - RITIRO_TIP           # punta ritirata (da armato)
RITIRO = TIP_S - TIP_R


def x_piano(x0, th):
    """x a z=0 del piano verticale x=x0 (a cane abbattuto) ruotato di th."""
    pt = rot((x0, ZB), th)
    a = math.radians(th)
    return pt[0] + (pt[1] - ZB) * math.tan(a)


def dx_piano(x0, th, h=0.05):
    return (x_piano(x0, th + h) - x_piano(x0, th - h)) / math.radians(2 * h)   # mm/rad


# corsa a vuoto: il labbro arretra quanto la faccia; deve tirare indietro il collare di RITIRO
DF = x_piano(X_STOP, 0) - x_piano(X_STOP, ANG_ARMO)
G_LOST = DF - RITIRO
X_FACE = X_STOP - T_LIP - G_LOST - L_COL        # faccia di spinta (= retro collare) ad abbattuto
L_PERC = TIP_S - X_FACE                         # lunghezza totale percussore
M_PERC = (math.pi / 4 * (D_COL ** 2 * L_COL + D_SHANK ** 2 * (L_PERC - L_COL))) * RHO_PLA
# angolo a cui la faccia incontra il collare (percussore ritirato) quando il cane cade
th_urto = ANG_ARMO
while x_piano(X_FACE, th_urto) < TIP_R - L_PERC and th_urto > 0:
    th_urto -= 0.01


def x_tip_cane(th):
    """Posizione della punta del percussore trascinato quasi-statico (armamento lento)."""
    spinto = x_piano(X_FACE, th) + L_PERC                       # se la faccia lo spinge
    tirato = x_piano(X_STOP - T_LIP, th) - 0.0 + (L_PERC - L_COL)   # se il labbro lo tira
    return min(TIP_S, max(min(spinto, TIP_S), min(tirato, TIP_S)) if th < 0.01 else min(tirato, TIP_S))


def perc_2d(tip):
    col = sbox(tip - L_PERC, -D_COL / 2, tip - L_PERC + L_COL, D_COL / 2)
    sh = sbox(tip - L_PERC + L_COL - 0.01, -D_SHANK / 2, tip, D_SHANK / 2)
    return col, sh


# =====================================================================
# GRILLETTO e dente di monta
# =====================================================================
# il naso sta sotto il perno del cane: la sua discesa (rotazione del grilletto) e' radiale
N0 = (P[0], P[1] - R_NASO)                      # cima-fronte del naso, grilletto in avanti (phi = 0)
PT = (N0[0] - L_NASO, N0[1])                    # perno del grilletto
PHI_CAMMA = -math.degrees(H_ENG / L_NASO)       # riposo: il naso appoggia sulla camma del cane
PHI_SGANCIO = -math.degrees((H_ENG + GIOCO_SGANCIO) / L_NASO)
PHI_FINE = PHI_SGANCIO - 1.0                    # fine corsa del grilletto (battuta)

# camma/dente del cane, a cane ARMATO: settore r <= R_NASO + H_ENG che finisce sul piano x = N0.x
R_CAMMA = R_NASO + H_ENG
W_CAMMA = ANG_ARMO + 14.0
a0 = -90.0                                       # faccia del dente (a cane armato) sotto il perno
settore = [P] + [(P[0] + R_CAMMA * math.cos(math.radians(a0 + W_CAMMA * i / 16)),
                  P[1] + R_CAMMA * math.sin(math.radians(a0 + W_CAMMA * i / 16))) for i in range(17)]
camma_armato = SPoly(settore).buffer(0)
camma0 = rotg(camma_armato, -ANG_ARMO, P)       # nel riferimento del cane abbattuto

# braccio del grilletto fino alla coppa inferiore della molla
cima0, t_cima0 = su_asse((coda0[0] - U[0] * R_CONT, coda0[1] - U[1] * R_CONT))   # cima coppa sup.
# a riposo (cane abbattuto, grilletto sulla camma) la molla e' lunga L1
L_ASSE_RIPOSO = L_COPPA + ML["L1"] + L_COPPA + R_CONT
BC_rip = (cima0[0] - U[0] * L_ASSE_RIPOSO, cima0[1] - U[1] * L_ASSE_RIPOSO)   # naso braccio, a riposo
BC0 = rot(BC_rip, -PHI_CAMMA, PT)               # stesso punto a grilletto in avanti (phi = 0)


def comp_gril(phi):
    """Compressione data dal grilletto (mm) rispetto al riposo (phi = PHI_CAMMA)."""
    c = rot(BC0, phi, PT)
    return dot((c[0] - BC_rip[0], c[1] - BC_rip[1]), U)


def dcomp_gril(phi, h=0.05):
    return (comp_gril(phi + h) - comp_gril(phi - h)) / math.radians(2 * h)


def F_molla(th, phi, m=ML):
    return m["k"] * (m["pre"] + comp_cane(th) + comp_gril(phi))


def L_molla(th, phi, m=ML):
    return m["L1"] - comp_cane(th) - comp_gril(phi)


# =====================================================================
# PROFILI 2D
# =====================================================================
zb = ZB
braccio = SPoly([
    (X_STOP, zb - 5.5), (X_STOP, zb + 5.0),
    (X_STOP - 3, zb + 9.5), (X_STOP - 8, zb + 12.0),
    (X_STOP - 13, zb + 13.5), (X_STOP - 16, zb + 12.0),          # sperone
    (X_STOP - 15, zb + 8.5), (X_FACE - 3.0, zb + 6.5),
    (P[0] - R_MOZZO * 0.9, P[1] + 2), (P[0] + R_MOZZO * 0.9, P[1] - 2),
])
mozzo = Point(P).buffer(R_MOZZO, 32)
coda_g = LineString([P, coda0]).buffer(R_CONT, 16)

# feritoia del collare: inviluppo del collare nel riferimento del cane in tutte le pose
def _tip_armamento(th):
    # armando, il percussore resta avanti finche' il labbro non lo prende, poi segue il labbro
    tirato = x_piano(X_STOP - T_LIP, th) + (L_PERC - L_COL)
    return min(TIP_S, tirato)


pose_arm = [ANG_ARMO * i / 26 for i in range(27)]
fer_col, fer_sh = [], []
for th in pose_arm:
    for tip in {_tip_armamento(th), TIP_S if th == 0 else _tip_armamento(th),
                TIP_R if th >= th_urto else _tip_armamento(th)}:
        col, sh = perc_2d(tip)
        fer_col.append(rotg(col.buffer(0.2), -th, P))
        fer_sh.append(rotg(sh.buffer(0.2), -th, P))
# in caduta: faccia sul collare da th_urto a 0
for i in range(11):
    th = th_urto * i / 10
    tip = x_piano(X_FACE, th) + L_PERC
    col, sh = perc_2d(tip)
    fer_col.append(rotg(col.buffer(0.2), -th, P))
    fer_sh.append(rotg(sh.buffer(0.2), -th, P))
fer_col = unary_union(fer_col)
fer_sh = unary_union(fer_sh)

cane2d = braccio.union(mozzo).union(coda_g).union(camma0).simplify(0.03)
cane2d_pieno = cane2d
cane2d_netto = cane2d.difference(fer_col)        # la feritoia del collare passa da parte a parte

# grilletto a phi = 0 (in avanti, naso nella tacca)
naso = sbox(N0[0] - W_NASO - 0.05, N0[1] - 2.6, N0[0] - 0.1, N0[1])
braccio_naso = sbox(PT[0], N0[1] - 3.0, N0[0] - W_NASO + 0.5, N0[1] - 1.6)
lama = SPoly([(PT[0] + 2, PT[1] - 3), (PT[0] + 8, PT[1] - 3), (PT[0] + 11, PT[1] - 10),
              (PT[0] + 11, PT[1] - 18), (PT[0] + 9, PT[1] - 24), (PT[0] + 6, PT[1] - 28),
              (PT[0] + 4, PT[1] - 27), (PT[0] + 6, PT[1] - 20), (PT[0] + 6, PT[1] - 12),
              (PT[0] + 2.5, PT[1] - 6)])
braccio_g = LineString([PT, BC0]).buffer(2.4, 16).union(Point(BC0).buffer(R_CONT, 24))
gril2d = unary_union([Point(PT).buffer(R_MOZZO_G, 24), naso, braccio_naso, lama, braccio_g]).simplify(0.03)
gril2d = gril2d.difference(Point(PT).buffer(D_PERNO_G / 2 + 0.15, 16))
DITO = (PT[0] + 9.5, PT[1] - 18)                 # dove preme il dito


def cane_pose(th, netto=True):
    return rotg(cane2d_netto if netto else cane2d_pieno, th, P)


def gril_pose(phi):
    return rotg(gril2d, phi, PT)


# =====================================================================
# SOLIDI
# =====================================================================
def solido_cane(th):
    s = solido(cane_pose(th), SP_CANE)
    # labbro: fessura stretta in Y per il gambo (il collare e' trattenuto ai lati)
    sh = rotg(fer_sh, th, P)
    s -= solido(sh, D_SHANK + 0.4)
    return s - Pos(P[0], 0, P[1]) * Rot(90, 0, 0) * Cylinder(D_PERNO / 2 + 0.15, SP_CANE + 2)


def solido_perc(tip):
    return M._cil_x(D_COL, tip - L_PERC, L_COL, z=ZB) + \
        M._cil_x(D_SHANK, tip - L_PERC + L_COL - 0.01, L_PERC - L_COL + 0.01, z=ZB)


def cil_lungo_u(d, base, L):
    ang = math.degrees(math.atan2(U[0], U[1]))
    return Pos(base[0], 0, base[1]) * Rot(0, ang, 0) * Cylinder(d / 2, L, align=(_C, _C, _MIN))


def assieme_molla(th, phi):
    """Molla + coppe nella posa (th, phi), lungo l'asse fisso."""
    cima = (cima0[0] - U[0] * comp_cane(th), cima0[1] - U[1] * comp_cane(th))
    L = L_molla(th, phi)
    b_sup = (cima[0] - U[0] * L_COPPA, cima[1] - U[1] * L_COPPA)
    b_mol = (b_sup[0] - U[0] * L, b_sup[1] - U[1] * L)
    b_inf = (b_mol[0] - U[0] * L_COPPA, b_mol[1] - U[1] * L_COPPA)
    return (cil_lungo_u(ML["De"], b_mol, L), cil_lungo_u(ML["De"] + 0.6, b_sup, L_COPPA),
            cil_lungo_u(ML["De"] + 0.6, b_inf, L_COPPA), b_inf)


TH_A, PHI_A = ANG_ARMO, 0.0                      # armato
TH_R, PHI_R = 0.0, PHI_CAMMA                     # riposo
cane_ar, cane_ab = solido_cane(TH_A), solido_cane(TH_R)
gril_ar, gril_rip = solido(gril_pose(PHI_A), SP_GRIL), solido(gril_pose(PHI_R), SP_GRIL)
tip_ar = _tip_armamento(TH_A)
perc_ar, perc_ab = solido_perc(tip_ar), solido_perc(TIP_S)
molla_ar, coppa_s_ar, coppa_i_ar, _ = assieme_molla(TH_A, PHI_A)
molla_rip, coppa_s_rip, coppa_i_rip, base_rip = assieme_molla(TH_R, PHI_R)
perno_cane = Pos(P[0], 0, P[1]) * Rot(90, 0, 0) * Cylinder(D_PERNO / 2, 22)
perno_gril = Pos(PT[0], 0, PT[1]) * Rot(90, 0, 0) * Cylinder(D_PERNO_G / 2, 22)

tamburo = M.tamburo_base()
scudo = M._cil_x(2 * q.R_tamb, X_SCUDO, p.t_sc, z=q.z_asse_tamb) - \
    M._cil_x(D_SHANK + 0.3, X_SCUDO - 0.1, p.t_sc + 0.2, z=ZB)
cartuccia = M._cil_x(p.cart_D, X_CAM, max(q.cart_L_tot), z=ZB)


def _vol(a, b):
    try:
        return (a & b).volume
    except Exception:
        return 0.0


righe = []
def out(s=""):
    righe.append(s)
    print(s)


# =====================================================================
# 1. MOLLA E CINEMATISMO
# =====================================================================
out("=== CONCEPT v2: UNA molla flottante nel manico + cartuccia PLA ===")
F = lambda th, phi: F_molla(th, phi)
b_h = lambda th: dcomp_cane(th)                  # braccio della molla sul cane = d(comp)/d(theta) [mm]
b_t = lambda phi: -dcomp_gril(phi)               # sul grilletto (positivo = coppia in avanti)
L_ar, L_sg = L_molla(TH_A, PHI_A), L_molla(TH_A, PHI_FINE)
lim = ML["Lp"] + p.margine_pacco
out(f"1. Molla '{MOLLA}' ({ML['nota']}): k={ML['k']:.3f} N/mm, L0 {ML['L0']:g}, pacco {ML['Lp']:.1f}, massa {ML['massa']:.2f} g")
out(f"   lunghezze: riposo {ML['L1']:.1f} | armato {L_ar:.1f} | armato+grilletto a fondo {L_sg:.1f} "
    f"(pacco+margine {lim:.1f}) -> {'OK' if L_sg >= lim else 'A PACCO!'}")
out(f"   cane: {ANG_ARMO:g} gradi, coda L={L_CODA:.1f}, compressione dall'alto {comp_cane(TH_A):.2f} mm")
out(f"   grilletto: perno ({PT[0]:.1f}, {PT[1]:.1f}), braccio nel manico L={math.dist(PT, BC0):.1f} mm, "
    f"riposo {PHI_CAMMA:.1f} gradi (sulla camma), sgancio {PHI_SGANCIO:.1f}, battuta {PHI_FINE:.1f}")
out(f"   compressione dal basso: in monta {comp_gril(PHI_A):+.2f} mm (il grilletto scatta avanti), "
    f"a fondo {comp_gril(PHI_FINE):+.2f} mm")
for nome, th, phi in (("riposo", TH_R, PHI_R), ("armato", TH_A, PHI_A), ("sgancio", TH_A, PHI_SGANCIO)):
    out(f"   {nome:8s}: F={F(th, phi):5.1f} N  coppia cane {-F(th, phi) * b_h(th):+6.0f} N*mm (- = in avanti)  "
        f"grilletto {F(th, phi) * b_t(phi):+6.0f} N*mm (+ = in avanti)")
ok_ritorno = all(b_t(ph) > 0 for ph in (PHI_A, PHI_CAMMA, PHI_FINE))
out(f"   RITORNO GRILLETTO dalla stessa molla: braccio {b_t(PHI_FINE):.1f}..{b_t(PHI_A):.1f} mm, "
    f"{'sempre in avanti' if ok_ritorno else 'NON torna!'}")

# dente: forza e sgancio
tau_h_ar = F(TH_A, PHI_A) * b_h(TH_A)
r_dente = math.dist(P, N0)
N_dente = tau_h_ar / r_dente                      # forza normale sul naso (orizzontale, passa per PT: dente neutro)
r_dito = math.dist(PT, DITO)
tau_t_ar = F(TH_A, PHI_SGANCIO) * b_t(PHI_SGANCIO)
F_dito = (tau_t_ar + MU * N_dente * L_NASO) / r_dito
sperone = (X_STOP - 14, zb + 13)
F_pollice = tau_h_ar / math.dist(P, sperone)
out(f"   dente di monta neutro (forza sul naso per il perno del grilletto): N={N_dente:.1f} N; "
    f"pollice sullo sperone ~{F_pollice:.1f} N, dito sul grilletto ~{F_dito:.1f} N "
    f"(molla {tau_t_ar / r_dito:.1f} + attrito {MU * N_dente * L_NASO / r_dito:.1f})")

# --- verifiche 2D di contatto tra cane e grilletto ---
def sovrap(th, phi):
    return cane_pose(th, netto=False).intersection(gril_pose(phi)).area


def segui(th):
    """Grilletto spinto avanti dalla molla: angolo piu' avanti senza compenetrare (phi <= 0)."""
    phi = 0.0
    while phi > PHI_FINE - 3 and sovrap(th, phi) > 1e-4:
        phi -= 0.1
    return phi


v_monta = sovrap(TH_A, 0.0)
v_preso = sovrap(TH_A - 2.0, 0.0)
v_caduta = max(sovrap(ANG_ARMO * i / 26, PHI_SGANCIO) for i in range(27))
phi_seg = [segui(ANG_ARMO * i / 13) for i in range(14)]
out(f"   contatti 2D cane/grilletto: in monta {v_monta:.3f} mm^2, cane spinto 2 gradi avanti "
    f"{v_preso:.2f} mm^2 ({'TRATTENUTO' if v_preso > 0.05 else 'SFUGGE!'}), "
    f"caduta col grilletto a {PHI_SGANCIO:.1f}: {v_caduta:.3f} mm^2 ({'libero' if v_caduta < 1e-3 else 'urta!'})")
out(f"   armando, il grilletto segue la camma: phi = {phi_seg[0]:.1f} (abbattuto) ... {min(phi_seg):.1f} ... "
    f"{phi_seg[-1]:.1f} (armato: scatto in avanti di {phi_seg[-1] - phi_seg[-2]:.1f} gradi)")
ponte = Point(B["cx_p"], B["cz_p"]).buffer(B["r_PONT"], 48)
d_ponte = min(ponte.exterior.distance(gril_pose(ph).intersection(sbox(-50, -80, 80, PT[1] - 8)))
              for ph in (0.0, PHI_FINE))
dentro = all(gril_pose(ph).intersection(sbox(-50, -80, 80, PT[1] - 8)).within(ponte) for ph in (0.0, PHI_FINE))
out(f"   lama nel ponticello di build.py (anello r{B['r_PONT']:g}): "
    + (f"dentro, gioco {d_ponte:.1f} mm" if dentro else f"ESCE: il ponticello va arretrato/allargato"))

# molla e braccio dentro l'impugnatura
def _imp(s_, d_):
    return (B["X_IMP0"] + s_ * B["_dir"][0] + d_ * B["_nrm"][0], B["Z_IMP0"] + s_ * B["_dir"][1] + d_ * B["_nrm"][1])
sopra = SPoly([_imp(2, -200), _imp(2, 200), _imp(-200, 200), _imp(-200, -200)])
materiale = grip.union(sopra)
D_SEDE = ML["De"] + 1.0


def verifica_foro(m):
    L_ax = L_COPPA + m["L1"] + L_COPPA + R_CONT
    fondo = (cima0[0] - U[0] * (L_ax + 2 * R_CONT), cima0[1] - U[1] * (L_ax + 2 * R_CONT))
    can = LineString([fondo, (cima0[0] + U[0] * 2, cima0[1] + U[1] * 2)]).buffer(D_SEDE / 2, cap_style=2)
    return can.difference(materiale.buffer(-PARETE)).area, materiale.boundary.distance(can), fondo


sp_foro, marg_foro, fondo_foro = verifica_foro(ML)
sweep_g = unary_union([gril_pose(PHI_A + (PHI_FINE - PHI_A) * i / 6) for i in range(7)])
braccio_fuori = sweep_g.intersection(sbox(-60, -90, PT[0] - 4, PT[1] - 4)).difference(materiale.buffer(-PARETE)).area
out(f"   foro molla d{D_SEDE:g} nell'impugnatura: esce dalla parete minima {sp_foro:.2f} mm^2 "
    f"({'ci sta' if sp_foro < 0.01 else 'FORA'}), parete minima {marg_foro:.1f} mm; "
    f"braccio del grilletto nel manico: esce {braccio_fuori:.2f} mm^2")
s_fondo = dot((fondo_foro[0] - B["X_IMP0"], fondo_foro[1] - B["Z_IMP0"]), B["_dir"])
out(f"   fondo del foro a s={s_fondo:.0f} mm sull'asse impugnatura (lungo {B['L_IMP']:g}): restano "
    f"~{B['L_IMP'] - s_fondo:.0f} mm di manico sotto")

# =====================================================================
# 2. PERCUSSORE
# =====================================================================
out("")
out(f"2. Percussore trascinato: gambo d{D_SHANK:g}, collare d{D_COL:g}x{L_COL:g}, L {L_PERC:.1f} mm, "
    f"~{M_PERC:.2f} g")
out(f"   punta: abbattuto x={TIP_S:.1f} (+{S_PUSH:.1f} in camera), armato x={tip_ar:.1f} "
    f"({X_SCUDO + p.t_sc - tip_ar:.1f} dentro lo scudo)")
out(f"   forcella: corsa a vuoto {G_LOST:.1f} mm, il cane prende il collare a {th_urto:.1f} gradi; "
    f"da li' spinge per {RITIRO:.1f} mm (0.6 aria + {S_PUSH:.1f} spinta)")
inc = math.degrees(math.atan2(X_FACE - P[0], -(ZB - P[1])))
out(f"   il cane arriva sul collare con {abs(inc):.0f} gradi di inclinazione: il gambo resta dritto in un foro tondo "
    f"d{D_SHANK + 0.3:.1f} (niente asola nello scudo)")
v_t = _vol(perc_ar, tamburo)
pose5 = [ANG_ARMO * i / 4 for i in range(5)]
v_cs = max(_vol(solido_cane(a), scudo) for a in pose5)
v_ct = max(_vol(solido_cane(a), tamburo) for a in pose5)
v_cp = max(_vol(solido_cane(a), solido_perc(_tip_armamento(a))) for a in pose5[1:])
v_gt = _vol(gril_ar, cane_ar) + _vol(gril_rip, cane_ab)
out(f"   compenetrazioni [mm^3]: percussore armato/tamburo {v_t:.2f}, cane/scudo {v_cs:.2f}, "
    f"cane/tamburo {v_ct:.2f}, cane/percussore {v_cp:.2f}, grilletto/cane {v_gt:.2f}")
out(f"   (a riposo il percussore sporge {S_PUSH:.1f} mm in camera: il tamburo e' bloccato, si ruota da armato)")

# =====================================================================
# 3+4. CARTUCCIA, ENERGIA, VELOCITA', GITTATA
# =====================================================================
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
out("")
out(f"3. Cartuccia intera dal profilo di params.scad: aperta {M_CART:.2f} g, chiusa {massa_cartuccia('chiusa'):.2f} g, "
    f"corta {massa_cartuccia('corta'):.2f} g (BB 6 mm: {M_BB} g)")
out(f"   trattenuta: fascia posteriore {p.cart_fascia:g} mm nella zona stretta (camera_c, interf {p.interf_c}): "
    f"stimata F={F_TRATT:g} N -> {F_TRATT * p.cart_fascia:.1f} mJ da pagare su {p.cart_fascia + 0.5:.1f} mm")
out("   La percussione da sola NON la lancia: un colpo secco sul fondello con la fascia ancora presa")
out("   rimbalza. Qui il percussore la accompagna per S_PUSH mm, finche' la fascia esce dalla zona stretta.")

# --- cane: massa e inerzia (con feritoia) ---
m_cane = cane2d_netto.area * SP_CANE * RHO_PLA
I_cane = J_geom(cane2d_netto, P) * SP_CANE * RHO_PLA     # g mm^2
r_eff = abs(dx_piano(X_FACE, th_urto / 2))
m_eff_ax = I_cane / r_eff ** 2


def simula_cane(m, m_proj, F_tr, s_push_extra=0.0, dt=2e-7):
    """Caduta del cane, urto col percussore, spinta della cartuccia (1D, SI)."""
    k = m["k"] * 1e3
    I = I_cane * 1e-9 + (m["massa"] / 3 * 1e-3) * (dcomp_cane(ANG_ARMO / 2) * 1e-3) ** 2
    mp, mc = M_PERC * 1e-3, m_proj * 1e-3
    pre = m["pre"] + comp_gril(PHI_FINE)          # dito tiene il grilletto a fondo
    def zeta(mr):
        le = math.log(E_REST)
        return -le / math.sqrt(math.pi ** 2 + le ** 2)
    c1 = 2 * zeta(0) * math.sqrt(K_CONT * (mp * m_eff_ax * 1e-3 / (mp + m_eff_ax * 1e-3)))
    c2 = 2 * zeta(0) * math.sqrt(K_CONT * (mp * mc / (mp + mc)))
    k_stop = 50 * K_CONT * (r_eff * 1e-3) ** 2
    c_stop = 2 * zeta(0) * math.sqrt(k_stop * I)
    th, om = math.radians(ANG_ARMO), 0.0
    xp, vp = _tip_armamento(ANG_ARMO) * 1e-3, 0.0   # punta tirata indietro dal labbro
    xc, vc = X_CAM * 1e-3, 0.0
    Lp = L_PERC * 1e-3
    E0 = m["k"] * ((pre + comp_cane(ANG_ARMO)) ** 2 - pre ** 2) / 2     # mJ
    KE_urto, t, libero, t_lib = None, 0.0, False, 0.0
    W_tr = 0.0
    while t < 0.03:
        thd = math.degrees(th)
        xf = x_piano(X_FACE, thd) * 1e-3
        dxf = dx_piano(X_FACE, thd) * 1e-3          # m/rad
        tau = -ETA_MECC * k * (pre + comp_cane(thd)) * 1e-3 * dcomp_cane(thd) * 1e-3
        # faccia del cane sul collare
        d1 = xf - (xp - Lp)
        F1 = max(0.0, K_CONT * d1 + c1 * (dxf * om - vp)) if d1 > 0 else 0.0
        if F1 > 0 and KE_urto is None:
            KE_urto = 0.5 * I * om ** 2 * 1e3
        # labbro che trattiene il collare (il percussore non puo' scappare avanti)
        xl = x_piano(X_STOP - T_LIP, thd) * 1e-3
        d3 = (xp - Lp + L_COL * 1e-3) - xl
        F3 = max(0.0, K_CONT * d3 + c1 * (vp - dx_piano(X_STOP - T_LIP, thd) * 1e-3 * om)) if d3 > 0 else 0.0
        # percussore sul fondello
        d2 = xp - xc
        F2 = max(0.0, K_CONT * d2 + c2 * (vp - vc)) if d2 > 0 else 0.0
        # battuta del cane sullo scudo
        Ts = (-k_stop * th - c_stop * om) if th < 0 else 0.0
        # trattenuta della fascia
        u = (xc - X_CAM * 1e-3) * 1e3
        ov = max(0.0, min(u + p.cart_fascia, p.cart_fascia + 0.5 + s_push_extra * 0) - max(u, 0.0))
        Ftr = F_tr * min(ov, p.cart_fascia) / p.cart_fascia
        acc_c_lib = F2 / mc
        if vc > 1e-6:
            ac = (F2 - Ftr) / mc
        elif F2 > Ftr:
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


def simula_spinta(m_proj, F_tr, dt=2e-7):
    """Riferimento: schema di oggi, molla da penna nel corpo che spinge il percussore a contatto."""
    k = q.m_k * 1e3
    asta_d, asta_L = q.asta_d, q.L2 - 2 - 1.5
    m_perc = math.pi / 4 * (asta_d ** 2 * asta_L + p.perc_col_D ** 2 * p.perc_col_L + p.perc_punta_d ** 2 * q.punta_L) * 1.24e-3
    md = (m_perc + molla("penna")["massa"] / 3) * 1e-3
    mc = m_proj * 1e-3
    le = math.log(E_REST)
    z = -le / math.sqrt(math.pi ** 2 + le ** 2)
    c2 = 2 * z * math.sqrt(K_CONT * md * mc / (md + mc))
    x, v, xc, vc, t = 0.0, 0.0, (0.5 + p.g_tamb) * 1e-3, 0.0, 0.0
    corsa = q.corsa * 1e-3
    libero, t_lib = False, 0.0
    while t < 0.03:
        Fs = ETA_MECC * k * (p.precarico * 1e-3 + max(corsa - x, 0))
        Fst = -50 * K_CONT * (x - corsa) if x > corsa else 0.0
        d2 = x - xc
        F2 = max(0.0, K_CONT * d2 + c2 * (v - vc)) if d2 > 0 else 0.0
        u = (xc - (0.5 + p.g_tamb) * 1e-3) * 1e3
        ov = max(0.0, min(u + p.cart_fascia, p.cart_fascia + 0.5) - max(u, 0.0))
        Ftr = F_tr * min(ov, p.cart_fascia) / p.cart_fascia
        if vc > 1e-6 or F2 > Ftr:
            ac = (F2 - Ftr) / mc
        else:
            ac, vc = 0.0, 0.0
        v += (Fs + Fst - F2) / md * dt; x += v * dt
        vc += ac * dt; xc += vc * dt
        t += dt
        if not libero and x >= corsa and F2 == 0 and vc > v:
            libero, t_lib = True, t
        if libero and t - t_lib > 2e-4:
            break
    return dict(v=vc, KE_c=0.5 * mc * vc ** 2 * 1e3, m_perc=m_perc)


def gittata(v, ang_deg, m_g, h=H_TIRO):
    """Volo con resistenza quadratica, da altezza h fino a terra [m]."""
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


out("")
out(f"4. Energia. Cane ~{m_cane:.1f} g, J={I_cane:.0f} g*mm^2, braccio al percussore {r_eff:.1f} mm -> "
    f"massa efficace assiale {m_eff_ax:.1f} g (cartuccia {M_CART:.2f} g, rapporto {m_eff_ax / M_CART:.1f})")
out(f"   modello: caduta con rendimento {ETA_MECC}, contatti elastici e={E_REST}, trattenuta {F_TRATT:g} N")
ris = {}
for nome in MOLLE:
    m = molla(nome)
    Fmax = m["k"] * (m["pre"] + comp_cane(ANG_ARMO) + comp_gril(PHI_FINE))
    L_min = m["L1"] - comp_cane(ANG_ARMO) - comp_gril(PHI_FINE)
    s = simula_cane(m, M_CART, F_TRATT)
    g0 = gittata(s["v"], 0, M_CART)
    gb, ab = miglior_gittata(s["v"], M_CART)
    sp, mg, _ = verifica_foro(m)
    ris[nome] = (s, g0, gb)
    out(f"   [{nome}] k {m['k']:.2f} N/mm, F max {Fmax:.1f} N, tau {m['tau'](Fmax):.0f} MPa "
        f"({'ok' if m['tau'](Fmax) <= TAU_AMM else 'TROPPO'}), L min {L_min:.1f} vs pacco+marg "
        f"{m['Lp'] + p.margine_pacco:.1f} ({'ok' if L_min >= m['Lp'] + p.margine_pacco - 0.05 else 'PACCO'}), "
        f"foro {'ci sta' if sp < 0.01 else 'FORA'}")
    out(f"      molla {s['E0']:.0f} mJ -> cane all'urto {s['KE_urto']:.0f} mJ -> cartuccia {s['KE_c']:.1f} mJ "
        f"({s['eta'] * 100:.0f}%), trattenuta pagata {s['W_tr']:.1f} mJ")
    out(f"      v uscita ~{s['v']:.1f} m/s; gittata da {H_TIRO} m: tiro teso {g0:.1f} m, alzando ({ab} gradi) {gb:.1f} m")
# sensibilita' alla trattenuta e confronto col BB
for Ft in (2.0, 10.0):
    s = simula_cane(ML, M_CART, Ft)
    out(f"   [{MOLLA}] con trattenuta {Ft:g} N: v {s['v']:.1f} m/s, tiro teso {gittata(s['v'], 0, M_CART):.1f} m")
sbb = simula_cane(ML, M_BB, F_TRATT)
out(f"   [{MOLLA}] stesso cane su un BB da {M_BB} g (stessa trattenuta): {sbb['KE_c']:.1f} mJ ({sbb['eta'] * 100:.0f}%), "
    f"v {sbb['v']:.1f} m/s -> la massa leggera NON aiuta: il cane rimbalza, l'energia resta a lui")
ssp = simula_spinta(M_CART, F_TRATT)
out(f"   riferimento spinta diretta di oggi (molla penna nel corpo, percussore {ssp['m_perc']:.1f} g a contatto "
    f"per {q.spinta_c:.1f} mm): {ssp['KE_c']:.1f} mJ, v {ssp['v']:.1f} m/s, tiro teso {gittata(ssp['v'], 0, M_CART):.1f} m")
e_bersaglio = 0.5 * M_CART * 1e-3 * 8.0 ** 2 * 1e3
out(f"   per ~4 m di tiro teso servono ~8 m/s = {e_bersaglio:.0f} mJ nella cartuccia")

# =====================================================================
# 5. ACCORCIAMENTO
# =====================================================================
x_dietro = min(cane_ab.bounding_box().min.X, coda0[0] - R_CONT, cima0[0] - D_SEDE / 2)
x_retro = x_dietro - PARETE - 2.0
x_tallone = grip.bounds[0]
lung = q.L_tel + B["CANNA_VISTA"] - min(B["X_DORSO0"], x_tallone)
out("")
out(f"5. Il canale percussore/molla (x 0 -> {X_SCUDO:g}) sparisce; resta solo la tasca del collare "
    f"(x {X_FACE:.0f}..{X_SCUDO:g}). Ingombro interno piu' arretrato x={x_dietro:.1f}")
out(f"   dorso del telaio in alto: da x={B['X_DORSO0']:g} a x~{x_retro:.1f} (-{x_retro - B['X_DORSO0']:.0f} mm); "
    f"sperone armato a x={cane_ar.bounding_box().min.X:.1f} (sopra la mano)")
out(f"   lunghezza totale ~{lung:.0f} mm INVARIATA: la fa il tallone dell'impugnatura (x={x_tallone:.0f}), "
    f"che resta dov'e' perche' davanti c'e' il grilletto")

# =====================================================================
# VERDETTO
# =====================================================================
sp_, g0p, gbp = ris["penna"]
sl_, g0l, gbl = ris["lunga"]
out("")
out("=== VERDETTO ===")
out(f"Cinematica: CHIUDE. Una molla flottante tra coda del cane e coda del grilletto fa sparo, riposo del cane,")
out(f"ritorno del grilletto e scatto in monta. Solo singola azione e tamburo a mano: la DA e la manina vogliono altre molle.")
out(f"Energia con la molla da penna: NON basta per 'qualche metro'. {sp_['E0']:.0f} mJ -> {sp_['KE_c']:.0f} mJ nella cartuccia "
    f"({sp_['v']:.1f} m/s, ~{g0p:.1f} m teso): l'urto cane->percussore->cartuccia perde ~{100 - sp_['eta'] * 100:.0f}%,")
out(f"poi la fascia si mangia {F_TRATT * p.cart_fascia:.0f} mJ. Si rompe li', non nella cinematica. In piu' la molla corta "
    f"lavora quasi a pacco ({L_sg:.1f} su {lim:.1f}).")
out(f"Con la molla lunga (De5, filo 0.7, L0 45: nel manico ci sta) {sl_['E0']:.0f} mJ -> {sl_['v']:.1f} m/s, ~{g0l:.1f} m teso / ~{gbl:.0f} m alzando.")
out(f"La cartuccia PLA e' compatibile con la percussione SOLO se il percussore la accompagna fuori dalla fascia")
out(f"(urto + spinta corta, come qui); la spinta diretta rende di piu' ({ssp['v']:.1f} contro {sp_['v']:.1f} m/s, stessa molla)")
out(f"ma rivuole il canale dietro lo scudo. Consiglio: tenere la percussione con molla lunga e cane alleggerito.")

# =====================================================================
# SHOW + EXPORT
# =====================================================================
COL_A, COL_S, COL_G = "#d9a441", "#ff7a00", "#b08030"
show_object(cane_ar, id="cane_armato", name=f"Cane armato (+{ANG_ARMO:g} gradi)", options={"color": COL_A, "alpha": 0.5})
show_object(cane_ab, id="cane_abbattuto", name="Cane abbattuto (riposo)", options={"color": COL_S})
show_object(gril_ar, id="grilletto_monta", name="Grilletto in monta (naso nella tacca)", options={"color": COL_G, "alpha": 0.5})
show_object(gril_rip, id="grilletto_riposo", name="Grilletto a riposo (sulla camma)", options={"color": COL_G})
show_object(perc_ar, id="percussore_ritirato", name="Percussore ritirato (armato)", options={"color": "#cccccc", "alpha": 0.5})
show_object(perc_ab, id="percussore_avanti", name="Percussore avanti (abbattuto)", options={"color": "#eeeeee"})
show_object(molla_ar, id="molla_armato", name="Molla compressa (armato)", options={"color": "#3060ff", "alpha": 0.5})
show_object(molla_rip, id="molla_riposo", name="Molla a riposo", options={"color": "#3060ff"})
show_object(coppa_s_rip, id="coppa_sup", name="Coppa superiore (sul cane)", options={"color": "#88aaff"})
show_object(coppa_i_rip, id="coppa_inf", name="Coppa inferiore (sul grilletto)", options={"color": "#88aaff"})
show_object(perno_cane, id="perno_cane", name="Perno cane M3", options={"color": "#888888"})
show_object(perno_gril, id="perno_grilletto", name="Perno grilletto", options={"color": "#888888"})
show_object(tamburo, id="tamburo", name="Tamburo (riferimento)", options={"color": "#4fa89a", "alpha": 0.4})
show_object(scudo, id="scudo", name="Scudo con foro del percussore", options={"color": "#4fa89a", "alpha": 0.4})
show_object(cartuccia, id="cartuccia", name="Cartuccia PLA in camera", options={"color": "#f2e3c6"})

os.makedirs(OUT, exist_ok=True)
pezzi = {"cane_armato": cane_ar, "cane_abbattuto": cane_ab, "grilletto_monta": gril_ar,
         "grilletto_riposo": gril_rip, "percussore_ritirato": perc_ar, "percussore_avanti": perc_ab,
         "molla_armato": molla_ar, "molla_riposo": molla_rip, "coppa_sup": coppa_s_rip, "coppa_inf": coppa_i_rip,
         "perno_cane": perno_cane, "perno_grilletto": perno_gril, "tamburo": tamburo, "scudo": scudo,
         "cartuccia": cartuccia}
export_stl(Compound([cane_ab, gril_rip, perc_ab, molla_rip, coppa_s_rip, coppa_i_rip, perno_cane, perno_gril,
                     tamburo, scudo, cartuccia]), os.path.join(OUT, "v2_assieme_riposo.stl"))
export_stl(Compound([cane_ar, gril_ar, perc_ar, molla_ar, coppa_s_ar, coppa_i_ar, perno_cane, perno_gril,
                     tamburo, scudo, cartuccia]), os.path.join(OUT, "v2_assieme_armato.stl"))
for nome, s in pezzi.items():
    export_stl(s, os.path.join(OUT, f"v2_{nome}.stl"))
print(f"export: {os.path.relpath(OUT, os.getcwd())}/v2_assieme_*.stl (+ un STL per pezzo, prefisso v2_)")
