# PROFILI 2D DEL DESIGN (piano XZ di build.py) - sagoma del revolver, senza solidi.
#
# Qui si disegna la SILHOUETTE: telaio, impugnatura, ponticello, guancette. Sono solo poligoni
# shapely (niente build123d), quindi il file gira in un attimo: si itera qui sulla forma
# guardando il disegno 2D (python profili.py -> stl/profili.png), poi build.py ne fa i solidi.
#
# DESIGN E MECCANISMO SONO SEPARATI. Dal meccanismo si legge solo la sua INTERFACCIA
# (meccanismo.py, sezione "INTERFACCIA COL DESIGN"): gli ingombri da chiudere nel telaio, l'asse
# della molla (= asse del manico), la lama del grilletto, lo scudo. La sagoma NON ha coordinate
# fisse nella zona del meccanismo: ogni punto e' "ingombro + qualcosa", dove il qualcosa e' una
# costante di STILE qui sotto. Se la cinematica cambia, la sagoma la segue da sola; se si cambia
# lo stile, la parete attorno al meccanismo (MARGINE) resta garantita perche' l'ingombro viene
# comunque unito alla sagoma.
#
# La forma e' quella della reference (riferimenti/side.png): revolver a telaio chiuso, cinghia
# superiore dritta, cane a vista sopra una sella che scende alla gobba, gobba il piu' possibile
# vicina al tamburo, dorso inclinato come la molla, calcio "a testa d'uccello", ponticello ovale.
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely import affinity  # noqa: E402
from shapely.geometry import LineString, Point, Polygon, box  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

import meccanica as M  # noqa: E402
import meccanismo as MEC  # noqa: E402

p, q = M.p, M.q
ZA = q.z_asse_tamb

# =====================================================================
# STILE: tutte le scelte estetiche stanno qui
# =====================================================================
W = 22.0                    # larghezza del telaio (fianchi piani, spigoli tondi)
MARGINE = 2.4               # parete minima fra gli ingombri del meccanismo e l'esterno
# --- davanti: tamburo e canna (quote da meccanica.py) ---
Z_TETTO = ZA + q.finestra_R + 4.2    # cinghia superiore: una linea dritta dal cane al mirino
Z_SOTTO = ZA - q.finestra_R - 4.3    # sotto del telaio (sotto il tamburo e sopra il grilletto)
CANNA_VISTA = 32.0          # canna oltre la sede (q.L_tel)
L_VOLATA = 8.0              # tappo arancione (concetti.volata)
L_TESTA_PERNO = 3.5         # testa zigrinata del perno del tamburo, sotto la canna
W_CAMICIA = 20.0            # camicia della canna: a fianchi piani come nella reference, un filo piu' stretta del telaio
ABBASSA_CAMICIA = 1.3       # la camicia sta sotto la cinghia di tanto; la linea la continua la bindella
L_FAZZOLETTO = 15.0         # il sotto della camicia scende in diagonale verso il telaio per questa lunghezza
R_ALLOGGIO = 7.0            # alloggio tondo del perno del tamburo, sotto la canna
W_BINDELLA = 6.5            # bindella (nervatura piatta) sopra la canna
# --- sella e gobba (dietro lo scudo) ---
L_CINGHIA_DIETRO = 4.0      # la cinghia superiore prosegue di tanto dietro lo scudo
# sella: (frazione del tratto gobba -> cinghia, frazione del dislivello). Una discesa continua
# dalla cinghia alla gobba, appena concava: passa giusto sopra la corsa del percussore, cosi' la
# gobba e' una spalla netta dove il dorso cambia direzione, senza ondulazioni.
SELLA_STILE = [(1.0, 1.0), (0.84, 0.80), (0.66, 0.665), (0.48, 0.575), (0.30, 0.50), (0.13, 0.44)]
ALZO_SELLA = 0.3            # la sella non scende mai sotto gli ingombri chiusi + questo
ALZO_GOBBA = 6.0            # altezza della gobba sopra la cima della sede molla
# --- dorso dell'impugnatura: (ascissa s lungo l'asse del manico, mm oltre l'ingombro) ---
GONFIA_DORSO = [(5.0, 1.6), (10.0, 0.8), (17.0, 0.2), (27.0, 0.8), (39.0, 2.6), (51.0, 4.6), (62.0, 5.6)]   # pancia verso il tallone
# --- calcio a testa d'uccello ---
ALLUNGO_CALCIO = 12.0       # di quanto il calcio prosegue sotto il meccanismo
PUNTA_CALCIO = 6.5          # di quanto la punta (davanti) sporge oltre il frontale
# --- frontale dell'impugnatura: (s contata dal fondo del meccanismo, mm oltre l'ingombro) ---
GONFIA_FRONTE = [(-9.0, 7.0), (-15.0, 4.6), (-22.0, 3.4), (-29.0, 3.6)]
# --- ponticello: ovale (due cerchi e il loro inviluppo) attorno alla lama del grilletto ---
PONT_R1, PONT_R2 = 11.2, 10.2
PONT_DIETRO_LAMA = 5.0      # centro del cerchio posteriore, davanti al bordo posteriore della lama
PONT_DAVANTI_LAMA = 10.0    # centro del cerchio anteriore, oltre il bordo anteriore della lama
T_PONT = 3.8                # spessore dell'anello
W_PONT = 9.0                # larghezza Y dell'anello (piu' stretto del telaio)
# --- guancette ---
RIENTRO_G = 1.8             # bordo del telaio a vista attorno alla guancetta
S_GUANCIA = 12.0            # la guancetta comincia a quest'ascissa lungo il dorso


