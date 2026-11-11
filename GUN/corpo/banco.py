# BANCO DI PROVA DEL MECCANISMO - proof of concept da stampare, senza estetica.
#
# Due piastre (gusci) ridotte alla zona del meccanismo, con sede molla, feritoie e fori delle
# spine IDENTICI al telaio vero (li calcola meccanismo.py, come per build.py), piu':
#   - lo scudo con il foro del percussore e la sede della canna (stessa di meccanica.py)
#   - al posto del tamburo un BLOCCO con una sola camera, che si cala dall'alto fra scudo e
#     canna (a cane armato: a riposo la punta del percussore entra nella camera, come nel
#     revolver, e lo blocca)
#   - 6 fori per viti M3x20 con dado, per aprire e richiudere i gusci quante volte serve
# Dipende solo da meccanica.py e meccanismo.py: niente profili.py, niente design.
#
#   python banco.py   -> stl/banco/stampa/*.stl   pezzi orientati per la stampa (piano a z = 0)
#                        stl/banco/assieme/*.stl  gli stessi pezzi montati (controlli, render)
#                        stl/banco/banco.png      disegno laterale
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build123d import Align, Axis, Box, Cylinder, Pos, Rot, export_stl  # noqa: E402
from shapely import affinity  # noqa: E402
from shapely.geometry import LineString, Point, Polygon, box as sbox  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

import forme as F  # noqa: E402
import meccanica as M  # noqa: E402
import meccanismo as MEC  # noqa: E402

p, q = M.p, M.q

# ---------------- quote del banco ----------------
W = 22.0                    # larghezza, come il telaio vero (stesse pareti attorno ai vani)
W2 = W / 2
PARETE_B = 4.0              # parete attorno agli ingombri del meccanismo
Z_ALTO = 13.0               # cima del blocco scudo / canna
Z_PAV = -10.5               # pavimento del vano del blocco camera
Z_BASSO = Z_PAV - 12.0      # sotto del banco davanti (sotto la canna c'e' posto per due viti)
L_DIETRO_SCUDO = 11.0       # guance piene dietro lo scudo
D_VITE, D_TESTA, H_TESTA = 3.3, 6.2, 3.0     # viti M3x20 a testa cilindrica
CH_DADO, H_DADO = 5.7, 2.6                   # sede del dado M3 (chiave 5.5)
N_VITI = 6
W_GUIDA, H_GUIDA = 6.0, 2.0                  # costola sul pavimento che centra il blocco camera
Z_BLOCCO_ALTO = Z_ALTO + 3.0                 # il blocco sporge sopra per prenderlo con le dita

# ---------------- sagoma 2D (piano XZ) ----------------
_ingombro = unary_union([MEC.INGOMBRO_CHIUSO, MEC.INGOMBRO_PERCUSSORE])
_corpo = _ingombro.buffer(PARETE_B, 24)
_davanti = sbox(MEC.X_SCUDO - L_DIETRO_SCUDO, Z_BASSO, q.L_tel, Z_ALTO)
# orecchie per le viti: lungo il dorso della sede molla e davanti al braccio del grilletto,
# nel riferimento dell'asse della molla (s lungo l'asse verso il fondo, d di traverso in avanti)
R_ORECCHIA = D_TESTA / 2 + 2.6


def _sd(s_, d_):
    return (MEC.CIMA0[0] - MEC.U[0] * s_ + MEC.NF[0] * d_, MEC.CIMA0[1] - MEC.U[1] * s_ + MEC.NF[1] * d_)


_ing_sd = affinity.affine_transform(affinity.translate(_ingombro, -MEC.CIMA0[0], -MEC.CIMA0[1]),
                                    [-MEC.U[0], -MEC.U[1], MEC.NF[0], MEC.NF[1], 0, 0])
_d_dietro = lambda s_: _ing_sd.intersection(sbox(s_ - 1, -300, s_ + 1, 300)).bounds[1]      # noqa: E731
_d_davanti = lambda s_: _ing_sd.intersection(sbox(s_ - 1, -300, s_ + 1, 300)).bounds[3]     # noqa: E731
_fuori = D_TESTA / 2 + 2.0
ORECCHIE = [_sd(s_, _d_dietro(s_) - _fuori) for s_ in (8.0, 36.0, 64.0)] + [_sd(60.0, _d_davanti(60.0) + _fuori)]
banco2d = unary_union([_corpo, _davanti] + [Point(c).buffer(R_ORECCHIA, 32) for c in ORECCHIE]) \
    .buffer(4.0, 24).buffer(-4.0, 24)
