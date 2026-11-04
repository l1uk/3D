# CONCEPT A2 - "FRONTIERA" dettagliato, stile revolver d'epoca (giocattolo).
# Rispetto ad A: scudo posteriore tondo con sportello di caricamento e
# scanalatura di carica sul fianco destro, cinghia superiore con tacca di
# mira, perno del tamburo con testa zigrinata, manicotto di volata con
# mirino e alloggio astina, tamburo scanalato con tacche del fermo e
# smussi, cane con sperone rigato, ponticello fuso nel frontale
# dell'impugnatura, guancette zigrinate con medaglione a stella, finte
# viti (coprono i perni in filamento dei gusci), anello per il cordino.
# Quote di tamburo/canna da meccanica.py; meccanismo a molla verticale (cinematica, pezzi
# mobili, vani) da meccanismo.py; qui solo il DESIGN: involucro, telaio, decori, montaggio,
# export. Colori da giocattolo.
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # meccanica.py e concetti.py sono qui
# show_object e' iniettato solo dentro agentcad; qui giriamo con Python puro
if "show_object" not in dir():
    def show_object(*a, **k):  # noqa: E306  (no-op fuori da agentcad)
        pass
from build123d import (Align, Axis, Box, SortBy, Sketch, Rectangle, mirror, Cylinder, Pos, Rot, Torus, Polygon,
                       Plane, extrude, fillet)
import concetti as C
import meccanica as M
import meccanismo as MEC     # meccanismo a molla verticale nel manico (MECCANISMO.md)
from concetti import p, q, arco, profilo, cil_x

# ---------------- palette e misure d'involucro ----------------
COL_TELAIO, COL_OTTONE, COL_AVORIO, COL_VOLATA = "#4fa89a", "#d9a441", "#f2e3c6", "#ff7a00"
W = 22                      # larghezza telaio
za = q.z_asse_tamb
CANNA_VISTA = 20.0          # canna oltre il frontale del telaio (snubnose; prima 40 mm)
x_front = q.L_tel           # frontale del telaio (fine sede canna)
x_bocca = x_front + CANNA_VISTA
L_CANNA = x_bocca - (q.x_spal + p.t_sp)   # lunghezza canna accorciata (sede invariata)
r_scudo = q.R_tamb + 1.0    # scudo posteriore tondo
t_scudo = MEC.T_SCUDO                  # il retro dello scudo e' la battuta del cane
x_scudo1 = MEC.X_SCUDO1                # faccia anteriore dello scudo
x_scudo0 = MEC.X_SCUDO
camera_carica = 4                       # camera allineata allo sportello (lato destro, -Y)
L_car = 6.0                             # scanalatura di carica dietro lo scudo
a_car = 2 * math.pi * camera_carica / p.n_camere
y_car, z_car = q.r_passo * math.sin(a_car), za + q.r_passo * math.cos(a_car)
slot_cane = MEC.SLOT_CANE               # feritoia del cane (serve alla cresta, sotto)

# ---------------- IMPUGNATURA (profilo parametrico inclinato) ----------------
# Coordinate locali dell'impugnatura: s lungo l'asse (verso il calcio), d di traverso
# (+ verso il frontale). L'asse parte da (X_IMP0, Z_IMP0) ed e' inclinato all'indietro.
ANG_IMP = 20.0              # inclinazione all'indietro rispetto alla verticale [gradi]
X_IMP0, Z_IMP0 = 2.0, -40.0 # origine dell'asse, sotto il telaio
L_IMP = 64.0                # lunghezza dell'asse fino al tallone
F_IMP = 19.0                # semi-larghezza lato frontale (dita)
B_IMP = 15.0                # semi-larghezza lato dorso, alle estremita'
PANCIA = 12.0               # bombatura convessa del dorso (massima sotto il cane)
PICCO_PANCIA = 0.7          # esponente: <1 sposta il massimo della pancia verso il telaio
H_TALL = 5.0                # discesa del fondo oltre L_IMP
R_PUNTA = 6.0               # raggio dello spigolo frontale del fondo (punta)
R_TALL = 14.0               # raggio del tallone (spigolo posteriore del fondo)
CONC_DITA = 8.0             # concavita' del frontale per le dita (profilo a S)
PICCO_CONC = 0.75           # esponente: <1 sposta la gola verso il telaio, poi il frontale torna in avanti
R_MIN = 1.0                 # raggio minimo dopo il rientro (guancette, campo)
N_IMP = 16                  # punti per curva
N_ARCO = 8                  # punti per raccordo del fondo
_a = math.radians(ANG_IMP)
_dir = (-math.sin(_a), -math.cos(_a))   # verso il calcio
_nrm = (math.cos(_a), -math.sin(_a))    # verso il frontale

def imp_xz(s, d):
    """Da coordinate locali dell'impugnatura al piano XZ."""
    return (X_IMP0 + s * _dir[0] + d * _nrm[0], Z_IMP0 + s * _dir[1] + d * _nrm[1])

def dorso(s, rientro=0.0):
    """Semi-larghezza del dorso: pancia convessa a seno, massima a meta'."""
    return B_IMP + PANCIA * math.sin(math.pi * min(max(s / L_IMP, 0), 1) ** PICCO_PANCIA) - rientro