def curva(pts, n=10, chiusa=False):
    """Curva liscia per i punti dati (Catmull-Rom centripeta), campionata n volte per tratto."""
    P = list(pts)
    if chiusa:
        P = [P[-1]] + P + P[:2]
    else:
        P = [(2 * P[0][0] - P[1][0], 2 * P[0][1] - P[1][1])] + P + \
            [(2 * P[-1][0] - P[-2][0], 2 * P[-1][1] - P[-2][1])]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        t0 = 0.0
        t1 = t0 + math.dist(p0, p1) ** 0.5
        t2 = t1 + math.dist(p1, p2) ** 0.5
        t3 = t2 + math.dist(p2, p3) ** 0.5
        for k in range(n):
            t = t1 + (t2 - t1) * k / n
            c = []
            for a in (0, 1):
                A1 = (t1 - t) / (t1 - t0) * p0[a] + (t - t0) / (t1 - t0) * p1[a]
                A2 = (t2 - t) / (t2 - t1) * p1[a] + (t - t1) / (t2 - t1) * p2[a]
                A3 = (t3 - t) / (t3 - t2) * p2[a] + (t - t2) / (t3 - t2) * p3[a]
                B1 = (t2 - t) / (t2 - t0) * A1 + (t - t0) / (t2 - t0) * A2
                B2 = (t3 - t) / (t3 - t1) * A2 + (t - t1) / (t3 - t1) * A3
                c.append((t2 - t) / (t2 - t1) * B1 + (t - t1) / (t2 - t1) * B2)
            out.append(tuple(c))
    if not chiusa:
        out.append(tuple(P[-2]))
    return out


def tondo(g, r):
    """Raccorda con raggio r gli spigoli convessi e concavi di una sagoma."""
    return g.buffer(-r, 24).buffer(2 * r, 24).buffer(-r, 24)


# =====================================================================
# INTERFACCIA COL MECCANISMO (solo questi nomi di meccanismo.py)
# =====================================================================
_O, _U, _NF = MEC.CIMA0, MEC.U, MEC.NF          # asse della molla = asse del manico
X_SCUDO = MEC.X_SCUDO
# ingombro da chiudere nel telaio, gia' con la parete attorno; "lisciato" per non copiare nella
# sagoma gli spigoli e le gole dei singoli pezzi
_ingombro = unary_union([MEC.INGOMBRO_CHIUSO, MEC.INGOMBRO_PERCUSSORE]).buffer(MARGINE, 24)
ingombro = _ingombro.buffer(5.0, 24).buffer(-5.0, 24)


def xz(s, d):
    """Dal riferimento del manico (s lungo l'asse verso il calcio, d di traverso verso il davanti) a XZ."""
    return (_O[0] - _U[0] * s + _NF[0] * d, _O[1] - _U[1] * s + _NF[1] * d)


# lo stesso ingombro nel riferimento del manico (s, d)
_ing_sd = affinity.affine_transform(affinity.translate(ingombro, -_O[0], -_O[1]),
                                    [-_U[0], -_U[1], _NF[0], _NF[1], 0, 0])
S_FONDO_MEC = _ing_sd.bounds[2]                 # ascissa del fondo del meccanismo (con la parete)


def _fascia(s):
    g = _ing_sd.intersection(box(s - 1.0, -300, s + 1.0, 300))
    return g.bounds[1], g.bounds[3]


def d_dietro(s):
    """Limite posteriore dell'ingombro all'ascissa s del manico."""
    return _fascia(min(s, S_FONDO_MEC - 1.5))[0]


