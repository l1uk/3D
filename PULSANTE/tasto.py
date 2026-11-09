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

# ---- Tetto ----
# Dalla foto di testa (reference/side.png) il cielo NON e' una cupola
# simmetrica: e' una falda inclinata TRASVERSALMENTE.
#   - lato davanti (Y=0) ALTO, spigolo con raccordo stretto
#   - la superficie scende, leggermente bombata, verso il lato dietro
#   - lato dietro (Y=H) BASSO, chiuso da un raccordo ampio ("spalla tonda")
# Longitudinalmente sale da sinistra (X=0) a destra (X=L).
# Lo realizzo come LOFT di sezioni trasversali YZ, una per stazione X,
# ciascuna larga quanto il pezzo in quel punto (il lato dietro e' obliquo).

from math import degrees, atan2, sqrt, pi, sin

r_front   = 1.5    # raggio del raccordo stretto sul lato davanti (mm)
r_back    = 4.5    # raggio del raccordo ampio sul lato dietro (mm)
crown     = 0.4    # bombatura della falda a meta' larghezza (mm)
sporgenza = 0.3    # la sezione deborda dalla pianta, la pianta la rifila

def larghezza(x):
    """Larghezza in Y del pezzo alla stazione x (lato dietro obliquo)."""
    return H_left + (H_right - H_left) * x / L

def quote_bordi(x):
    """(quota lato davanti, quota lato dietro) alla stazione x."""
    t = x / L
    zf = z_FL + (z_FR - z_FL) * t
    zb = z_BL + (z_BR - z_BL) * t
    return zf, zb

def quota_tetto(x, y):
    """Quota Z approssimata della falda in (x,y), senza i raccordi di bordo.
    Usata solo come ripiego per posare i bollini."""
    zf, zb = quote_bordi(x)
    s = max(0.0, min(1.0, y / larghezza(x)))
    return zf + (zb - zf) * s + 4 * crown * s * (1 - s)

def arco_trasversale(x):
    """Faccia-sezione nel piano YZ alla stazione x: fianco davanti, falda
    ad arco poco bombato che scende verso dietro, fianco dietro; poi i due
    spigoli alti raccordati (stretto davanti, ampio dietro). Tutti archi e
    rette tangenti: niente ondulazioni da spline."""
    zf, zb = quote_bordi(x)
    W = larghezza(x)
    y0, y1 = -sporgenza, W + sporgenza
    ym = 0.5 * (y0 + y1)
    with BuildSketch(Plane.YZ.offset(x)) as s:
        with BuildLine():
            Line((y0, 0.0), (y0, zf))                                  # fianco davanti
            ThreePointArc((y0, zf), (ym, 0.5 * (zf + zb) + crown), (y1, zb))  # falda
            Line((y1, zb), (y1, 0.0))                                  # fianco dietro
            Line((y1, 0.0), (y0, 0.0))                                 # base
        make_face()
        vf = s.vertices().sort_by_distance(Vector(y0, zf, 0))[0]  # coord. locali
        fillet(vf, radius=r_front)
        vb = s.vertices().sort_by_distance(Vector(y1, zb, 0))[0]
        fillet(vb, radius=r_back)
    return s.sketch

# loft delle sezioni, poi intersezione col corpo base (silhouette in pianta)
stazioni = [0.001] + [L * k / 8 for k in range(1, 8)] + [L - 0.001]
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

from math import asin
def asin_ok(h, rr):
    return asin(min(1.0, h / rr))

clip_hook_p = clip_depth - clip_thk   # sporgenza del dente OLTRE il contorno esterno
clip_up     = 0.5                     # la gamba risale nella parete per fondersi

