"""Utilita' per i concept estetici (render di massima, non pezzi da stampa).

Ogni concept definisce solo l'INVOLUCRO (profili laterali, decorazioni).
Posizione e misure di tamburo, canna, canale e finestra arrivano da
meccanica.py, quindi tutti i concept hanno la stessa meccanica.
"""
from __future__ import annotations

import math

from build123d import (Align, Axis, Box, Cylinder, Plane, Polygon, Pos, Rot,
                       extrude, fillet)

import meccanica as M

p, q = M.p, M.q


def arco(cx, cz, r, a0, a1, n=10):
    """Punti di un arco (gradi), per profili curvi."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def profilo(pts, spessore, r2d=0.0, r3d=0.0, y0=0.0):
    """Profilo nel piano XZ estruso simmetrico in Y, con raccordi 2D e 3D."""
    f = Polygon(*pts, align=None)
    if r2d > 0:
        try:
            f = fillet(f.vertices(), r2d)
        except Exception:
            pass
    s = extrude(Plane.XZ * f, amount=spessore / 2, both=True)
    if r3d > 0:
        try:
            s = fillet(s.edges().filter_by(Axis.Y, reverse=True), r3d)
        except Exception:
            pass
    return s.translate((0, y0, 0))


def cil_x(d, x0, L, z=0.0, y=0.0):
    return M._cil_x(d, x0, L, z=z, y=y)


def sottrai_meccanica(telaio):
    """Toglie all'involucro i volumi funzionali (uguali per tutti i concept)."""
    t = telaio - M.vuoto_finestra_tamburo()
    t -= M.vuoto_canale()
    t -= M.vuoto_canna(x_bocca())
    t -= M.vuoto_asse_tamburo(q.x_cam - 12, q.x_sede + 6)
    return t


def tamburo(stile: str):
    """Tamburo funzionale + decoro esterno secondo lo stile."""
    t = M.tamburo_base()
    n = int(p.n_camere)
    za = q.z_asse_tamb
    if stile == "scanalato":            # scanalature tra le camere (western)
        for i in range(n):
            a = 2 * math.pi * (i + 0.5) / n
            r = q.R_tamb + 2.2
            t -= cil_x(7.5, q.x_cam + 3, q.L_tamb - 6, z=za + r * math.cos(a), y=r * math.sin(a))
    elif stile == "anelli":             # gole circonferenziali (retro)
        for xr in (q.x_cam + 4, q.x_cam + q.L_tamb - 6):
            ring = cil_x(q.D_tamb + 1, xr, 2, z=za) - cil_x(q.D_tamb - 2, xr - 0.1, 2.2, z=za)
            t -= ring
    elif stile == "sfaccettato":        # tamburo a N facce piane (moderno)
        for i in range(n):
            a = 2 * math.pi * (i + 0.5) / n
            r = q.R_tamb - 1.0
            blocco = Box(q.L_tamb + 2, 30, 10, align=(Align.MIN, Align.CENTER, Align.MIN))
            blocco = blocco.translate((0, 0, r)).rotate(Axis.X, -math.degrees(a))
            t -= blocco.translate((q.x_cam - 1, 0, za))
    return t


def canna():
    return M.canna()


def volata(x_bocca, d_est):
    """Tappo arancione: calza la canna (o la camicia) alla volata."""
    L = 8
    return cil_x(d_est + 4, x_bocca - L + 1.5, L) \
        - cil_x(d_est + p.gioco_press, x_bocca - L, L) \
        - cil_x(p.canna_d_c + 1, x_bocca - L, L + 3)


def x_bocca():
    return q.x_spal + p.t_sp + p.canna_L
