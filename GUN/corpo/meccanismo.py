# MECCANISMO A MOLLA VERTICALE NEL MANICO - cinematica e pezzi mobili (fonte unica).
#
# Questo file e' la MECCANICA/CINEMATICA del revolver, separata dal DESIGN estetico di build.py,
# allo stesso modo in cui meccanica.py e' la fonte delle quote di tamburo/canna/camere:
#   - meccanica.py  : quote di tamburo, canna, camere, finestra (parametri.py)
#   - meccanismo.py : (questo) perni, angoli armato/riposo, corsa e molla reale, profili e solidi
#                     dei pezzi mobili, inviluppi (vani) da togliere al telaio, verifiche delle pose
#   - build.py      : involucro, telaio, decori, guancette, montaggio, export
#
# Origine: concept_molla_verticale_final.py (vedi MECCANISMO.md). Le quote sono le stesse; i profili
# NON vengono piu' letti da concept_stl/final_profili.json ma ricalcolati qui dalle stesse formule
# (shapely, piano XZ di build.py: X asse canna, Z alto, Y laterale, y = 0 piano dei gusci, mm).
#
# Cosa chiede al telaio (build.py) e cosa gli da':
#   - riceve: il profilo laterale del telaio, il ponticello in 2D, la semi-larghezza locale della
#     guaina e la quota di cima del profilo (funzioni passate a vani_telaio());
#   - restituisce: vani_telaio() -> {larghezza Y: geometria XZ} da sottrarre al telaio,
#     solidi dei pezzi mobili A RIPOSO (cane(), grilletto(), ...), e i controlli delle pose.
# Le quote si cambiano QUI; build.py non contiene numeri del meccanismo.
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely import affinity  # noqa: E402
from shapely.geometry import LineString, Point, Polygon as SPoly, box as sbox  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

import meccanica as M  # noqa: E402

p, q = M.p, M.q
PARETE = p.parete_min                 # 1.6 mm
ZA = q.z_asse_tamb

# =====================================================================
# QUOTE CINEMATICHE
# =====================================================================
# --- scudo (battuta del cane) ---
T_SCUDO = 4.0                         # spessore dello scudo posteriore
X_SCUDO1 = q.x_cam - p.g_tamb         # 44.0 faccia anteriore dello scudo
X_SCUDO = X_SCUDO1 - T_SCUDO          # 40.0 retro dello scudo: battuta del cane a riposo
ZB = 0.0                              # quota dell'asse del percussore (= asse canna)

# --- cane ---
X_PERNO = 30.5                        # perno del cane: spina d'acciaio d3
Z_PERNO = -20.0
P = (X_PERNO, Z_PERNO)
D_PERNO = 3.0
R_MOZZO = 5.0
SP_CANE = 7.0                         # con 8 la parete verso la scanalatura di carica scende a 1.1 mm
ANG_ARMO = 30.0                       # rotazione da riposo ad armato [gradi]
CORSA_CODA = 10.35                    # = 2 x L_CODA x sin(15): compressione della molla data dal cane
R_CONT = 3.2                          # raggio della coda nel contatto con la coppa
Z_SPERONE = 21.5
ALLEGG = None                         # foro di alleggerimento (dx dal perno, z, raggio): tolto, vale +-5 cm di gittata (dinamica.py)

# --- percussore flottante (trascinato dalla forcella del cane) ---
D_SHANK = 2.6
D_COL, L_COL = 5.0, 2.0
T_LIP = 3.6                           # labbro della forcella: pelle >= 1.6 sulla faccia di battuta
S_PUSH = p.cart_fascia + 0.5 + 0.5    # quanto la punta entra nella camera a riposo
RITIRO_TIP = 0.3                      # da armato la punta sta 0.3 dietro la faccia dello scudo

# --- grilletto / dente di monta ---
R_NASO = 8.0
H_ENG = 1.2                           # aggancio del dente
GIOCO_SGANCIO = 0.3
L_NASO = 14.5
W_NASO = 2.5
SP_GRIL = 6.0
D_PERNO_G = 2.0                       # spina d'acciaio d2
R_MOZZO_G = 3.5
R_BRACCIO = 2.4
OFF_EXTRA = 0.6                       # luce in piu' fra braccio del grilletto e pattino

# --- rullino (perno di filamento 1.75 nella forcella del grilletto) ---
R_RULL = 3.5                          # d7
W_RULL = 2.4
R_FORC = 2.6
D_PERNO_R = 1.75

# --- sede molla nel manico ---
ANG_MOLLA = 32.0                      # asse della molla dalla verticale
D_SEDE = 9.2                          # canale QUADRO 9.2 x 9.2 (meta' in ogni guscio)
L_COPPA = 3.0
L_PIST = 6.0                          # pistone quadro 8.8: non ruota, tiene orientato il pattino
T_PAD = 2.0                           # pattino su cui rotola il rullino
D_PIST = D_SEDE - 0.4
GIOCO_VANO = 0.3                      # luce dei vani attorno agli inviluppi dei pezzi
R_PIATTO_COPPA, PEND_COPPA = 0.4, 0.32   # cima della coppa a cono (vedi coppa())