# La gamba NON e' un blocchetto piatto messo dentro il guscio: parte dalla
# superficie ESTERNA del corpo. Ogni gamba e' un settore di corona attorno al
# centro del raccordo d'angolo: faccia esterna sul raggio r del raccordo (a filo
# col fianco del corpo), faccia interna a r - clip_thk. Il dente sporge di
# clip_hook_p oltre il fianco, con invito curvo sotto (scatto).
def clip_solid(r):
    """Clip costruita attorno all'asse Z (centro del raccordo all'origine),
    centrata sulla direzione +X (= verso l'esterno dell'angolo)."""
    ri = r - clip_thk
    n = 8
    pts = [(ri, clip_up), (r, clip_up), (r, -clip_len + hook_h),
           (r + clip_hook_p, -clip_len + hook_h)]
    # invito curvo: dalla punta del dente scende fino al filo gamba in fondo
    for i in range(n - 1, -1, -1):
        t = (pi / 2) * i / n
        pts.append((r + clip_hook_p * sin(t), -clip_len + hook_h * (1 - cos(t))))
    pts.append((ri, -clip_len))
    with BuildSketch(Plane.XZ) as s:
        with BuildLine():
            Polyline(*pts, close=True)
        make_face()
    anello = revolve(s.sketch, axis=Axis.Z, revolution_arc=360)

    # fascia rastremata (4.3 in alto -> 3.17 in fondo), lunga lungo +X
    with BuildSketch(Plane.YZ) as t:
        with BuildLine():
            Polyline((-clip_w_top / 2, clip_up), (clip_w_top / 2, clip_up),
                     (clip_w_bot / 2, -clip_len), (-clip_w_bot / 2, -clip_len),
                     close=True)
        make_face()
    fascia = extrude(t.sketch, amount=r + 5, both=True)
    semi = Box(r + 5, 2 * r + 10, 4 * clip_len,
               align=(Align.MIN, Align.CENTER, Align.CENTER))
    return anello & fascia & semi

# Posizione: il centro di ogni raccordo sta sulla bisettrice dell'angolo a
# distanza r/sin(theta/2) dal vertice (gli angoli non sono tutti a 90 gradi).
from math import acos, hypot
clips = []
n_c = len(corner_pts)
for i, ((cx, cy), r) in enumerate(zip(corner_pts, corner_r)):
    (px, py), (nx, ny) = corner_pts[i - 1], corner_pts[(i + 1) % n_c]
    l1, l2 = hypot(px - cx, py - cy), hypot(nx - cx, ny - cy)
    u1 = ((px - cx) / l1, (py - cy) / l1)
    u2 = ((nx - cx) / l2, (ny - cy) / l2)
    half = acos(u1[0] * u2[0] + u1[1] * u2[1]) / 2.0
    bx, by = u1[0] + u2[0], u1[1] + u2[1]
    lb = hypot(bx, by)
    bx, by = bx / lb, by / lb                      # bisettrice verso l'interno
    k = r / sin(half)
    cen = (cx + bx * k, cy + by * k)               # centro del raccordo
    a = degrees(atan2(-by, -bx))                   # direzione verso l'esterno
    # la gamba deve restare dentro l'arco del raccordo (non sui lati dritti)
    arco_semi = (pi - 2 * half) / 2
    assert asin_ok(clip_w_top / 2, r - clip_thk) < arco_semi, "clip oltre il raccordo"
    c = clip_solid(r).rotate(Axis.Z, a).translate((cen[0], cen[1], 0))
    clips.append(c)

corpo = corpo + sum(clips[1:], clips[0])

# =====================================================================
#  Bollini INCAVATI (fossette) sul tetto (griglia come nell'originale)
# =====================================================================
domes   = True
dome_d  = 3.8
dome_h  = 0.7    # profondita' della fossetta
dome_pos = [
    (7.6,16.4),(13.2,17.4),(19.0,17.4),(24.8,16.8),(30.6,15.9),
    (6.0,11.0),(26.4,11.2),(32.6,10.6),
    (8.6,5.2),(14.8,4.6),(21.0,4.6),(27.2,4.6),(33.2,5.0),
]
if domes:
    # Ogni bollino = FOSSETTA incavata nel tetto (come nell'originale):
    # sfera il cui punto piu' basso sta dome_h SOTTO la superficie,
    # sottratta dal corpo. Resta una calotta concava di diametro dome_d.
    R_dome = (dome_d*dome_d/4 + dome_h*dome_h) / (2*dome_h)

    def quota_reale(px, py):
        """Z della superficie del tetto in (px,py): raggio verticale dall'
        alto verso il basso contro il corpo pieno, primo impatto."""
        ax = Axis((px, py, z_max + 20), (0, 0, -1))
        hits = guscio_pieno.find_intersection_points(ax)
        zs = [p[0].Z for p in hits] if hits else []
        return max(zs) if zs else quota_tetto(px, py)

    fossette = []
    for (px, py) in dome_pos:
        zs = quota_reale(px, py)
        fossette.append(Sphere(radius=R_dome).translate((px, py, zs - dome_h + R_dome)))
    # il cielo e' spesso top_thk: la fossetta non deve sfondarlo
    assert dome_h < top_thk - 0.5, "fossette troppo profonde per il cielo"
    corpo = corpo - sum(fossette[1:], fossette[0])