def arco_imp(cs, cd, r, t0, t1, n=N_ARCO):
    """Punti (s, d) di un arco di centro (cs, cd), angolo misurato da +d verso +s."""
    return [(cs + r * math.sin(t0 + (t1 - t0) * i / n), cd + r * math.cos(t0 + (t1 - t0) * i / n))
            for i in range(n + 1)]

def profilo_imp(rientro=0.0, s0=0.0, s1=L_IMP, s_dorso=None):
    """Contorno chiuso dell'impugnatura: frontale in discesa, punta raccordata,
    fondo, tallone a grande raggio, dorso a pancia in salita."""
    f = F_IMP - rientro
    s_f = s1 + H_TALL                           # quota del fondo
    r_p = max(R_PUNTA - rientro, R_MIN)
    r_t = max(R_TALL - rientro, R_MIN)
    s_t = s_f - r_t                             # inizio del tallone sul dorso
    b_t = dorso(s_t, rientro)                   # il tallone prosegue la pancia senza scalino
    s_p = s_f - r_p
    def fronte_d(s):
        u = min(max(s / s_p, 0), 1)
        return f - CONC_DITA * math.sin(math.pi * u ** PICCO_CONC)
    fronte = [(s0 + (s_p - s0) * i / N_IMP, fronte_d(s0 + (s_p - s0) * i / N_IMP))
              for i in range(N_IMP + 1)]
    punta = arco_imp(s_p, f - r_p, r_p, 0, math.pi / 2)[1:]
    tallone = arco_imp(s_t, -b_t + r_t, r_t, math.pi / 2, math.pi)
    s_fine = s0 if s_dorso is None else s_dorso   # il dorso puo' fermarsi prima (fusione con la gobba)
    retro = [(s_t - (s_t - s_fine) * i / N_IMP, -dorso(s_t - (s_t - s_fine) * i / N_IMP, rientro))
             for i in range(1, N_IMP + 1)]
    return [imp_xz(s, d) for (s, d) in fronte + punta + tallone + retro]

# ---------------- TELAIO ----------------
# Dorso del telaio: un quarto di ellisse convessa dal calcio (dietro il cane) alla cinghia superiore
# Dorso NON accorciato (MECCANISMO.md modifica 17, facoltativa): (-1,-23) con i vani finali lascia
# sede molla/grilletto 19 mm^2 fuori dalla parete minima; i valori intermedi validi in XZ
# (fino a ~(-3.7,-21.9)) rompono il loft della guaina (intersezione vuota o solido non valido).
# Per accorciarlo va prima reso robusto il loft (vedi riassunto del lavoro).
X_DORSO0, Z_DORSO0 = -28.0, -12.0    # dorso piu' pieno dietro il cane (prima -14,-8)
X_DORSO1, Z_DORSO1 = 22.0, 12.3      # dove la curva si appiattisce sulla cinghia
N_DORSO = 8
dorso_telaio = [(X_DORSO0 + (X_DORSO1 - X_DORSO0) * (1 - math.cos(math.pi / 2 * i / N_DORSO)),
                 Z_DORSO0 + (Z_DORSO1 - Z_DORSO0) * math.sin(math.pi / 2 * i / N_DORSO))
                for i in range(N_DORSO + 1)]
# Blocco sopra la canna: spigolo alto-anteriore raccordato con un quarto d'ellisse
# (la cinghia scende dolcemente verso il frontale) e angolo basso-anteriore ad arco.
A_FRONTE = 44.0             # lunghezza (X) del raccordo superiore anteriore: la cinghia scende dal tamburo alla volata
Z_FRONTE = 9.5              # quota del frontale dove l'ellisse arriva verticale (> bordo sede canna)
N_FRONTE = 8
R_FONDO_F = 11.0            # raggio dell'angolo basso-anteriore del frontale (rastremazione sotto la canna)
fronte_alto = [(x_front - A_FRONTE + A_FRONTE * math.sin(math.pi / 2 * i / N_FRONTE),
                Z_FRONTE + (12.5 - Z_FRONTE) * math.cos(math.pi / 2 * i / N_FRONTE))
               for i in range(N_FRONTE + 1)]
fronte_basso = [(x_front - R_FONDO_F + R_FONDO_F * math.cos(math.pi / 2 * i / N_FRONTE),
                 -12.0 - R_FONDO_F * math.sin(math.pi / 2 * i / N_FRONTE))
                for i in range(N_FRONTE + 1)]
# Fusione gobba-impugnatura: il dorso dell'impugnatura si ferma a S_FUSIONE e una curva di
# Hermite (tangenti continue) lo porta alla gobba posteriore del telaio: niente gradino.
S_FUSIONE = 8.0             # dove il dorso dell'impugnatura cede il posto alla curva di raccordo
N_FUSO = 10
_p0 = imp_xz(S_FUSIONE, -dorso(S_FUSIONE))
_p0b = imp_xz(S_FUSIONE + 1, -dorso(S_FUSIONE + 1))
_t0 = (_p0[0] - _p0b[0], _p0[1] - _p0b[1])               # tangente in salita lungo il dorso
_p1, _t1 = (X_DORSO0, Z_DORSO0), (0.0, 1.0)              # la gobba parte in verticale
_k = math.dist(_p0, _p1)
_t0 = (_t0[0] / math.hypot(*_t0) * _k, _t0[1] / math.hypot(*_t0) * _k)
_t1 = (_t1[0] * _k, _t1[1] * _k)
def _hermite(u):
    h00, h10, h01, h11 = 2*u**3 - 3*u**2 + 1, u**3 - 2*u**2 + u, -2*u**3 + 3*u**2, u**3 - u**2
    return (h00*_p0[0] + h10*_t0[0] + h01*_p1[0] + h11*_t1[0],
            h00*_p0[1] + h10*_t0[1] + h01*_p1[1] + h11*_t1[1])