# --- MOLLA REALE: inox 304, filo 1.0, De 8, tagliata a L0 60 (20 spire a passo 3) ---
MOLLA_d, MOLLA_De, MOLLA_PASSO = 1.0, 8.0, 3.0
MOLLA_Dm = MOLLA_De - MOLLA_d
MOLLA_G = 68000.0                     # MPa
MOLLA_NM = 2.0                        # spire non attive (capi chiusi)
L0_TAGLIO = 60.0
MOLLA_SPIRE = round(L0_TAGLIO / MOLLA_PASSO)
L1_GEOM = 58.0                        # sede fra coppa e pistone SENZA distanziali, a riposo
SP_DIST = 4.0                         # distanziale nominale (scelto in concept_molla_verticale_final: 23.5 N armata)
L_MOLLA_RIP = L1_GEOM - SP_DIST       # molla montata a riposo: 54 mm

# --- larghezze dei vani nel telaio ---
SLOT_CANE = SP_CANE + p.gioco_rot     # 7.5
SLOT_GRIL = SP_GRIL + p.gioco_rot     # 6.5
D_PERC_FORO = D_SHANK + 0.3           # foro del percussore nello scudo
HW_MIN = SLOT_CANE / 2 + PARETE       # semi-larghezza minima del telaio attorno alla feritoia del cane

# =====================================================================
# MOLLA: modello
# =====================================================================
def variante(**quote):
    """Copia indipendente di questo modulo con alcune QUOTE CINEMATICHE cambiate, per gli studi
    (studio_cinematica.py): variante(ANG_ARMO=40, CORSA_CODA=9.6). Vale per le costanti scritte
    a inizio riga come `NOME = valore`. Il modulo vero non cambia: la configurazione ufficiale
    resta quella scritta in questo file."""
    import re
    import types
    src = open(os.path.abspath(__file__)).read()
    for nome, val in quote.items():
        src, n = re.subn(rf"(?m)^{nome} = [^#\n]*", lambda _m: f"{nome} = {val!r}  ", src, count=1)
        assert n == 1, f"quota non trovata: {nome}"
    mod = types.ModuleType("meccanismo_variante")
    mod.__file__ = os.path.abspath(__file__)
    exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    mod.QUOTE_VARIANTE = dict(quote)
    return mod


def k_molla(L0=L0_TAGLIO):
    na = L0 / MOLLA_PASSO - MOLLA_NM
    return MOLLA_G * MOLLA_d ** 4 / (8 * MOLLA_Dm ** 3 * na)


# =====================================================================
# UTILITA' 2D
# =====================================================================
U = (math.sin(math.radians(ANG_MOLLA)), math.cos(math.radians(ANG_MOLLA)))   # asse molla, verso l'alto
NF = (U[1], -U[0])                    # normale "in avanti" all'asse molla


def rot(pt, ang, c=P):
    a = math.radians(ang)
    dx, dz = pt[0] - c[0], pt[1] - c[1]
    return (c[0] + dx * math.cos(a) - dz * math.sin(a), c[1] + dx * math.sin(a) + dz * math.cos(a))


def rotg(g, ang, c):
    return affinity.rotate(g, ang, origin=c)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def poligoni(g):
    if g is None or g.is_empty:
        return []
    return [g] if g.geom_type == "Polygon" else [x for x in g.geoms if x.geom_type == "Polygon"]


def lungo_asse(o, t):
    """Punto a distanza t lungo -U (verso il calcio) dall'origine o."""
    return (o[0] - U[0] * t, o[1] - U[1] * t)


def banda_asse(o, t0, t1, r):
    return LineString([lungo_asse(o, t0), lungo_asse(o, t1)]).buffer(r, cap_style=2)


def sottili(g, t=PARETE, amin=1.0):
    """Zone del profilo 2D piu' sottili di t (apertura morfologica), trascurando gli spigoli (< amin mm^2)."""
    op = g.buffer(-t / 2, 16).buffer(t / 2, 16)
    return [c for c in poligoni(g.difference(op.buffer(0.02))) if c.area > amin]


# =====================================================================
# CINEMATICA
# =====================================================================
# --- cane: la coda comprime la molla lungo l'asse ---
L_CODA = CORSA_CODA / (2 * math.sin(math.radians(ANG_ARMO / 2)))
_n_perp = (-U[1], U[0])
if _n_perp[0] > 0:
    _n_perp = (-_n_perp[0], -_n_perp[1])
coda_mid = (P[0] + L_CODA * _n_perp[0], P[1] + L_CODA * _n_perp[1])
coda0 = rot(coda_mid, -ANG_ARMO / 2)


def comp_cane(th):
    """Compressione della molla [mm] data dal cane ruotato di th gradi da riposo."""
    c = rot(coda0, th)
    return -dot((c[0] - coda0[0], c[1] - coda0[1]), U)


