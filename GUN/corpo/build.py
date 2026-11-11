# REVOLVER GIOCATTOLO "FRONTIERA" - design dell'involucro (stile revolver d'epoca, come la reference).
#
# Chi fa cosa:
#   meccanica.py  : quote di tamburo, canna, camere, finestra (da params.scad)
#   meccanismo.py : cinematica e pezzi mobili (cane, grilletto, molla nel manico), vani da togliere
#   profili.py    : SILHOUETTE 2D del design (telaio, impugnatura, ponticello, guancette)
#   forme.py      : dal profilo 2D al solido con gli spigoli tondi
#   build.py      : (questo) solidi, dettagli, montaggio, export
#
# Forma: telaio a fianchi piani e spigoli tondi (come un revolver vero, non una guaina gonfia),
# cinghia superiore dritta, tamburo che sporge dai fianchi dentro la finestra, scudo tondo, cane a
# vista sopra la sella, camicia della canna con bindella e alloggio del perno del tamburo sotto
# (la testa zigrinata del perno fa da astina), ponticello ovale sottile, guancette bombate con
# zigrinatura e medaglione, mirino a rampa. Colori da giocattolo, volata arancione.
#
#   GUN_VELOCE=1  salta i dettagli lenti (zigrinatura, elica della molla): per iterare sulla forma
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # i moduli del progetto sono qui
# show_object e' iniettato solo dentro agentcad; qui giriamo con Python puro
if "show_object" not in dir():
    def show_object(*a, **k):  # noqa: E306  (no-op fuori da agentcad)
        pass
from build123d import (Align, Axis, Box, Compound, Cylinder, Plane, Pos, Rot, SortBy, Sphere, export_stl,
                       fillet, mirror)
from shapely import affinity
from shapely.geometry import LineString as SLine, Point as SPoint, Polygon as SPoly, box as sbox
from shapely.ops import unary_union

import concetti as C
import forme as F
import meccanica as M
import meccanismo as MEC     # meccanismo a molla verticale nel manico (MECCANISMO.md)
import profili as PR
from concetti import p, q, cil_x

VELOCE = os.environ.get("GUN_VELOCE", "") not in ("", "0")
_t0 = time.time()


def _tempo(cosa, solido=None):
    ok = "" if solido is None or solido.is_valid else "   <-- SOLIDO NON VALIDO"
    print(f"[{time.time() - _t0:6.1f} s] {cosa}{ok}", flush=True)


# ---------------- palette e misure d'involucro ----------------
COL_TELAIO, COL_OTTONE, COL_AVORIO, COL_VOLATA = "#4fa89a", "#d9a441", "#f2e3c6", "#ff7a00"
COL_ACCIAIO = "#9aa0a6"                 # solo per i pezzi di riferimento (acciaio / filamento)
W = PR.W                                # larghezza telaio
W2 = W / 2
R_SPIGOLO = 2.5                         # raggio degli spigoli del telaio
za = q.z_asse_tamb
x_bocca = PR.X_BOCCA
L_CANNA = x_bocca - (q.x_spal + p.t_sp)   # lunghezza canna (sede invariata)
r_scudo = q.R_tamb + 1.0                # scudo posteriore tondo
t_scudo = MEC.T_SCUDO                   # il retro dello scudo e' la battuta del cane
x_scudo1 = MEC.X_SCUDO1                 # faccia anteriore dello scudo
x_scudo0 = MEC.X_SCUDO
camera_carica = 4                       # camera allineata allo sportello (lato destro, -Y)
L_car = 6.0                             # scanalatura di carica dietro lo scudo
a_car = 2 * math.pi * camera_carica / p.n_camere
y_car, z_car = q.r_passo * math.sin(a_car), za + q.r_passo * math.cos(a_car)

assert PR.verifica().area < 0.5, f"vani del meccanismo fuori dalla sagoma: {PR.verifica().area:.1f} mm^2"

# ---------------- TELAIO ----------------
# sagoma di profili.py, fianchi piani a y = +-W/2, spigoli tondi R_SPIGOLO
telaio = F.prisma_tondo(PR.telaio2d, -W2, W2, R_SPIGOLO, R_SPIGOLO)

