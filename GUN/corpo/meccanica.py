"""Meccanica del revolver: quote derivate e volumi da sottrarre.

Le quote hanno gli stessi nomi e le stesse formule di provino_balistico.scad
(L1, L2, corsa, x_sc, x_cam, ...), calcolate dai parametri di GUN/params.scad.
Qui c'e' solo la geometria FUNZIONALE (canali, camere, sedi, perni): la
forma estetica (involucro) sta negli script dei concept/parti e non deve
mai cambiare queste quote.

Sistema di riferimento (come il provino):
  X = asse canna, da dietro (x=0 faccia posteriore del tappo) verso la volata
  Z = alto, asse canna a z = 0
  Y = laterale, piano di divisione dei due gusci a y = 0
"""
from __future__ import annotations

import math
from types import SimpleNamespace

from parametri import carica

P = carica()
p = SimpleNamespace(**P)


# ---------------- molla (lib.scad) ----------------
def molla_Di(d, De): return De - 2 * d
def molla_n_att(nt, nm): return nt - nm
def molla_L_pacco(d, nt): return nt * d
def molla_k(d, De, na, G): return G * d**4 / (8 * (De - d)**3 * na)
def molla_E(k, x1, x2): return 0.5 * k * (x2 * x2 - x1 * x1)


def calcola(p=p) -> SimpleNamespace:
    q = SimpleNamespace()
    # --- identiche al provino ---
    q.m_Di = molla_Di(p.molla_d, p.molla_De)
    q.m_na = molla_n_att(p.molla_n_tot, p.molla_n_morte)
    q.m_Lp = molla_L_pacco(p.molla_d, p.molla_n_tot)
    q.m_k = molla_k(p.molla_d, p.molla_De, q.m_na, p.molla_G)
    q.L1 = p.molla_L0 - p.precarico
    q.corsa = min(p.corsa_max, q.L1 - (q.m_Lp + p.margine_pacco))
    q.L2 = q.L1 - q.corsa
    q.E_mJ = molla_E(q.m_k, p.precarico, p.precarico + q.corsa)
    q.x_cr_f = p.L_tappo + q.L1
    q.x_sc = q.x_cr_f + p.perc_col_L
    q.x_cam = q.x_sc + p.t_sc + p.g_tamb
    q.x_spal = q.x_cam + p.cam_L + p.g_tamb
    q.x_sede = q.x_spal + p.t_sp
    q.L_tel = q.x_sede + p.L_sede
    q.punta_L = p.t_sc - 0.5 + q.corsa
    q.spinta = q.corsa - 0.5 - p.g_tamb - p.boss_fondo
    q.spinta_c = q.corsa - 0.5 - p.g_tamb
    q.asta_d = q.m_Di - 0.3
    q.boss_L = p.boss_fondo + p.boss_prof
    q.cart_L_tot = [Lb + p.cart_ogiva_L + p.cart_punta_L for Lb in p.cart_bossolo_L]

    # --- revolver: canale con riserva di corsa ---
    # Il collare puo' arretrare di corsa + corsa_riserva: il canale e la
    # sede molla sono lunghi abbastanza per una molla piu' lunga o una
    # corsa maggiore senza ridisegnare il corpo (si regola con spessori
    # dietro la molla, sul tappo posteriore).
    q.corsa_disp = q.corsa + p.corsa_riserva
    q.x_canale_0 = q.x_cr_f - q.corsa_disp - 2.0   # inizio del canale dietro il collare ad armato
    q.L_canale = q.x_sc                             # dal retro (x=0) allo scudo

    # --- tamburo ---
    q.L_tamb = p.cam_L                              # contiene la cartuccia intera
    q.camera_d = max(p.cart_D, p.boss_D) + 0.25 + p.comp_foro_v
    q.foro_orlo = p.boss_orlo_D + 0.4 + p.comp_foro_v   # svaso per bossoli con orlo
    n = int(p.n_camere)
    # passo: due camere vicine separate da parete_min
    q.r_passo = (q.camera_d + p.parete_min) / (2 * math.sin(math.pi / n))
    # interno: il perno deve stare dentro le camere con parete_min
    q.r_passo = max(q.r_passo, p.tamb_asse_d / 2 + p.gioco_rot / 2 + p.parete_min + q.camera_d / 2)
    q.R_tamb = q.r_passo + q.camera_d / 2 + p.tamb_par_est
    q.D_tamb = 2 * q.R_tamb
    q.z_asse_tamb = -q.r_passo                      # asse del tamburo sotto la canna
    q.finestra_L = q.L_tamb + 2 * p.g_tamb          # = x_spal - x_cam + g_tamb
    q.finestra_R = q.R_tamb + p.gioco_rot / 2
    # massa tamburo approssimata (pieno meno camere) per bilanciamento
    vol = math.pi * (q.R_tamb**2 - n * (q.camera_d / 2)**2 - (p.tamb_asse_d / 2)**2) * q.L_tamb
    q.m_tamb = vol * 1.24e-3
    return q