# sotto il mozzo del grilletto la sagoma finisce dritta e la lama esce libera (niente ponticello)
Z_SOTTO_GRIL = MEC.PT[1] - 9.5
_lama = MEC.VANO_LAMA.intersection(sbox(-300, -300, 300, Z_SOTTO_GRIL))
vano_dito = unary_union([Point(_lama.bounds[0] + 5.0, Z_SOTTO_GRIL + 0.4 - 12.0).buffer(12.0, 48),
                         Point(_lama.bounds[2] + 12.0, Z_SOTTO_GRIL + 0.4 - 12.0).buffer(12.0, 48)]).convex_hull
banco2d = banco2d.difference(vano_dito)
banco2d = banco2d.buffer(-2.0, 24).buffer(4.0, 24).buffer(-2.0, 24)       # spigoli raccordati r 2
if banco2d.geom_type != "Polygon":
    banco2d = max(banco2d.geoms, key=lambda g: g.area)
assert _ingombro.buffer(MEC.PARETE).difference(banco2d).area < 0.5, "ingombri del meccanismo fuori dal banco"

# vano del blocco camera: fra scudo e spalla della canna, aperto in alto e sui fianchi
X_VANO0, X_VANO1 = MEC.X_SCUDO1, MEC.X_SCUDO1 + q.finestra_L
vano_blocco2d = sbox(X_VANO0, Z_PAV, X_VANO1, 50)
# feritoia del cane aperta verso l'alto (come in profili.py)
_cane_aperto = MEC.vano_cane.difference(_ingombro.buffer(MEC.PARETE))
camino2d = unary_union([affinity.translate(_cane_aperto, 0, 0.25 * k) for k in range(0, 161)]) \
    .buffer(0.15, 8).buffer(-0.15, 8).simplify(0.03)


def z_cima(x):
    g = banco2d.intersection(LineString([(x, -500), (x, 500)]))
    return None if g.is_empty else g.bounds[3]


# ---------------- viti dei gusci: dove c'e' materiale pieno, ben distribuite ----------------
_vuoti = unary_union([MEC.vano_cane, MEC.vano_gril, MEC.vano_molla, camino2d, vano_blocco2d,
                      sbox(q.x_spal - 1, -p.canna_D / 2 - 0.2, q.L_tel + 1, p.canna_D / 2 + 0.2),
                      Point(MEC.P).buffer(3.0), Point(MEC.PT).buffer(2.5)])
_zona = banco2d.buffer(-(D_TESTA / 2 + 2.0)).difference(_vuoti.buffer(D_TESTA / 2 + 1.6))
_cand = []
_x0, _z0, _x1, _z1 = _zona.bounds
_x = _x0
while _x <= _x1:
    _z = _z0
    while _z <= _z1:
        if _zona.contains(Point(_x, _z)):
            _cand.append((_x, _z))
        _z += 1.5
    _x += 1.5
# le quattro orecchie attorno al manico + due nel blocco davanti (le piu' lontane fra loro)
VITI = list(ORECCHIE)
for _c in VITI:
    assert _zona.buffer(0.3).contains(Point(_c)), f"orecchia senza materiale attorno alla vite: {_c}"
_cand = [c for c in _cand if c[0] > MEC.X_SCUDO1]
assert len(_cand) >= 2, "non c'e' posto per le viti davanti"
while len(VITI) < N_VITI:
    VITI.append(max(_cand, key=lambda c: min(math.dist(c, v) for v in VITI)))


# ---------------- solidi (posizione di montaggio) ----------------
def _banco():
    s = F.prisma_tondo(banco2d, -W2, W2)                  # fianchi piani, spigoli vivi: si stampa sdraiato
    # vano del blocco camera + costola di guida sul pavimento
    s -= Box(X_VANO1 - X_VANO0, W + 2, 80, align=(Align.MIN, Align.CENTER, Align.MIN)).translate((X_VANO0, 0, Z_PAV))
    s += Box(X_VANO1 - X_VANO0 + 1.0, W_GUIDA, H_GUIDA + 0.5, align=(Align.MIN, Align.CENTER, Align.MIN)) \
        .translate((X_VANO0 - 0.5, 0, Z_PAV - 0.5))
    # meccanica: sede della canna, foro del percussore nello scudo
    s -= M.vuoto_canna()
    s -= M._cil_x(MEC.D_PERC_FORO, MEC.X_SCUDO - 0.1, MEC.T_SCUDO + 0.2)
    # vani del meccanismo, calcolati da meccanismo.py sulla sagoma del banco (come per il telaio)
    vani = MEC.vani_telaio(banco2d, Polygon(), vano_dito, lambda x, z: W2, z_cima, W)
    for w, g in vani.items():
        s -= MEC.estrudi(g, w)
    s -= MEC.estrudi(camino2d, MEC.SLOT_CANE)
    s -= MEC.foro_spine()
    # viti M3: foro passante, testa incassata a sinistra (+Y), dado esagonale a destra (-Y)
    for vx, vz in VITI:
        s -= Pos(vx, 0, vz) * Rot(90, 0, 0) * Cylinder(D_VITE / 2, W + 2)
        s -= Pos(vx, W2 - H_TESTA / 2 + 0.01, vz) * Rot(90, 0, 0) * Cylinder(D_TESTA / 2, H_TESTA)
        esag = Polygon([(vx + CH_DADO / math.sqrt(3) * math.cos(math.radians(60 * i)),
                         vz + CH_DADO / math.sqrt(3) * math.sin(math.radians(60 * i))) for i in range(6)])
        s -= F.prisma(esag, -W2 - 0.01, -W2 + H_DADO)
    return s