# camicia della canna: blocco a fianchi piani (PR.camicia2d) con gli spigoli tondi, bindella sopra
# e un solco lungo i fianchi fra canna e alloggio del perno
_cam = F.prisma_tondo(PR.camicia2d, -PR.W_CAMICIA / 2, PR.W_CAMICIA / 2, 2.4, 2.4)
_cam += F.prisma(PR.bindella2d, -PR.W_BINDELLA / 2, PR.W_BINDELLA / 2)
_z_solco = (za + p.tamb_asse_d / 2 - p.canna_D / 2) / 2          # a meta' fra canna e perno
for s in (1, -1):
    _cam -= Box(PR.X_CAMICIA1 - PR.X_FRONTE - 9.0, 1.4, 1.5, align=(Align.MIN, Align.CENTER, Align.CENTER)) \
        .translate((PR.X_FRONTE + 4.5, s * PR.W_CAMICIA / 2, _z_solco))
telaio += _cam
_tempo("telaio: sagoma e camicia", telaio)

# ponticello: anello ovale sottile, piu' stretto del telaio, spigoli tondi
telaio += F.prisma_tondo(PR.ponticello2d, -PR.W_PONT / 2, PR.W_PONT / 2, 1.3, 1.3)
_tempo("telaio: ponticello", telaio)

# scudo posteriore tondo (spigolo dietro raccordato)
_scudo = cil_x(2 * r_scudo, x_scudo0, t_scudo, z=za)
try:
    _scudo = fillet(_scudo.edges().group_by(Axis.X)[0], 1.2)
except Exception as err:
    print("raccordo dello scudo saltato:", err)
telaio += _scudo

# mire: tacca posteriore nella cinghia, mirino a rampa sulla bindella
telaio -= Box(7, 2.4, 1.4, align=(Align.MIN, Align.CENTER, Align.MAX)).translate((36.5, 0, PR.Z_TETTO + 0.01))
_xm = PR.X_CAMICIA1
telaio += F.prisma(SPoly([(_xm - 15, PR.Z_TETTO - 0.5), (_xm - 5.5, PR.Z_TETTO + 3.8), (_xm - 3.0, PR.Z_TETTO + 3.8),
                          (_xm - 2.2, PR.Z_TETTO - 0.5)]).buffer(-0.6, 8).buffer(0.6, 8), -1.3, 1.3)
_tempo("telaio: ponticello, scudo, mire", telaio)

viti = [MEC.PT, MEC.P, (PR.X_FRONTE - 3.8, za - 14.5)]   # (x, z) delle teste a vista: le due spine + una finta
# filetto della cartella: un solco sottile sui fianchi che ripete il contorno del telaio dietro
# il tamburo (come la cartella laterale dei revolver veri) e rompe la superficie piana. Si taglia
# prima di posare le teste delle viti, che cosi' lo coprono dove lo incontrano. Il solco e' la
# differenza fra due prismi a contorno liscio (una spline ciascuno): un taglio solo, veloce.
PROF_FILETTO, W_FILETTO = 0.6, 0.9
_cartella = PR.telaio2d.intersection(sbox(-60, PR.Z_SOTTO, x_scudo0 - 0.5, 40)).difference(PR.guancia2d.buffer(2.6))
_cartella = PR.tondo(_cartella.buffer(-3.6, 24), 2.0)
for s in (1, -1):
    _y = sorted((s * (W2 - PROF_FILETTO), s * (W2 + 1.0)))
    telaio -= F.prisma_tondo(_cartella.buffer(W_FILETTO / 2, 24), *_y) \
        - F.prisma_tondo(_cartella.buffer(-W_FILETTO / 2, 24), _y[0] - 0.1, _y[1] + 0.1)
_tempo("telaio: filetto della cartella", telaio)

