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
    t = x / L                        # 0 a sinistra, 1 a destra
    z0, z1 = z_FL + 0.6, z_FR + 1.0  # quote cresta agli estremi
    return z0 + (z1 - z0) * t + 1.0 * (t - t * t)  # leggera convessita'

z_fianco = 2.6    # altezza del fianco quasi verticale prima della cupola
bordo    = 1.2    # rientro in Y dove la cupola comincia a curvare

def quota_tetto(x, y):
    """Stima della quota Z della superficie del tetto in (x,y): cresta al
    centro in Y che cala verso i fianchi come una parabola. Serve a posare
    i bollini sulla cupola."""
    zc = quota_cresta(x)
    yc = H_right / 2.0
    half = H_right / 2.0
    t = (y - yc) / half                       # -1..+1 sui bordi
    t = max(-1.0, min(1.0, t))
    return z_fianco + (zc - z_fianco) * (1 - t * t)

def arco_trasversale(x):
    """Faccia-sezione nel piano YZ alla stazione x: fianchi corti quasi
    verticali raccordati da una cupola piena (spline a cresta larga)."""
    zc = quota_cresta(x)
    y0, y1 = 0.0, H_right
    yc = (y0 + y1) / 2.0
    # quota dove la cupola si innesta sui fianchi
    zf = min(z_fianco, zc - 1.0)
    # spline del cielo: fianco -> spalla -> cresta larga -> spalla -> fianco
    with BuildSketch(Plane.YZ.offset(x)) as s:
        with BuildLine():
            Spline(
                (y0, zf),
                (y0 + bordo + 2.0, zc - 0.25),
                (yc, zc),
                (y1 - bordo - 2.0, zc - 0.25),
                (y1, zf),
            )
            Line((y1, zf), (y1, 0.0))        # fianco destro
            Line((y1, 0.0), (y0, 0.0))       # base
            Line((y0, 0.0), (y0, zf))        # fianco sinistro
        make_face()
    return s.sketch

# costruisco il tetto come loft tra piu' sezioni, poi lo interseco col
# corpo base per ritagliare la silhouette in pianta.
stazioni = [0.001, L * 0.2, L * 0.4, L * 0.6, L * 0.8, L - 0.001]
sezioni = [arco_trasversale(x) for x in stazioni]
tetto = loft(sezioni)

corpo = corpo & tetto

# ---- Raccordo morbido dello spigolo tetto/fianco ----
# Lo spigolo perimetrale in alto (dove la cupola incontra il fianco)
# nell'originale e' arrotondato. Raccordo gli spigoli piu' alti.
r_bordo = 1.2
# raccordo solo lo spigolo perimetrale piu' alto (giro cupola/fianco)
cand = corpo.edges().filter_by_position(
    Axis.Z, z_fianco - 0.3, z_max + 5, inclusive=(True, True))
if cand:
    try:
        corpo = fillet(cand, radius=r_bordo)
    except Exception as e:
        print("fillet bordo saltato:", e)

# =====================================================================
#  Svuotamento interno (guscio a parete costante) + feature
# =====================================================================
wall    = 1.78   # spessore parete
top_thk = 1.6    # spessore del cielo (STIMA)

# Cavita': copia del guscio ridotta verso l'interno, aperta sul fondo.
# Uso offset negativo della sola faccia inferiore come apertura -> shell.
guscio_pieno = corpo
bottom_face = corpo.faces().sort_by(Axis.Z)[0]   # faccia inferiore (z=0)
try:
    corpo = offset(corpo, amount=-wall, openings=bottom_face)
except Exception as e:
    print("shell fallito, uso cavita' booleana:", e)
    # fallback: sottraggo una copia rimpicciolita
    cav = scale(guscio_pieno, (1 - 2*wall/L, 1 - 2*wall/H_right, 1))
    cav = cav.translate((wall, wall, -1.0))
    corpo = guscio_pieno - cav

from math import cos, sin, pi

# =====================================================================
#  Clip a scatto (4, agli angoli, orientate in diagonale)
# =====================================================================
clip_len    = 9.0    # lunghezza gamba sotto il guscio
clip_w_top  = 4.3    # larghezza gamba all'attacco
clip_w_bot  = 3.17   # larghezza gamba in punta
clip_thk    = 2.12   # spessore gamba
clip_depth  = 3.11   # profondita' totale gamba + dente
hook_h      = 2.54   # altezza del dente
clip_ang    = [225, 315, 45, 135]   # orientamento dente: BL, BR, TR, TL
clip_inset  = 0.6    # rientro verso l'interno rispetto all'angolo

