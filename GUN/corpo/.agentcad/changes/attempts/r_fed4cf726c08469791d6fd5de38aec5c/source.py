# CONCEPT C - "COMPATTO": moderno a spigoli smussati, stile blaster.
# Telaio a facce piane con smussi, camicia piena sotto la canna con
# bindella superiore, tamburo a facce, impugnatura angolata con due
# appoggi per le dita, ponticello squadrato. Colori viola/giallo/grafite.
import os, sys
sys.path.insert(0, os.getcwd())
from build123d import Box, Align
import concetti as C
from concetti import p, q, profilo, cil_x

W = 24
x_fr = C.x_bocca() - 6
telaio_pts = [
    (-6, 0), (0, 12), (q.x_cam - 4, 13), (x_fr, 13), (x_fr, -18), (q.x_spal + 2, -24),
    (q.x_spal, -37), (q.x_cam - 6, -37), (27, -40), (26, -50), (22, -54), (22, -62),
    (19, -66), (19, -74), (16, -78), (14, -96), (-16, -96), (-18, -60), (-12, -30)]
telaio = profilo(telaio_pts, W, r2d=1.5, r3d=1.6)
# bindella superiore e scarico laterale sulla camicia
telaio += Box(x_fr - q.x_cam, 6, 3, align=(Align.MIN, Align.CENTER, Align.MIN)).translate((q.x_cam - 4, 0, 13))
for s in (1, -1):
    telaio -= Box(x_fr - q.x_spal - 14, 2, 8, align=(Align.MIN, Align.CENTER, Align.CENTER)) \
        .translate((q.x_spal + 8, s * W / 2, -10))
telaio = C.sottrai_meccanica(telaio)
# la camicia arriva fino alla volata: foro passante per la canna
telaio -= cil_x(p.canna_D + p.gioco, q.x_sede, x_fr - q.x_sede + 1)

guance = profilo([(24, -44), (20, -56), (20, -62), (17, -66), (17, -74), (14, -78),
                  (12, -92), (-13, -92), (-15, -60), (-11, -42)], 3, r2d=1, r3d=0.8)
ponte = profilo([(q.x_cam - 4, -37), (q.x_cam - 1, -37), (q.x_cam - 1, -56), (24, -56),
                 (24, -52), (q.x_cam - 5, -52)], 7, r2d=1)
cane = profilo([(4, -4), (12, -4), (11, 10), (2, 18), (-8, 18), (-8, 14), (0, 9)], 8, r2d=1)
grilletto = profilo([(32, -34), (39, -34), (38, -50), (33, -50), (33, -44)], 6, r2d=1)

tamb = C.tamburo("sfaccettato")
canna = C.canna()
volata = C.volata(C.x_bocca(), p.canna_D)

show_object(telaio, id="telaio", name="Telaio (2 gusci)", options={"color": "#7b5bd6"})
show_object(tamb, id="tamburo", options={"color": "#f2c230"})
show_object(canna, id="canna", options={"color": "#f2c230"})
show_object(guance.translate((0, W / 2 + 1.5, 0)), id="guancia_dx", options={"color": "#3a3a40"})
show_object(guance.translate((0, -W / 2 - 1.5, 0)), id="guancia_sx", options={"color": "#3a3a40"})
show_object(ponte, id="ponticello", options={"color": "#7b5bd6"})
show_object(cane, id="cane", options={"color": "#f2c230"})
show_object(grilletto, id="grilletto", options={"color": "#f2c230"})
show_object(volata, id="volata", options={"color": "#ff7a00"})
