# CONCEPT ESPLORATIVO - cane imperniato + molla verticale nell'impugnatura.
#
# Esperimento: NON e' il corpo corrente, non tocca build.py/meccanica.py.
# Modella solo lo SCHEMA cinematico: cane (armato e scattato), perno, molla
# nell'impugnatura, punta del cane sul fondo della cartuccia. Le quote di
# tamburo/scudo/molla arrivano da meccanica.py (parametri.py -> params.scad);
# il profilo dell'impugnatura si legge da build.py via AST (senza eseguirlo).
#
# Sistema: X = asse canna, Z = alto, asse canna z = 0, mm.
# Rotazioni nel piano XZ: angolo positivo = antiorario visto da +Y verso
# l'origine con X a destra e Z in alto (= il cane va INDIETRO, si arma).
#
# ---------------------------------------------------------------------
# RISULTATI (valori con i parametri di default; il file li ristampa):
#
#  0. ATTENZIONE, il bersaglio richiesto (x 44.3, z -12.45) NON e' il fondo
#     di una cartuccia: z = -12.45 e' l'ASSE del tamburo (perno d6). La camera
#     in linea con la canna sta a z = 0 (asse tamburo + r_passo 12.45). La
#     punta qui mira a (44.3, 0); la distanza dal punto richiesto e' stampata.
#  1. Angolo di rotazione armato -> scattato: 26 gradi, perno in (35, -20),
#     6 mm dietro lo scudo (mozzo R5 fino a x=40, scudo da x=41).
#  2. Punta da scattato: x = 44.30 a z = 0.00, distanza residua 0.00 mm
#     (misurata sul solido, compenetrazione con cartuccia/tamburo 0 mm^3).
#     Raggio punta 22 mm: arriva ad arco con 25 gradi d'inclinazione, il foro
#     nello scudo va fatto ad asola (~3.1 x 5.2). Da armato la punta e' 6.4 mm
#     dietro lo scudo: il tamburo puo' ruotare. Dal punto richiesto
#     (44.3, -12.45) la punta dista 12.45 mm: e' proprio la differenza di quota.
#  3. Il canale dietro lo scudo (x 0 -> 41) sparisce tutto. Ingombro interno
#     piu' arretrato x ~ 12: il dorso del telaio puo' finire a x ~ 8 invece di
#     x = -28 (gobba attuale), cioe' -36 mm in alto. MA la lunghezza totale
#     (~143 mm) la fa il tallone dell'impugnatura (x ~ -35): se l'impugnatura
#     resta dov'e' (davanti c'e' il grilletto) la pistola NON si accorcia.
#  4. Molla attuale (De 5, L0 29) parallela all'impugnatura (20 gradi): L2 = 18
#     ad armato (pacco + margine 17.1, ok). Foro d6 lungo 34 mm: ci sta senza
#     forare, parete minima residua 8.5 mm. Con questa leva la molla resta nel
#     raccordo tra telaio e impugnatura; sotto restano ~64 mm di manico liberi.
#  5. Leva della coda 19.5 mm, compressione 9.0 mm -> 55.6 mJ immagazzinati,
#     uguali a oggi. Pollice sullo sperone ~6 N. Ma il cane pesa ~4 g (massa
#     efficace alla punta ~3 g contro una cartuccia di ~1 g): all'urto (e = 0.4)
#     passa alla cartuccia solo ~36%, cioe' ~20 mJ. Il percussore di oggi
#     invece spinge per 8.2 mm restando a contatto.
#
#  DOVE SI ROMPE (vedi riassunto a fine esecuzione):
#   - il perno del tamburo oggi sporge 12 mm dietro il tamburo (x 32.3) ed
#     e' proprio dove passa il braccio del cane: va accorciato fino allo scudo;
#   - la punta del cane va solo a CONTATTO: non puo' spingere la cartuccia per
#     8 mm dentro la camera come fa il percussore (spinta_c) perche' si muove
#     ad arco. Serve un percussore flottante corto nello scudo.
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

from build123d import Align, Box, Compound, Cylinder, Pos, Rot, export_stl  # noqa: E402
from shapely.geometry import LineString, Point, Polygon as SPoly  # noqa: E402
from shapely import affinity  # noqa: E402

import meccanica as M  # noqa: E402
from concetti import profilo  # noqa: E402

p, q = M.p, M.q
_C, _MIN = Align.CENTER, Align.MIN
QUI = os.path.dirname(os.path.abspath(__file__))

