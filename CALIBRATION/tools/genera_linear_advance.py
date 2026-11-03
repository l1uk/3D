#!/usr/bin/env python3
# =====================================================================
# Generatore G-code: test Linear Advance (K-factor) per Ender 3 V2
# =====================================================================
# Stampa un singolo layer con N linee. Ogni linea: 20 mm lenta,
# 40 mm veloce, 20 mm lenta, con un K diverso (M900 K...).
# Le tacche sopra la cornice indicano i punti di cambio velocita'.
# Le etichette (es. 0.4) sono stampate a destra di una linea su due.
#
# Serve un firmware con LIN_ADVANCE: per il Professional Firmware di
# mriscoc e' una build "Special Configurations / LinearAdvance".
# Verifica: manda "M900" dal terminale. Se risponde con "Advance K="
# c'e'; se risponde "Unknown command" questo test non ha effetto.
#
# Lettura: scegli la linea in cui il passaggio lenta->veloce->lenta
# e' piu' uniforme (niente bozzo a fine tratto veloce = K basso,
# niente buco/assottigliamento all'inizio del tratto veloce = K alto).
# Poi in Cura (Start G-code, dopo M420) aggiungi:  M900 K<valore>
# oppure salva in firmware:  M900 K<valore>  e  M500
#
# Uso:
#   python3 genera_linear_advance.py                        (default PLA)
#   python3 genera_linear_advance.py --k-fine 1.5 --k-passo 0.1
#   python3 genera_linear_advance.py -o ../gcode/la_test.gcode
# =====================================================================

import argparse
import math

# Cifre a 7 segmenti come polilinee in un box 1 x 2 (unita' -> scalate).
# Ogni cifra e' una lista di tratti; ogni tratto una lista di punti.
CIFRE = {
    "0": [[(0, 0), (1, 0), (1, 2), (0, 2), (0, 0)]],
    "1": [[(1, 0), (1, 2)]],
    "2": [[(0, 2), (1, 2), (1, 1), (0, 1), (0, 0), (1, 0)]],
    "3": [[(0, 2), (1, 2), (1, 0), (0, 0)], [(0, 1), (1, 1)]],
    "4": [[(0, 2), (0, 1), (1, 1)], [(1, 2), (1, 0)]],
    "5": [[(1, 2), (0, 2), (0, 1), (1, 1), (1, 0), (0, 0)]],
    "6": [[(1, 2), (0, 2), (0, 0), (1, 0), (1, 1), (0, 1)]],
    "7": [[(0, 2), (1, 2), (1, 0)]],
    "8": [[(0, 0), (1, 0), (1, 2), (0, 2), (0, 0)], [(0, 1), (1, 1)]],
    "9": [[(1, 1), (0, 1), (0, 2), (1, 2), (1, 0), (0, 0)]],
    ".": [[(0.5, 0), (0.5, 0.35)]],
}
LARG_CHAR = {".": 0.6}


def fmt_k(k):
    s = "%.3f" % k
    s = s.rstrip("0").rstrip(".")
    return s if s else "0"