def _su_asse(pt):
    t = dot((pt[0] - coda_mid[0], pt[1] - coda_mid[1]), U)
    return (coda_mid[0] + t * U[0], coda_mid[1] + t * U[1]), t


# --- percussore flottante ---
X_STOP = X_SCUDO - 0.05
TIP_S = q.x_cam + S_PUSH              # punta a riposo (entra nella camera: blocca il tamburo)
TIP_R = X_SCUDO1 - RITIRO_TIP         # punta da armato


def x_piano(x0, th):
    pt = rot((x0, ZB), th)
    a = math.radians(th)
    return pt[0] + (pt[1] - ZB) * math.tan(a)


G_LOST = x_piano(X_STOP, 0) - x_piano(X_STOP, ANG_ARMO) - (TIP_S - TIP_R)
X_FACE = X_STOP - T_LIP - G_LOST - L_COL
L_PERC = TIP_S - X_FACE
th_urto = ANG_ARMO
while x_piano(X_FACE, th_urto) < TIP_R - L_PERC and th_urto > 0:
    th_urto -= 0.01


def perc_2d(tip):
    col = sbox(tip - L_PERC, -D_COL / 2, tip - L_PERC + L_COL, D_COL / 2)
    sh = sbox(tip - L_PERC + L_COL - 0.01, -D_SHANK / 2, tip, D_SHANK / 2)
    return col, sh


def tip_armamento(th):
    return min(TIP_S, x_piano(X_STOP - T_LIP, th) + (L_PERC - L_COL))


# --- grilletto ---
N0 = (P[0], P[1] - R_NASO)
PT = (N0[0] - L_NASO, N0[1])          # perno del grilletto (16, -28)
PHI_CAMMA = -math.degrees(H_ENG / L_NASO)                  # a riposo: naso sul cerchio della camma
PHI_SGANCIO = -math.degrees((H_ENG + GIOCO_SGANCIO) / L_NASO)
PHI_FINE = PHI_SGANCIO - 1.0                               # grilletto a fondo
R_CAMMA = R_NASO + H_ENG
W_CAMMA = ANG_ARMO + 14.0
_settore = [P] + [(P[0] + R_CAMMA * math.cos(math.radians(-90.0 + W_CAMMA * i / 16)),
                   P[1] + R_CAMMA * math.sin(math.radians(-90.0 + W_CAMMA * i / 16))) for i in range(17)]
camma0 = rotg(SPoly(_settore).buffer(0), -ANG_ARMO, P)

# --- asse molla, coppa, pistone, rullino ---
CIMA0, _ = _su_asse((coda0[0] - U[0] * R_CONT, coda0[1] - U[1] * R_CONT))   # contatto coda/coppa a riposo
T_PIST0 = L_COPPA + L1_GEOM           # cima del pistone (senza distanziali), a riposo
T_PAD1 = T_PIST0 + L_PIST + T_PAD     # faccia inferiore del pattino
T_BC = T_PAD1 + R_RULL                # centro del rullino a riposo
BC_RIP = lungo_asse(CIMA0, T_BC)
BC0 = rot(BC_RIP, -PHI_CAMMA, PT)     # centro del rullino col grilletto a phi = 0


def comp_gril(phi):
    """Compressione della molla [mm] data dal grilletto (rullino sul pattino) a phi gradi."""
    c = rot(BC0, phi, PT)
    return dot((c[0] - BC_RIP[0], c[1] - BC_RIP[1]), U)


def lat_naso(phi):
    c = rot(BC0, phi, PT)
    return dot((c[0] - CIMA0[0], c[1] - CIMA0[1]), NF)


_LAT = [lat_naso(PHI_FINE + (0.0 - PHI_FINE) * i / 20) for i in range(21)]
LAT_MIN, LAT_MAX = min(_LAT), max(_LAT)
CORSA_CANE = comp_cane(ANG_ARMO)      # ~10.35 mm: corsa utile della molla
CORSA_GRIL = comp_gril(PHI_FINE)


def forza_molla(th=0.0, phi=PHI_CAMMA, k=None):
    """Forza della molla [N] nella posa (th, phi), distanziale nominale."""
    k = k_molla() if k is None else k
    return k * (L0_TAGLIO - (L_MOLLA_RIP - comp_cane(th) - comp_gril(phi) + comp_gril(PHI_CAMMA)))


