"""Fianco della panchina v8 in ferro battuto (build123d), due varianti.

Orientamento = stampa: faccia interna sul piatto (z=0), dorso delle barre
verso +Z (esterno della panchina). X = u, Y = altezza dal tavolo (come la v7).
Fasce di seduta e schienale: piattine piatte spesse sp, con gli stessi fori
della v7 (stesso clearance), cosi' le linguette restano a filo.
"""
from build123d import Box, Polygon, extrude, Location

import params_v7 as q
from ferro import barra, fascetta, banda, bez3, spirale, unisci

sp, rs = q.sp, q.rs
c2 = q.P["clearance"] / 2
S, Pb = q.S, q.Pb
W_STR = 5.0      # barre strutturali (larghezza alla base)
W_ORN = 2.6      # ornamenti


def fori():
    """Fori delle linguette, identici alla v7 (poligoni nel piano u,z)."""
    lt = q.lt
    poli = []
    for w in q.ling_seduta:
        poli.append([S(w - lt/2 - c2, -sp - c2), S(w + lt/2 + c2, -sp - c2),
                     S(w + lt/2 + c2, c2), S(w - lt/2 - c2, c2)])
    for a in q.ling_schienale:
        poli.append([Pb(a - lt/2 - c2, -sp - c2), Pb(a + lt/2 + c2, -sp - c2),
                     Pb(a + lt/2 + c2, c2), Pb(a - lt/2 - c2, c2)])
    out = None
    for p in poli:
        f = extrude(Polygon(*p, align=None), 20).moved(Location((0, 0, -5)))
        out = f if out is None else out + f
    return out


def fasce():
    return (banda(S(q.P["w_front"] + 2, -sp/2), S(q.P["w_back"] + 1, -sp/2), q.r_band, sp)
            + banda(Pb(-1, -sp/2), Pb(q.P["h_back"] - 2, -sp/2), q.r_band, sp))


def elementi_A():
    """Variante A, "Classica": le linee della v7, in tondo forgiato."""
    u_coda, z_arm, uat = q.P["u_coda"], q.z_arm, q.u_attacco
    x_arm = Pb(q.a_arm, -sp/2)[0]
    gamba_post = unisci(bez3(S(q.P["w_back"], -sp/2), (20, 38), (36, rs), (uat, rs)),
                        [(u_coda, rs)],
                        spirale((u_coda, rs + 5.5), 5.5, 1.9, -90, 215))
    braccio = unisci([(x_arm, z_arm), (-40, z_arm)], spirale((-40, z_arm - 4.4), 4.4, 1.6, 90, 400))
    piede_ant = unisci([(-27, rs), (-40, rs)], spirale((-40, rs + 4), 4, 1.5, -90, -330))
    gamba_ant = bez3((-33, rs), (-29, 22), (-38, 40), (-35.5, z_arm))
    controvento = bez3(Pb(40, -sp - 3), (46, 74), (36, 26), (56, rs))
    orn1 = unisci(bez3((-32.5, 13), (-10, 0), (-22, 34), (-4, 31)), spirale((-4, 26), 5, 1.9, 90, -200))
    orn2 = unisci(bez3((-15, z_arm), (-21, z_arm - 4), (-11, q.z_E + 6), (-24, q.z_E + 5)), [S(-26, 3)])
    pezzi = [
        barra(gamba_post, [(0, 6.4), (0.45, W_STR), (0.7, W_STR), (1, 2.0)], flare=1.5, flare_fine=1.0),
        barra(braccio, [(0, W_STR), (0.35, W_STR), (1, 1.9)], flare_fine=1.0),
        barra(piede_ant, [(0, W_STR), (0.3, W_STR), (1, 1.9)], flare_fine=1.0),
        barra(gamba_ant, W_STR, flare=1.2, flare_fine=1.2),
        barra(controvento, (3.6, 2.6), flare=1.6, flare_fine=1.6),
        barra(orn1, [(0, 3.2), (0.6, W_ORN), (1, 1.6)], flare=1.4, flare_fine=1.0),
        barra(orn2, (W_ORN, 2.2), flare=1.4, flare_fine=1.2),
        fascetta(gamba_ant, 0.5, W_STR + 1.4),
        fascetta(controvento, 0.55, 3.4),
    ]
    return pezzi