def d_davanti(s):
    """Limite anteriore dell'ingombro all'ascissa s del manico."""
    return _fascia(min(s, S_FONDO_MEC - 1.5))[1]


def z_ingombro(x):
    """Quota piu' alta dell'ingombro chiuso alla coordinata x (-inf se non c'e')."""
    g = ingombro.intersection(LineString([(x, -500), (x, 500)]))
    return -math.inf if g.is_empty else g.bounds[3]


# =====================================================================
# QUOTE DERIVATE
# =====================================================================
X_BOCCA = q.L_tel + CANNA_VISTA
X_CAMICIA1 = X_BOCCA - (L_VOLATA - 1.5) - L_TESTA_PERNO - 1.0   # fine della camicia della canna
X_FRONTE = q.x_spal + 7.4   # frontale del telaio sotto la canna (davanti al tamburo)

# ---------------- vano del ponticello (dove sta il dito) ----------------
_lama = MEC.VANO_LAMA.intersection(box(-300, -300, 300, Z_SOTTO))      # la lama che esce sotto il telaio
PONT_C1 = (_lama.bounds[0] + PONT_DIETRO_LAMA, Z_SOTTO + 0.4 - PONT_R1)
PONT_C2 = (_lama.bounds[2] + PONT_DAVANTI_LAMA, Z_SOTTO + 0.4 - PONT_R2)
vano_ponticello = unary_union([Point(PONT_C1).buffer(PONT_R1, 48),
                               Point(PONT_C2).buffer(PONT_R2, 48)]).convex_hull

# ---------------- sagoma del telaio ----------------
# gobba: subito dietro e sopra la cima della sede della molla
_s_cima = affinity.affine_transform(affinity.translate(MEC.vano_molla, -_O[0], -_O[1]),
                                    [-_U[0], -_U[1], _NF[0], _NF[1], 0, 0]).bounds[0] - MARGINE   # cima della sede molla
GOBBA = xz(_s_cima - ALZO_GOBBA, d_dietro(0.0) + 1.2)
# sella: dalla cinghia (dietro lo scudo) scende e risale alla gobba; il cane resta a vista sopra
_x0s, _x1s = GOBBA[0], X_SCUDO - L_CINGHIA_DIETRO
_zb = GOBBA[1] - ALZO_GOBBA                      # quota di base: la cima della sede molla
SELLA = [(_x0s + (_x1s - _x0s) * u, max(_zb + (Z_TETTO - _zb) * f, z_ingombro(_x0s + (_x1s - _x0s) * u) + ALZO_SELLA))
         for u, f in SELLA_STILE] + [GOBBA]
# dorso dell'impugnatura: l'ingombro (la molla) + una bombatura leggera verso il tallone
DORSO = [xz(s, d_dietro(s) - e) for s, e in GONFIA_DORSO]
# calcio a testa d'uccello: tallone tondo, fondo che scende verso la punta
_sf = S_FONDO_MEC + ALLUNGO_CALCIO
_db = d_dietro(S_FONDO_MEC - 8) - GONFIA_DORSO[-1][1]
_df = d_davanti(S_FONDO_MEC - 8) + GONFIA_FRONTE[0][1] + PUNTA_CALCIO - 3.0
CALCIO = [xz(_sf - 11.5, _db + 0.2), xz(_sf - 4.4, _db + 2.9), xz(_sf - 0.2, _db + 8.5), xz(_sf, _db + 16.3),
          xz(_sf - 2.3, _df - 18.5), xz(_sf - 5.3, _df - 8.5), xz(_sf - 8.0, _df - 2.6), xz(_sf - 12.5, _df),
          xz(_sf - 16.0, _df - 0.4)]
# frontale dell'impugnatura: sale fino alla radice del ponticello (li' la sagoma e' il vano del dito)
FRONTE = [xz(S_FONDO_MEC + s, d_davanti(S_FONDO_MEC + s) + e) for s, e in GONFIA_FRONTE] + \
    [(PONT_C1[0] - 17.5, PONT_C1[1] - 12.7), (PONT_C1[0] - 12.1, PONT_C1[1] - 10.1), (PONT_C1[0] - 8.0, PONT_C1[1] - 7.2)]
_contorno = (
    curva(SELLA + DORSO + CALCIO + FRONTE, 10)
    + [(PONT_C1[0] - 1.5, Z_SOTTO - 4), (PONT_C1[0] - 1.5, Z_SOTTO),   # (dentro il vano del dito)
       (X_FRONTE, Z_SOTTO), (X_FRONTE, Z_TETTO)])                      # sotto il tamburo, frontale