def clip_solid():
    """Clip orientata: gamba lungo -Z, dente che sporge verso +X locale.
    Costruita all'origine, verra' posizionata e ruotata agli angoli."""
    # gamba rastremata: loft tra sezione in alto e in basso
    with BuildSketch(Plane.XY.offset(0.0)) as s_top:
        with Locations((-clip_thk/2, 0)):
            Rectangle(clip_thk, clip_w_top)
    with BuildSketch(Plane.XY.offset(-clip_len)) as s_bot:
        with Locations((-clip_thk/2, 0)):
            Rectangle(clip_thk, clip_w_bot)
    gamba = loft([s_top.sketch, s_bot.sketch])

    # dente a uncino in punta: profilo laterale nel piano XZ, estruso in Y
    p = clip_depth - clip_thk
    with BuildSketch(Plane.XZ) as s_hook:
        with BuildLine():
            pts = [(-clip_thk/2, -clip_len)]
            # faccia esterna curva (quarto d'arco) dal fondo gamba in su
            n = 8
            for i in range(n + 1):
                t = (pi/2) * i / n
                pts.append((p * sin(t), -clip_len + (hook_h) * (1 - cos(t))))
            pts.append((-clip_thk/2, -clip_len + hook_h))
            Polyline(*pts, close=True)
        make_face()
    dente = extrude(s_hook.sketch, amount=clip_w_bot/2, both=True)
    return gamba + dente

clip0 = clip_solid()

# Posiziona le 4 clip: ogni clip sta appena DENTRO la parete, vicino
# all'angolo, con il dente rivolto verso l'esterno in diagonale.
# Il centro del cerchio di raccordo di ciascun angolo:
#   BL: (+r,+r)  BR: (-r,+r)  TR: (-r,-r)  TL: (+r,-r)  rispetto al vertice.
segni = [(+1, +1), (-1, +1), (-1, -1), (+1, -1)]   # verso l'interno
clips = []
for (cx, cy), r, a, (sx, sy) in zip(corner_pts, corner_r, clip_ang, segni):
    ar = a * pi / 180.0
    cen = (cx + sx * r, cy + sy * r)             # centro del raccordo
    # attacco della gamba: sul raccordo, rientrato di clip_thk cosi' la
    # faccia esterna del dente sfiora la parete interna del guscio
    d = r - clip_thk - clip_inset
    hook_pt = (cen[0] + d * cos(ar), cen[1] + d * sin(ar))
    c = clip0.rotate(Axis.Z, a)
    c = c.translate((hook_pt[0], hook_pt[1], 0))
    clips.append(c)

corpo = corpo + sum(clips[1:], clips[0])

# =====================================================================
#  Boss centrale interno (pernetto che preme il contatto)
# =====================================================================
boss     = True
boss_d   = 8.0
boss_h   = 3.0          # quanto sporge dal cielo verso il basso (interno)
boss_pos = (20.0, 11.0)
if boss:
    # cilindro che parte dal cielo interno e scende nella cavita';
    # lo interseco con il corpo pieno per ancorarlo alla volta
    pilastro = Cylinder(radius=boss_d/2, height=20).translate(
        (boss_pos[0], boss_pos[1], 0))
    # tengo solo la parte entro il guscio pieno e sotto il cielo interno
    inner_solid = guscio_pieno  # riferimento della volta
    tappo = pilastro & inner_solid
    # lo abbasso: voglio un bottoncino che scende di boss_h dal cielo
    corpo = corpo + (tappo & guscio_pieno)

# =====================================================================
#  Bollini in rilievo sul tetto (griglia come nell'originale)
# =====================================================================
domes   = True
dome_d  = 3.8
dome_h  = 0.7
dome_pos = [
    (7.6,16.4),(13.2,17.4),(19.0,17.4),(24.8,16.8),(30.6,15.9),
    (6.0,11.0),(26.4,11.2),(32.6,10.6),
    (8.6,5.2),(14.8,4.6),(21.0,4.6),(27.2,4.6),(33.2,5.0),
]
if domes:
    # Ogni bollino = calotta sferica. Centro la sfera cosi' che il suo
    # polo sporga di dome_h oltre la superficie stimata; unisco al corpo.
    # L'eccesso che rientrasse nel guscio non crea problemi (e' gia' pieno).
    R_dome = (dome_d*dome_d/4 + dome_h*dome_h) / (2*dome_h)
    rilievi = []
    for (px, py) in dome_pos:
        zs = quota_tetto(px, py)
        # polo della sfera a zs + dome_h  ->  centro a polo - R_dome
        s = Sphere(radius=R_dome).translate((px, py, zs + dome_h - R_dome))
        rilievi.append(s)
    # unisco tutte le sfere, poi tengo solo cio' che sta sopra la
    # superficie reale: (sfere + corpo) ma ritagliato per non gonfiare
    # l'interno. Uso l'unione diretta: la sfera interseca il tetto pieno
    # e aggiunge solo la piccola calotta che emerge.
    bolle = sum(rilievi[1:], rilievi[0])
    corpo = corpo + bolle

show_object(corpo)