dorso_fuso = [_hermite(i / N_FUSO) for i in range(1, N_FUSO)]
telaio_pts = (
    dorso_telaio + [(30, 12), (q.x_cam - 1, 12.5)] + fronte_alto + fronte_basso + [
     # spigolo basso anteriore: davanti alla finestra del tamburo e all'apertura inferiore (che
     # finiscono a x_spal) restano >= 1.8 mm (prima (x_spal+1.5,-30), (x_spal,-37): lamella da 0 a 1.5)
     (q.x_spal + 3, -23), (q.x_spal + 2.6, -30), (q.x_spal + 1.8, -37),
     (26, -38)] + profilo_imp(s_dorso=S_FUSIONE) + dorso_fuso)
# ---------------- SEZIONE VARIABILE DEL TELAIO (guaina in loft) ----------------
# Prima il telaio era il profilo laterale estruso a larghezza fissa W: due piani
# paralleli, "una tavola". Ora il profilo laterale (telaio_pts) dice DOVE c'e'
# materiale e una guaina fatta di sezioni trasversali (loft lungo X) dice QUANTO e'
# largo a ogni quota: fianchi bombati, cresta tonda, retro piu' stretto del davanti.
# Sotto Z_INNESTO (impugnatura) la larghezza resta W con fianchi piani: li' poggiano
# le guancette. La meccanica si sottrae dopo, come prima.
W2 = W / 2
Z_INNESTO = -38.0           # sotto questa quota: impugnatura a fianchi piani
W_DIETRO = 18.0             # larghezza del telaio dietro il cane (davanti resta W)
X_STRETTO = X_DORSO0        # da qui all'indietro la larghezza e' W_DIETRO
X_PIENO = q.x_cam - 10      # da qui in avanti la larghezza e' W
BOMBA_DIETRO = 0.8          # bombatura dei fianchi oltre la larghezza [mm], dietro
BOMBA_DAVANTI = 1.2         # ... e davanti
R_CRESTA = 6.0              # raggio della cresta del dorso in sezione
R_CRESTA_DAV = 11.0         # davanti (sopra il tamburo): cresta = semicerchio pieno, raccordo ampio sui fianchi
ALZO_CRESTA_DAV = 0.0       # davanti la volta arriva esattamente al profilo: niente piano piatto con spigoli
ALZO_CRESTA = 3.0           # la guaina chiude sopra il profilo: dorso a volta, non a spigolo
PASSO_SEZ = 6.0             # distanza tra le sezioni del loft
DILATA_X = 4.0              # la cresta segue il dorso con questo margine in X (niente tagli)
Z_FONDO_GUAINA = -150.0
W_EST = W + 2 * BOMBA_DAVANTI + 4   # il profilo si estrude piu' largo: la larghezza la decide la guaina

# parete minima ai lati della feritoia del cane (aperta in alto): la cresta non deve
# assottigliarla sotto parete_min neanche dove e' piu' stretta
_h_cima = (W_DIETRO / 2) * math.sqrt(1 - (R_CRESTA / (R_CRESTA + ALZO_CRESTA)) ** 2)
assert _h_cima - slot_cane / 2 >= p.parete_min, \
    f"cresta troppo stretta sulla feritoia del cane: {_h_cima - slot_cane / 2:.2f} mm"

from shapely.geometry import LineString as _SLine, Polygon as _SPoly  # noqa: E402
from build123d import Edge, Wire, Solid  # noqa: E402

_sagoma = _SPoly(telaio_pts).buffer(0)

def _z_cima(x):
    """Quota piu' alta del profilo laterale alla coordinata x (None se fuori)."""
    g = _sagoma.intersection(_SLine([(x, -500), (x, 500)]))
    return None if g.is_empty else g.bounds[3]

def _z_cresta(x):
    """Quota della cresta: il massimo del dorso in un intorno di x, cosi' il loft non
    scende mai sotto il profilo tra una sezione e l'altra."""
    zs = [z for k in range(-int(DILATA_X), int(DILATA_X) + 1) if (z := _z_cima(x + k)) is not None]
    return max(zs + [Z_INNESTO + R_CRESTA + 2])

def _liscio(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)