# l'ingombro del meccanismo e' comunque dentro: lo stile puo' solo aggiungere
telaio2d = tondo(Polygon(_contorno).buffer(0).union(ingombro).difference(vano_ponticello), 2.5)

# ---------------- feritoia del cane, aperta verso l'alto ----------------
# La parte del cane che non e' ingombro chiuso (cresta, collo, sperone, in tutte le pose) esce dal
# dorso: sopra di lei il telaio si apre fino in cima. Senza questo, dove il cane sfiora la sagoma
# resterebbe un velo di materiale di pochi centesimi sopra la feritoia.
_cane_aperto = MEC.vano_cane.difference(_ingombro)
camino_cane2d = unary_union([affinity.translate(_cane_aperto, 0, 0.25 * k) for k in range(0, 161)]) \
    .buffer(0.15, 8).buffer(-0.15, 8).simplify(0.03)

# ---------------- camicia della canna ----------------
# davanti al frontale: un blocco a fianchi piani che avvolge canna e perno del tamburo (sotto),
# come nella reference. Il sotto risale in diagonale dal telaio (fazzoletto); sopra corre la
# bindella, che continua la linea della cinghia fino al mirino.
_z_all = ZA - R_ALLOGGIO
camicia2d = tondo(Polygon([(X_FRONTE - 3.0, Z_TETTO - ABBASSA_CAMICIA), (X_CAMICIA1, Z_TETTO - ABBASSA_CAMICIA),
                           (X_CAMICIA1, _z_all), (X_FRONTE + L_FAZZOLETTO, _z_all),
                           (X_FRONTE - 3.0, Z_SOTTO + 3.0)]), 2.0)
# (0.4 sotto la cinghia: a filo le due facce coincidono e l'unione dei solidi fallisce)
_z_bind = Z_TETTO - 0.4
bindella2d = Polygon([(X_FRONTE - 3.0, Z_TETTO - ABBASSA_CAMICIA - 1.0), (X_FRONTE - 3.0, _z_bind),
                      (X_CAMICIA1 - 2.0, _z_bind), (X_CAMICIA1 - 0.8, Z_TETTO - ABBASSA_CAMICIA - 1.0)])

# ---------------- ponticello ----------------
ponticello2d = vano_ponticello.buffer(T_PONT, 48).difference(vano_ponticello)
ponticello2d = ponticello2d.difference(box(-200, Z_SOTTO - 0.5, 200, 200))   # sopra c'e' il telaio

# ---------------- guancette ----------------
# coprono l'impugnatura fino a un bordo lasciato a vista; in alto finiscono su una linea obliqua,
# dal dorso sotto la gobba (dietro) alla radice del ponticello (davanti), come nella reference
G_ALTO_DIETRO = xz(S_GUANCIA, d_dietro(S_GUANCIA))
G_ALTO_DAVANTI = (PONT_C1[0] - 9.5, PONT_C1[1] - 3.7)
_dx, _dz = G_ALTO_DAVANTI[0] - G_ALTO_DIETRO[0], G_ALTO_DAVANTI[1] - G_ALTO_DIETRO[1]
_A = (G_ALTO_DIETRO[0] - 0.5 * _dx, G_ALTO_DIETRO[1] - 0.5 * _dz)
_B = (G_ALTO_DAVANTI[0] + 0.5 * _dx, G_ALTO_DAVANTI[1] + 0.5 * _dz)
_sotto_linea = Polygon([_A, _B, (_B[0] + 4 * _dz, _B[1] - 4 * _dx), (_A[0] + 4 * _dz, _A[1] - 4 * _dx)])
# il bordo alto non e' una retta ma un arco che sale verso il telaio (come la guancetta della reference)
_Lg = math.hypot(_dx, _dz)
_Rg = 2.6 * _Lg
_hg = math.sqrt(_Rg ** 2 - (_Lg / 2) ** 2)
_cg = ((G_ALTO_DIETRO[0] + G_ALTO_DAVANTI[0]) / 2 + _dz / _Lg * _hg, (G_ALTO_DIETRO[1] + G_ALTO_DAVANTI[1]) / 2 - _dx / _Lg * _hg)
_sotto_linea = _sotto_linea.union(Point(_cg).buffer(_Rg, 96))
guancia2d = tondo(telaio2d.buffer(-RIENTRO_G, 24).intersection(_sotto_linea), 4.0)
campo_zigrino2d = guancia2d.buffer(-5.0, 16)       # campo zigrinato dentro la guancetta
ASSE_MANICO = (-_U[0], -_U[1])                     # direzione dell'asse del manico, verso il calcio


