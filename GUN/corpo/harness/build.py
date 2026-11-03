# CONCEPT A2 - "FRONTIERA" dettagliato, stile revolver d'epoca (giocattolo).
# Rispetto ad A: scudo posteriore tondo con sportello di caricamento e
# scanalatura di carica sul fianco destro, cinghia superiore con tacca di
# mira, perno del tamburo con testa zigrinata, manicotto di volata con
# mirino e alloggio astina, tamburo scanalato con tacche del fermo e
# smussi, cane con sperone rigato, ponticello fuso nel frontale
# dell'impugnatura, guancette zigrinate con medaglione a stella, finte
# viti (coprono i perni in filamento dei gusci), anello per il cordino.
# Meccanica da meccanica.py; involucro da qui. Colori da giocattolo.
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
# show_object e' iniettato solo dentro agentcad; qui giriamo con Python puro per l'harness
if "show_object" not in dir():
    def show_object(*a, **k):  # noqa: E306  (no-op fuori da agentcad)
        pass
from build123d import (Align, Axis, Box, SortBy, Sketch, Rectangle, mirror, Cylinder, Pos, Rot, Torus, Polygon,
                       Plane, extrude, fillet)
import concetti as C
import meccanica as M
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
t_scudo = 4.0
x_scudo1 = q.x_cam - p.g_tamb          # faccia anteriore dello scudo
x_scudo0 = x_scudo1 - t_scudo
camera_carica = 4                       # camera allineata allo sportello (lato destro, -Y)
L_car = 6.0                             # scanalatura di carica dietro lo scudo
a_car = 2 * math.pi * camera_carica / p.n_camere
y_car, z_car = q.r_passo * math.sin(a_car), za + q.r_passo * math.cos(a_car)
slot_cane = 8 + p.gioco_rot             # cane spesso 8
slot_gril = 6 + p.gioco_rot             # grilletto spesso 6
z_fondo_cane = p.canale_D / 2 + p.parete_min   # sotto c'e' il canale del percussore

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

def profilo_imp(rientro=0.0, s0=0.0, s1=L_IMP):
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
    retro = [(s_t - (s_t - s0) * i / N_IMP, -dorso(s_t - (s_t - s0) * i / N_IMP, rientro))
             for i in range(1, N_IMP + 1)]
    return [imp_xz(s, d) for (s, d) in fronte + punta + tallone + retro]

# ---------------- TELAIO ----------------
# Dorso del telaio: un quarto di ellisse convessa dal calcio (dietro il cane) alla cinghia superiore
X_DORSO0, Z_DORSO0 = -28.0, -12.0    # dorso piu' pieno dietro il cane (prima -14,-8)
X_DORSO1, Z_DORSO1 = 22.0, 12.3      # dove la curva si appiattisce sulla cinghia
N_DORSO = 8
dorso_telaio = [(X_DORSO0 + (X_DORSO1 - X_DORSO0) * (1 - math.cos(math.pi / 2 * i / N_DORSO)),
                 Z_DORSO0 + (Z_DORSO1 - Z_DORSO0) * math.sin(math.pi / 2 * i / N_DORSO))
                for i in range(N_DORSO + 1)]
# Blocco sopra la canna: spigolo alto-anteriore raccordato con un quarto d'ellisse
# (la cinghia scende dolcemente verso il frontale) e angolo basso-anteriore ad arco.
A_FRONTE = 24.0             # lunghezza (X) del raccordo superiore anteriore
Z_FRONTE = 9.5              # quota del frontale dove l'ellisse arriva verticale (> bordo sede canna)
N_FRONTE = 8
R_FONDO_F = 9.0             # raggio dell'angolo basso-anteriore del frontale
fronte_alto = [(x_front - A_FRONTE + A_FRONTE * math.sin(math.pi / 2 * i / N_FRONTE),
                Z_FRONTE + (12.5 - Z_FRONTE) * math.cos(math.pi / 2 * i / N_FRONTE))
               for i in range(N_FRONTE + 1)]
fronte_basso = [(x_front - R_FONDO_F + R_FONDO_F * math.cos(math.pi / 2 * i / N_FRONTE),
                 -12.0 - R_FONDO_F * math.sin(math.pi / 2 * i / N_FRONTE))
                for i in range(N_FRONTE + 1)]
telaio_pts = (
    dorso_telaio + [(30, 12), (q.x_cam - 1, 12.5)] + fronte_alto + fronte_basso + [
     (q.x_spal + 3, -23), (q.x_spal + 1.5, -30), (q.x_spal, -37),
     (26, -38)] + profilo_imp() + [(-21, -31), (-27, -22)])
telaio = profilo(telaio_pts, W, r2d=2.5, r3d=1.8)

# Dorso bombato in sezione: il tetto del telaio e' una volta tonda (cilindro lungo X),
# non una faccia piatta a spigoli vivi; i fianchi scendono verso il tamburo.
R_VOLTA = 13.0              # raggio della volta in sezione (YZ)
Z_TETTO = 12.5              # quota della cinghia superiore
X_VOLTA0 = -30.0            # da dietro il cane fino al frontale
volta = Box(x_front - X_VOLTA0 + 2, W + 8, 14, align=(Align.MIN, Align.CENTER, Align.MIN)) \
    .translate((X_VOLTA0, 0, Z_TETTO - 9))
volta -= cil_x(2 * R_VOLTA, X_VOLTA0 - 1, x_front - X_VOLTA0 + 4, z=Z_TETTO - R_VOLTA)
telaio -= volta