# =====================================================================
# PARAMETRI DEL CONCEPT
# =====================================================================
# bersaglio: fondo della cartuccia nella camera allineata alla canna
X_BERSAGLIO = q.x_cam                    # 44.3: faccia posteriore del tamburo
Z_BERSAGLIO = q.z_asse_tamb + q.r_passo  # 0.0: camera in alto = asse canna
Z_RICHIESTO = q.z_asse_tamb              # -12.45: quota scritta nel brief (asse tamburo!)
X_SCUDO = q.x_sc                         # 41: retro dello scudo (resta: ci appoggia la cartuccia)

# perno del cane: subito dietro lo scudo, sotto la canna
X_PERNO, Z_PERNO = 35.0, -20.0
D_PERNO = 3.0                # vite/perno acciaio M3 (la molla e' troppo forte per il filamento)
R_MOZZO = 5.0                # mozzo del cane attorno al perno (35+5 = 40 < scudo 41)
W_TELAIO = 22.0              # larghezza telaio (il perno lo attraversa)

# cane
SP_CANE = 8.0                # spessore (come build.py)
L_NASO = 3.5                 # naso che attraversa lo scudo (3 mm) + gioco 0.3 + 0.2
D_NASO = 2.6
ANG_ARMO = 26.0              # rotazione armato -> scattato [gradi]
CORSA_MOLLA = 9.0            # compressione in piu' della molla ad armato (= corsa attuale)

# molla: la stessa dell'attuale (De 5, filo 0.6, L0 29) da meccanica.py
PRECARICO = p.precarico      # 2 mm a cane abbattuto
L_COPPA = 4.0                # coppa/puntone tra coda del cane e molla
T_FONDO = 3.0                # tappo a vite sotto la molla
D_SEDE = p.molla_De + 1.0    # foro della molla nell'impugnatura

# stime per l'energia
RHO_PLA = 1.24e-3 * 0.85     # g/mm^3, pezzo stampato pieno-ish (pareti + 50% riempimento)
M_CART = 1.0                 # g, cartuccia intera in PLA (stima)
E_REST = 0.4                 # coefficiente di restituzione PLA-PLA (stima grossolana)

# impugnatura: spostamento in avanti rispetto a build.py (0 = dove e' oggi)
DX_IMP = 0.0
# parete minima di materiale attorno al canale della molla
PARETE = p.parete_min

OUT = os.path.join(QUI, "concept_stl")


# =====================================================================
# IMPUGNATURA: si legge da build.py senza eseguirlo (solo costanti e
# funzioni del profilo, niente geometria build123d)
# =====================================================================
def _impugnatura_da_build():
    src = open(os.path.join(QUI, "build.py")).read()
    albero = ast.parse(src)
    servono = {"ANG_IMP", "X_IMP0", "Z_IMP0", "L_IMP", "F_IMP", "B_IMP", "PANCIA",
               "PICCO_PANCIA", "H_TALL", "R_PUNTA", "R_TALL", "CONC_DITA", "PICCO_CONC",
               "R_MIN", "N_IMP", "N_ARCO", "_a", "_dir", "_nrm", "X_DORSO0", "Z_DORSO0"}
    funzioni = {"imp_xz", "dorso", "arco_imp", "profilo_imp"}
    corpo = []
    for nodo in albero.body:
        if isinstance(nodo, ast.Assign):
            nomi = set()
            for t in nodo.targets:
                nomi |= {n.id for n in ast.walk(t) if isinstance(n, ast.Name)}
            if nomi & servono:
                corpo.append(nodo)
        elif isinstance(nodo, ast.FunctionDef) and nodo.name in funzioni:
            corpo.append(nodo)
    ns = {"math": math}
    exec(compile(ast.Module(body=corpo, type_ignores=[]), "build.py", "exec"), ns)
    return ns


B = _impugnatura_da_build()
U_MOLLA = (-B["_dir"][0], -B["_dir"][1])   # asse impugnatura verso l'alto (la molla spinge cosi')
grip = affinity.translate(SPoly(B["profilo_imp"]()).buffer(0), xoff=DX_IMP)


# =====================================================================
# CINEMATICA 2D (piano XZ)
# =====================================================================
P = (X_PERNO, Z_PERNO)


