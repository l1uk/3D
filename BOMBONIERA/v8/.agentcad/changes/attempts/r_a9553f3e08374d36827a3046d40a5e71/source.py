# Prova tecnica: barra a sezione "D" (piatta sotto, semiellisse sopra) che
# segue una spline nel piano XY e si assottiglia; due barre unite + raccordo.
import math

def sezione_D(w, h, k=10):
    """Semiellisse: base piatta larga w su z=0, altezza h. Nel piano locale (x=laterale, y=alto)."""
    pts = [(w / 2 * math.cos(math.pi * i / k), h * math.sin(math.pi * i / k)) for i in range(k + 1)]
    return pts

def barra(punti2d, w0, w1, h0, h1, stazioni=8):
    path = Spline(*[Vector(x, y, 0) for x, y in punti2d])
    sez = []
    for i in range(stazioni + 1):
        t = i / stazioni
        w = w0 + (w1 - w0) * t
        h = h0 + (h1 - h0) * t
        loc = path ^ t                     # Location tangente al percorso
        tan = path % t
        lat = Vector(-tan.Y, tan.X, 0).normalized()
        o = path @ t
        pl = Plane(origin=o, x_dir=lat, z_dir=tan)
        pts = [pl.from_local_coords((x, 0, y)) if False else (o + lat * x + Vector(0, 0, y)) for x, y in sezione_D(w, h)]
        sez.append(Face(Wire.make_polygon(pts, close=True)))
    return loft(sez, ruled=False)

a = barra([(0, 0), (20, 8), (40, 0), (55, -10)], 5, 2.4, 3.6, 2.2)
b = barra([(20, -15), (22, 0), (21, 15)], 4, 4, 3.2, 3.2)
u = a + b
show_object(u, name="unione")