class Gcode:
    def __init__(self, a):
        self.a = a
        self.out = []
        self.x = self.y = 0.0
        self.z = 0.0
        self.retratto = False
        area = math.pi * (a.diametro_filo / 2) ** 2
        self.e_mm = a.larghezza * a.layer / area * a.flusso

    def w(self, s):
        self.out.append(s)

    def retrai(self):
        if not self.retratto:
            self.w("G1 E-%.3f F%d" % (self.a.retr, self.a.retr_vel * 60))
            self.retratto = True

    def ripristina(self):
        if self.retratto:
            self.w("G1 E%.3f F%d" % (self.a.retr, self.a.retr_vel * 60))
            self.retratto = False

    def viaggio(self, x, y, retrai=True):
        if retrai:
            self.retrai()
            self.w("G0 Z%.2f F1200" % (self.z + 0.4))
        self.w("G0 X%.3f Y%.3f F%d" % (x, y, self.a.viaggio * 60))
        if retrai:
            self.w("G0 Z%.2f F1200" % self.z)
        self.x, self.y = x, y

    def linea(self, x, y, vel):
        self.ripristina()
        d = math.hypot(x - self.x, y - self.y)
        self.w("G1 X%.3f Y%.3f E%.5f F%d" % (x, y, d * self.e_mm, vel * 60))
        self.x, self.y = x, y

    def testo(self, s, x, y, h):
        """Scrive s con cifre a 7 segmenti, angolo basso-sinistro in (x, y), altezza h."""
        u = h / 2.0
        cx = x
        for ch in s:
            for tratto in CIFRE[ch]:
                px, py = tratto[0]
                dist = math.hypot(cx + px * u - self.x, y + py * u - self.y)
                # salti corti senza retrazione, lunghi con retrazione
                self.viaggio(cx + px * u, y + py * u, retrai=dist > 4)
                for px, py in tratto[1:]:
                    self.linea(cx + px * u, y + py * u, self.a.vel_testo)
            cx += (LARG_CHAR.get(ch, 1.0) + 0.6) * u


def genera(a):
    g = Gcode(a)
    n = int(round((a.k_fine - a.k_inizio) / a.k_passo)) + 1
    ks = [a.k_inizio + i * a.k_passo for i in range(n)]
    L1, L2, L3 = a.tratto_lento, a.tratto_veloce, a.tratto_lento
    lung = L1 + L2 + L3
    x0, y0, dy = a.x0, a.y0, a.spazio
    y_top = y0 + (n - 1) * dy
    m = 4.0  # margine cornice

    # controllo ingombro sul piatto
    x_max = x0 + lung + m + 3 + 4 * 1.6 * a.h_testo / 2 + 2
    y_max = y_top + m + 5
    if x0 - m < 5 or y0 - m < 5 or x_max > a.piatto - 5 or y_max > a.piatto - 5:
        raise SystemExit("Il pattern esce dal piatto: riduci k-passo/range o sposta x0/y0 "
                         "(x %.0f..%.0f, y %.0f..%.0f)" % (x0 - m, x_max, y0 - m, y_max))

    g.w("; Linear Advance K-factor test - Ender 3 V2 - generato da genera_linear_advance.py")
    g.w("; K da %s a %s passo %s (%d linee) | lenta %d mm/s, veloce %d mm/s"
        % (fmt_k(a.k_inizio), fmt_k(a.k_fine), fmt_k(a.k_passo), n, a.vel_lenta, a.vel_veloce))
    g.w("; ugello %d C, piatto %d C, layer %.2f, larghezza %.2f, flusso %.2f"
        % (a.temp, a.letto, a.layer, a.larghezza, a.flusso))
    g.w("M117 Test Linear Advance")
    g.w("M140 S%d" % a.letto)
    g.w("M104 S%d" % min(a.temp, 160))  # preriscaldo senza colare
    g.w("G28")
    if a.mesh:
        g.w("M420 S1 ; attiva la mesh salvata (Manual Mesh del Professional Firmware)")
    g.w("G90")
    g.w("M83 ; estrusione relativa")
    g.w("M106 S0")
    g.w("G0 Z5 F1200")
    g.w("M190 S%d" % a.letto)
    g.w("M109 S%d" % a.temp)
    g.w("M900 K0")
    g.w("G92 E0")

    # linea di spurgo sul bordo sinistro (come lo Start G-code di Cura)
    g.z = 0.3
    g.w("G0 X0.1 Y20 F5000")
    g.w("G0 Z0.3 F1200")
    g.w("G1 X0.1 Y200 E15 F1500")
    g.w("G0 X0.4 Y200 F5000")
    g.w("G1 X0.4 Y20 E15 F1500")
    g.x, g.y = 0.4, 20
    g.retratto = False
    g.retrai()
    g.w("G0 Z2 F1200")

    g.z = a.layer
    # cornice (2 giri) a velocita' lenta: stabilizza la pressione e fa da ancora
    g.w("; cornice")
    for off in (m, m - a.larghezza):
        g.viaggio(x0 - off, y0 - off)
        for px, py in [(x0 + lung + off, y0 - off), (x0 + lung + off, y_top + off),
                       (x0 - off, y_top + off), (x0 - off, y0 - off)]:
            g.linea(px, py, a.vel_lenta)

    # tacche di riferimento sopra la cornice ai cambi di velocita'
    for xt in (x0 + L1, x0 + L1 + L2):
        g.viaggio(xt, y_top + m + 1)
        g.linea(xt, y_top + m + 4, a.vel_lenta)

    # linee di test
    for i, k in enumerate(ks):
        y = y0 + i * dy
        g.w("; K = %s" % fmt_k(k))
        g.viaggio(x0, y)
        g.w("M400")
        g.w("M900 K%s" % fmt_k(k))
        g.w("M117 K=%s" % fmt_k(k))
        g.linea(x0 + L1, y, a.vel_lenta)
        g.linea(x0 + L1 + L2, y, a.vel_veloce)
        g.linea(x0 + lung, y, a.vel_lenta)

    # etichette (una linea su due), con K=0
    g.w("M400")
    g.w("M900 K0")
    g.w("; etichette")
    for i, k in enumerate(ks):
        if i % 2:
            continue
        g.testo(fmt_k(k), x0 + lung + m + 3, y0 + i * dy - a.h_testo / 2, a.h_testo)

    # fine
    g.retrai()
    g.w("G0 Z10 F1200")
    g.w("G0 X0 Y200 F6000 ; piatto in avanti")
    g.w("M104 S0")
    g.w("M140 S0")
    g.w("M107")
    g.w("M84")
    g.w("M117 LA test finito")
    return "\n".join(g.out) + "\n"