def rot(pt, ang, c=P):
    """Ruota pt di ang gradi (antiorario = verso l'armamento) attorno a c."""
    a = math.radians(ang)
    dx, dz = pt[0] - c[0], pt[1] - c[1]
    return (c[0] + dx * math.cos(a) - dz * math.sin(a), c[1] + dx * math.sin(a) + dz * math.cos(a))


# coda: a meta' rotazione e' perpendicolare all'asse molla, cosi' la corda
# dell'arco (= compressione) e' quasi tutta lungo la molla
L_CODA = CORSA_MOLLA / (2 * math.sin(math.radians(ANG_ARMO / 2)))
n_perp = (-U_MOLLA[1], U_MOLLA[0])           # perpendicolare alla molla, verso dietro
if n_perp[0] > 0:
    n_perp = (-n_perp[0], -n_perp[1])
coda_mid = (P[0] + L_CODA * n_perp[0], P[1] + L_CODA * n_perp[1])
coda_sc = rot(coda_mid, -ANG_ARMO / 2)       # coda a cane scattato (piu' in alto)
coda_ar = rot(coda_mid, +ANG_ARMO / 2)       # coda a cane armato (piu' in basso)

# profilo del cane a SCATTATO (coordinate assolute)
X_FACCIA = X_BERSAGLIO - L_NASO              # 40.8: 0.2 mm dietro lo scudo
zb = Z_BERSAGLIO
braccio = SPoly([
    (X_FACCIA, zb - 5.0), (X_FACCIA, zb + 5.0),            # faccia che batte sullo scudo
    (X_FACCIA - 3, zb + 9.5), (X_FACCIA - 8, zb + 12.0),   # dorso sotto la cinghia
    (X_FACCIA - 13, zb + 13.5), (X_FACCIA - 16, zb + 12.0),  # sperone
    (X_FACCIA - 15, zb + 8.5), (X_FACCIA - 10, zb + 6.5),  # rientro sotto lo sperone
    (P[0] - R_MOZZO * 0.9, P[1] + 2), (P[0] + R_MOZZO * 0.9, P[1] - 2),
])
mozzo = Point(P).buffer(R_MOZZO, 32)
coda = LineString([P, coda_sc]).buffer(3.2, 16)
cane2d = braccio.union(mozzo).union(coda).simplify(0.05)


def solido_cane(ang):
    """Cane 3D ruotato di ang (0 = scattato, ANG_ARMO = armato)."""
    pts = [rot(pt, ang) for pt in list(cane2d.exterior.coords)[:-1]]
    corpo = profilo(pts, SP_CANE, r2d=0.6)
    naso_c = rot((X_FACCIA - 0.5, zb), ang)
    naso = Pos(naso_c[0], 0, naso_c[1]) * Rot(0, 90 - ang, 0) * \
        Cylinder(D_NASO / 2, L_NASO + 0.5, align=(_C, _C, _MIN))
    return (corpo + naso) - Pos(P[0], 0, P[1]) * Rot(90, 0, 0) * Cylinder(D_PERNO / 2 + 0.15, SP_CANE + 2)


cane_sc = solido_cane(0.0)
cane_ar = solido_cane(ANG_ARMO)
perno = Pos(P[0], 0, P[1]) * Rot(90, 0, 0) * Cylinder(D_PERNO / 2, W_TELAIO)  # attraversa il telaio
asse_rot = Pos(P[0], 0, P[1]) * Rot(90, 0, 0) * Cylinder(0.3, 40)                         # asse (filo sottile)

# ---------------- molla nell'impugnatura ----------------
L1 = p.molla_L0 - PRECARICO                  # molla a cane scattato
# compressione effettiva dalla cinematica: proiezione dello spostamento della coda sull'asse
delta = (coda_sc[0] - coda_ar[0]) * U_MOLLA[0] + (coda_sc[1] - coda_ar[1]) * U_MOLLA[1]
L2 = L1 - delta                              # molla compressa (cane armato)
R_CONT = 3.2                                 # raggio del naso della coda (contatto con la coppa)
top_sc = (coda_sc[0] - U_MOLLA[0] * R_CONT, coda_sc[1] - U_MOLLA[1] * R_CONT)
# la molla e' sulla retta per coda_mid parallela a U: proietto la quota di contatto
def _su_asse(pt):
    t = (pt[0] - coda_mid[0]) * U_MOLLA[0] + (pt[1] - coda_mid[1]) * U_MOLLA[1]
    return (coda_mid[0] + t * U_MOLLA[0], coda_mid[1] + t * U_MOLLA[1])