q = calcola()


def verifica(q=q, p=p) -> list[str]:
    errori = []
    if q.corsa <= 3: errori.append("corsa troppo corta")
    if q.L2 < q.m_Lp + p.margine_pacco: errori.append("molla a pacco")
    if p.cam_L < max(q.cart_L_tot) + 0.5: errori.append("tamburo corto per la cartuccia")
    parete_tra = 2 * q.r_passo * math.sin(math.pi / p.n_camere) - q.camera_d
    if parete_tra < p.parete_min - 1e-6: errori.append(f"parete tra camere {parete_tra:.2f}")
    if p.tamb_par_est - p.tacca_fermo < p.parete_min - 1e-6 - 0.6:
        errori.append("parete esterna sotto le tacche troppo sottile")
    return errori


def report(q=q) -> str:
    return "\n".join([
        f"MOLLA: k={q.m_k:.3f} N/mm  L1={q.L1} L2={q.L2} corsa={q.corsa} energia={q.E_mJ:.1f} mJ",
        f"CANALE: corsa disponibile {q.corsa_disp} mm (riserva inclusa), scudo a x={q.x_sc}",
        f"CAMERA: x_cam={q.x_cam} x_spal={q.x_spal} x_sede={q.x_sede} L_tel={q.L_tel}",
        f"TAMBURO: {int(p.n_camere)} camere d={q.camera_d:.2f}  r_passo={q.r_passo:.2f}  "
        f"D={q.D_tamb:.1f}  L={q.L_tamb}  asse z={q.z_asse_tamb:.2f}  ~{q.m_tamb:.1f} g",
    ])


# =====================================================================
# Volumi meccanici (build123d). Ogni funzione ritorna un solido da
# SOTTRARRE all'involucro, gia' posizionato nel sistema di riferimento.
# =====================================================================
def _cil_x(d, x0, L, z=0.0, y=0.0):
    from build123d import Cylinder, Align
    c = Cylinder(d / 2, L, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return c.rotate(Axis_y(), 90).translate((x0, y, z))


def Axis_y():
    from build123d import Axis
    return Axis.Y


def vuoto_canale():
    """Canale del percussore + molla + tappo posteriore, con riserva."""
    return _cil_x(p.canale_D, -1, q.x_sc + 1) + \
        _cil_x(p.perc_punta_d + 0.4, q.x_sc - 0.1, p.t_sc + 0.2)


def vuoto_finestra_tamburo():
    """Finestra del tamburo: cilindro con gioco + uscita laterale per caricare."""
    return _cil_x(2 * q.finestra_R, q.x_cam - p.g_tamb, q.finestra_L, z=q.z_asse_tamb)


def vuoto_asse_tamburo(x0, x1):
    return _cil_x(p.tamb_asse_d + p.gioco_rot, x0, x1 - x0, z=q.z_asse_tamb)


def vuoto_canna(x_fine=None):
    """Stessa sede del provino: spalla + sede a pressione leggera.
    x_fine: fin dove prosegue il foro se l'involucro va oltre L_tel
    (la canna si sfila sempre dal davanti)."""
    x_fine = max(q.L_tel, x_fine or 0) + 1
    return _cil_x(p.canna_d_c + 0.6, q.x_spal - 0.01, p.t_sp + 0.02) + \
        _cil_x(p.canna_D + p.gioco_press, q.x_sede, x_fine - q.x_sede)


def tamburo_base():
    """Tamburo funzionale (senza decorazioni): camere, perno, cricchetto liscio."""
    from build123d import Cylinder, Align, Pos
    n = int(p.n_camere)
    t = _cil_x(q.D_tamb, q.x_cam, q.L_tamb, z=q.z_asse_tamb)
    for i in range(n):
        a = 2 * math.pi * i / n
        t -= _cil_x(q.camera_d, q.x_cam - 0.1, q.L_tamb + 0.2,
                    z=q.z_asse_tamb + q.r_passo * math.cos(a), y=q.r_passo * math.sin(a))
    t -= _cil_x(p.tamb_asse_d + p.gioco_rot, q.x_cam - 0.1, q.L_tamb + 0.2, z=q.z_asse_tamb)
    return t


def canna(L=None):
    L = L or p.canna_L
    return _cil_x(p.canna_D, q.x_spal + p.t_sp, L) - \
        _cil_x(p.canna_d_c + p.comp_foro_v, q.x_spal + p.t_sp - 0.1, L + 0.2)


if __name__ == "__main__":
    print(report())
    e = verifica()
    print("VERIFICA:", "ok" if not e else e)
