"""Elementi in "ferro battuto" stampabili in piano (build123d).

Ogni barra e' un loft di sezioni a D lungo una spline nel piano XY:
base piatta su z=0 (appoggia sul piatto, nessuno sbalzo sotto), dorso a
semiellisse verso +Z. Larghezza e altezza variano lungo il percorso: le barre
si assottigliano verso volute e riccioli come il ferro forgiato.

Coordinate: X = u (orizzontale del fianco, verso il retro), Y = z (altezza
dal tavolo), Z = spessore (verso l'esterno della panchina).
"""
import math

from build123d import (Vector, Spline, Line, Wire, Face, Location, Plane, Axis,
                       loft, extrude, chamfer, SlotCenterToCenter)

H_MAX = 4.2     # altezza massima del dorso (mm)
H_MIN = 1.4     # minimo: 7 layer da 0.2
MAX_GIRO = 120  # gradi di curva massimi per singolo loft


def altezza(w):
    return max(H_MIN, min(H_MAX, 0.8 * w))


def bez3(p0, p1, p2, p3, k=28):
    out = []
    for i in range(k + 1):
        t = i / k
        a, b, c, e = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + e * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + e * p3[1]))
    return out


def spirale(c, r0, r1, a0, a1, k=28):
    out = []
    for i in range(k + 1):
        t = i / k
        r, a = r0 + (r1 - r0) * t, math.radians(a0 + (a1 - a0) * t)
        out.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a)))
    return out


def unisci(*tratti):
    """Concatena liste di punti togliendo i duplicati di giunzione."""
    out = []
    for t in tratti:
        for p in t:
            if not out or math.dist(p, out[-1]) > 0.05:
                out.append(tuple(p))
    return out


def ricampiona(pts, passo=1.2):
    """Punti a distanza costante lungo la polilinea: la spline non oscilla."""
    pts = unisci(pts)
    cum = [0.0]
    for a, b in zip(pts, pts[1:]):
        cum.append(cum[-1] + math.dist(a, b))
    n = max(3, int(cum[-1] / passo) + 1)
    out, j = [], 0
    for i in range(n + 1):
        s = cum[-1] * i / n
        while j < len(cum) - 2 and cum[j + 1] < s:
            j += 1
        seg = cum[j + 1] - cum[j]
        u = (s - cum[j]) / seg if seg else 0
        a, b = pts[j], pts[j + 1]
        out.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
    return out


def _percorso(pts):
    return Spline(*[Vector(x, y, 0) for x, y in ricampiona(pts)])


def _sezione(o, lat, w, h, k=8):
    """Wire chiuso della sezione a D centrata in o: larga w lungo lat, alta h."""
    arco = [o + lat * (w / 2 * math.cos(math.pi * i / k)) + Vector(0, 0, h * math.sin(math.pi * i / k))
            for i in range(k + 1)]
    return Wire([Spline(*arco), Line(arco[-1], arco[0])])


def _w_at(larghezze, s):
    for (s0, w0), (s1, w1) in zip(larghezze, larghezze[1:]):
        if s <= s1:
            u = (s - s0) / (s1 - s0) if s1 > s0 else 0.0
            u = u * u * (3 - 2 * u)                  # transizione morbida
            return w0 + (w1 - w0) * u
    return larghezze[-1][1]


def barra(pts, larghezze, stazioni=None, flare=0.0, flare_fine=0.0, flare_len=0.15):
    """Barra a D lungo i punti 2D pts.

    larghezze: numero, (w_inizio, w_fine) oppure [(s, w), ...] con s in [0,1]
    (frazione di lunghezza). L'altezza segue la larghezza.
    flare / flare_fine: allargamento all'attacco / alla fine = raccordo forgiato
    dove la barra si salda a un'altra.
    """
    if isinstance(larghezze, (int, float)):
        larghezze = [(0, larghezze), (1, larghezze)]
    elif not isinstance(larghezze[0], (tuple, list)):
        larghezze = [(0, larghezze[0]), (1, larghezze[1])]
    path = _percorso(pts)
    stazioni = stazioni or max(6, min(48, int(path.length / 2.2)))
    sez, tangenti = [], []
    for i in range(stazioni + 1):
        t = i / stazioni
        w = _w_at(larghezze, t)
        if flare and t < flare_len:
            w += flare * (1 - t / flare_len) ** 2
        if flare_fine and t > 1 - flare_len:
            w += flare_fine * ((t - 1 + flare_len) / flare_len) ** 2
        tan = path % t
        lat = Vector(-tan.Y, tan.X, 0).normalized()
        sez.append(Face(_sezione(path @ t, lat, w, altezza(w))))
        tangenti.append(math.atan2(tan.Y, tan.X))
    # Una voluta stretta dentro un solo loft si sovrappone a se stessa e rompe le
    # booleane: si spezza la barra in tratti con al massimo ~MAX_GIRO di curva,
    # che condividono la sezione di confine, e si fondono.
    tratti, inizio, giro = [], 0, 0.0
    for i in range(1, len(sez)):
        dz = (tangenti[i] - tangenti[i - 1] + math.pi) % (2 * math.pi) - math.pi
        giro += abs(dz)
        if giro > math.radians(MAX_GIRO) and i - inizio >= 2:
            tratti.append(sez[inizio:i + 1])
            inizio, giro = i, 0.0
    tratti.append(sez[inizio:])
    if len(tratti[-1]) < 2:
        tratti[-2].extend(tratti.pop()[1:])
    pezzi = [loft(t) for t in tratti]
    return pezzi[0] if len(pezzi) == 1 else pezzi[0].fuse(*pezzi[1:]).clean()


def bottone(p, r, h=None):
    """Calotta (testa di voluta / ribattino) con base su z=0."""
    h = 0.8 * r if h is None else h
    sez = []
    for i in range(7):
        z = h * i / 7
        rr = r * math.sqrt(max(1 - (z / h) ** 2, 1e-4))
        sez.append(Face(Wire.make_circle(rr, Plane.XY.offset(z).move(Location((p[0], p[1], 0))))))
    sez.append(Face(Wire.make_circle(0.06 * r, Plane.XY.offset(0.995 * h).move(Location((p[0], p[1], 0))))))
    return loft(sez)


def fascetta(pts, s, w, lungo=1.8):
    """Collare forgiato attorno a una barra (pts) alla frazione s della lunghezza."""
    path = _percorso(pts)
    o, tan = path @ s, (path % s).normalized()
    lat = Vector(-tan.Y, tan.X, 0)
    h = altezza(w) + 0.5
    return loft([Face(_sezione(o + tan * d, lat, w, h)) for d in (-lungo / 2, lungo / 2)], ruled=True)


def banda(p0, p1, r, spessore, smusso=0.5):
    """Piattina con i fori delle linguette: stadio da p0 a p1, smusso a 45° sopra."""
    s = SlotCenterToCenter(math.dist(p0, p1), 2 * r,
                           rotation=math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0])))
    s = s.moved(Location(((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, 0)))
    b = extrude(s, spessore)
    if smusso:
        b = chamfer(b.edges().group_by(Axis.Z)[-1], smusso)
    return b