def _sezione(x):
    """Sezione trasversale chiusa (piano YZ) della guaina alla coordinata x."""
    t = _liscio((x - X_STRETTO) / (X_PIENO - X_STRETTO))
    w = W_DIETRO / 2 + (W2 - W_DIETRO / 2) * t          # semi-larghezza sotto la cresta
    b = BOMBA_DIETRO + (BOMBA_DAVANTI - BOMBA_DIETRO) * t
    zt = _z_cresta(x)
    r_cr = R_CRESTA + (R_CRESTA_DAV - R_CRESTA) * t
    zc0 = max(zt - r_cr, Z_INNESTO + 4)                  # inizio della cresta
    zmax = zt + ALZO_CRESTA + (ALZO_CRESTA_DAV - ALZO_CRESTA) * t
    lato = []
    for u in (0.25, 0.5, 0.75, 1.0):                     # fianco: da W2 a w, con pancia
        lato.append((W2 + (w - W2) * _liscio(u) + b * math.sin(math.pi * u),
                     Z_INNESTO + (zc0 - Z_INNESTO) * u))
    for k in (1, 2, 3, 4):                               # cresta ellittica
        a = math.pi / 2 * k / 5
        lato.append((w * math.cos(a), zc0 + (zmax - zc0) * math.sin(a)))
    punti = ([(x, W2, Z_INNESTO)] + [(x, h, z) for h, z in lato] + [(x, 0.0, zmax)]
             + [(x, -h, z) for h, z in reversed(lato)] + [(x, -W2, Z_INNESTO)])
    curva = Edge.make_spline(punti, tangents=[(0, 0, 1), (0, 0, -1)])
    return Wire([Edge.make_line((x, -W2, Z_FONDO_GUAINA), (x, W2, Z_FONDO_GUAINA)),
                 Edge.make_line((x, W2, Z_FONDO_GUAINA), (x, W2, Z_INNESTO)),
                 curva,
                 Edge.make_line((x, -W2, Z_INNESTO), (x, -W2, Z_FONDO_GUAINA))])

_x0, _x1 = _sagoma.bounds[0] - PASSO_SEZ, _sagoma.bounds[2] + PASSO_SEZ
_n_sez = int(math.ceil((_x1 - _x0) / PASSO_SEZ)) + 1
guaina = Solid.make_loft([_sezione(_x0 + i * (_x1 - _x0) / (_n_sez - 1)) for i in range(_n_sez)])

# Due meta' unite sul piano Z_INNESTO:
#  - sopra: profilo largo intersecato con la guaina (fianchi bombati, cresta, retro stretto)
#  - sotto: impugnatura come prima, profilo largo W con il perimetro raccordato (fianchi
#    piani per le guancette). Raccordarla dopo l'intersezione lasciava un raccordo
#    troncato a meta' contorno e il solido non si chiudeva.
_sopra = Box(400, 100, 300, align=(Align.CENTER, Align.CENTER, Align.MIN)).translate((0, 0, Z_INNESTO))
_sotto = Box(400, 100, 300, align=(Align.CENTER, Align.CENTER, Align.MAX)).translate((0, 0, Z_INNESTO))
telaio = (profilo(telaio_pts, W_EST, r2d=2.5) & guaina & _sopra) \
    + (profilo(telaio_pts, W, r2d=2.5, r3d=1.8) & _sotto)

# apertura sopra e sotto il tamburo: ai lati restano solo un ponte superiore sottile
# e un'anima inferiore centrale, cosi' si vede la rotondita' del cilindro (lato e 3/4)
PONTE_SUP_W = 6.0           # larghezza Y del ponte superiore sopra il tamburo
ANIMA_INF_W = 6.0           # larghezza Y dell'anima sotto il tamburo
Z_APRI_SUP = za + 0.45 * q.R_tamb   # il taglio parte da questa quota e sale
Z_APRI_INF = za - 0.45 * q.R_tamb   # e da questa scende
X_APRI0, L_APRI = q.x_cam - p.g_tamb, q.finestra_L
for _s in (1, -1):
    telaio -= Box(L_APRI, W, 40, align=(Align.MIN, Align.CENTER, Align.MIN)).translate(
        (X_APRI0, _s * (PONTE_SUP_W / 2 + W / 2), Z_APRI_SUP))
    telaio -= Box(L_APRI, W, 40, align=(Align.MIN, Align.CENTER, Align.MAX)).translate(
        (X_APRI0, _s * (ANIMA_INF_W / 2 + W / 2), Z_APRI_INF))

def y_superficie(solido, x, z, lato):
    """Y della superficie esterna del solido sul fianco +1 (sinistro) o -1 (destro)."""
    hit = solido.find_intersection_points(Axis((x, lato * 80, z), (0, -lato, 0)))
    ys = [(h[0] if isinstance(h, tuple) else h).Y for h in hit]
    if not ys:
        return lato * W2
    return max(ys) if lato > 0 else min(ys)

# ponticello: anello pieno e tondeggiante, infilato nel telaio e raccordato davanti e dietro
cx_p, cz_p = 36, -46
R_PONT, r_PONT = 17.5, 12.0   # raggio esterno / interno (parete 5.5 mm, prima 3.5)
W_PONT = 10.0                 # larghezza in Y (prima 7)
Z_PONT_TOP = -30.3            # l'anello rientra nel telaio: nessun pezzo appeso
pont = Pos(cx_p, 0, cz_p) * Rot(90, 0, 0) * (Cylinder(R_PONT, W_PONT) - Cylinder(r_PONT, W_PONT + 1))
pont -= Box(60, 20, 30, align=(Align.CENTER, Align.CENTER, Align.MIN)).translate((cx_p, 0, Z_PONT_TOP))
# gattoni di raccordo: davanti verso il frontale, dietro verso l'impugnatura
GATTONI = ([(45.3, -33), (60.2, -33), (56.2, -42), (52.7, -50), (47.1, -52.3)],
           [(26.7, -33), (12.3, -33), (16.2, -42), (21.7, -50), (25.1, -51.3)])
for pts in GATTONI:
    pont += Pos(0, W_PONT / 2, 0) * Rot(90, 0, 0) * extrude(Polygon(*pts, align=None), W_PONT)
telaio += pont

# scudo posteriore tondo
telaio += cil_x(2 * r_scudo, x_scudo0, t_scudo, z=za)