cima_sc = _su_asse(top_sc)                   # cima della coppa, cane scattato
cima_ar = (cima_sc[0] - U_MOLLA[0] * delta, cima_sc[1] - U_MOLLA[1] * delta)
base_molla = (cima_ar[0] - U_MOLLA[0] * (L_COPPA + L2), cima_ar[1] - U_MOLLA[1] * (L_COPPA + L2))
fondo_sede = (base_molla[0] - U_MOLLA[0] * T_FONDO, base_molla[1] - U_MOLLA[1] * T_FONDO)
ang_molla = math.degrees(math.atan2(U_MOLLA[0], U_MOLLA[1]))   # inclinazione dalla verticale


def _cil_lungo_u(d, base, L):
    return Pos(base[0], 0, base[1]) * Rot(0, ang_molla, 0) * Cylinder(d / 2, L, align=(_C, _C, _MIN))


molla = _cil_lungo_u(p.molla_De, base_molla, L2)                   # molla COMPRESSA (armato)
coppa = _cil_lungo_u(p.molla_De + 0.6, (base_molla[0] + U_MOLLA[0] * L2,
                                         base_molla[1] + U_MOLLA[1] * L2), L_COPPA)
sede = _cil_lungo_u(D_SEDE, fondo_sede, T_FONDO + L2 + delta + L_COPPA + 2)  # ingombro del foro

# riferimenti: tamburo, scudo, cartuccia in camera (dalla meccanica)
tamburo = M.tamburo_base()
scudo = M._cil_x(2 * q.R_tamb, X_SCUDO, p.t_sc, z=q.z_asse_tamb)
cartuccia = M._cil_x(p.cart_D, q.x_cam, max(q.cart_L_tot), z=Z_BERSAGLIO)
perno_tamb_oggi = M._cil_x(p.tamb_asse_d, q.x_cam - 12, 12 + q.L_tamb, z=q.z_asse_tamb)


# =====================================================================
# VERIFICHE
# =====================================================================
def _vol(a, b):
    try:
        return (a & b).volume
    except Exception:
        return 0.0


righe = []
def out(s=""):
    righe.append(s)
    print(s)


out("=== CONCEPT MOLLA VERTICALE: verifiche ===")
out(f"0. Bersaglio: il brief dice z={Z_RICHIESTO:.2f}, ma li' c'e' l'ASSE del tamburo (perno d{p.tamb_asse_d:g}).")
out(f"   La camera in linea con la canna e' a z={Z_BERSAGLIO:.2f}: si mira li'. "
    f"Distanza tra i due punti = {abs(Z_BERSAGLIO - Z_RICHIESTO):.2f} mm.")

# 1 angolo
out(f"1. Rotazione cane armato -> scattato: {ANG_ARMO:.1f} gradi (perno in ({P[0]:g}, {P[1]:g}))")

# 2 punta: misurata sul solido scattato
bb = cane_sc.bounding_box()
x_punta = bb.max.X
naso_asse = (X_BERSAGLIO, Z_BERSAGLIO)
r_punta = math.dist(P, naso_asse)
inc = math.degrees(math.atan2(naso_asse[0] - P[0], naso_asse[1] - P[1]))  # vel. perpendicolare al raggio
out(f"2. Punta da scattato: x={x_punta:.2f} (bersaglio {X_BERSAGLIO:.2f}) a z={Z_BERSAGLIO:.2f}: "
    f"distanza residua {X_BERSAGLIO - x_punta:.2f} mm")
out(f"   compenetrazione con cartuccia/tamburo: {_vol(cane_sc, cartuccia):.2f} / {_vol(cane_sc, tamburo):.2f} mm^3")
out(f"   raggio punta {r_punta:.1f} mm, arriva inclinata di {inc:.0f} gradi sull'asse "
    f"(foro nello scudo da asolare di ~{L_NASO * math.tan(math.radians(inc)):.1f} mm in Z)")
out(f"   dal punto richiesto (z={Z_RICHIESTO:.2f}) la punta dista {math.dist((x_punta, Z_BERSAGLIO), (X_BERSAGLIO, Z_RICHIESTO)):.2f} mm")
punta_ar = rot((X_BERSAGLIO, Z_BERSAGLIO), ANG_ARMO)
out(f"   da armato la punta e' a ({punta_ar[0]:.1f}, {punta_ar[1]:.1f}): "
    + (f"{X_SCUDO - punta_ar[0]:.1f} mm dietro lo scudo -> tamburo libero di ruotare" if punta_ar[0] < X_SCUDO
       else "ANCORA NELLO SCUDO: il tamburo non puo' ruotare!"))