# =====================================================================
# PROFILI 2D DEI PEZZI MOBILI
# =====================================================================
P0, P1 = P
_braccio_cane = SPoly([
    (X_STOP, ZB - 5.5), (X_STOP, ZB + 5.0), (X_STOP - 1.5, ZB + 9.0),
    # cresta e sperone (solo forma, la cinematica non li usa): come nella reference il collo sale
    # stretto e lo sperone gira all'indietro ad arco, scendendo in punta (a virgola). Da armato la
    # punta resta in aria dietro la gobba del telaio.
    (P0 + 6.0, 13.5), (P0 + 4.2, 17.5), (P0 + 1.2, Z_SPERONE - 1.2), (P0 - 2.8, Z_SPERONE - 0.2),
    (P0 - 7.2, Z_SPERONE - 0.9), (P0 - 11.2, Z_SPERONE - 2.7), (P0 - 13.6, Z_SPERONE - 4.8),
    (P0 - 13.9, Z_SPERONE - 6.4), (P0 - 12.6, Z_SPERONE - 7.4), (P0 - 10.4, Z_SPERONE - 6.8),
    (P0 - 7.0, Z_SPERONE - 5.5), (P0 - 3.6, Z_SPERONE - 5.6), (P0 - 1.6, Z_SPERONE - 7.4),
    (P0 - 1.1, ZB + 12.0), (P0 - 1.9, ZB + 9.0),
    (X_FACE - 3.0, ZB + 6.5),
    (P0 - R_MOZZO * 0.9, P1 + 2), (P0 + R_MOZZO * 0.9, P1 - 2),
])
SPERONE = (P0 - 9.0, Z_SPERONE - 2.0)     # dove preme il pollice (per la forza di armamento)
_coda_g = LineString([P, coda0]).buffer(R_CONT, 16)
TH_ALL = [ANG_ARMO * i / 26 for i in range(27)]

# tasca del collare e feritoia del gambo del percussore nella forcella del cane (inviluppo dell'armamento)
_fer_col = []
for _th in TH_ALL:
    for _tip in {tip_armamento(_th), TIP_S if _th == 0 else tip_armamento(_th),
                 TIP_R if _th >= th_urto else tip_armamento(_th)}:
        _fer_col.append(rotg(perc_2d(_tip)[0].buffer(0.2), -_th, P))
for _i in range(11):
    _th = th_urto * _i / 10
    _fer_col.append(rotg(perc_2d(x_piano(X_FACE, _th) + L_PERC)[0].buffer(0.2), -_th, P))
fer_col = unary_union(_fer_col)
fer_sh = unary_union([rotg(perc_2d(tip_armamento(th))[1].buffer(0.2), -th, P) for th in TH_ALL] +
                     [rotg(perc_2d(x_piano(X_FACE, th_urto * i / 10) + L_PERC)[1].buffer(0.2), -th_urto * i / 10, P)
                      for i in range(11)])
W_FER_SH = D_SHANK + 0.4              # larghezza della feritoia del gambo nella forcella

cane2d_pieno = _braccio_cane.union(Point(P).buffer(R_MOZZO, 32)).union(_coda_g).union(camma0).simplify(0.03)
if ALLEGG:
    cane2d_pieno = cane2d_pieno.difference(Point(P0 + ALLEGG[0], ALLEGG[1]).buffer(ALLEGG[2], 24))
cane2d = cane2d_pieno.difference(fer_col)            # cane a riposo, con la tasca del collare

_naso = sbox(N0[0] - W_NASO - 0.05, N0[1] - 2.6, N0[0] - 0.1, N0[1])
_braccio_naso = sbox(PT[0], N0[1] - 3.4, N0[0] - W_NASO + 0.5, N0[1] - 1.6)
_lama = unary_union([
    LineString([PT, (29.0, -32.5)]).buffer(2.2, 16),
    SPoly([(27.0, -31.5), (32.0, -31.5), (36.0, -37.0), (37.2, -44.0), (36.3, -50.0), (34.2, -54.0),
           (32.4, -53.2), (33.2, -47.5), (32.3, -41.0), (29.0, -35.5)]),
])
# braccio nel manico: scende DAVANTI alla molla e porta la forcella del rullino sotto il pattino
OFF_K = max(D_SEDE / 2, LAT_MAX + 1.6) + R_BRACCIO + 0.8 + max(0.0, -LAT_MIN) + OFF_EXTRA
_K_rip = (BC_RIP[0] + NF[0] * OFF_K, BC_RIP[1] + NF[1] * OFF_K)
_K_alto = lungo_asse((CIMA0[0] + NF[0] * OFF_K, CIMA0[1] + NF[1] * OFF_K), T_PIST0 - 4.0)
_braccio_rip = LineString([PT, _K_alto, _K_rip, BC_RIP]).buffer(R_BRACCIO, 16, join_style=1)
_braccio_g = rotg(_braccio_rip, -PHI_CAMMA, PT).union(Point(BC0).buffer(R_FORC, 24))
gril2d = unary_union([Point(PT).buffer(R_MOZZO_G, 24), _naso, _braccio_naso, _lama, _braccio_g]).simplify(0.03)
gril2d = gril2d.difference(Point(PT).buffer(D_PERNO_G / 2 + 0.15, 16))     # definito a phi = 0
gril2d_netto = gril2d.difference(Point(BC0).buffer((D_PERNO_R + 0.15) / 2, 16))
rull2d = Point(BC0).buffer(R_RULL, 32).difference(Point(BC0).buffer((D_PERNO_R + 0.25) / 2, 16))


def cane_pose(th, netto=True):
    return rotg(cane2d if netto else cane2d_pieno, th, P)


def gril_pose(phi):
    return rotg(gril2d, phi, PT)


def rull_pose(phi):
    return rotg(rull2d, phi, PT)


