# =====================================================================
#  Copritasto clacson  —  ricostruzione in build123d (B-rep)
#  Obiettivo: silhouette fedele allo schizzo e tetto a volta bombato.
#
#  Sistema di riferimento:
#    X = lato lungo  (0 = lato sinistro basso/stretto)
#    Y = lato corto  (0 = bordo "davanti", in basso nella vista dall'alto)
#    Z = altezza     (0 = bordo inferiore del guscio)
#
#  Fase corrente: SILHOUETTE in pianta, per validare la forma dall'alto
#  prima di curare profilo laterale, cavita' e clip.
# =====================================================================

# ---- Pianta (dallo schizzo quotato, mm) ----
L        = 38.92   # lunghezza totale (X)
H_right  = 23.85   # altezza lato destro (Y)
H_left   = 20.56   # altezza lato sinistro (Y)

# Raggi d'angolo (STIMA da verificare col calibro)
r_BL = 7.0    # basso-sinistra
r_BR = 6.6    # basso-destra
r_TR = 6.5    # alto-destra (il piu' chiuso/appuntito)
r_TL = 9.2    # alto-sinistra (il piu' tondo)

# I 4 vertici vivi del quadrilatero in pianta (senza raccordo)
P_BL = (0.0, 0.0)
P_BR = (L,   0.0)
P_TR = (L,   H_right)
P_TL = (0.0, H_left)
corner_pts = [P_BL, P_BR, P_TR, P_TL]
corner_r   = [r_BL, r_BR, r_TR, r_TL]


def plan_wire():
    """Contorno chiuso in pianta con 4 raggi d'angolo distinti."""
    with BuildLine() as ln:
        Polyline(*corner_pts, close=True)
        # raccorda ogni vertice con il suo raggio; i vertici della
        # Polyline chiusa sono i 4 punti vivi, in ordine
        for p, r in zip(corner_pts, corner_r):
            v = ln.vertices().sort_by_distance(Vector(*p))[0]
            fillet(v, radius=r)
    return ln.line


# ---- Altezze del corpo (dallo schizzo, mm) ----
# Il cielo e' una VOLTA bombata, non un piano inclinato. Quote agli angoli:
z_FL = 6.84    # davanti-sinistra (bordo Y=0, X=0)
z_FR = 10.08   # davanti-destra   (bordo Y=0, X=L)
z_BR = 8.51    # dietro-destra    (bordo Y=H, X=L)
z_BL = 5.3     # dietro-sinistra  (dallo schizzo lato sinistro ~4.9-5.9)

z_max = 11.0   # cresta della volta, un filo sopra z_FR

# ---- Corpo base: estrusione piena della silhouette ----
with BuildSketch(Plane.XY) as sk:
    add(plan_wire())
    make_face()

corpo = extrude(sk.sketch, amount=z_max + 5)

# ---- Volta del tetto ----
# Il cielo e' bombato in due direzioni:
#   - trasversale (Y): porzione di cilindro con asse lungo X
#   - longitudinale (X): piu' alto a destra, piu' basso a sinistra
# Realizzo la volta tagliando il corpo con un grande cilindro il cui
# asse e' parallelo a X. Il raggio R controlla la curvatura trasversale;
# l'inclinazione del cilindro (rotazione attorno a Y) da' il digrado X.

from math import degrees, atan2, sqrt

# Tetto a doppia curvatura realizzato con un LOFT di sezioni trasversali
# ad arco. Per ogni stazione X creo un arco in Y-Z la cui quota di cresta
# segue il profilo longitudinale (campana che sale verso destra). Il loft
# di questi archi da' un tetto bombato sia in X sia in Y, come l'originale.

R_trasv = 17.0    # raggio della curvatura trasversale (in Y) della volta

def quota_cresta(x):
    """Profilo longitudinale della cresta (Z al centro in Y) lungo X.
    Sale da sinistra (basso) a destra (alto) con sommita' arrotondata."""
    t = x / L                       # 0 a sinistra, 1 a destra
    z0, z1 = z_FL + 0.6, z_FR + 1.0  # quote cresta agli estremi
    # curva leggermente convessa: interpolazione con un pizzico di bombatura
    return z0 + (z1 - z0) * t + 1.2 * (t - t * t) * 0

def arco_trasversale(x):
    """Faccia-sezione (arco chiuso) nel piano YZ alla stazione x."""
    zc = quota_cresta(x)
    # larghezza utile in Y a questa X (il contorno in pianta e' quasi
    # dritto sui lati lunghi: uso l'intera H come span, il loft seguira'
    # comunque il contorno grazie all'intersezione col corpo base)
    y0, y1 = 0.0, H_right
    yc = (y0 + y1) / 2.0
    half = (y1 - y0) / 2.0
    # l'arco e' una corda del cerchio di raggio R_trasv con freccia tale
    # che al centro arrivi a zc e ai bordi scenda a z_fianco
    z_base = 0.0
    with BuildSketch(Plane.YZ.offset(x)) as s:
        with BuildLine():
            # arco superiore (convesso) + chiusura in basso
            top = ThreePointArc((y0, z_base), (yc, zc), (y1, z_base))
            Line((y1, z_base), (y0, z_base))
        make_face()
    return s.sketch

# costruisco il tetto come loft tra piu' sezioni, poi lo interseco col
# corpo base per ritagliare la silhouette in pianta.
stazioni = [0.001, L * 0.25, L * 0.5, L * 0.75, L - 0.001]
sezioni = [arco_trasversale(x) for x in stazioni]
tetto = loft(sezioni)

corpo = corpo & tetto

show_object(corpo)
