# STUDIO DELLA CINEMATICA - quanto spazio occupa il meccanismo dietro il tamburo, e a che prezzo.
#
# Confronta varianti di meccanismo.py (meccanismo.variante) con lo stesso metro: ingombro dietro lo
# scudo, forze, resa balistica (dinamica.py), interferenze fra i pezzi, pareti sottili.
# Non usa il design: serve a scegliere le quote cinematiche prima di disegnare l'involucro.
#
#   python studio_cinematica.py            -> tabella + stl/studio_cinematica.png
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import box as sbox  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

import dinamica as DIN  # noqa: E402
import meccanismo as MEC  # noqa: E402

F_LIM = 23.5          # forza massima della molla (grilletto a fondo): uguale per tutte le varianti


def misura(m):
    """Misure d'ingombro e di salute di una variante."""
    chiuso = unary_union([m.vano_molla, m.vano_gril, m.vano_cane.intersection(sbox(-200, -200, 200, -2.0))])
    alto = chiuso.intersection(sbox(-200, -16, 200, 50))
    r = dict(
        dietro_scudo=m.X_SCUDO - alto.bounds[0],                       # scudo -> retro del meccanismo, in alto
        x_dorso_48=chiuso.intersection(sbox(-200, -49, 200, -47)).bounds[0],   # retro all'altezza del dito
        z_fondo=chiuso.bounds[1],
        coda=m.L_CODA,
        sottili_cane=sum(c.area for c in m.sottili(m.cane2d)),
        sottili_gril=sum(c.area for c in m.sottili(m.gril2d_netto)),
    )
    pose = m.verifica_pose()
    r["interferenze"] = sum(v for k, v in pose.items() if "[mm]" not in k)
    r["luce_min"] = min(v for k, v in pose.items() if "[mm]" in k)
    # la punta dello sperone da armato (serve al design: deve passare sopra la gobba)
    sp = max(m.poligoni(m.cane_pose(m.ANG_ARMO))[0].exterior.coords, key=lambda c: c[1] - c[0])
    r["sperone_armato"] = (round(min(c[0] for c in m.cane_pose(m.ANG_ARMO).exterior.coords), 1),)
    return r


VARIANTI = [
    ("ufficiale", {}),
    ("armo 35", dict(ANG_ARMO=35.0)),
    ("armo 40", dict(ANG_ARMO=40.0)),
    ("armo 45", dict(ANG_ARMO=45.0)),
    ("armo 40, molla 26", dict(ANG_ARMO=40.0, ANG_MOLLA=26.0)),
    ("armo 40, molla 38", dict(ANG_ARMO=40.0, ANG_MOLLA=38.0)),
    ("armo 40, molla 44", dict(ANG_ARMO=40.0, ANG_MOLLA=44.0)),
    ("armo 45, molla 38", dict(ANG_ARMO=45.0, ANG_MOLLA=38.0)),
]

if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    n = len(VARIANTI)
    fig, axs = plt.subplots(2, (n + 1) // 2, figsize=(5 * ((n + 1) // 2), 11))
    for ax, (nome, quote) in zip(axs.flat, VARIANTI):
        try:
            m = MEC.variante(**quote) if quote else MEC
            g, d = misura(m), DIN.valuta(m, F_lim=F_LIM)
        except Exception as err:
            print(f"{nome:22s} NON COSTRUIBILE: {type(err).__name__}: {err}")
            continue
        f, s = d["forze"], d["sim"]
        print(f"{nome:22s} coda {g['coda']:4.1f} | dietro scudo {g['dietro_scudo']:4.1f} | dorso@-48 x {g['x_dorso_48']:6.1f} | "
              f"fondo z {g['z_fondo']:6.1f} | dist {d['molla']['sp']:4.1f} | pollice {f['F_poll']:4.1f} N | "
              f"grilletto {f['F_dito']:4.1f} N | dente {f['N_dente']:3.0f} N | ritorno {f['ritorno']:5.1f} | "
              f"E {s['E0']:3.0f} -> {s['KE_c']:2.0f} mJ | gittata {d['gittata']:.2f} m | "
              f"interf {g['interferenze']:.2f} | luce {g['luce_min']:.2f} | sottili cane {g['sottili_cane']:.1f} gril {g['sottili_gril']:.1f}"
              + ("" if d["pacco_ok"] else " | A PACCO"))
        for geo, kw in ((m.vano_molla, dict(fc="#88f", alpha=.35)), (m.vano_gril, dict(fc="#fc8", alpha=.35)),
                        (m.vano_cane, dict(fc="#f88", alpha=.25)), (m.cane_pose(0), dict(fc="none", ec="k", lw=1.2)),
                        (m.cane_pose(m.ANG_ARMO), dict(fc="none", ec="k", lw=.6, ls=":")),
                        (m.gril_pose(m.PHI_CAMMA), dict(fc="none", ec="brown", lw=1.2))):
            for pg in m.poligoni(geo):
                ax.fill(*pg.exterior.xy, **kw)
        ax.add_patch(plt.Rectangle((m.X_SCUDO, m.ZA - m.q.R_tamb), 4 + m.q.L_tamb, 2 * m.q.R_tamb, fc="#dc8", alpha=.5))
        ax.set_title(f"{nome}\ndietro scudo {g['dietro_scudo']:.1f} mm, gittata {d['gittata']:.2f} m", fontsize=10)
        ax.set_aspect("equal"); ax.grid(True, alpha=.3); ax.set_xlim(-45, 70); ax.set_ylim(-90, 30)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl", "studio_cinematica.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, dpi=55, bbox_inches="tight")
    print(out)