# finte viti: teste a vista sui fianchi. Quelle su MEC.P e MEC.PT sono le teste delle spine
# d'acciaio di cane e grilletto: forate, la spina passa.
PERNI_SPINA = MEC.PERNI_SPINA           # (x, z) del perno -> diametro della spina
for (vx, vz) in viti:
    for s in (1, -1):
        ys = s * W2
        # sulle spine d'acciaio la testa e' un anello: almeno 1.6 di parete attorno al foro
        r_testa = max(2.6, PERNI_SPINA[(vx, vz)] / 2 + 1.6) if (vx, vz) in PERNI_SPINA else 2.6
        testa = Pos(vx, ys, vz) * Rot(90, 0, 0) * Cylinder(r_testa, 1.6)
        taglio = Pos(vx, ys + s * 0.8, vz) * Rot(0, 35, 0) * Box(4.4, 0.6, 1.6)
        if (vx, vz) in PERNI_SPINA:
            # niente taglio del cacciavite: attraverso il foro lascerebbe due mezzelune da 0.4 mm
            telaio = telaio + testa - Pos(vx, ys, vz) * Rot(90, 0, 0) * Cylinder(PERNI_SPINA[(vx, vz)] / 2, 4)
        else:
            telaio = telaio + testa - taglio

# sede della leva finta sul fianco sinistro (vedi LEVA)
# (un bottone tondo subito dietro lo scudo, sotto la sella, come il pulsante della reference)
R_LEVA = 4.4
LEVA_C = (x_scudo0 - R_LEVA - 3.6, PR.z_cima(x_scudo0 - R_LEVA - 3.6) - R_LEVA - 6.2)
leva2d = SPoint(LEVA_C).buffer(R_LEVA, 48)
telaio -= F.prisma(leva2d.buffer(0.15), W2 - 0.8, W2 + 1)

# meccanica comune (finestra tamburo, sede canna, foro del percussore nello scudo)
telaio = telaio - M.vuoto_finestra_tamburo() - M.vuoto_canna(x_bocca)
telaio -= cil_x(MEC.D_PERC_FORO, x_scudo0 - 0.1, t_scudo + 0.2)
# il foro del perno del tamburo sbuca dietro nella feritoia del cane e davanti dall'alloggio
telaio -= M.vuoto_asse_tamburo(MEC.X_FORO_TAMB, PR.X_CAMICIA1 + 1)
# vani del meccanismo (feritoie di cane e grilletto, sede molla, raccordi dei setti sottili): li
# calcola meccanismo.py dalla sagoma di questo telaio. Prismi simmetrici in Y, uno per larghezza.
VANI_MEC = MEC.vani_telaio(PR.telaio2d, PR.ponticello2d, PR.vano_ponticello,
                           lambda x, z: W2, PR.z_cima, W)
for _w, _g in VANI_MEC.items():
    telaio -= MEC.estrudi(_g, _w)
telaio -= MEC.estrudi(PR.camino_cane2d, MEC.SLOT_CANE)     # feritoia del cane aperta verso l'alto
telaio -= MEC.foro_spine()
# scanalatura di carica sul fianco destro + passaggio nello scudo
car = cil_x(q.camera_d, x_scudo0 - L_car, x_scudo1 - x_scudo0 + L_car + 0.1, z=z_car, y=y_car)
car += Box(x_scudo1 - x_scudo0 + L_car + 0.1, 20, q.camera_d, align=(Align.MIN, Align.MAX, Align.CENTER)) \
    .translate((x_scudo0 - L_car, y_car, z_car))
telaio -= car
_tempo("telaio: viti, meccanica, vani", telaio)

# sportello di caricamento (chiuso): riempie il passaggio nello scudo
sportello = (cil_x(q.camera_d - p.gioco, x_scudo0 + 0.2, t_scudo - 0.4, z=z_car, y=y_car)
             + Box(t_scudo - 0.4, 20, q.camera_d - p.gioco, align=(Align.MIN, Align.MAX, Align.CENTER))
             .translate((x_scudo0 + 0.2, y_car, z_car)))
sportello &= cil_x(2 * r_scudo - p.gioco, x_scudo0, t_scudo, z=za)
y_scudo_est = -math.sqrt(r_scudo**2 - (z_car - za)**2)      # bordo dello scudo a quota z_car
sportello += Pos(x_scudo0 + t_scudo / 2, y_scudo_est - 0.6, z_car) * Box(2.5, 1.5, 3)  # unghiata


# ---------------- TAMBURO ----------------
R_SCAN_TAMB = 5.0           # raggio delle scanalature del tamburo
FUORI_SCAN = 2.6            # di quanto l'asse della scanalatura sta fuori dal tamburo
X_SCAN0 = q.x_cam + 10.5    # centro della calotta di fondo; davanti la scanalatura e' aperta
R_FONDO_SCAN = 6.5          # raggio della calotta di fondo


