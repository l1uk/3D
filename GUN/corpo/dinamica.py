# DINAMICA DEL MECCANISMO - forze, urto, gittata (stesso modello di concept_molla_verticale_final.py).
#
# Tutte le funzioni prendono il meccanismo come argomento `m` (il modulo meccanismo, o una sua
# variante da meccanismo.variante()): cosi' si confrontano cinematiche diverse con lo stesso
# metro. Non dipende dal design (profili.py / build.py).
#
#   python dinamica.py        -> tabella della configurazione ufficiale
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import Polygon as SPoly, box as sbox  # noqa: E402

# --- ipotesi del modello (come v2/v3/final) ---
RHO_PLA = 1.24e-3 * 0.85              # g/mm3, pezzi stampati
RHO_CART = 1.24e-3 * 0.95
RHO_ACC = 7.85e-3
F_TRATT = 5.0                         # trattenuta della cartuccia in camera [N]
E_REST = 0.4                          # coefficiente di restituzione degli urti
ETA_MECC = 0.85                       # rendimento della molla sul cane (attriti)
K_CONT = 1.0e6                        # rigidezza di contatto [N/m]
CD, RHO_ARIA, H_TIRO = 0.8, 1.2, 1.2
MU = 0.3                              # PLA/PLA a secco
MU_NASO = 0.09                        # rullino sul perno di filamento
DITO = (36.8, -44.0)                  # dove il dito preme sulla lama del grilletto


def _J_poligono(pts, c):
    s, n = 0.0, len(pts)
    for i in range(n):
        x0, z0 = pts[i][0] - c[0], pts[i][1] - c[1]
        x1, z1 = pts[(i + 1) % n][0] - c[0], pts[(i + 1) % n][1] - c[1]
        s += (x0 * z1 - x1 * z0) * (x0 * x0 + x0 * x1 + x1 * x1 + z0 * z0 + z0 * z1 + z1 * z1)
    return abs(s) / 12.0


def J_geom(m, g, c):
    tot = 0.0
    for pg in m.poligoni(g):
        tot += _J_poligono(list(pg.exterior.coords)[:-1], c)
        for h in pg.interiors:
            tot -= _J_poligono(list(h.coords)[:-1], c)
    return tot


def massa_cartuccia(p):
    Lb = p.cart_bossolo_L[0]
    R, Rc, Rg, Ro = p.cart_D / 2, p.cart_D_corpo / 2, p.cart_gola_D / 2, p.cart_ogiva_D / 2
    f = p.cart_fascia
    g0, g1 = f, f + 0.8
    ri_g, ri = Rg - p.cart_parete, Rc - p.cart_parete
    arco = [(Ro * math.cos(math.radians(90 * i / 12)),
             Lb + p.cart_ogiva_L + p.cart_punta_L * math.sin(math.radians(90 * i / 12))) for i in range(1, 13)]
    prof = SPoly([(0, 0), (R, 0), (R, g0), (Rg, g0), (Rg, g1), (Rc, g1 + (Rc - Rg)), (Rc, Lb - f), (R, Lb - f),
                  (R, Lb), (Ro, Lb), (Ro, Lb + p.cart_ogiva_L)] + arco).buffer(0)
    cav = SPoly([(0, 0), (ri_g, 0), (ri_g, g1 + 0.5), (ri, g1 + 0.5 + (ri - ri_g)), (ri, Lb - ri), (0, Lb)]).buffer(0)
    sez = prof.difference(cav).union(sbox(0, 0, 1.5, Lb - 1.4))
    return 2 * math.pi * sez.centroid.x * sez.area * RHO_CART


def _d(f, x, h=0.05):
    return (f(x + h) - f(x - h)) / math.radians(2 * h)


def molla(m, sp=None, fac=1.0):
    """Molla montata con il distanziale sp [mm] (default: quello nominale del meccanismo)."""
    sp = m.SP_DIST if sp is None else sp
    nt = m.L0_TAGLIO / m.MOLLA_PASSO
    k = m.k_molla() * fac
    L1 = m.L1_GEOM - sp
    return dict(k=k, L1=L1, pre=m.L0_TAGLIO - L1, Lp=(nt + 1) * m.MOLLA_d, sp=sp,
                massa=nt * math.pi * m.MOLLA_Dm * math.pi * m.MOLLA_d ** 2 / 4 * RHO_ACC)


