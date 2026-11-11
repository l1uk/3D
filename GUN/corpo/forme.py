# FORME 3D di servizio per build.py: dal profilo 2D (shapely, piano XZ) al solido con gli
# spigoli tondi.
#
# prisma_tondo() estrude una sagoma in Y e arrotonda gli spigoli delle due facce: invece di un
# fillet (che sui contorni liberi a molte curve fallisce spesso) costruisce il solido come loft
# rigato fra sezioni via via rientrate. Ogni sezione e' UNA sola curva chiusa (spline per punti
# corrispondenti), quindi il solido ha poche facce grandi e i booleani restano veloci.
import math

from shapely.geometry import Point, Polygon as SPoly


def _campiona(anello, passo):
    """Punti equidistanti lungo un anello shapely (senza ripetere il primo)."""
    n = max(24, int(round(anello.length / passo)))
    return [anello.interpolate(anello.length * i / n).coords[0] for i in range(n)]


def _sezioni(pg, y0, y1, r0, r1, passo, n_arco):
    """Per un poligono senza fori: lista di (y, punti XZ) dalla faccia y0 alla faccia y1.
    r0 / r1: raggio dello spigolo sulle due facce (0 = spigolo vivo). r < 0: lo spigolo si
    allarga invece di rientrare (serve per i fori)."""
    base = _campiona(pg.exterior, passo)
    # normali uscenti nei punti di base (servono per la corrispondenza fra le sezioni)
    verso = 1.0 if pg.exterior.is_ccw else -1.0
    norm = []
    for i in range(len(base)):
        a, c = base[i - 1], base[(i + 1) % len(base)]
        tx, tz = c[0] - a[0], c[1] - a[1]
        m = math.hypot(tx, tz) or 1.0
        norm.append((verso * tz / m, -verso * tx / m))

    def rientrata(d):
        if abs(d) < 1e-6:
            return base
        g = pg.buffer(-d, 24)
        if g.geom_type != "Polygon":
            g = max(g.geoms, key=lambda x: x.area)
        b = g.exterior
        # corrispondenza: ogni punto di base si sposta di d lungo la normale e si porta sul contorno
        # rientrato (il punto piu' vicino).
        # Negli angoli il rientro "mangia" contorno e piu' punti cadono sullo stesso: le ascisse
        # si rendono strettamente crescenti (passo minimo), se no la spline non si costruisce.
        L, eps = b.length, 0.05
        sposta = [(pt[0] - n[0] * d, pt[1] - n[1] * d) for pt, n in zip(base, norm)]
        asc = [b.project(Point(pt)) for pt in sposta]
        if sum(1 for i in range(len(asc)) if asc[i] < asc[i - 1]) > len(asc) / 2:
            b = b.reverse() if hasattr(b, "reverse") else type(b)(list(b.coords)[::-1])
            asc = [b.project(Point(pt)) for pt in sposta]
        s0 = asc[0]
        rel = [(s - s0) % L for s in asc]
        for i in range(1, len(rel)):
            if rel[i] - rel[i - 1] > L / 2:          # salto all'indietro attraverso l'origine
                rel[i] = rel[i - 1]
            rel[i] = max(rel[i], rel[i - 1] + eps)
        tetto = L - eps
        for i in range(len(rel) - 1, 0, -1):         # non si supera il giro
            if rel[i] > tetto:
                rel[i] = tetto
            tetto = rel[i] - eps
        return [b.interpolate((s0 + r) % L).coords[0] for r in rel]

    sez = []
    if r0:
        for k in range(n_arco, 0, -1):
            a = math.pi / 2 * k / n_arco
            sez.append((y0 + abs(r0) * (1 - math.sin(a)), rientrata(r0 * (1 - math.cos(a)))))
    sez.append((y0 + abs(r0), base))
    sez.append((y1 - abs(r1), base))
    if r1:
        for k in range(1, n_arco + 1):
            a = math.pi / 2 * k / n_arco
            sez.append((y1 - abs(r1) * (1 - math.sin(a)), rientrata(r1 * (1 - math.cos(a)))))
    return sez


def _loft(sez, asse="y"):
    """Loft rigato fra le sezioni (quota, punti): quota lungo Y con punti XZ, o lungo X con punti YZ."""
    from build123d import Edge, Solid, Wire
    p3 = (lambda q, a, b: (a, q, b)) if asse == "y" else (lambda q, a, b: (q, a, b))
    fili = [Wire([Edge.make_spline([p3(q, a, b) for a, b in pts], periodic=True)]) for q, pts in sez]
    return Solid.make_loft(fili, ruled=True)


def prisma_tondo(g, y0, y1, r0=0.0, r1=0.0, passo=0.7, n_arco=5):
    """Solido dalla sagoma XZ g (shapely, anche con fori o a piu' pezzi) fra y0 e y1, con gli
    spigoli delle facce y0 e y1 arrotondati di r0 e r1."""
    pezzi = [g] if g.geom_type == "Polygon" else [x for x in g.geoms if x.geom_type == "Polygon"]
    s = None
    for pg in pezzi:
        corpo = _loft(_sezioni(SPoly(pg.exterior), y0, y1, r0, r1, passo, n_arco))
        for h in pg.interiors:
            corpo -= _loft(_sezioni(SPoly(h), y0 - 0.01, y1 + 0.01, -r0, -r1, passo, n_arco))
        s = corpo if s is None else s + corpo
    return s


def _pezzi(g):
    return [g] if g.geom_type == "Polygon" else [x for x in g.geoms if x.geom_type == "Polygon"]


def prisma(g, y0, y1):
    """Prisma a spigoli vivi dalla sagoma XZ g (anche con fori) fra y0 e y1."""
    from build123d import Face, Solid, Vector, Wire
    s = None
    for pg in _pezzi(g):
        if pg.area < 1e-3:
            continue
        filo = lambda anello: Wire.make_polygon([(x, y0, z) for x, z in list(anello.coords)[:-1]], close=True)
        f = Solid.extrude(Face(filo(pg.exterior), [filo(h) for h in pg.interiors]), Vector(0, y1 - y0, 0))
        s = f if s is None else s + f
    return s


def estruso_x(g, x0, x1, r0=0.0, r1=0.0, passo=0.5, n_arco=4):
    """Solido dalla sezione YZ g (shapely, senza fori) estrusa lungo X fra x0 e x1, con gli
    spigoli delle facce x0 e x1 arrotondati di r0 e r1. Il contorno e' una sola spline chiusa."""
    return _loft(_sezioni(SPoly(g.exterior), x0, x1, r0, r1, passo, n_arco), asse="x")