pose = [ANG_ARMO * i / 4 for i in range(5)]
ASOLA = L_NASO * math.tan(math.radians(inc)) + 0.5     # asola verticale nello scudo per il naso
foro_scudo = Pos(X_SCUDO - 0.1, 0, Z_BERSAGLIO + ASOLA / 2) * Box(p.t_sc + 0.2, D_NASO + 0.5, D_NASO + 0.5 + ASOLA, align=(_MIN, _C, _C))
v_scudo = max(_vol(solido_cane(a), scudo - foro_scudo) for a in pose)
v_tamb = max(_vol(solido_cane(a), tamburo) for a in pose)
out(f"   cane in 5 pose (0..{ANG_ARMO:g} gradi) contro scudo (asola {D_NASO + 0.5:.1f}x{D_NASO + 0.5 + ASOLA:.1f}) / tamburo: {v_scudo:.2f} / {v_tamb:.2f} mm^3")

# perno del tamburo: oggi sporge dietro fino a x_cam-12
v_perno = max(_vol(solido_cane(a), perno_tamb_oggi) for a in pose)
out(f"   !! interferenza cane / perno tamburo attuale (da x={q.x_cam - 12:.1f}): {v_perno:.0f} mm^3 "
    f"-> il perno deve fermarsi allo scudo (x>={X_SCUDO:g})")

# 3 accorciamento
x_dietro_mecc = min(cane_ar.bounding_box().min.X, cane_sc.bounding_box().min.X,
                    sede.bounding_box().min.X)
# lo sperone ad armato esce sopra il dorso come in ogni revolver: conta solo la parte interna
x_dietro_int = min(cane_sc.bounding_box().min.X, coda_ar[0] - R_CONT, cima_sc[0] - D_SEDE / 2)
x_retro_nuovo = x_dietro_int - PARETE - 2.0
x_tallone = grip.bounds[0]
lung_oggi = q.L_tel + 20 - min(B["X_DORSO0"], x_tallone)   # canna vista 20 (build.py CANNA_VISTA)
out(f"3. Canale percussore (x 0 -> {X_SCUDO:g}) sparisce. Ingombro interno piu' arretrato: x={x_dietro_int:.1f}")
out(f"   retro del telaio in alto: da x={B['X_DORSO0']:g} (gobba oggi) a x~{x_retro_nuovo:.1f}: "
    f"-{x_retro_nuovo - B['X_DORSO0']:.0f} mm sul dorso")
out(f"   sperone ad armato arretra fino a x={cane_ar.bounding_box().min.X:.1f} (sopra la mano, fuori dal telaio)")
out(f"   ma il tallone dell'impugnatura e' a x={x_tallone:.1f} (DX_IMP={DX_IMP:g}): lunghezza totale "
    f"~{lung_oggi:.0f} mm invariata finche' l'impugnatura non avanza (davanti c'e' il grilletto)")

# 4 molla nell'impugnatura
d_asse = ((cima_sc[0] - (B["X_IMP0"] + DX_IMP)) * B["_nrm"][0] + (cima_sc[1] - B["Z_IMP0"]) * B["_nrm"][1])
canale = LineString([fondo_sede, (cima_sc[0] + U_MOLLA[0], cima_sc[1] + U_MOLLA[1])]).buffer(D_SEDE / 2, cap_style=2)
# materiale = impugnatura + telaio sopra di essa (semipiano s < 2 lungo l'asse impugnatura):
# il bordo s = 0 del profilo e' la giunzione col telaio, non una parete
def _imp(s_, d_):
    return (B["X_IMP0"] + DX_IMP + s_ * B["_dir"][0] + d_ * B["_nrm"][0],
            B["Z_IMP0"] + s_ * B["_dir"][1] + d_ * B["_nrm"][1])