def _blocco_camera(interf=0.10, n_tacche=0):
    """Blocco con una sola camera, guidato dalla costola. Come il blocco camera_c del provino:
    in fondo (lato scudo) una FASCIA DI TRATTENUTA stretta di `interf` sul diametro tiene la
    cartuccia per attrito, poi il foro si allarga come le camere del tamburo. Le tacche in cima
    dicono quale variante di interferenza e'."""
    from build123d import Cone
    b = Box(q.L_tamb, W, Z_BLOCCO_ALTO - Z_PAV, align=(Align.MIN, Align.CENTER, Align.MIN)).translate((q.x_cam, 0, Z_PAV))
    b -= Box(q.L_tamb + 1, W_GUIDA + 0.5, H_GUIDA + 0.3, align=(Align.MIN, Align.CENTER, Align.MIN)) \
        .translate((q.x_cam - 0.5, 0, Z_PAV - 0.01))
    d_fascia = p.cart_D - interf + p.comp_foro_v
    b -= M._cil_x(d_fascia, q.x_cam - 0.1, q.L_tamb + 0.2)                                  # fascia di trattenuta
    b -= M._cil_x(q.camera_d, q.x_cam + p.cart_fascia + 0.5, q.L_tamb)                      # poi il foro si allarga
    b -= Pos(q.x_cam - 0.01, 0, 0) * Rot(0, 90, 0) * Cone((p.cart_D + 0.8) / 2, d_fascia / 2, 0.5,
                                                         align=(Align.CENTER, Align.CENTER, Align.MIN))   # invito
    # presa per le dita: due incavi sui fianchi in alto
    for s in (1, -1):
        b -= Pos(q.x_cam + q.L_tamb / 2, s * (W2 + 3.0), Z_BLOCCO_ALTO - 4.5) * Rot(0, 90, 0) * Cylinder(4.5, q.L_tamb + 1)
    for i in range(n_tacche):
        b -= Pos(q.x_cam + q.L_tamb / 2 + (i - (n_tacche - 1) / 2) * 3, 0, Z_BLOCCO_ALTO) * Cylinder(0.75, 1.2)
    return b


def _distanziale(t):
    return Cylinder(MEC.D_PIST / 2, t, align=(Align.CENTER, Align.CENTER, Align.MIN))


def _a_terra(s):
    bb = s.bounding_box()
    return s.translate((-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -bb.min.Z))


def _sdraiato(s):
    """Pezzo piatto nel piano XZ: lo si stende sul piano di stampa."""
    return _a_terra(s.rotate(Axis.X, -90))