def pistone_2d(dt=0.0):
    """Pistone quadro + pattino; dt = spostamento lungo -U (compressione data dal grilletto: dt < 0)."""
    o = lungo_asse(CIMA0, dt)
    cil = banda_asse(o, T_PIST0, T_PIST0 + L_PIST + 0.05, D_PIST / 2)
    a, b = LAT_MIN - 1.6 - 0.5, LAT_MAX + 1.6 + 0.5
    c0, c1 = lungo_asse(o, T_PIST0 + L_PIST), lungo_asse(o, T_PAD1)
    pad = SPoly([(c0[0] + NF[0] * a, c0[1] + NF[1] * a), (c0[0] + NF[0] * b, c0[1] + NF[1] * b),
                 (c1[0] + NF[0] * b, c1[1] + NF[1] * b), (c1[0] + NF[0] * a, c1[1] + NF[1] * a)])
    return cil.union(pad)


def molla_2d(L, De, dt_cima=0.0):
    return banda_asse(lungo_asse(CIMA0, dt_cima), L_COPPA, L_COPPA + L, De / 2)


# =====================================================================
# INVILUPPI (vani nel telaio)
# =====================================================================
PHI_ALL = [PHI_FINE - 0.5 + (0.5 - PHI_FINE + 0.5) * i / 14 for i in range(15)]
sweep_cane = unary_union([cane_pose(th, netto=False) for th in TH_ALL])
sweep_gril = unary_union([gril_pose(f) for f in PHI_ALL] + [rull_pose(f) for f in PHI_ALL])
_cg = [comp_gril(f) for f in PHI_ALL]
sweep_pist = unary_union([pistone_2d(-min(_cg)), pistone_2d(-max(_cg)), pistone_2d(0.0)])
vano_cane = sweep_cane.buffer(GIOCO_VANO)
vano_gril = sweep_gril.buffer(GIOCO_VANO)
# sede: canale quadro dalla cima (1 mm sopra il contatto della coda) fino sotto il pistone + corsa del pattino
vano_molla = unary_union([banda_asse(CIMA0, -1.0, T_PIST0 + L_PIST + 0.5, D_SEDE / 2), sweep_pist.buffer(GIOCO_VANO)])
foro_pc = Point(P).buffer(D_PERNO / 2, 24)
foro_pg = Point(PT).buffer(D_PERNO_G / 2, 24)
X_CANE_BAND = vano_cane.intersection(sbox(-50, ZA - p.tamb_asse_d / 2 - 0.5, 200, ZA + p.tamb_asse_d / 2 + 0.5)).bounds[2]
X_PERNO_TAMB = round(X_CANE_BAND + 0.4, 1)   # il perno del tamburo parte davanti alla feritoia del cane
X_FORO_TAMB = round(X_CANE_BAND - 0.5, 1)    # il suo foro sbuca nella feritoia (niente setto sottile)


# =====================================================================
# INTERFACCIA COL DESIGN: tutto quello che l'involucro (profili.py, build.py) deve sapere
# =====================================================================
# Il design NON legge altre quote da qui: prende questi ingombri, gli assi e i perni, e ci
# costruisce attorno la sagoma. Se la cinematica cambia, questi cambiano e la sagoma li segue.
#   INGOMBRO_CHIUSO     : cio' che deve stare DENTRO il telaio con parete attorno (sede molla,
#                         braccio e mozzo del grilletto, rullino, mozzo/coda/camma del cane in tutte le pose)
#   INGOMBRO_PERCUSSORE : corsa del percussore dietro lo scudo (conviene coprirla con le guance)
#   vano_molla          : la sede della molla (la sua cima e' dove sta la gobba del telaio)
#   vano_cane           : inviluppo del cane intero; la parte alta (cresta, sperone) esce dal dorso
#   VANO_LAMA           : inviluppo della lama del grilletto, che esce sotto il telaio nel ponticello
#   CIMA0, U, NF        : origine e direzioni dell'asse della molla = asse naturale del manico
#   P, PT, PERNI_SPINA  : perni di cane e grilletto (teste delle spine a vista sui fianchi)
#   X_SCUDO, X_SCUDO1, T_SCUDO, SLOT_CANE, SLOT_GRIL, D_PERC_FORO, X_PERNO_TAMB, X_FORO_TAMB
_chiuso_cane = unary_union([Point(P).buffer(R_MOZZO, 32), _coda_g, camma0])
_interno_gril = unary_union([Point(PT).buffer(R_MOZZO_G, 24), _naso, _braccio_naso, _braccio_g])
INGOMBRO_CHIUSO = unary_union(
    [vano_molla]
    + [rotg(_chiuso_cane, th, P).buffer(GIOCO_VANO) for th in TH_ALL]
    + [rotg(_interno_gril, f, PT).buffer(GIOCO_VANO) for f in PHI_ALL]
    + [rull_pose(f).buffer(GIOCO_VANO) for f in PHI_ALL])