def elementi_B():
    """Variante B, "Coup de fouet": linee a frusta piu' marcate alla Horta,
    lira dietro lo schienale con germoglio, tralci asimmetrici."""
    u_coda, z_arm, uat = q.P["u_coda"], q.z_arm, q.u_attacco
    x_arm = Pb(q.a_arm, -sp/2)[0]
    gamba_post = unisci(bez3(S(q.P["w_back"], -sp/2), (28, 46), (28, rs), (uat, rs)),
                        [(u_coda, rs)],
                        spirale((u_coda, rs + 6), 6, 1.9, -90, 250))
    braccio = unisci(bez3((x_arm, z_arm), (-8, z_arm + 3.5), (-26, z_arm - 2.5), (-40, z_arm)),
                     spirale((-40, z_arm - 4.6), 4.6, 1.6, 90, 430))
    piede_ant = unisci([(-26, rs), (-38, rs)], spirale((-38, rs + 4.4), 4.4, 1.5, -90, -350))
    gamba_ant = bez3((-31, rs), (-22, 24), (-46, 40), (-36, z_arm))
    lira = bez3(Pb(48, -sp - 3), (62, 84), (26, 30), (58, rs))
    germoglio = unisci(bez3(Pb(28, -sp - 2.5), (44, 60), (30, 30), (46, 20)),
                       spirale((44, 24), 3.4, 1.5, -60, 200))
    frusta = unisci(bez3((-31, 9), (-2, -4), (-24, 38), (2, 33)), spirale((1, 28), 5, 1.9, 80, -230))
    tralcio = unisci(bez3((-12, z_arm), (-24, z_arm - 9), (-4, q.z_E + 9), (-20, q.z_E + 3)),
                     spirale((-20, q.z_E + 6.5), 3.5, 1.5, -90, -330))
    pezzi = [
        barra(gamba_post, [(0, 6.6), (0.4, W_STR), (0.72, W_STR), (1, 2.0)], flare=1.5, flare_fine=1.0),
        barra(braccio, [(0, W_STR), (0.45, W_STR), (1, 1.9)], flare=1.0, flare_fine=1.0),
        barra(piede_ant, [(0, W_STR), (0.25, W_STR), (1, 1.9)], flare_fine=1.0),
        barra(gamba_ant, [(0, W_STR + 0.6), (0.5, W_STR - 0.6), (1, W_STR)], flare=1.2, flare_fine=1.2),
        barra(lira, [(0, 3.8), (0.5, 2.8), (1, 3.4)], flare=1.6, flare_fine=1.8),
        barra(germoglio, [(0, 2.8), (0.6, 2.4), (1, 1.6)], flare=1.4, flare_fine=1.0),
        barra(frusta, [(0, 3.4), (0.55, 2.6), (1, 1.6)], flare=1.6, flare_fine=1.0),
        barra(tralcio, [(0, 2.8), (0.6, 2.3), (1, 1.6)], flare=1.4, flare_fine=1.0),
        fascetta(gamba_ant, 0.48, W_STR + 1.2),
        fascetta(lira, 0.62, 3.6),
    ]
    return pezzi


def fianco(variante="A"):
    el = elementi_A() if variante == "A" else elementi_B()
    corpo = fasce().fuse(*el).clean()          # una sola fusione: tutte le barre insieme
    corpo = corpo.cut(fori(), Box(400, 60, 20).moved(Location((0, -30, 0))))  # fori + niente sotto il tavolo
    solidi = corpo.solids()
    if len(solidi) != 1:
        raise ValueError(f"fianco {variante}: {len(solidi)} corpi separati, qualche barra non e' attaccata")
    return solidi[0]