def tamburo():
    t = M.tamburo_base()
    n = int(p.n_camere)
    # smussi sugli spigoli esterni davanti (1.2) e dietro (0.6), prima delle scanalature
    for gruppo, r in ((-1, 1.2), (0, 0.6)):
        try:
            e = t.edges().group_by(Axis.X)[gruppo].sort_by(SortBy.RADIUS)[-1]
            t = t.chamfer(r, None, [e])
        except Exception as err:
            print("smusso tamburo saltato:", err)
    for i in range(n):
        a = 2 * math.pi * i / n
        yc, zc = q.r_passo * math.sin(a), za + q.r_passo * math.cos(a)
        # svaso d'imbocco davanti a ogni camera
        # raggio limitato: tra due svasi vicini resta almeno meta' parete_min
        r_svaso = min(q.camera_d / 2 + 0.8,
                      q.r_passo * math.sin(math.pi / p.n_camere) - p.parete_min / 4)
        t -= Pos(q.x_cam + q.L_tamb - 0.8, yc, zc) * Rot(0, 90, 0) * \
            Cylinder(r_svaso, 1.7, align=(Align.CENTER, Align.CENTER, Align.MIN))
        # tacca del fermo, in linea con la camera (sopra la parete piu' spessa)
        tacca = Box(3.0, 3.2, 2 * p.tacca_fermo, align=(Align.MIN, Align.CENTER, Align.CENTER))
        t -= Pos(q.x_cam + 1.2, 0, za) * Rot(-math.degrees(a), 0, 0) * tacca.translate((0, 0, q.R_tamb))
        # scanalature tra le camere, come nei revolver veri: larghe, a fondo tondo dietro e
        # aperte sul davanti del tamburo
        af = 2 * math.pi * (i + 0.5) / n
        r = q.R_tamb + FUORI_SCAN
        ys, zs = r * math.sin(af), za + r * math.cos(af)
        # fondo: calotta di raggio R_FONDO_SCAN > raggio della scanalatura, cosi' incontra il
        # cilindro con uno spigolo netto (una semisfera tangente lascia triangoli degeneri nell'STL)
        t -= cil_x(2 * R_SCAN_TAMB, X_SCAN0 - R_FONDO_SCAN, q.L_tamb + R_FONDO_SCAN, z=zs, y=ys) \
            & (Pos(X_SCAN0, ys, zs) * Sphere(R_FONDO_SCAN)
               + Box(q.L_tamb, 40, 40, align=(Align.MIN, Align.CENTER, Align.CENTER)).translate((X_SCAN0, ys, zs)))
    return t


# parete fra scanalatura e camera vicina
_d_scan = math.sqrt((q.R_tamb + FUORI_SCAN) ** 2 + q.r_passo ** 2
                    - 2 * (q.R_tamb + FUORI_SCAN) * q.r_passo * math.cos(math.pi / p.n_camere))
assert _d_scan - R_SCAN_TAMB - q.camera_d / 2 >= p.parete_min, "scanalature del tamburo troppo profonde"

# ---------------- PERNO DEL TAMBURO (sfilabile dal davanti) ----------------
# Attraversa l'alloggio sotto la canna: la testa zigrinata sporge davanti alla camicia, sotto la
# volata, come l'astina dell'estrattore. Parte davanti alla feritoia del cane (MEC.X_PERNO_TAMB).
G_TESTA_PERNO = 0.3         # luce tra la testa del perno e la faccia dell'alloggio
x_testa = PR.X_CAMICIA1 + G_TESTA_PERNO
perno = cil_x(p.tamb_asse_d, MEC.X_PERNO_TAMB, x_testa + 1 - MEC.X_PERNO_TAMB, z=za) \
    + cil_x(9, x_testa, PR.L_TESTA_PERNO, z=za)
for i in range(10):
    a = 2 * math.pi * i / 10
    perno -= cil_x(1.2, x_testa - 0.1, PR.L_TESTA_PERNO + 0.5, z=za + 4.6 * math.cos(a), y=4.6 * math.sin(a))