INGOMBRO_PERCUSSORE = sbox(tip_armamento(ANG_ARMO) - L_PERC - GIOCO_VANO, ZB - D_COL / 2 - GIOCO_VANO,
                           X_SCUDO, ZB + D_COL / 2 + GIOCO_VANO)
VANO_LAMA = unary_union([rotg(_lama, f, PT) for f in PHI_ALL]).buffer(GIOCO_VANO)


def vani_telaio(tel, ponticello, vano_pont, semi_larghezza, z_cima, w_telaio):
    """Vani del meccanismo da togliere al telaio: {larghezza Y: geometria XZ (shapely)}.

    tel: profilo laterale del telaio (shapely); ponticello / vano_pont: anello del ponticello e il
    suo foro in 2D; semi_larghezza(x, z): semi-larghezza Y della guaina; z_cima(x): quota piu' alta
    del profilo; w_telaio: larghezza piena del telaio. Ogni vano e' un prisma simmetrico in Y; i vani della stessa larghezza sono gia' uniti.
    """
    finestra = sbox(q.x_cam - p.g_tamb, ZA - q.finestra_R, q.x_cam - p.g_tamb + q.finestra_L, ZA + q.finestra_R)
    # (+0.03: il raccordo fra feritoia del cane e foro dell'asse entra di 0.03 nel foro vero; a filo
    #  le facce coincidono e il booleano lascia una cavita' chiusa nel telaio)
    foro_tamb = sbox(X_FORO_TAMB + 0.03, ZA - (p.tamb_asse_d + p.gioco_rot) / 2, 200, ZA + (p.tamb_asse_d + p.gioco_rot) / 2)
    foro_perc = sbox(X_SCUDO - 0.1, -D_PERC_FORO / 2, X_SCUDO1 + 0.1, D_PERC_FORO / 2)

    # spianatura della cresta sopra la feritoia del cane: dove la guaina e' piu' stretta di feritoia +
    # 2 pareti le guance finirebbero a lama: la' la feritoia si allarga a 2 HW_MIN (piano come un top strap)
    qs = []
    gc = vano_cane.intersection(tel)
    x = math.floor(gc.bounds[0])
    while x <= gc.bounds[2]:
        zc = z_cima(x)
        z = math.floor(gc.bounds[1])
        while zc is not None and z <= zc + 0.5:
            if gc.buffer(0.3).contains(Point(x, z)) and semi_larghezza(x, z) < HW_MIN:
                qs.append(sbox(x - 0.5, z - 0.25, x + 0.5, z + 0.25))
            z += 0.25
        x += 0.5
    spianatura = unary_union(qs).buffer(0.25).intersection(tel) if qs else None

    # setti < PARETE fra due vani: si fondono nel vano piu' stretto
    vani = [("cane", vano_cane, SLOT_CANE), ("grilletto", vano_gril, SLOT_GRIL), ("molla", vano_molla, D_SEDE),
            ("foro perno cane", foro_pc, w_telaio), ("foro perno grilletto", foro_pg, w_telaio),
            ("foro asse tamburo", foro_tamb, p.tamb_asse_d + p.gioco_rot), ("finestra tamburo", finestra, w_telaio),
            ("foro percussore", foro_perc, D_PERC_FORO)]
    if spianatura is not None and not spianatura.is_empty:
        vani.append(("spianatura cresta", spianatura, 2 * HW_MIN))
    raccordi = []
    for i in range(len(vani)):
        for j in range(i + 1, len(vani)):
            ni, gi, wi = vani[i]
            nj, gj, wj = vani[j]
            if gi.distance(gj) >= PARETE or (ni.startswith("foro perno") and nj in ("cane", "grilletto")):
                continue
            u_ = gi.union(gj)
            chiuso = u_.buffer(PARETE / 2 + 0.05, 16).buffer(-(PARETE / 2 + 0.05), 16)
            sl = chiuso.difference(u_).intersection(gi.buffer(PARETE + 0.1)).intersection(gj.buffer(PARETE + 0.1))
            if sl.area > 0.01:
                raccordi.append((sl, min(wi, wj)))
    # lingue sottili di materiale fra due vani (non sul bordo esterno): si fondono anch'esse
    tel_mat = tel.union(ponticello)
    apert = unary_union([vano_cane.difference(tel).buffer(1.2), vano_gril.intersection(vano_pont.buffer(1.0)).buffer(1.2),
                         vano_gril.difference(tel_mat).buffer(1.2)])
    vt = unary_union([v for _, v, _ in vani] + [r for r, _ in raccordi] + [vano_pont])
    mat = tel_mat.difference(vt).intersection(sbox(-40, -95, X_SCUDO1 + 2, 30))
    for c in sottili(mat):
        if c.distance(tel.exterior) > 0.3 and c.difference(apert).area > 0.5:
            w_ = min([w for _, v, w in vani if v.distance(c) < 0.05] or [SLOT_GRIL])
            raccordi.append((c.buffer(0.1), w_))

    out = {}

    def agg(g, w):
        w = round(w, 3)
        out[w] = g if w not in out else out[w].union(g)

    agg(vano_cane, SLOT_CANE)
    agg(vano_gril, SLOT_GRIL)
    agg(vano_molla, D_SEDE)
    if spianatura is not None and not spianatura.is_empty:
        # la spianatura e' tagliata esattamente sul bordo del telaio (facce coincidenti: il booleano
        # fallisce): la si prolunga di 4 mm in su, nell'aria sopra il telaio
        su = unary_union([affinity.translate(spianatura, 0, 0.25 * k) for k in range(17)]).simplify(0.01)
        assert su.intersection(tel).difference(spianatura.buffer(0.02)).area < 0.05, "spianatura: il prolungamento entra nel telaio"
        agg(su, 2 * HW_MIN)
    # Si saltano le schegge che il 2D vede alle imboccature dei FORI tondi (percussore, asse tamburo):
    # nel piano y = 0 il foro e' una fascia e accanto restano quadratini di ~0.85 mm che in 3D non sono
    # setti (il foro e' tondo) e, tagliati, lasciano T-junction nella mesh STL.
    fori_tondi = [(0.0, D_PERC_FORO / 2), (ZA, (p.tamb_asse_d + p.gioco_rot) / 2)]

    def scheggia_di_foro(pg):
        xs, zs = [v[0] for v in pg.exterior.coords], [v[1] for v in pg.exterior.coords]
        return min(xs) >= X_FORO_TAMB - 0.1 and any(
            r - 0.1 <= min(abs(z - zc) for z in zs) and max(abs(z - zc) for z in zs) <= r + 1.15
            and (min(zs) - zc) * (max(zs) - zc) > 0 for zc, r in fori_tondi)
    for g, w in raccordi:
        pgs = [pg for pg in poligoni(g) if pg.area > 1e-3 and not scheggia_di_foro(pg)]
        if pgs:
            agg(unary_union(pgs), w)
    # apertura + chiusura morfologica: toglie aghi e fessure < 0.06 mm nate dalle unioni (T-junction)
    eps = 0.03
    return {w: g.buffer(-eps).buffer(2 * eps).buffer(-eps).simplify(0.005) for w, g in sorted(out.items())}