# =====================================================================
#  Simbolo clacson inciso sul tetto (zona centrale-sinistra)
# =====================================================================
horn       = True
horn_depth = 0.45        # profondita' dell'incisione
horn_pos   = (9.4, 11.2) # centro del bordo del bocchino (a sinistra)

# manico della trombetta (sotto la canna)
handle_cx = horn_pos[0] + 4.0   # centro dell'ansa in X
handle_w  = 3.6                 # larghezza esterna dell'ansa
handle_h  = 2.7                 # quanto scende sotto l'asse della canna
handle_r  = 1.2                 # raggio degli angoli
handle_t  = 0.6                 # spessore del tratto

def horn_sketch():
    """Trombetta stilizzata, bocca verso destra:
      - bordo del bocchino: asola verticale arrotondata
      - coppa del bocchino che si stringe nella canna
      - canna sottile
      - campana a svasatura ESPONENZIALE (come uno strumento vero)
      - bocca bombata (arco) verso l'esterno
    Sta nella fascia centrale libera tra le file di bollini."""
    from math import exp, log
    ox, oy = horn_pos
    rim_w, rim_h = 0.7, 2.4          # bordo del bocchino
    x_cup0, x_cup1 = ox + 0.2, ox + 1.6
    hw_cup = 0.85                    # mezza larghezza coppa all'imbocco
    hw_tube = 0.38                   # mezza larghezza canna
    x_fl0, x_fl1 = ox + 5.6, ox + 12.2   # inizio / fine svasatura
    hw_bell = 2.9                    # mezza apertura della campana
    bulge = 0.7                      # bombatura della bocca

    k = log(hw_bell / hw_tube) / (x_fl1 - x_fl0)
    n = 7
    flare = [(x_fl0 + (x_fl1 - x_fl0) * i / n,
              hw_tube * exp(k * (x_fl1 - x_fl0) * i / n)) for i in range(1, n + 1)]
    top = ([(x_cup0, hw_cup), (x_cup1, hw_tube), (x_fl0, hw_tube)]
           + flare)
    with BuildSketch(Plane.XY) as s:
        with BuildLine():
            # coppa (rettilinea) + canna
            Polyline(*[(x, oy - y) for (x, y) in top[:3]][::-1])
            Spline(*[(x, oy - y) for (x, y) in top[2:]])           # svasatura sotto
            ThreePointArc((x_fl1, oy - hw_bell), (x_fl1 + bulge, oy),
                          (x_fl1, oy + hw_bell))                    # bocca
            Spline(*[(x, oy + y) for (x, y) in top[2:]][::-1])     # svasatura sopra
            Polyline(*[(x, oy + y) for (x, y) in top[:3]][::-1])
            Line((x_cup0, oy + hw_cup), (x_cup0, oy - hw_cup))
        make_face()
        # bordo del bocchino
        with Locations((ox, oy)):
            SlotCenterToCenter(rim_h - rim_w, rim_w, rotation=90)

    # MANICO: ansa a "U" arrotondata sotto la canna, tra coppa e campana.
    # Anello (rettangolo raccordato meno il suo interno) tenuto solo sotto
    # l'asse della canna, cosi' i due bracci si innestano nel tubo.
    with BuildSketch(Plane.XY) as m:
        with Locations((handle_cx, oy)):
            RectangleRounded(handle_w, 2 * handle_h, handle_r)
            RectangleRounded(handle_w - 2 * handle_t, 2 * (handle_h - handle_t),
                             handle_r - handle_t, mode=Mode.SUBTRACT)
        with Locations((handle_cx, oy + handle_h)):
            Rectangle(handle_w + 1, 2 * handle_h, mode=Mode.SUBTRACT)
    return s.sketch + m.sketch

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

# =====================================================================
#  Versione SPECCHIATA lungo il lato corto
# =====================================================================
# Specchio rispetto al piano parallelo al lato corto (YZ) passante per meta'
# lunghezza: sinistra e destra si scambiano, la sagoma resta in X 0..L.
# specchiato=False ridà la versione originale.
specchiato = True
if specchiato:
    corpo = corpo.mirror(Plane.YZ.offset(L / 2))

show_object(corpo)