def forze(m, ml):
    """Forze statiche [N]: molla, pollice sullo sperone, dito sul grilletto, carico sul dente."""
    b_h = lambda th: _d(m.comp_cane, th)            # noqa: E731  braccio della molla sul cane [mm/rad]
    b_t = lambda phi: -_d(m.comp_gril, phi)         # noqa: E731
    F = lambda th, phi: ml["k"] * (ml["pre"] + m.comp_cane(th) + m.comp_gril(phi) - m.comp_gril(m.PHI_CAMMA))  # noqa: E731
    a_assiale = m.T_BC - m.dot((m.PT[0] - m.CIMA0[0], m.PT[1] - m.CIMA0[1]), (-m.U[0], -m.U[1]))
    F_arm, F_sg = F(m.ANG_ARMO, 0.0), F(m.ANG_ARMO, m.PHI_SGANCIO)
    N_dente = F_arm * b_h(m.ANG_ARMO) / math.dist(m.P, m.N0)
    F_dito = (F_sg * b_t(m.PHI_SGANCIO) + MU * N_dente * m.L_NASO + MU_NASO * F_sg * a_assiale) / math.dist(m.PT, DITO)
    ritorno = F(0.0, m.PHI_CAMMA) * b_t(m.PHI_CAMMA) - MU_NASO * F(0.0, m.PHI_CAMMA) * a_assiale
    F_poll = max(F(th, 0.0) * b_h(th) for th in (0.0, m.ANG_ARMO / 2, m.ANG_ARMO)) / math.dist(m.P, m.SPERONE)
    return dict(F_rip=F(0.0, m.PHI_CAMMA), F_arm=F_arm, F_max=F(m.ANG_ARMO, m.PHI_FINE), F_dito=F_dito,
                F_poll=F_poll, ritorno=ritorno, N_dente=N_dente,
                L_min=ml["L1"] - m.comp_cane(m.ANG_ARMO) - (m.comp_gril(m.PHI_FINE) - m.comp_gril(m.PHI_CAMMA)))


def simula(m, ml, dt=2e-7):
    """Caduta del cane, urto col percussore, spinta della cartuccia (1D, SI)."""
    p, q = m.p, m.q
    I_cane = J_geom(m, m.cane2d, m.P) * m.SP_CANE * RHO_PLA
    m_perc = math.pi / 4 * (m.D_COL ** 2 * m.L_COL + m.D_SHANK ** 2 * (m.L_PERC - m.L_COL)) * RHO_PLA
    m_cart = massa_cartuccia(p)
    dxp = lambda x0, th: _d(lambda t: m.x_piano(x0, t), th)      # noqa: E731
    r_eff = abs(dxp(m.X_FACE, m.th_urto / 2))
    m_eff_ax = I_cane / r_eff ** 2
    k = ml["k"] * 1e3
    I = I_cane * 1e-9 + (ml["massa"] / 3 * 1e-3) * (_d(m.comp_cane, m.ANG_ARMO / 2) * 1e-3) ** 2
    mp, mc = m_perc * 1e-3, m_cart * 1e-3
    pre = ml["pre"] + m.comp_gril(m.PHI_FINE) - m.comp_gril(m.PHI_CAMMA)
    le = math.log(E_REST)
    z_ = -le / math.sqrt(math.pi ** 2 + le ** 2)
    c1 = 2 * z_ * math.sqrt(K_CONT * (mp * m_eff_ax * 1e-3 / (mp + m_eff_ax * 1e-3)))
    c2 = 2 * z_ * math.sqrt(K_CONT * (mp * mc / (mp + mc)))
    k_stop = 50 * K_CONT * (r_eff * 1e-3) ** 2
    c_stop = 2 * z_ * math.sqrt(k_stop * I)
    th, om = math.radians(m.ANG_ARMO), 0.0
    xp, vp = m.tip_armamento(m.ANG_ARMO) * 1e-3, 0.0
    x_cam = q.x_cam * 1e-3
    xc, vc = x_cam, 0.0
    Lp = m.L_PERC * 1e-3
    E0 = ml["k"] * ((pre + m.comp_cane(m.ANG_ARMO)) ** 2 - pre ** 2) / 2
    KE_urto, t, libero, t_lib = None, 0.0, False, 0.0
    # tabelle della cinematica (la simulazione fa ~10^5 passi)
    N = 400
    th_max = m.ANG_ARMO + 1.0
    tab = []
    for i in range(N + 1):
        a = -2.0 + (th_max + 2.0) * i / N
        tab.append((m.x_piano(m.X_FACE, a), dxp(m.X_FACE, a), m.comp_cane(a), _d(m.comp_cane, a),
                    m.x_piano(m.X_STOP - m.T_LIP, a), dxp(m.X_STOP - m.T_LIP, a)))

    def cin(thd):
        u = (thd + 2.0) / (th_max + 2.0) * N
        i = min(max(int(u), 0), N - 1)
        f = u - i
        return [tab[i][j] + (tab[i + 1][j] - tab[i][j]) * f for j in range(6)]
    while t < 0.03:
        xf, dxf, cc, dcc, xl, dxl = cin(math.degrees(th))
        xf, dxf, xl, dxl = xf * 1e-3, dxf * 1e-3, xl * 1e-3, dxl * 1e-3
        tau = -ETA_MECC * k * (pre + cc) * 1e-3 * dcc * 1e-3
        d1 = xf - (xp - Lp)
        F1 = max(0.0, K_CONT * d1 + c1 * (dxf * om - vp)) if d1 > 0 else 0.0
        if F1 > 0 and KE_urto is None:
            KE_urto = 0.5 * I * om ** 2 * 1e3
        d3 = (xp - Lp + m.L_COL * 1e-3) - xl
        F3 = max(0.0, K_CONT * d3 + c1 * (vp - dxl * om)) if d3 > 0 else 0.0
        d2 = xp - xc
        F2 = max(0.0, K_CONT * d2 + c2 * (vp - vc)) if d2 > 0 else 0.0
        Ts = (-k_stop * th - c_stop * om) if th < 0 else 0.0
        u = (xc - x_cam) * 1e3
        ov = max(0.0, min(u + p.cart_fascia, p.cart_fascia + 0.5) - max(u, 0.0))
        Ftr = F_TRATT * min(ov, p.cart_fascia) / p.cart_fascia
        if vc > 1e-6 or F2 > Ftr:
            ac = (F2 - Ftr) / mc
        else:
            ac, vc = 0.0, 0.0
        al = (tau - F1 * dxf + F3 * dxf + Ts) / I
        ap = (F1 - F2 - F3) / mp
        om += al * dt
        th += om * dt
        vp += ap * dt
        xp += vp * dt
        vc += ac * dt
        xc += vc * dt
        t += dt
        if not libero and u > p.cart_fascia + 0.5 and F2 == 0 and vc > vp:
            libero, t_lib = True, t
        if libero and t - t_lib > 2e-4:
            break
    KE_c = 0.5 * mc * vc ** 2 * 1e3
    return dict(E0=E0, KE_urto=KE_urto or 0.0, KE_c=KE_c, v=vc, eta=KE_c / E0, m_cart=m_cart,
                I_cane=I_cane, m_cane=m.cane2d.area * m.SP_CANE * RHO_PLA)


