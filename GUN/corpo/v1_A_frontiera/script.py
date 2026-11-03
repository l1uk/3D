# CONCEPT A - "FRONTIERA": western stilizzato da giocattolo.
# Impugnatura a manico d'aratro, ponticello tondo, tamburo scanalato,
# cane a sperone lungo, canna tonda con alloggio astina sotto.
# Colori allegri (verde acqua, crema, ottone), volata arancione.
# Render di massima: meccanica reale da meccanica.py, involucro indicativo.
import os, sys
sys.path.insert(0, os.getcwd())
from build123d import Axis
import concetti as C
from concetti import p, q, arco, profilo, cil_x

W = 22   # larghezza telaio

telaio_pts = (
    [(-5, 8), (4, 11), (q.x_cam - 2, 12.5), (q.L_tel, 11.5), (q.L_tel + 2, 7),
     (q.L_tel + 2, -9), (q.x_sede + 6, -19), (q.x_spal + 3, -26), (q.x_spal + 1, -37),
     (30, -37), (24, -48), (18, -62), (14, -80), (14, -95), (10, -104)]
    + arco(-6, -96, 14, -60, -150, 6)
    + [(-24, -86), (-20, -68), (-14, -48), (-10, -28), (-8, -10)]
)
telaio = profilo(telaio_pts, W, r2d=2.5, r3d=2.0)
telaio = C.sottrai_meccanica(telaio)

# ponticello: anello sotto il telaio
pont = (cil_x(1, 0, 1))  # segnaposto per tipo
from build123d import Cylinder, Box, Align, Rot, Pos
anello = Pos(40, 0, -40) * Rot(90, 0, 0) * (Cylinder(17, 7, ) - Cylinder(13, 8))
anello = anello - Box(60, 20, 40, align=(Align.CENTER, Align.CENTER, Align.MIN)).translate((40, 0, -38.5))

guance = profilo([(24, -44), (18, -62), (14, -80), (13, -94), (8, -100), (-12, -100),
                  (-20, -86), (-17, -68), (-12, -48), (-8, -40)], 4, r2d=3, r3d=1.5)
guancia_dx = guance.translate((0, W / 2 + 1.5, 0))
guancia_sx = guance.translate((0, -W / 2 - 1.5, 0))

cane = profilo([(4, -6), (12, -6), (13, 6), (8, 16)] + arco(-4, 16, 12, 20, 130, 6)
               + [(-14, 22), (-8, 14), (0, 8)], 7, r2d=2)
grilletto = profilo([(34, -32), (40, -32), (38, -44), (33, -54), (30, -53), (34, -44)], 6, r2d=1.5)

tamb = C.tamburo("scanalato")
canna = C.canna()
alloggio = cil_x(8, q.x_sede, 42, z=-11.5) - cil_x(4, q.x_sede - 1, 45, z=-11.5)
mirino = profilo([(C.x_bocca() - 14, 6), (C.x_bocca() - 4, 6), (C.x_bocca() - 5, 11),
                  (C.x_bocca() - 10, 11)], 3, r2d=1)
volata = C.volata(C.x_bocca(), p.canna_D)

show_object(telaio, id="telaio", name="Telaio (2 gusci)", options={"color": "#4fa89a"})
show_object(tamb, id="tamburo", name="Tamburo", options={"color": "#d9a441"})
show_object(canna + mirino, id="canna", name="Canna", options={"color": "#4fa89a"})
show_object(alloggio, id="alloggio", name="Alloggio astina", options={"color": "#d9a441"})
show_object(guancia_dx, id="guancia_dx", options={"color": "#f2e3c6"})
show_object(guancia_sx, id="guancia_sx", options={"color": "#f2e3c6"})
show_object(cane, id="cane", name="Cane", options={"color": "#d9a441"})
show_object(grilletto, id="grilletto", name="Grilletto", options={"color": "#d9a441"})
show_object(anello, id="ponticello", options={"color": "#4fa89a"})
show_object(volata, id="volata", name="Volata", options={"color": "#ff7a00"})