# ---------------- LEVA FINTA (decoro, fianco sinistro) ----------------
# Nella reference dietro il tamburo c'e' il pulsante di sblocco: qui e' solo un decoro in ottone
# incollato nella sua sede (0.8 mm), con il dorso zigrinato.
leva = F.prisma_tondo(leva2d, W2 - 0.8, W2 + 1.8, 0.0, 0.9)
# gola ad anello e tre tacche sul dorso, per il pollice
leva -= Pos(LEVA_C[0], W2 + 1.8, LEVA_C[1]) * Rot(90, 0, 0) * (Cylinder(R_LEVA - 1.2, 1.0) - Cylinder(R_LEVA - 1.9, 1.2))
for dx in (-1.1, 0.0, 1.1):
    leva -= Pos(LEVA_C[0] + dx, W2 + 1.8, LEVA_C[1]) * Box(0.5, 1.0, 3.0)

# ---------------- MECCANISMO A MOLLA VERTICALE (meccanismo.py, MECCANISMO.md) ----------------
# Pezzi funzionali, tutti A RIPOSO (cane abbattuto sullo scudo, naso del grilletto sulla camma):
# profili, quote e cinematica stanno in meccanismo.py; qui solo i colori e il montaggio.
cane = MEC.cane()
grilletto = MEC.grilletto()
rullino = MEC.rullino()
perno_rullino = MEC.perno_rullino()                # filamento PLA 1.75 (riferimento)
percussore = MEC.percussore()
coppa = MEC.coppa()
distanziale = MEC.distanziale()
pistone = MEC.pistone()
# spine d'acciaio (riferimento): lunghe quanto il telaio sul perno, 0.2 sotto ogni fianco
spina_cane = MEC.spina_cane(W - 0.4)
spina_gril = MEC.spina_grilletto(W - 0.4)
_tempo("tamburo (definizione), perno, meccanismo")

# ---------------- GUANCETTE ----------------
# Seguono la sagoma dell'impugnatura (PR.guancia2d), bombate: lo spigolo esterno ha raggio R_G.
T_G = 4.6                   # spessore della guancetta
R_G = 3.2                   # raggio dello spigolo esterno (bombatura)
PASSO_ZIGR = 3.2            # passo della zigrinatura a rombi
SOLCO_ZIGR = 0.8            # larghezza dei solchi
_cg = PR.guancia2d.centroid
_ax = PR.ASSE_MANICO          # asse del manico (verso il calcio)
_ang_ax = math.degrees(math.atan2(_ax[1], _ax[0]))
x_med, z_med = _cg.x - 13 * _ax[0], _cg.y - 13 * _ax[1]      # medaglione, in alto
x_vg, z_vg = _cg.x + 13 * _ax[0], _cg.y + 13 * _ax[1]        # vite della guancetta, in basso


def guancia_sx():
    """Guancetta sinistra (+Y); la destra e' la sua specchiata."""
    y_out = W2 + T_G
    g = F.prisma_tondo(PR.guancia2d, W2, y_out, 0.0, R_G)
    if not VELOCE:
        # zigrinatura: griglia di solchi a +-30 gradi dall'asse del manico, in 2D, poi un solo taglio
        righe = []
        for k in range(-16, 17):
            for da in (30, -30):
                r = sbox(-SOLCO_ZIGR / 2, -80, SOLCO_ZIGR / 2, 80)
                r = affinity.translate(r, k * PASSO_ZIGR / math.sin(math.radians(60)), 0)
                righe.append(affinity.translate(affinity.rotate(r, _ang_ax + 90 + da, origin=(0, 0)), _cg.x, _cg.y))
        solchi = unary_union(righe).intersection(PR.campo_zigrino2d) \
            .difference(SPoint(x_med, z_med).buffer(8.2, 32)).difference(SPoint(x_vg, z_vg).buffer(4.2, 24))
        g -= F.prisma(solchi, y_out - 0.7, y_out + 1)
    # medaglione a stella in rilievo + vite della guancetta
    stella = SPoly([(x_med + 4.5 * math.cos(math.radians(90 + 36 * i)) * (1 if i % 2 == 0 else 0.42),
                     z_med + 4.5 * math.sin(math.radians(90 + 36 * i)) * (1 if i % 2 == 0 else 0.42))
                    for i in range(10)])
    g -= Pos(x_med, y_out, z_med) * Rot(90, 0, 0) * Cylinder(5.6, 1.4)
    g += Pos(x_med, y_out, z_med) * Rot(90, 0, 0) * (Cylinder(6.8, 1.6) - Cylinder(5.6, 2))
    g += F.prisma(stella, y_out - 0.8, y_out + 0.8)
    vite = Pos(x_vg, y_out, z_vg) * Rot(90, 0, 0) * Cylinder(2.6, 1.6)
    vite -= Pos(x_vg, y_out + 0.7, z_vg) * Box(4.4, 0.8, 0.6)
    return g + vite