# =====================================================================
# SOLIDI (build123d) DEI PEZZI MOBILI, tutti A RIPOSO
# =====================================================================
def estrudi(g, larghezza):
    """Prisma simmetrico in Y (piano dei gusci) dalla geometria XZ shapely g."""
    from build123d import Plane, Polygon, extrude
    s = None
    for pg in poligoni(g):
        if pg.area < 1e-3:
            continue                 # schegge degeneri
        f = extrude(Plane.XZ * Polygon(*list(pg.exterior.coords)[:-1], align=None), amount=larghezza / 2, both=True)
        for h in pg.interiors:
            f -= extrude(Plane.XZ * Polygon(*list(h.coords)[:-1], align=None), amount=50, both=True)
        s = f if s is None else s + f
    return s


def _cil_y(c, d, L):
    from build123d import Cylinder, Pos, Rot
    return Pos(c[0], 0, c[1]) * Rot(90, 0, 0) * Cylinder(d / 2, L)


def cil_lungo_u(d, base, L):
    """Cilindro d x L sull'asse della molla, da base verso l'alto."""
    from build123d import Align, Cylinder, Pos, Rot
    return Pos(base[0], 0, base[1]) * Rot(0, ANG_MOLLA, 0) * \
        Cylinder(d / 2, L, align=(Align.CENTER, Align.CENTER, Align.MIN))


def cane():
    """Cane imperniato (spina d3), coda che comprime la molla, forcella del percussore, unghiatura."""
    from build123d import Box, Pos, Rot
    s = estrudi(cane2d, SP_CANE) - estrudi(fer_sh, W_FER_SH) - _cil_y(P, D_PERNO + 0.3, 10)
    # unghiatura: solchi sul dorso dello sperone (dove appoggia il pollice), profondi 0.6
    a, b = (P0 - 6.2, Z_SPERONE - 0.75), (P0 - 11.4, Z_SPERONE - 3.3)
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    for t in (0.0, 0.33, 0.66, 1.0):
        gx, gz = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        s -= Pos(gx, 0, gz) * Rot(0, -ang, 0) * Box(0.8, 10, 1.2)
    return s


def grilletto():
    """Grilletto imperniato (spina d2) a riposo: naso sulla camma, lama, braccio con la forcella del rullino."""
    s = estrudi(rotg(gril2d_netto, PHI_CAMMA, PT), SP_GRIL)
    s -= _cil_y(BC_RIP, 2 * (R_RULL + 0.5), W_RULL + 0.2)          # gola della forcella
    s -= _cil_y(BC_RIP, D_PERNO_R + 0.15, 8)                        # foro d1.90 del perno
    return s


def rullino():
    return _cil_y(BC_RIP, 2 * R_RULL, W_RULL) - _cil_y(BC_RIP, D_PERNO_R + 0.25, W_RULL + 1)


def perno_rullino():
    """Perno di filamento PLA 1.75 (riferimento, non si stampa)."""
    return _cil_y(BC_RIP, D_PERNO_R, SP_GRIL - 0.2)