sopra = SPoly([_imp(2, -200), _imp(2, 200), _imp(-200, 200), _imp(-200, -200)])
materiale = grip.union(sopra)
sporge = canale.difference(materiale.buffer(-PARETE)).area
marg = materiale.boundary.distance(canale)
s_di = lambda pt: (pt[0] - B["X_IMP0"] - DX_IMP) * B["_dir"][0] + (pt[1] - B["Z_IMP0"]) * B["_dir"][1]
s_fondo_imp = B["L_IMP"] + B["H_TALL"]
s_tappo = s_di(fondo_sede)
# quanto si potrebbe allungare la sede verso il calcio restando dentro con parete minima
extra = 0.0
while extra < 80 and LineString([fondo_sede, (fondo_sede[0] - U_MOLLA[0] * (extra + 1), fondo_sede[1] - U_MOLLA[1] * (extra + 1))]) \
        .buffer(D_SEDE / 2, cap_style=2).within(materiale.buffer(-PARETE)):
    extra += 1
out(f"4. Molla De {p.molla_De:g} filo {p.molla_d:g} L0 {p.molla_L0:g}: scattato L1={L1:.1f}, armato L2={L2:.1f} "
    f"(pacco {q.m_Lp:.1f} + margine {p.margine_pacco:g} = {q.m_Lp + p.margine_pacco:.1f}) "
    f"{'OK' if L2 >= q.m_Lp + p.margine_pacco else 'A PACCO!'}")
out(f"   asse molla inclinato {ang_molla:.0f} gradi (parallelo all'impugnatura), a {d_asse:+.1f} mm dall'asse impugnatura")
out(f"   ingombro foro d{D_SEDE:g} lungo {T_FONDO + L2 + delta + L_COPPA:.1f} mm, fondo a ({fondo_sede[0]:.1f}, {fondo_sede[1]:.1f})")
out(f"   area del foro che esce dalla parete minima: {sporge:.2f} mm^2 -> "
    f"{'CI STA senza forare' if sporge < 0.01 else 'FORA il manico!'}; "
    f"parete minima rimasta attorno al foro {marg:.1f} mm")
out(f"   il foro occupa l'impugnatura fino a s={s_tappo:.0f} mm su {s_fondo_imp:g}: restano ~{extra:.0f} mm "
    f"di manico libero sotto il tappo (molla piu' lunga o piu' corsa = piu' energia)")
out("   NB: con questa leva la molla sta quasi tutta nel raccordo telaio/impugnatura, non giu' nel manico")

# 5 energia e leva
k = q.m_k
E = 0.5 * k * ((PRECARICO + delta) ** 2 - PRECARICO ** 2)
def braccio_leva(pt):   # distanza del perno dalla retta della molla per il contatto pt
    rx, rz = pt[0] - P[0], pt[1] - P[1]
    return abs(rx * U_MOLLA[1] - rz * U_MOLLA[0])
F_sc, F_ar = k * PRECARICO, k * (PRECARICO + delta)
tau_ar = F_ar * braccio_leva(coda_ar)
sperone = rot((X_FACCIA - 14, zb + 13), 0)
F_pollice = tau_ar / math.dist(P, sperone)


def _J_poligono(pts, c):
    """Momento polare d'area (mm^4) di un poligono rispetto al punto c."""
    s = 0.0
    n = len(pts)
    for i in range(n):
        x0, z0 = pts[i][0] - c[0], pts[i][1] - c[1]
        x1, z1 = pts[(i + 1) % n][0] - c[0], pts[(i + 1) % n][1] - c[1]
        cr = x0 * z1 - x1 * z0
        s += cr * (x0 * x0 + x0 * x1 + x1 * x1 + z0 * z0 + z0 * z1 + z1 * z1)
    return abs(s) / 12.0


m_cane = cane2d.area * SP_CANE * RHO_PLA
I_cane = _J_poligono(list(cane2d.exterior.coords)[:-1], P) * SP_CANE * RHO_PLA   # g mm^2
m_eff = I_cane / r_punta ** 2
cos_i = math.cos(math.radians(inc))
m_eff_ax = m_eff / cos_i ** 2                   # massa vista lungo l'asse canna
eta = m_eff_ax * M_CART * (1 + E_REST) ** 2 / (m_eff_ax + M_CART) ** 2
E_cart = E * eta
# oggi: percussore leggero (collare + punta) che accelera e poi spinge
m_perc = math.pi * ((p.perc_col_D / 2) ** 2 * p.perc_col_L + (p.perc_punta_d / 2) ** 2 * q.punta_L) * RHO_PLA
out(f"5. Compressione molla dalla cinematica: {delta:.2f} mm (oggi {q.corsa:g}), k={k:.3f} N/mm")
out(f"   energia immagazzinata {E:.1f} mJ (oggi {q.E_mJ:.1f} mJ) -> paragonabile")
out(f"   braccio di leva coda: {braccio_leva(coda_sc):.1f} mm scattato, {braccio_leva(coda_ar):.1f} mm armato; "
    f"forza molla {F_sc:.1f} -> {F_ar:.1f} N; coppia ad armato {tau_ar:.0f} N*mm")