if __name__ == "__main__":
    import json
    import time
    t0 = time.time()
    qui = os.path.dirname(os.path.abspath(__file__))
    d_st, d_as = os.path.join(qui, "stl", "banco", "stampa"), os.path.join(qui, "stl", "banco", "assieme")
    os.makedirs(d_st, exist_ok=True)
    os.makedirs(d_as, exist_ok=True)

    banco = _banco()
    print(f"[{time.time() - t0:5.1f} s] banco: valido {banco.is_valid}", flush=True)
    meta_sx = Box(500, 100, 500, align=(Align.CENTER, Align.MIN, Align.CENTER))
    guscio_sx, guscio_dx = banco & meta_sx, banco - meta_sx
    blocchi = [_blocco_camera(i, k + 1) for k, i in enumerate(p.interf_c)]     # 1, 2, 3 tacche
    blocco = blocchi[1]
    cane, grilletto, rullino = MEC.cane(), MEC.grilletto(), MEC.rullino()
    percussore, coppa, pistone = MEC.percussore(), MEC.coppa(), MEC.pistone()
    canna = M.canna()

    assieme = {"guscio_sx": guscio_sx, "guscio_dx": guscio_dx, "blocco_camera": blocco, "cane": cane,
               "grilletto": grilletto, "rullino": rullino, "percussore": percussore, "coppa": coppa,
               "pistone": pistone, "distanziale_4": MEC.distanziale(), "canna": canna}
    colori = {"guscio_sx": "#4fa89a", "guscio_dx": "#8fd0c4", "blocco_camera": "#d9a441", "cane": "#d9a441",
              "grilletto": "#d9a441", "rullino": "#f2e3c6", "percussore": "#f2e3c6", "coppa": "#f2e3c6",
              "pistone": "#f2e3c6", "distanziale_4": "#f2e3c6", "canna": "#4fa89a"}
    for n, s in assieme.items():
        if not s.is_valid:
            print("ATTENZIONE: pezzo non valido:", n)
        export_stl(s, os.path.join(d_as, n + ".stl"))
    json.dump(colori, open(os.path.join(d_as, "colori.json"), "w"), indent=1)

    # --- orientati per la stampa ---
    stampa = {
        # gusci: faccia esterna sul piano, vani aperti verso l'alto (niente ponti, niente supporti)
        "guscio_sx": _a_terra(guscio_sx.rotate(Axis.X, -90)),
        "guscio_dx": _a_terra(guscio_dx.rotate(Axis.X, 90)),
        "cane": _sdraiato(cane), "grilletto": _sdraiato(grilletto), "pistone": _sdraiato(pistone),
        "rullino": _a_terra(rullino.rotate(Axis.X, 90)),
        # asse verticale: fori e steli tondi escono meglio
        "percussore": _a_terra(percussore.rotate(Axis.Y, -90)),          # in piedi sul collare
        "canna": _a_terra(canna.rotate(Axis.Y, -90)),
        "coppa": _a_terra((Rot(0, -MEC.ANG_MOLLA, 0) * Pos(-MEC.B_COPPA[0], 0, -MEC.B_COPPA[1]) * coppa)),
    }
    for k, b_ in enumerate(blocchi):      # lato scudo in basso: la fascia stretta e' la prima a stamparsi
        stampa[f"blocco_camera_v{k + 1}"] = _a_terra(b_.rotate(Axis.Y, -90))
    for t in (0.5, 1, 2, 4, 8):
        stampa[f"distanziale_{t:g}mm"] = _distanziale(t)
    for n, s in stampa.items():
        export_stl(s, os.path.join(d_st, n + ".stl"))
    print(f"[{time.time() - t0:5.1f} s] export: {len(stampa)} pezzi in stl/banco/stampa, {len(assieme)} in stl/banco/assieme")
    print("viti M3 (x, z):", [(round(x, 1), round(z, 1)) for x, z in VITI])
    print(f"spine: cane d{MEC.D_PERNO:g} x {W:g}, grilletto d{MEC.D_PERNO_G:g} x {W:g}; perno rullino: filamento 1.75 x {MEC.SP_GRIL - 0.2:g}")

    # --- disegno laterale ---
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(13, 10))

    def dr(g, **k):
        for pg in MEC.poligoni(g):
            ax.fill(*pg.exterior.xy, **k)
    dr(banco2d.difference(vano_blocco2d), fc="#bfe3dc", ec="k", lw=1.2)
    dr(MEC.vano_molla, fc="#88f", alpha=.35)
    dr(MEC.vano_gril, fc="#fc8", alpha=.4)
    dr(MEC.vano_cane.union(camino2d).intersection(banco2d), fc="#f88", alpha=.3)
    dr(MEC.cane_pose(0), fc="none", ec="k", lw=1.3)
    dr(MEC.cane_pose(MEC.ANG_ARMO), fc="none", ec="k", lw=.6, ls=":")
    dr(MEC.gril_pose(MEC.PHI_CAMMA), fc="none", ec="brown", lw=1.3)
    ax.add_patch(plt.Rectangle((q.x_cam, Z_PAV), q.L_tamb, Z_BLOCCO_ALTO - Z_PAV, fc="#d9a441", ec="k", alpha=.8))
    ax.add_patch(plt.Rectangle((q.x_sede, -p.canna_D / 2), p.canna_L, p.canna_D, fc="none", ec="g"))
    for vx, vz in VITI:
        ax.add_patch(plt.Circle((vx, vz), D_TESTA / 2, fc="w", ec="k"))
        ax.plot(vx, vz, "k+")
    ax.set_aspect("equal")
    ax.grid(True, alpha=.3)
    fig.savefig(os.path.join(qui, "stl", "banco", "banco.png"), dpi=60, bbox_inches="tight")