def gittata(v, m_g, p, ang_deg=0.0, h=H_TIRO):
    A = math.pi * (p.cart_D / 2 * 1e-3) ** 2
    kd = 0.5 * RHO_ARIA * CD * A / (m_g * 1e-3)
    x, z = 0.0, h
    vx, vz = v * math.cos(math.radians(ang_deg)), v * math.sin(math.radians(ang_deg))
    dt = 1e-4
    while z > 0:
        vv = math.hypot(vx, vz)
        vx -= kd * vv * vx * dt
        vz -= (9.81 + kd * vv * vz) * dt
        x += vx * dt
        z += vz * dt
    return x


def valuta(m, sp=None, fac=1.0, F_lim=None):
    """Riassunto di una configurazione. Con F_lim sceglie il distanziale piu' spesso (passi di
    0.5 mm) che tiene la molla armata, a grilletto a fondo, entro F_lim [N]."""
    if F_lim is not None:
        sp = 0.0
        for i in range(0, 32):
            if forze(m, molla(m, i / 2, fac))["F_max"] <= F_lim + 1e-9:
                sp = i / 2
    ml = molla(m, sp, fac)
    f, s = forze(m, ml), simula(m, ml)
    return dict(molla=ml, forze=f, sim=s, gittata=gittata(s["v"], s["m_cart"], m.p),
                pacco_ok=f["L_min"] >= ml["Lp"] + m.p.margine_pacco)


def riga(r):
    f, s, ml = r["forze"], r["sim"], r["molla"]
    return (f"distanziale {ml['sp']:g} mm | molla {f['F_rip']:.1f} -> {f['F_max']:.1f} N | pollice {f['F_poll']:.1f} N | "
            f"grilletto {f['F_dito']:.1f} N | dente {f['N_dente']:.0f} N | ritorno grilletto {f['ritorno']:.1f} Nmm | "
            f"molla {s['E0']:.0f} mJ -> cartuccia {s['KE_c']:.0f} mJ ({100 * s['eta']:.0f}%) | "
            f"{s['v']:.1f} m/s | gittata {r['gittata']:.2f} m" + ("" if r["pacco_ok"] else " | MOLLA A PACCO"))


if __name__ == "__main__":
    import meccanismo as MEC
    print(riga(valuta(MEC)))