# cinghia superiore: scanalatura di mira e tacca posteriore
telaio -= Box(q.x_cam + q.L_tamb - 6, 1.6, 1.0, align=(Align.MIN, Align.CENTER, Align.MAX)).translate((6, 0, 12.6))
telaio -= Pos(4, 0, 12.6) * Rot(0, 0, 0) * Box(2.5, 2.2, 2.0, align=(Align.CENTER, Align.CENTER, Align.MAX))

# finte viti: coprono le teste dei perni in filamento che uniscono i gusci
# (le vecchie (10,-10), (30,-6), (4,-36) cadevano nei vani del meccanismo; (16,-28) e (30.5,-20) sono
#  le teste finte delle spine d'acciaio di grilletto e cane: forate, la spina passa)
viti = [(6.1, -7.8), MEC.PT, (8.7, -0.3), (74.6, -19.5), (14.8, -42.3), MEC.P]
PERNI_SPINA = MEC.PERNI_SPINA           # (x, z) del perno -> diametro della spina
# i fianchi ora sono curvi: ogni testa si appoggia sulla superficie reale, non su y = W/2
_fianchi = {(vx, vz, s): y_superficie(telaio, vx, vz, s) for (vx, vz) in viti for s in (1, -1)}
for (vx, vz) in viti:
    for s in (1, -1):
        ys = _fianchi[(vx, vz, s)]
        # sulle spine d'acciaio la testa e' un anello: almeno 1.6 di parete attorno al foro
        r_testa = max(2.6, PERNI_SPINA[(vx, vz)] / 2 + 1.6) if (vx, vz) in PERNI_SPINA else 2.6
        testa = Pos(vx, ys, vz) * Rot(90, 0, 0) * Cylinder(r_testa, 1.6)
        taglio = Box(4.4, 0.6, 0.8 * 2, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        taglio = Pos(vx, ys + s * 0.8, vz) * Rot(0, 35, 0) * taglio
        if (vx, vz) in PERNI_SPINA:
            # testa forata: la spina del perno passa. Niente taglio del cacciavite: attraverso il
            # foro lascerebbe due mezzelune da 0.4 mm
            telaio = telaio + testa - Pos(vx, ys, vz) * Rot(90, 0, 0) * Cylinder(PERNI_SPINA[(vx, vz)] / 2, 4)
        else:
            telaio = telaio + testa - taglio

# meccanica comune (finestra tamburo, sede canna). Il canale orizzontale percussore+molla
# (M.vuoto_canale) non c'e' piu': la molla sta nel manico (MECCANISMO.md, modifica approvata).
# Resta solo il foro del percussore nello scudo.
telaio = telaio - M.vuoto_finestra_tamburo() - M.vuoto_canna(x_bocca)
telaio -= cil_x(MEC.D_PERC_FORO, x_scudo0 - 0.1, t_scudo + 0.2)
# il foro del perno del tamburo sbuca nella feritoia del cane (niente setto sottile)
telaio -= M.vuoto_asse_tamburo(MEC.X_FORO_TAMB, x_front + 1)
# vani del meccanismo (feritoie di cane e grilletto, sede molla, spianatura della cresta, raccordi
# dei setti sottili): li calcola meccanismo.py dalla sagoma di questo telaio. Sono prismi simmetrici
# in Y gia' uniti per larghezza: un solo booleano per larghezza (niente T-junction nella mesh STL).
from shapely.geometry import MultiPoint as _SMulti, Point as _SPoint, box as _sbox  # noqa: E402
_cache_sez = {}
def semi_larghezza(x, z):
    """Semi-larghezza Y del telaio nel punto (x, z), dalla sezione della guaina."""
    if z <= Z_INNESTO:
        return W2
    k = round(x)
    if k not in _cache_sez:
        _cache_sez[k] = _SMulti([((e @ (i / 40)).Y, (e @ (i / 40)).Z) for e in _sezione(float(k)).edges()
                                 for i in range(41)]).convex_hull
    g = _cache_sez[k].intersection(_SLine([(-60, z), (60, z)]))
    return 0.0 if g.is_empty else min(-g.bounds[0], g.bounds[2])

_anello_pont = _SPoint(cx_p, cz_p).buffer(R_PONT, 64).difference(_SPoint(cx_p, cz_p).buffer(r_PONT, 64)) \
    .difference(_sbox(-200, Z_PONT_TOP, 200, 200))
ponticello_xz = _anello_pont.union(_SPoly(GATTONI[0]).buffer(0)).union(_SPoly(GATTONI[1]).buffer(0))
VANI_MEC = MEC.vani_telaio(_sagoma, ponticello_xz, _SPoint(cx_p, cz_p).buffer(r_PONT, 64),
                           semi_larghezza, _z_cima, W)
for _w, _g in VANI_MEC.items():
    telaio -= MEC.estrudi(_g, _w)
telaio -= MEC.foro_spine()
# scanalatura di carica sul fianco destro + passaggio nello scudo
car = cil_x(q.camera_d, x_scudo0 - L_car, x_scudo1 - x_scudo0 + L_car + 0.1, z=z_car, y=y_car)
car += Box(x_scudo1 - x_scudo0 + L_car + 0.1, 20, q.camera_d, align=(Align.MIN, Align.MAX, Align.CENTER)) \
    .translate((x_scudo0 - L_car, y_car, z_car))
telaio -= car

# sportello di caricamento (chiuso): riempie il passaggio nello scudo
sportello = (cil_x(q.camera_d - p.gioco, x_scudo0 + 0.2, t_scudo - 0.4, z=z_car, y=y_car)
             + Box(t_scudo - 0.4, 20, q.camera_d - p.gioco, align=(Align.MIN, Align.MAX, Align.CENTER))
             .translate((x_scudo0 + 0.2, y_car, z_car)))
sportello &= cil_x(2 * r_scudo - p.gioco, x_scudo0, t_scudo, z=za)
y_scudo_est = -math.sqrt(r_scudo**2 - (z_car - za)**2)      # bordo dello scudo a quota z_car
sportello += Pos(x_scudo0 + t_scudo / 2, y_scudo_est - 0.6, z_car) * Box(2.5, 1.5, 3)  # unghiata

# ---------------- TAMBURO ----------------
def tamburo():
    t = M.tamburo_base()
    n = int(p.n_camere)
    for i in range(n):
        a = 2 * math.pi * i / n
        yc, zc = q.r_passo * math.sin(a), za + q.r_passo * math.cos(a)
        # svaso d'imbocco davanti a ogni camera
        # raggio limitato: tra due svasi vicini resta almeno meta' parete_min
        r_svaso = min(q.camera_d / 2 + 0.8,
                      q.r_passo * math.sin(math.pi / p.n_camere) - p.parete_min / 4)
        t -= Pos(q.x_cam + q.L_tamb - 0.8, yc, zc) * Rot(0, 90, 0) * \
            Cylinder(r_svaso, 1.7, align=(Align.CENTER, Align.CENTER, Align.MIN))
        # tacca del fermo, in linea con la camera (sopra la parete piu' spessa)
        tacca = Box(3.0, 3.2, 2 * p.tacca_fermo, align=(Align.MIN, Align.CENTER, Align.CENTER))
        t -= Pos(q.x_cam + 1.2, 0, za) * Rot(-math.degrees(a), 0, 0) * tacca.translate((0, 0, q.R_tamb))
        # scanalature tra le camere
        af = 2 * math.pi * (i + 0.5) / n
        r = q.R_tamb + 2.2
        t -= cil_x(7.5, q.x_cam + 6, q.L_tamb - 9, z=za + r * math.cos(af), y=r * math.sin(af))
    # smussi sugli spigoli esterni davanti (1.2) e dietro (0.6)
    for gruppo, r in ((-1, 1.2), (0, 0.6)):
        try:
            e = t.edges().group_by(Axis.X)[gruppo].sort_by(SortBy.RADIUS)[-1]
            t = t.chamfer(r, None, [e])
        except Exception as err:
            print("smusso tamburo saltato:", err)
    return t

# ---------------- PERNO DEL TAMBURO (sfilabile) ----------------
G_TESTA_PERNO = 0.3         # luce tra la testa del perno e il frontale del telaio
L_TESTA_PERNO = 3.5
# il gambo entra di 1 mm nella testa: prima finiva sul frontale e i due erano corpi staccati
# parte davanti alla feritoia del cane (MEC.X_PERNO_TAMB, x 39.6): appoggio 4.4 nello scudo
perno = cil_x(p.tamb_asse_d, MEC.X_PERNO_TAMB, x_front + G_TESTA_PERNO + 1 - MEC.X_PERNO_TAMB, z=za) \
    + cil_x(9, x_front + G_TESTA_PERNO, L_TESTA_PERNO, z=za)
for i in range(10):
    a = 2 * math.pi * i / 10
    perno -= cil_x(1.2, x_front + 0.2, 4, z=za + 4.6 * math.cos(a), y=4.6 * math.sin(a))

# ---------------- MANICOTTO DI VOLATA SNUBNOSE: un solo manicotto corto, tozzo, tondo ----------------
D_MAN = 22.0                # diametro del manicotto: ~ altezza del telaio (paffuto, snubnose)
R_MAN = 4.0                 # raccordo delle due testate (tondeggiante)
# parte poco oltre la testa del perno del tamburo (x_front+0.3+3.5), cosi' non la ingloba
x_m0, x_m1 = x_front + 4.5, x_bocca - 7     # dal davanti del perno fin quasi alla volata
D_man = D_MAN
manicotto = cil_x(D_man, x_m0, x_m1 - x_m0)  # un solo manicotto tozzo, senza flangia/anello
manicotto = fillet(manicotto.edges(), R_MAN)
manicotto -= cil_x(p.canna_D + p.gioco, x_m0 - 1, x_m1 - x_m0 + 2)
# astina: solo un pomello tondo decorativo sul fianco destro del manicotto
astina = Pos((x_m0 + x_m1) / 2 - 4, -D_man / 2 + 0.5, 0) * Rot(90, 0, 0) * Cylinder(3.0, 2.5)

# ---------------- MECCANISMO A MOLLA VERTICALE (meccanismo.py, MECCANISMO.md) ----------------
# Pezzi funzionali, tutti A RIPOSO (cane abbattuto sullo scudo, naso del grilletto sulla camma):
# profili, quote e cinematica stanno in meccanismo.py; qui solo i colori e il montaggio.
COL_ACCIAIO = "#9aa0a6"                            # solo per i pezzi di riferimento (acciaio / filamento)
cane = MEC.cane()
grilletto = MEC.grilletto()
rullino = MEC.rullino()
perno_rullino = MEC.perno_rullino()                # filamento PLA 1.75 (riferimento)
percussore = MEC.percussore()
coppa = MEC.coppa()
distanziale = MEC.distanziale()
pistone = MEC.pistone()
molla = MEC.molla()                                # acciaio: riferimento
# spine d'acciaio (riferimento): lunghe quanto il telaio sul perno, 0.2 sotto ogni fianco
spina_cane = MEC.spina_cane(2 * semi_larghezza(*MEC.P) - 0.4)
spina_gril = MEC.spina_grilletto(2 * semi_larghezza(*MEC.PT) - 0.4)

# ---------------- GUANCETTE ----------------
RIENTRO_G = 2.5             # bordo telaio lasciato attorno alla guancetta
S_G0 = 3.0                  # inizio guancetta lungo l'asse
g_pts = profilo_imp(RIENTRO_G, S_G0, L_IMP - RIENTRO_G)
t_g = 3.5
RIENTRO_Z = 6.0             # margine tra bordo guancetta e campo zigrinato
campo_pts = profilo_imp(RIENTRO_Z, S_G0 + 12, L_IMP - 14)
S_MED, S_VITE_G = 28.0, 44.0   # medaglione e vite lungo l'asse
x_med, z_med = imp_xz(S_MED, 0)
x_vg, z_vg = imp_xz(S_VITE_G, 0)
x_zc, z_zc = imp_xz(L_IMP / 2, 0)   # centro della griglia di zigrinatura

passo_zigr = 3.5      # passo della zigrinatura a rombi (piu' fine = piu' lento)
solco_zigr = 0.8      # larghezza dei solchi (>= 2 linee da 0.42 non serve: e' un solco)

def guancia_sx():
    """Guancetta sinistra (+Y); la destra e' la sua specchiata."""
    y_out = W / 2 + t_g
    g = profilo(g_pts, t_g, r2d=3, r3d=1.4).translate((0, W / 2 + t_g / 2, 0))
    # zigrinatura: griglia di solchi a +-30 gradi costruita in 2D, poi un solo taglio
    campo = Polygon(*campo_pts, align=None)
    passo_x = passo_zigr / math.sin(math.radians(60))
    righe = [Pos(x_zc + k * passo_x, z_zc) * Rot(0, 0, ang) * Rectangle(solco_zigr, 90)
             for k in range(-12, 13) for ang in (30, -30)]
    solchi = (Sketch() + righe) & campo
    g -= extrude(Plane.XZ * solchi, amount=0.7, both=True).translate((0, y_out, 0))
    # medaglione a stella in rilievo + vite della guancetta
    stella = [(4.5 * math.cos(math.radians(90 + 36 * i)) * (1 if i % 2 == 0 else 0.42),
               4.5 * math.sin(math.radians(90 + 36 * i)) * (1 if i % 2 == 0 else 0.42)) for i in range(10)]
    disco = Pos(x_med, y_out, z_med) * Rot(90, 0, 0) * Cylinder(6.5, 1.4)
    med = Pos(x_med, y_out, z_med) * Rot(90, 0, 0) * (Cylinder(6.5, 1.6) - Cylinder(5.5, 2))
    st = extrude(Plane.XZ * Polygon(*stella, align=None), amount=0.8, both=True).translate((x_med, y_out, z_med))
    g = g - disco + med + st
    vite = Pos(x_vg, y_out, z_vg) * Rot(90, 0, 0) * Cylinder(2.4, 1.6)
    vite -= Pos(x_vg, y_out + 0.7, z_vg) * Box(4, 0.8, 0.6)
    return g + vite

# ---------------- CAPPETTA DEL CALCIO (ottone, manico d'aratro) ----------------
# Guscio in ottone che avvolge il tallone: la fetta del profilo dell'impugnatura dal fondo in su
# per CAP_H lungo l'asse, svuotata di CAP_T davanti, dietro e SUL FONDO. Il telaio ha la battuta
# corrispondente (rientra di CAP_T + G_CAP sotto la cappetta): esterno a filo come prima.
# Prima l'interno rientrava solo davanti e dietro: la cappetta non aveva fondo (pareti ~0 mm al
# tallone, z ~ -100) e si compenetrava col telaio per 2.2 mm. Segue l'inclinazione (profilo_imp/imp_xz).
CAP_H = 16.0               # quanto risale la cappetta lungo l'asse del manico
CAP_T = 2.2                # spessore del guscio (fianchi, fronte, retro, fondo)
G_CAP = 0.1                # luce di incollaggio fra cappetta e telaio
S_CAP = L_IMP - CAP_H      # da dove parte la cappetta lungo l'asse
cap_pieno = profilo(profilo_imp(s0=S_CAP), W + 2 * CAP_T, r2d=2.5, r3d=1.8)
cap_dentro = profilo(profilo_imp(CAP_T, s0=S_CAP - 0.5, s1=L_IMP - CAP_T), W + 2 * G_CAP, r2d=2.5, r3d=1.4)
# taglio netto in alto (perpendicolare all'asse del manico) per il bordo della cappetta
x_cut, z_cut = imp_xz(S_CAP, 0)
piano_alto = Box(80, W + 12, 80, align=(Align.MIN, Align.CENTER, Align.CENTER))
piano_alto = Pos(x_cut, 0, z_cut) * Rot(0, ANG_IMP, 0) * piano_alto.translate((0, 0, 0))
cappetta = (cap_pieno - cap_dentro) - piano_alto
# battuta nel telaio: sotto la cappetta il calcio resta al profilo interno meno G_CAP (i fianchi
# del telaio, piani a y = +-W/2, non si toccano: la cappetta li copre con G_CAP di luce)
_nucleo_cap = profilo(profilo_imp(CAP_T + G_CAP, s0=S_CAP - 1, s1=L_IMP - CAP_T - G_CAP), W + 12, r2d=2.5)
# (l'esterno del taglio e' il profilo allargato di 3 mm: a filo del telaio lasciava schegge da 0.1 mm3)
telaio -= (profilo(profilo_imp(-3, s0=S_CAP, s1=L_IMP + 3), W + 12) - _nucleo_cap) - piano_alto

# ---------------- ANELLO PER IL CORDINO ----------------
x_cor, z_cor = imp_xz(L_IMP + H_TALL + 6, -2)    # occhiello sotto il tallone
x_att, z_att = imp_xz(L_IMP + H_TALL, -2)
cordino = Pos(x_cor, 0, z_cor) * Rot(90, 0, 0) * Torus(5, 1.2)
cordino += Pos(x_att, 0, z_att) * Rot(0, -ANG_IMP, 0) * Box(4, 4, 4)

# ---------------- MONTAGGIO ----------------
tamb = tamburo()
canna = M.canna(L_CANNA)
volata = C.volata(x_bocca, p.canna_D)

show_object(telaio, id="telaio", name="Telaio (2 gusci)", options={"color": COL_TELAIO})
show_object(tamb, id="tamburo", name="Tamburo", options={"color": COL_OTTONE})
show_object(perno, id="perno", name="Perno tamburo", options={"color": COL_OTTONE})
show_object(sportello, id="sportello", name="Sportello di carica", options={"color": COL_OTTONE})
show_object(canna, id="canna", name="Canna", options={"color": COL_TELAIO})
show_object(manicotto, id="manicotto", name="Manicotto con mirino e alloggio", options={"color": COL_OTTONE})
show_object(astina, id="astina", name="Astina (estetica)", options={"color": COL_TELAIO})
g_sx = guancia_sx()
show_object(g_sx, id="guancia_sx", options={"color": COL_AVORIO})
show_object(mirror(g_sx, Plane.XZ), id="guancia_dx", options={"color": COL_AVORIO})
show_object(cane, id="cane", name="Cane (imperniato, spina d3)", options={"color": COL_OTTONE})
show_object(grilletto, id="grilletto", name="Grilletto (con forcella del rullino)", options={"color": COL_OTTONE})
show_object(rullino, id="rullino", name="Rullino d7", options={"color": COL_AVORIO})
show_object(percussore, id="percussore", name="Percussore flottante", options={"color": COL_AVORIO})
show_object(coppa, id="coppa", name="Coppa della molla", options={"color": COL_AVORIO})
show_object(distanziale, id="distanziale", name="Distanziale 4 mm", options={"color": COL_AVORIO})
show_object(pistone, id="pistone", name="Pistone + pattino", options={"color": COL_AVORIO})
# riferimento, non PLA: non vanno nell'assieme dei pezzi da stampare
show_object(molla, id="molla_rif", name="Molla inox 1.0x8 L0 60 (riferimento)", options={"color": COL_ACCIAIO, "floating": True})
show_object(spina_cane, id="spina_cane_rif", name="Spina d3 x 24 (acciaio, riferimento)", options={"color": COL_ACCIAIO})
show_object(spina_gril, id="spina_gril_rif", name="Spina d2 x 23.4 (acciaio, riferimento)", options={"color": COL_ACCIAIO})
show_object(perno_rullino, id="perno_rullino_rif", name="Perno rullino, filamento 1.75 (riferimento)", options={"color": COL_ACCIAIO})
show_object(cappetta, id="cappetta", name="Cappetta calcio", options={"color": COL_OTTONE})
show_object(cordino, id="cordino", name="Anello cordino", options={"color": COL_OTTONE})
show_object(volata, id="volata", name="Volata", options={"color": COL_VOLATA})


# ---------------- EXPORT PER L'HARNESS ----------------
# L'harness valuta stl/assieme.stl. show_object() serve ad agentcad; qui
# raccogliamo tutti i pezzi in un unico STL multi-corpo per i cancelli e il render.
# (Non e' il file di stampa: i pezzi veri si esportano separati, come nel provino.)
from build123d import Compound, export_stl  # noqa: E402

_pezzi_harness = [telaio, tamb, perno, sportello, canna, manicotto, astina,
                  g_sx, mirror(g_sx, Plane.XZ), cane, grilletto, cappetta, cordino, volata,
                  rullino, percussore, coppa, distanziale, pistone]
# pezzi di riferimento (acciaio / filamento, non si stampano): file a parte
_rif_acciaio = [molla, spina_cane, spina_gril, perno_rullino]
_STL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")   # sempre GUN/corpo/stl, da qualunque cwd
os.makedirs(_STL, exist_ok=True)
export_stl(Compound(_pezzi_harness), os.path.join(_STL, "assieme.stl"))
export_stl(Compound(_rif_acciaio), os.path.join(_STL, "riferimento_acciaio.stl"))
print("export harness: stl/assieme.stl (+ stl/riferimento_acciaio.stl, solo riferimento)")