# ponticello tondo fuso nel frontale dell'impugnatura
cx_p, cz_p = 36, -46
pont = Pos(cx_p, 0, cz_p) * Rot(90, 0, 0) * (Cylinder(16.5, 7) - Cylinder(13, 8))
pont -= Box(60, 20, 30, align=(Align.CENTER, Align.CENTER, Align.MIN)).translate((cx_p, 0, -37.5))
telaio += pont

# scudo posteriore tondo
telaio += cil_x(2 * r_scudo, x_scudo0, t_scudo, z=za)

# cinghia superiore: scanalatura di mira e tacca posteriore
telaio -= Box(q.x_cam + q.L_tamb - 6, 1.6, 1.0, align=(Align.MIN, Align.CENTER, Align.MAX)).translate((6, 0, 12.6))
telaio -= Pos(4, 0, 12.6) * Rot(0, 0, 0) * Box(2.5, 2.2, 2.0, align=(Align.CENTER, Align.CENTER, Align.MAX))

# finte viti: coprono le teste dei perni in filamento che uniscono i gusci
viti = [(10, -10), (16, -28), (30, -6), (q.x_spal + 8, -19.5), (4, -36)]
for (vx, vz) in viti:
    for s in (1, -1):
        testa = Pos(vx, s * W / 2, vz) * Rot(90, 0, 0) * Cylinder(2.6, 1.6)
        taglio = Box(4.4, 0.6, 0.8 * 2, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        taglio = Pos(vx, s * (W / 2 + 0.8), vz) * Rot(0, 35, 0) * taglio
        telaio = telaio + testa - taglio

# meccanica comune (finestra tamburo, canale percussore, sede canna)
telaio = telaio - M.vuoto_finestra_tamburo() - M.vuoto_canale() - M.vuoto_canna(x_bocca)
telaio -= M.vuoto_asse_tamburo(q.x_cam - 12, x_front + 1)
# feritoie del cane e del grilletto
telaio -= Box(34, slot_cane, 40, align=(Align.MIN, Align.CENTER, Align.MIN)).translate((-18, 0, z_fondo_cane))
telaio -= Box(15, slot_gril, 20, align=(Align.MIN, Align.CENTER, Align.MIN)).translate((28, 0, -42))
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
perno = cil_x(p.tamb_asse_d, q.x_cam - 10, x_front - (q.x_cam - 10), z=za) \
    + cil_x(9, x_front + 0.3, 3.5, z=za)
for i in range(10):
    a = 2 * math.pi * i / 10
    perno -= cil_x(1.2, x_front + 0.2, 4, z=za + 4.6 * math.cos(a), y=4.6 * math.sin(a))

# ---------------- MANICOTTO DI VOLATA SNUBNOSE: un solo manicotto corto, tozzo, tondo ----------------
SP_MAN = 5.0                # spessore radiale del manicotto oltre la canna
R_MAN = 4.0                 # raccordo delle due testate (tondeggiante)
x_m0, x_m1 = x_front, x_bocca - 7          # dal frontale del telaio fin quasi alla volata
D_man = p.canna_D + 2 * SP_MAN
manicotto = cil_x(D_man, x_m0, x_m1 - x_m0)
manicotto = fillet(manicotto.edges(), R_MAN)
manicotto -= cil_x(p.canna_D + p.gioco, x_m0 - 1, x_m1 - x_m0 + 2)
# astina: solo un pomello tondo decorativo sul fianco destro del manicotto
astina = Pos((x_m0 + x_m1) / 2, -D_man / 2 + 0.5, 0) * Rot(90, 0, 0) * Cylinder(3.0, 2.5)

# ---------------- CANE ----------------
cane = profilo([(1, 6), (14, 6), (15, 11), (12.5, 18), (7, 22.5), (0, 24.5), (-8, 25),
                (-14.5, 23.5), (-13, 20.5), (-6, 19), (-2, 13)], 8, r2d=1.2, r3d=1.0)
for i in range(6):                         # rigatura dello sperone
    gx = -12.5 + 2 * i
    gz = 23.5 + 1.5 * (1 - abs(gx + 5) / 9)
    cane -= Pos(gx, 0, gz + 0.6) * Box(0.7, 10, 1.6)

# ---------------- GRILLETTO ----------------
grilletto = profilo([(33, -27), (40, -27), (39.5, -36), (38, -44), (35, -51), (31.5, -55.5),
                     (29.5, -54.5), (32, -48), (33.5, -40)], 6, r2d=1.2, r3d=0.8)

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
show_object(cane, id="cane", name="Cane", options={"color": COL_OTTONE})
show_object(grilletto, id="grilletto", name="Grilletto", options={"color": COL_OTTONE})
show_object(cordino, id="cordino", name="Anello cordino", options={"color": COL_OTTONE})
show_object(volata, id="volata", name="Volata", options={"color": COL_VOLATA})


# ---------------- EXPORT PER L'HARNESS ----------------
# L'harness valuta stl/assieme.stl. show_object() serve ad agentcad; qui
# raccogliamo tutti i pezzi in un unico STL multi-corpo per i cancelli e il render.
# (Non e' il file di stampa: i pezzi veri si esportano separati, come nel provino.)
from build123d import Compound, export_stl  # noqa: E402

_pezzi_harness = [telaio, tamb, perno, sportello, canna, manicotto, astina,
                  g_sx, mirror(g_sx, Plane.XZ), cane, grilletto, cordino, volata]
os.makedirs("stl", exist_ok=True)
export_stl(Compound(_pezzi_harness), "stl/assieme.stl")
print("export harness: stl/assieme.stl")
