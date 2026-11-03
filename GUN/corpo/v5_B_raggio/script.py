# CONCEPT B - "RAGGIO": retro-futuro anni '50 / steampunk leggero.
# Telaio molto arrotondato, camicia alettata sulla canna (manicotto separato,
# la canna resta sostituibile), tamburo con gole, cane ad anello,
# impugnatura inclinata con pomolo sferico, oblo' decorativo sul fianco.
# Colori: rame, ottone, verde petrolio, volata arancione.
import os, sys
sys.path.insert(0, os.getcwd())
from build123d import Cylinder, Sphere, Pos, Rot
import concetti as C
from concetti import p, q, arco, profilo, cil_x

W = 22
telaio_pts = (
    [(-8, 2)] + arco(4, 2, 10, 180, 90, 5)[1:]
    + [(q.x_cam - 4, 13), (q.L_tel, 12), (q.L_tel + 3, 4), (q.L_tel + 3, -10),
       (q.x_spal + 2, -24), (q.x_spal, -37), (28, -38), (20, -50), (14, -70), (12, -88),
       (-14, -88), (-16, -70), (-12, -40), (-10, -20)]
)
telaio = profilo(telaio_pts, W, r2d=6, r3d=3)
# oblo' decorativo sul fianco (rilievo ad anello)
for s in (1, -1):
    oblo = Pos(14, s * W / 2, -16) * Rot(90, 0, 0) * (Cylinder(9, 2.4) - Cylinder(6, 3))
    telaio += oblo
telaio = C.sottrai_meccanica(telaio)

pomolo = Pos(-1, 0, -92) * Sphere(15)
pomolo -= Pos(-1, 0, -70) * Cylinder(14, 20)   # piano di appoggio sul fondo grip
guance = profilo([(18, -48), (13, -68), (11, -84), (-11, -84), (-13, -68), (-10, -44)],
                 4, r2d=4, r3d=1.5)

# camicia alettata: si infila sulla canna dal davanti
x0 = q.L_tel + 3.5
Lc = C.x_bocca() - 7 - x0
camicia = cil_x(p.canna_D + 4, x0, Lc) - cil_x(p.canna_D + p.gioco, x0 - 1, Lc + 2)
for i in range(int((Lc - 4) // 5)):
    camicia += cil_x(26, x0 + 4 + i * 5, 2) - cil_x(p.canna_D + p.gioco, x0, 50)

cane = profilo([(4, -4), (12, -4), (10, 8)] + arco(-2, 16, 9, 30, 330, 12)[:1] + [(0, 6)], 7, r2d=1.5)
cane += Pos(-4, 0, 18) * Rot(90, 0, 0) * (Cylinder(8, 7) - Cylinder(4.5, 8))
grilletto = profilo([(34, -32), (40, -32), (37, -46), (31, -50), (30, -47), (34, -42)], 6, r2d=1.5)
gancio = profilo([(q.x_spal - 4, -37), (q.x_spal - 2, -37)] + arco(40, -42, 15, 0, -170, 10)
                 + [(25, -38), (28, -38)] + arco(40, -42, 11, -170, 0, 10), 7, r2d=0.8)

tamb = C.tamburo("anelli")
canna = C.canna()
volata = C.volata(C.x_bocca(), p.canna_D)

show_object(telaio, id="telaio", name="Telaio (2 gusci)", options={"color": "#2f6f73"})
show_object(tamb, id="tamburo", options={"color": "#b87333"})
show_object(canna, id="canna", options={"color": "#d4af37"})
show_object(camicia, id="camicia", name="Camicia alettata", options={"color": "#b87333"})
show_object(guance.translate((0, W / 2 + 1.5, 0)), id="guancia_dx", options={"color": "#d4af37"})
show_object(guance.translate((0, -W / 2 - 1.5, 0)), id="guancia_sx", options={"color": "#d4af37"})
show_object(pomolo, id="pomolo", options={"color": "#b87333"})
show_object(cane, id="cane", options={"color": "#d4af37"})
show_object(grilletto, id="grilletto", options={"color": "#d4af37"})
show_object(gancio, id="ponticello", options={"color": "#2f6f73"})
show_object(volata, id="volata", options={"color": "#ff7a00"})