def z_cima(x):
    """Quota piu' alta della sagoma del telaio alla coordinata x (None se fuori)."""
    g = telaio2d.intersection(LineString([(x, -500), (x, 500)]))
    return None if g.is_empty else g.bounds[3]


def verifica():
    """Area [mm^2] degli ingombri chiusi del meccanismo (con MARGINE di parete) che escono dalla
    sagoma. Deve essere zero: lo e' per costruzione, salvo dove il vano del dito li taglia."""
    return _ingombro.difference(telaio2d.union(ponticello2d).buffer(0.05))


def misure():
    """Le misure che dicono se la sagoma e' compatta (per confrontare le iterazioni)."""
    dorso_x = lambda z: telaio2d.intersection(box(-300, z - 0.5, 300, z + 0.5)).bounds[0]   # noqa: E731
    alto = telaio2d.intersection(box(-300, -12, X_SCUDO, 50))
    return {"scudo -> gobba [mm]": X_SCUDO - alto.bounds[0],
            "grilletto -> dorso [mm]": _lama.bounds[2] - dorso_x(PONT_C1[1]),
            "spessore manico [mm]": (d_davanti(40) + 4.8) - (d_dietro(40) - 1.4),
            "lunghezza [mm]": X_BOCCA + 1.5 - telaio2d.bounds[0],
            "altezza [mm]": Z_TETTO - telaio2d.bounds[1]}


def disegna(path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(15, 11))

    def dr(g, **k):
        for pg in MEC.poligoni(g):
            x, z = pg.exterior.xy
            ax.fill(x, z, **k)
            for h in pg.interiors:
                hx, hz = h.xy
                ax.fill(hx, hz, fc="white", ec=k.get("ec"))
    dr(MEC.cane_pose(0).difference(telaio2d), fc="#d9a441", ec="k", lw=1.0)   # il cane si vede solo sopra la sella
    dr(telaio2d, fc="#4fa89a", ec="k", lw=1.2)
    dr(ponticello2d, fc="#4fa89a", ec="k", lw=1.2)
    dr(camicia2d, fc="#4fa89a", ec="k", lw=1.2)
    dr(bindella2d, fc="#4fa89a", ec="k", lw=1.2)
    dr(guancia2d, fc="#f2e3c6", ec="k", lw=1.0)
    ax.add_patch(plt.Rectangle((q.x_cam, ZA - q.R_tamb), q.L_tamb, 2 * q.R_tamb, fc="#d9a441", ec="k"))
    ax.add_patch(plt.Rectangle((MEC.X_SCUDO, ZA - q.R_tamb - 1), MEC.T_SCUDO, 2 * q.R_tamb + 2, fc="#4fa89a", ec="k"))
    ax.add_patch(plt.Rectangle((X_CAMICIA1, -7.5), X_BOCCA - X_CAMICIA1, 15, fc="#4fa89a", ec="k"))
    ax.add_patch(plt.Rectangle((X_BOCCA - L_VOLATA + 1.5, -9.5), L_VOLATA, 19, fc="#ff7a00", ec="k"))
    ax.add_patch(plt.Rectangle((X_CAMICIA1 + 0.3, ZA - 4.5), L_TESTA_PERNO, 9, fc="#d9a441", ec="k"))
    dr(MEC.cane_pose(0), fc="none", ec="k", lw=.5)
    dr(MEC.cane_pose(MEC.ANG_ARMO), fc="none", ec="k", lw=.6, ls=":")
    dr(MEC.gril_pose(MEC.PHI_CAMMA).intersection(vano_ponticello.buffer(3)), fc="#d9a441", ec="k", lw=1.0)
    dr(_ingombro, fc="none", ec="m", lw=.7, ls="--")
    dr(verifica(), fc="red", ec="red")
    ax.set_aspect("equal")
    ax.grid(True, alpha=.3)
    ax.set_xticks(range(-50, 130, 10))
    ax.set_yticks(range(-110, 30, 10))
    fig.savefig(path, dpi=60, bbox_inches="tight")


if __name__ == "__main__":
    f = verifica()
    print(f"ingombri fuori sagoma (margine {MARGINE}): {f.area:.2f} mm^2", "" if f.is_empty else [round(v, 1) for v in f.bounds])
    for k, v in misure().items():
        print(f"  {k:26s} {v:6.1f}")
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl", "profili.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    disegna(out)
    print(out)