# ---------------- MONTAGGIO ----------------
tamb = tamburo()
_tempo("tamburo")
canna = M.canna(L_CANNA)
volata = C.volata(x_bocca, p.canna_D)
g_sx = guancia_sx()
g_dx = mirror(g_sx, Plane.XZ)
_tempo("guancette")

PEZZI = {   # nome: (solido, colore) - i pezzi da stampare
    "telaio": (telaio, COL_TELAIO), "tamburo": (tamb, COL_OTTONE), "perno": (perno, COL_OTTONE),
    "sportello": (sportello, COL_OTTONE), "canna": (canna, COL_TELAIO),
    "guancia_sx": (g_sx, COL_AVORIO), "guancia_dx": (g_dx, COL_AVORIO),
    "cane": (cane, COL_OTTONE), "grilletto": (grilletto, COL_OTTONE), "volata": (volata, COL_VOLATA),
    "leva": (leva, COL_OTTONE),
    "rullino": (rullino, COL_AVORIO), "percussore": (percussore, COL_AVORIO), "coppa": (coppa, COL_AVORIO),
    "distanziale": (distanziale, COL_AVORIO), "pistone": (pistone, COL_AVORIO),
}
NOMI = {"telaio": "Telaio (2 gusci)", "perno": "Perno tamburo (testa zigrinata sotto la canna)",
        "sportello": "Sportello di carica", "cane": "Cane (imperniato, spina d3)",
        "grilletto": "Grilletto (con forcella del rullino)", "rullino": "Rullino d7",
        "percussore": "Percussore flottante", "coppa": "Coppa della molla",
        "distanziale": "Distanziale 4 mm", "pistone": "Pistone + pattino",
        "leva": "Bottone finto (decoro, si incolla)"}
for _n, (_s, _c) in PEZZI.items():
    show_object(_s, id=_n, name=NOMI.get(_n, _n.replace("_", " ").capitalize()), options={"color": _c})
# riferimento, non PLA: non vanno nell'assieme dei pezzi da stampare
RIFERIMENTI = {"spina_cane_rif": spina_cane, "spina_gril_rif": spina_gril, "perno_rullino_rif": perno_rullino}
if not VELOCE:
    RIFERIMENTI["molla_rif"] = MEC.molla()             # elica vera (lenta): solo nella build completa
for _n, _s in RIFERIMENTI.items():
    show_object(_s, id=_n, name=_n.replace("_", " "), options={"color": COL_ACCIAIO, "floating": True})

# ---------------- EXPORT ----------------
# stl/assieme.stl: tutti i pezzi in un STL multi-corpo (cancelli e render dell'harness; non e' il
# file di stampa). stl/parti/<nome>.stl + colori.json: un file per pezzo, per i render a colori.
import json  # noqa: E402

_STL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")   # sempre GUN/corpo/stl
os.makedirs(os.path.join(_STL, "parti"), exist_ok=True)
for _n, (_s, _c) in PEZZI.items():
    if not _s.is_valid:
        print(f"ATTENZIONE: {_n} non e' un solido valido")
    export_stl(_s, os.path.join(_STL, "parti", _n + ".stl"))
json.dump({_n: _c for _n, (_s, _c) in PEZZI.items()}, open(os.path.join(_STL, "parti", "colori.json"), "w"), indent=1)
export_stl(Compound([_s for _s, _ in PEZZI.values()]), os.path.join(_STL, "assieme.stl"))
export_stl(Compound(list(RIFERIMENTI.values())), os.path.join(_STL, "riferimento_acciaio.stl"))
_tempo("export: stl/assieme.stl, stl/parti/*.stl (+ stl/riferimento_acciaio.stl, solo riferimento)")