def main():
    p = argparse.ArgumentParser(description="Genera il test Linear Advance (Ender 3 V2)")
    p.add_argument("-o", "--uscita", default="linear_advance_test.gcode")
    p.add_argument("--temp", type=int, default=210, help="temperatura ugello (dalla torre)")
    p.add_argument("--letto", type=int, default=60)
    p.add_argument("--k-inizio", type=float, default=0.0)
    p.add_argument("--k-fine", type=float, default=1.0)
    p.add_argument("--k-passo", type=float, default=0.05)
    p.add_argument("--vel-lenta", type=int, default=20)
    p.add_argument("--vel-veloce", type=int, default=70)
    p.add_argument("--vel-testo", type=int, default=15)
    p.add_argument("--viaggio", type=int, default=150)
    p.add_argument("--tratto-lento", type=float, default=20)
    p.add_argument("--tratto-veloce", type=float, default=40)
    p.add_argument("--layer", type=float, default=0.2)
    p.add_argument("--larghezza", type=float, default=0.48)
    p.add_argument("--flusso", type=float, default=1.0, help="moltiplicatore (es. 0.965)")
    p.add_argument("--diametro-filo", type=float, default=1.75)
    p.add_argument("--retr", type=float, default=5.0)
    p.add_argument("--retr-vel", type=int, default=45)
    p.add_argument("--x0", type=float, default=55)
    p.add_argument("--y0", type=float, default=55)
    p.add_argument("--spazio", type=float, default=5)
    p.add_argument("--h-testo", type=float, default=3.5)
    p.add_argument("--piatto", type=float, default=220)
    p.add_argument("--no-mesh", dest="mesh", action="store_false", help="non mandare M420 S1")
    a = p.parse_args()

    if not (180 <= a.temp <= 250):
        raise SystemExit("Temperatura PLA fuori range (180-250)")
    if not (40 <= a.letto <= 70):
        raise SystemExit("Piatto PLA fuori range (40-70)")
    if a.k_passo <= 0 or a.k_fine <= a.k_inizio:
        raise SystemExit("Range K non valido")

    with open(a.uscita, "w", encoding="utf-8") as f:
        f.write(genera(a))
    print("Scritto", a.uscita)


if __name__ == "__main__":
    main()