def percussore():
    """Percussore flottante a riposo (collare d5 x 2, gambo d2.6): la punta blocca il tamburo."""
    return M._cil_x(D_COL, TIP_S - L_PERC, L_COL, z=ZB) + \
        M._cil_x(D_SHANK, TIP_S - L_PERC + L_COL - 0.01, L_PERC - L_COL + 0.01, z=ZB)


# basi lungo l'asse a riposo
B_COPPA = lungo_asse(CIMA0, L_COPPA)          # base della coppa = cima della molla
B_MOLLA = lungo_asse(B_COPPA, L_MOLLA_RIP)    # base della molla = cima del distanziale


def coppa():
    """Coppa d8.6 x 3 con la cima a cono: a riposo il fianco della coda del cane scende sotto il piano
    della coppa (0.27 mm/mm verso il davanti); piatto r 0.4, poi -0.32 mm/mm."""
    from build123d import Align, Cone, Cylinder, Pos, Rot
    r_c = (MOLLA_De + 0.6) / 2
    h_cono = PEND_COPPA * (r_c - R_PIATTO_COPPA)
    al = (Align.CENTER, Align.CENTER, Align.MIN)
    return Pos(B_COPPA[0], 0, B_COPPA[1]) * Rot(0, ANG_MOLLA, 0) * (
        Cylinder(r_c, L_COPPA - h_cono, align=al)
        + Pos(0, 0, L_COPPA - h_cono) * Cone(r_c, R_PIATTO_COPPA, h_cono, align=al))


def distanziale():
    return cil_lungo_u(D_PIST, lungo_asse(B_MOLLA, SP_DIST), SP_DIST - 0.02)


def pistone():
    """Pistone quadro 8.8 + pattino del rullino, a riposo."""
    return estrudi(pistone_2d(), D_PIST)


def molla():
    """Molla vera (elica di filo d1) a riposo (riferimento, acciaio)."""
    from build123d import Circle, Helix, Plane, Pos, Rot, sweep
    try:
        el = Helix(pitch=L_MOLLA_RIP / MOLLA_SPIRE, height=L_MOLLA_RIP, radius=MOLLA_Dm / 2)
        prof = Plane(origin=el @ 0, z_dir=el % 0) * Circle(MOLLA_d / 2)
        return Pos(B_MOLLA[0], 0, B_MOLLA[1]) * Rot(0, ANG_MOLLA, 0) * sweep(prof, path=el)
    except Exception as err:
        print("elica della molla non riuscita, tubo al suo posto:", err)
        return cil_lungo_u(MOLLA_De, B_MOLLA, L_MOLLA_RIP) - cil_lungo_u(MOLLA_De - 2 * MOLLA_d, B_MOLLA, L_MOLLA_RIP)


def spina_cane(L):
    return _cil_y(P, D_PERNO, L)


def spina_grilletto(L):
    return _cil_y(PT, D_PERNO_G, L)


def foro_spine():
    """Fori nominali delle spine d'acciaio nel telaio (la spina entra a leggera interferenza)."""
    return _cil_y(P, D_PERNO, 60) + _cil_y(PT, D_PERNO_G, 60)


PERNI_SPINA = {P: D_PERNO, PT: D_PERNO_G}     # centro XZ -> diametro (teste finte forate in build.py)


# =====================================================================
# VERIFICHE DELLE POSE (2D nel piano y = 0: tutti i pezzi stanno sul piano dei gusci)
# =====================================================================
def verifica_pose():
    """Interferenze [mm^2] / luci [mm] fra i pezzi mobili in tutte le pose di armamento e scatto."""
    r = {}
    r["cane/grilletto armamento"] = max(cane_pose(th).buffer(-0.02).intersection(gril_pose(PHI_CAMMA)).area
                                        for th in TH_ALL[:-1])
    r["cane/grilletto armato"] = cane_pose(ANG_ARMO).buffer(-0.02).intersection(gril_pose(0.0)).area
    r["cane/grilletto riposo"] = cane_pose(0.0).buffer(-0.02).intersection(gril_pose(PHI_CAMMA)).area
    r["cane/grilletto scatto"] = max(cane_pose(th).intersection(gril_pose(PHI_FINE)).area for th in TH_ALL)
    r["rullino/pattino (contatto)"] = max(rull_pose(f).buffer(-0.02).intersection(pistone_2d(-comp_gril(f))).area
                                          for f in PHI_ALL)
    r["luce grilletto/pistone [mm]"] = min(
        gril_pose(f).difference(Point(rot(BC0, f, PT)).buffer(R_FORC + 0.01)).distance(pistone_2d(-comp_gril(f)))
        for f in PHI_ALL)
    r["luce cane/coppa+molla [mm]"] = min(
        cane_pose(th).difference(rotg(_coda_g, th, P).buffer(0.01)).distance(
            molla_2d(L_MOLLA_RIP - comp_cane(th), MOLLA_De + 0.6, comp_cane(th))) for th in TH_ALL)
    return r
