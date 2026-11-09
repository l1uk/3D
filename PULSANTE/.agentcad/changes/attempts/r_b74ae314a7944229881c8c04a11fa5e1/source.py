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
# Nota: la morbidezza dello spigolo tetto/fianco e' gia' data dalla
# spline della sezione trasversale (vedi arco_trasversale), che arriva
# quasi tangente al fianco. Niente fillet esplicito qui: su questa volta
# a spline il raccordo perimetrale e' fragile e fa fallire lo shell.

# =====================================================================
#  Svuotamento interno (guscio a parete costante)
# =====================================================================
wall    = 1.78   # spessore parete laterale
top_thk = 1.6    # spessore del cielo (STIMA)

guscio_pieno = corpo   # riferimento del volume pieno

# Costruisco la CAVITA' come una copia interna del corpo: stessa volta,
# rimpicciolita di 'wall' sui lati (contorno in pianta offsettato verso
# l'interno) e ribassata di 'top_thk' sotto il cielo. Questo e' robusto
# dove l'offset/shell di OCC fallisce sulla volta a spline.

def plan_wire_inset(delta):
    """Contorno in pianta rientrato di 'delta' (offset 2D verso l'interno)."""
    with BuildSketch(Plane.XY) as s:
        add(plan_wire())
        make_face()
    inner = offset(s.sketch, amount=-delta, kind=Kind.INTERSECTION)
    return inner

# base interna estrusa
cav_sk = plan_wire_inset(wall)
cav = extrude(cav_sk, amount=z_max + 5)

# volta interna: come il tetto ma abbassata di top_thk, cosi' il cielo
# ha spessore costante. Rifaccio il loft delle sezioni traslate in -Z.
cav_sezioni = []
for x in stazioni:
    sec = arco_trasversale(x)
    cav_sezioni.append(sec.moved(Location((0, 0, -top_thk))))
cav_tetto = loft(cav_sezioni)
cav = cav & cav_tetto

# la cavita' deve essere aperta sul fondo: parte sotto z=0
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
    # pernetto interno sotto il cielo: cilindro che parte dalla quota del
    # cielo interno e scende di boss_h nella cavita'. Lo unisco al corpo.
    z_cielo_int = quota_tetto(boss_pos[0], boss_pos[1]) - top_thk
    h_boss = boss_h + 3          # il cilindro risale dentro il cielo
    pilastro = Cylinder(radius=boss_d/2, height=h_boss)
    pilastro = pilastro.translate(
        (boss_pos[0], boss_pos[1], z_cielo_int - h_boss/2 + 0.1))
    corpo = corpo + pilastro

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
    # Ogni bollino = CALOTTA che sporge sopra il tetto. Costruisco una
    # sfera il cui polo e' a dome_h sopra la superficie, poi tengo solo la
    # parte ESTERNA al corpo pieno (sfera - guscio_pieno): resta la calotta
    # emergente, senza invadere la cavita' interna.
    R_dome = (dome_d*dome_d/4 + dome_h*dome_h) / (2*dome_h)

    def quota_reale(px, py):
        """Z della superficie del tetto in (px,py): raggio verticale dall'
        alto verso il basso contro il corpo pieno, primo impatto."""
        ax = Axis((px, py, z_max + 20), (0, 0, -1))
        hits = guscio_pieno.find_intersection_points(ax)
        zs = [p[0].Z for p in hits] if hits else []
        return max(zs) if zs else quota_tetto(px, py)

    calotte = []
    for (px, py) in dome_pos:
        zs = quota_reale(px, py)
        s = Sphere(radius=R_dome).translate((px, py, zs + dome_h - R_dome))
        cal = s - guscio_pieno
        if cal.volume > 1e-3:
            calotte.append(cal)
    if calotte:
        corpo = corpo + sum(calotte[1:], calotte[0])

# =====================================================================
#  Simbolo clacson inciso sul tetto (zona centrale-sinistra)
# =====================================================================
horn       = True
horn_depth = 0.45        # profondita' dell'incisione
horn_pos   = (9.0, 11.2) # origine (bocchino) del simbolo in pianta

def horn_sketch():
    """Profilo 2D stilizzato del clacson: bocchino verticale a sinistra,
    canna orizzontale, campana svasata a destra. Contenuto nella fascia
    centrale tra le file di bollini."""
    ox, oy = horn_pos
    with BuildSketch(Plane.XY) as s:
        with Locations((ox, oy)):
            # bocchino verticale (imboccatura)
            with Locations((0.0, 0.0)):
                Rectangle(1.0, 3.2)
            # canna orizzontale corta
            with Locations((2.3, 0.0)):
                Rectangle(4.0, 1.1)
            # campana svasata a tromba (trapezio contenuto in +/-2.1 in Y)
            with BuildLine():
                Polyline((4.1, -0.7), (7.2, -2.1), (7.2, 2.1),
                         (4.1, 0.7), close=True)
            make_face()
    return s.sketch

if horn:
    sk_h = horn_sketch()
    # prisma verticale del simbolo
    prisma = extrude(sk_h, amount=z_max + 20)
    # colonna piena sotto il simbolo
    colonna = prisma & guscio_pieno
    # guscio abbassato di horn_depth: cio' che sta sopra e' il solco
    giu = guscio_pieno.translate((0, 0, -horn_depth))
    solco = colonna - giu
    if solco.volume > 1e-3:
        corpo = corpo - solco

show_object(corpo)