out(f"   forza al pollice sullo sperone (r={math.dist(P, sperone):.0f} mm): ~{F_pollice:.1f} N  (oggi {F_ar:.1f} N sul pomolo)")
out(f"   cane ~{m_cane:.1f} g, massa efficace alla punta {m_eff:.1f} g (assiale {m_eff_ax:.1f} g) vs cartuccia ~{M_CART:g} g "
    f"(percussore di oggi ~{m_perc:.1f} g)")
out(f"   urto con e={E_REST}: alla cartuccia ~{eta * 100:.0f}% -> ~{E_cart:.0f} mJ. "
    f"Il percussore di oggi invece SPINGE per {q.spinta_c:.1f} mm a contatto: rende di piu'.")

# ---------------- riassunto ----------------
out("")
out("=== RIASSUNTO ===")
out(f"Schema promettente per le PROPORZIONI: niente canale, perno del cane {X_SCUDO - X_PERNO:.0f} mm dietro lo scudo, ruota di "
    f"{ANG_ARMO:.0f} gradi, molla attuale ci sta comoda nel manico ({E:.0f} mJ come oggi).")
out(f"Si rompe in 3 punti: (a) il bersaglio z=-12.45 del brief e' l'asse del tamburo, la camera e' a z=0; "
    f"(b) il perno del tamburo oggi sporge fino a x={q.x_cam - 12:.1f}, proprio sul braccio del cane: va accorciato allo scudo;")
out(f"(c) la punta arriva ad arco ({inc:.0f} gradi) e solo a contatto: non spinge la cartuccia per {q.spinta_c:.1f} mm, "
    f"e il cane pesante cede solo ~{eta * 100:.0f}% dell'energia -> serve un percussore flottante nello scudo.")
out(f"Il dorso si accorcia di ~{x_retro_nuovo - B['X_DORSO0']:.0f} mm, ma la lunghezza totale no "
    f"finche' l'impugnatura (tallone x={x_tallone:.0f}) resta dietro il grilletto.")

# =====================================================================
# SHOW + EXPORT
# =====================================================================
COL_A, COL_S = "#d9a441", "#ff7a00"
show_object(cane_ar, id="cane_armato", name=f"Cane armato (+{ANG_ARMO:g} gradi)", options={"color": COL_A, "alpha": 0.5})
show_object(cane_sc, id="cane_scattato", name="Cane scattato", options={"color": COL_S})
show_object(perno, id="perno_cane", name="Perno del cane (M3)", options={"color": "#888888"})
show_object(asse_rot, id="asse_rotazione", name="Asse di rotazione", options={"color": "#000000"})
show_object(molla, id="molla", name="Molla compressa (armato)", options={"color": "#3060ff"})
show_object(coppa, id="coppa", name="Coppa/puntone molla", options={"color": "#88aaff"})
show_object(sede, id="sede_molla", name="Foro molla nell'impugnatura", options={"color": "#3060ff", "alpha": 0.2})
show_object(tamburo, id="tamburo", name="Tamburo (riferimento)", options={"color": "#4fa89a", "alpha": 0.4})
show_object(scudo, id="scudo", name="Scudo posteriore (riferimento)", options={"color": "#4fa89a", "alpha": 0.4})
show_object(cartuccia, id="cartuccia", name="Cartuccia in camera", options={"color": "#f2e3c6"})

os.makedirs(OUT, exist_ok=True)
pezzi = {"cane_armato": cane_ar, "cane_scattato": cane_sc, "perno_cane": perno,
         "molla_compressa": molla, "coppa": coppa, "sede_molla": sede,
         "tamburo": tamburo, "scudo": scudo, "cartuccia": cartuccia}
export_stl(Compound(list(pezzi.values())), os.path.join(OUT, "assieme_molla_verticale.stl"))
for nome, s in pezzi.items():
    export_stl(s, os.path.join(OUT, f"{nome}.stl"))
print(f"export: {os.path.relpath(OUT, os.getcwd())}/assieme_molla_verticale.stl (+ un STL per pezzo)")
