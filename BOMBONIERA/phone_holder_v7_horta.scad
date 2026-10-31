// =====================================================================
// PHONE HOLDER BOMBONIERA DI LAUREA - v7 "PANCHINA HORTA"
// Evoluzione della v6: fianchi in ferro battuto Art Nouveau alla
// Victor Horta (linee a "coup de fouet", volute).
//  - la gamba posteriore e' una frusta che corre lunga sul tavolo e finisce
//    in un ricciolo: sposta indietro l'appoggio (56 -> 90 mm) e la panchina
//    regge il tocco sullo schermo senza ribaltarsi (vedi VERIFICA STABILITA')
//  - controvento a frusta dietro lo schienale, voluta sul bracciolo
//  - schienale piu' alto (62 mm) per accompagnare meglio il telefono
// Stesso sistema di incastri, cavo e seduta della v6.
// Ender 3 V2 - PLA - stampa piatta, ZERO supporti
//
// STAMPA (STL in stl/, rigenerabili con tools/esporta_stl.sh)
//  0. stl/test/test_giunti_ugello04.stl         -> tara clearance e gioco_manneken
//  1. stl/piatti/piatto1_fianchi_ugello04.stl   -> 2 fianchi (142 x 217 mm)
//  2. stl/piatti/piatto2_seduta_schienale_ugello04.stl
//  3. stl/piatti/piatto3_manneken_ugello02.stl  -> 2 Manneken, ugello 0.2, layer 0.08-0.12
// MONTAGGIO: linguette di seduta e schienale nei fianchi, poi i Manneken
// dall'alto nelle fessure della terza doga (faccia incisa verso chi guarda).
// Obiettivo zero colla: giochi tarati col provino.
// =====================================================================

/* [Testi] */
targa_riga1 = "DOTT. LUCA";
targa_riga2 = "BRUXELLES · MMXXVI";
frase       = "Grazie di esserci stati.";
mostra_targa = true;
mostra_frase = true;

/* [Panchina (mm)] */
alpha      = 65;    // inclinazione schienale = telefono
beta       = 6;     // inclinazione all'indietro della seduta
sp         = 3.2;   // spessore pannelli
L_in       = 92;    // luce tra i fianchi (telefoni fino a ~86 mm con cover)
w_front    = -36;   // bordo anteriore seduta (dall'angolo seduta/schienale)
w_back     = 4.3;   // la seduta passa sotto lo schienale
h_back     = 62;    // altezza schienale lungo l'inclinazione
bracciolo  = 18;    // altezza braccioli sopra la seduta
u_coda     = 90;    // fin dove la gamba posteriore tocca il tavolo (stabilita')
/* [Giochi degli incastri (gioco totale, mm)] */
// Obiettivo: incastri a pressione, zero colla. Valori da tarare col provino
// modalita = "test_giunti" (stampato con le impostazioni definitive).
clearance      = 0.15;  // [-0.05:0.05:0.40] linguette seduta/schienale nei fianchi
gioco_manneken = 0.15;  // [-0.05:0.05:0.40] tenone Manneken nella doga
giochi_test    = [0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30];

/* [Fermo anti-scivolamento] */
// Due listelli sulla seduta davanti al piede del telefono: il telefono non
// puo' scivolare in avanti. Centro libero per plug e overmold.
mostra_fermo     = true;
tipo_fermo       = "manneken"; // [manneken, listello]
spessore_max_tel = 14.5;  // telefono + cover piu' spesso che deve entrare
// Manneken Pis: due sagome di profilo che si guardano (e fanno pipi' verso il
// cavo). Si stampano piatte, il tenone entra in una fessura della doga.
x_manneken  = 30;    // posizione dei piedi dal centro
t_manneken  = 2.4;   // spessore della sagoma
t_tenone    = 1.6;   // spessore del tenone (lato telefono)
h_manneken  = 21;    // altezza della statuina (piedistallo escluso)
w_zampillo  = 1.0;   // larghezza dello zampillo (min ~1 mm con ugello 0.4)
prof_dettagli = 0.5; // profondita' delle incisioni (luci dello stencil)
h_fermo          = 4.0;   // altezza sopra la seduta
w_fermo          = 2.4;   // spessore del listello
luce_fermo       = 22;    // spazio libero centrale (overmold ~11 mm)

/* [Cavo USB-C] */
spazio_cavo = 55;   // tratto dritto: dalla punta del plug a dove si piega
inserzione  = 6.5;
asse        = 4.5;  // asse della porta dalla schiena del telefono
margine     = 4;    // aria tra la piega del cavo e il tavolo

/* [Verifica stabilita'] */
// telefono di riferimento: grande e leggero = il caso peggiore per il tocco
L_tel     = 175;   // mm
m_tel     = 170;   // g
t_tel     = 10;    // spessore con cover
F_minima  = 0.8;   // N: un tap medio e' ~0.5 N, uno swipe 0.8-1.2 N
m_panca   = 33;    // g (stampa reale, verifica in Cura)
u_cg_panca = 9;    // baricentro panchina (dall'STL)

/* [Vista] */
modalita = "assemblato"; // [assemblato, piatto1_fianchi, piatto2_seduta_schienale, manneken, seduta, schienale, fianco, test_giunti, check]
telefono = true;
$fn = 40;
include <manneken_pis_data.scad>

// =====================================================================
// GEOMETRIA
// =====================================================================
d = [cos(alpha), sin(alpha)];        // lungo lo schienale, verso l'alto
n = [-sin(alpha), cos(alpha)];       // normale schienale, verso il davanti
g = [cos(beta), -sin(beta)];         // lungo la seduta, verso il retro
m = [sin(beta), cos(beta)];          // normale seduta, verso l'alto
tratto = spazio_cavo - inserzione;
z_E = margine + tratto*sin(alpha) - asse*cos(alpha);   // angolo seduta/schienale
E = [0, z_E];
function P(a, b) = E + a*d + b*n;    // piano schienale
function S(w, h) = E + w*g + h*m;    // piano seduta
function bez3(p0, p1, p2, p3, k=28) = [for (i=[0:k]) let(t=i/k)
    pow(1-t,3)*p0 + 3*pow(1-t,2)*t*p1 + 3*(1-t)*t*t*p2 + pow(t,3)*p3];
function spirale(c, r0, r1, a0, a1, k=28) = [for (i=[0:k]) let(t=i/k, r=r0+(r1-r0)*t, a=a0+(a1-a0)*t)
    c + r*[cos(a), sin(a)]];

module on_back() multmatrix([[1,0,0,0],[0,d[0],n[0],E[0]],[0,d[1],n[1],E[1]],[0,0,0,1]]) children();
module off_back() multmatrix([[1,0,0,0],[0,d[0],d[1],-(d*E)],[0,n[0],n[1],-(n*E)],[0,0,0,1]]) children();
module on_seat() multmatrix([[1,0,0,0],[0,g[0],m[0],E[0]],[0,g[1],m[1],E[1]],[0,0,0,1]]) children();

x_in  = L_in/2;          // faccia interna fianco
x_out = x_in + sp;       // faccia esterna fianco
xi    = x_in - 0.15;     // fine di seduta/schienale
c2    = clearance/2;
lt    = 9;               // lunghezza linguette
ling_seduta    = [-26, -4];     // posizioni (w)
ling_schienale = [8, 52];       // posizioni (a)
z_arm = z_E + bracciolo;

// doghe
gap_s = 1.6;  n_s = 5;
doga_s = (w_back - w_front - (n_s-1)*gap_s) / n_s;
gap_b = 2.4;
doghe_b = [[0, 16], [18.4, 35], [37.4, h_back]];   // [inizio, fine] lungo a

// =====================================================================
// VERIFICA STABILITA'
// Ribaltamento all'indietro attorno al punto d'appoggio posteriore (u_coda).
// Forza critica di un dito che preme perpendicolare allo schermo all'85%
// dell'altezza del telefono (la zona delle notifiche).
// =====================================================================
function F_crit(L, mt, frac=0.85) = let(
    up = L/2*d[0] + t_tel/2*n[0],
    uc = (mt*up + m_panca*u_cg_panca) / (mt + m_panca),
    Mr = (mt + m_panca)/1000 * 9.81 * (u_coda - uc),          // N*mm
    Pp = P(frac*L, t_tel),
    braccio = sin(alpha)*Pp[1] - cos(alpha)*(u_coda - Pp[0]))
    Mr / braccio;
u_cg_tel = L_tel/2*d[0] + t_tel/2*n[0];
echo(str("Seduta a ", z_E, " mm dal tavolo"));
echo(str("Appoggio posteriore u=", u_coda, ", baricentro telefono u=", u_cg_tel));
for (t = [[140,150], [150,170], [165,200], [175,170], [185,250]])
    echo(str("Telefono ", t[0], " mm / ", t[1], " g: forza di tocco che lo ribalta = ",
             F_crit(t[0], t[1]), " N (in alto), ", F_crit(t[0], t[1], 0.5), " N (centro)"));
assert(u_cg_tel < u_coda - 30, "Instabile anche da fermo: allunga u_coda");
assert(F_crit(L_tel, m_tel) >= F_minima, "Si ribalta toccando lo schermo: allunga u_coda");

// =====================================================================
// SEDUTA (coordinate locali x, w; w verso il retro). Stampa: faccia sopra in alto
// =====================================================================
module seduta_2d() difference() {
    union() {
        translate([-xi, w_front]) offset(r=1.2) offset(delta=-1.2) square([2*xi, w_back - w_front]);
        for (s=[-1,1], w=ling_seduta)
            translate([s > 0 ? xi - 0.5 : -x_out, w - lt/2]) square([sp + 0.65, lt]);
    }
    for (i=[1:n_s-1]) let(w0 = w_front + i*doga_s + (i-1)*gap_s)
        translate([-xi + 4, w0]) offset(r=gap_s/2 - 0.01) offset(delta=-(gap_s/2 - 0.01))
            square([2*xi - 8, gap_s]);
    hull() for (w=[-10.5+3, -0.3-3]) translate([0, w]) offset(r=3) square([9, 0.01], center=true);
}
// distanza lungo la seduta tra lo schienale e la faccia anteriore del telefono
w_fermo_in = -(spessore_max_tel / sin(180 - alpha - beta) + 0.4);
// ---------------------------------------------------------------------
// MANNEKEN PIS - sagoma di profilo, guarda verso +x, y=0 = piano seduta.
// Statua di Duquesnoy (1619), pubblico dominio. Disegno originale.
// ---------------------------------------------------------------------
// Contorno dallo stencil di Wikimedia Commons (CC BY-SA 4.0, vedi
// manneken_pis_data.scad). Le zone di luce dello stencil diventano incisioni
// sulla faccia a vista; zampillo e piedistallo sono ridisegnati per la stampa.
module st2(p, r) for (i=[0:len(p)-2]) hull() { translate(p[i]) circle(r); translate(p[i+1]) circle(r); }
function bez2(p0, p1, p2, k=24) = [for (i=[0:k]) let(t=i/k) (1-t)*(1-t)*p0 + 2*(1-t)*t*p1 + t*t*p2];
mp_k    = h_manneken / (109.7 - 13.9);   // scala svg -> mm
mp_base = 1.2;                           // altezza del piedistallo
module mp_frame() translate([0, mp_base]) scale(mp_k) translate([-31, -13.9]) children();
mp_S = [(46.6 - 31)*mp_k, (55.6 - 13.9)*mp_k + mp_base];   // la manina
module mp_corpo_2d() {
    mp_frame() offset(r=-mp_chiusura) offset(r=mp_chiusura)   // chiude tacche troppo fini (capelli)
        difference() {
            polygon(mp_main);
            translate([-10, -10]) square([200, 23.9]);    // piedistallo e gocce originali
            translate([46.3, 0]) square([30, 53]);        // zampillo originale (0.2 mm)
        }
}
module mp_dettagli_2d()     // zone di luce dello stencil
    mp_frame() difference() {
        union() for (h = mp_holes) if (abs(poly_area(h)) > mp_soglia) polygon(h);
        for (i = mp_islands) polygon(i);
    }
function poly_area(p) = 0.5*abs(sum2([for (i=[0:len(p)-1]) p[i][0]*p[(i+1)%len(p)][1] - p[(i+1)%len(p)][0]*p[i][1]]));
function sum2(v, i=0) = i >= len(v) ? 0 : v[i] + sum2(v, i+1);
mp_soglia   = 5;     // svg mm^2: le luci piu' piccole non si stampano
mp_chiusura = 3.5;   // svg mm (~0.75 mm reali): riempie le tacche del contorno
module manneken_2d() {
    $fn = 24;
    mp_corpo_2d();
    translate([-3.6, 0]) offset(r=0.5) offset(delta=-0.5) square([7.4, mp_base + 0.3]);   // piedistallo
    st2(bez2(mp_S, mp_S + [3.6, 0.8], [mp_S[0] + 6.2, 0.6]), w_zampillo/2);             // zampillo
    translate([mp_S[0] + 6.2, 0.5]) scale([1.5, 0.5]) circle(1);                          // schizzo
}
// pezzo da stampare: sagoma + tenone (piu' sottile, sul lato del telefono).
// La faccia superiore in stampa e' quella a vista: li' vanno le incisioni.
module manneken() {
    difference() {
        linear_extrude(t_manneken, convexity=10) manneken_2d();
        translate([0, 0, t_manneken - prof_dettagli]) linear_extrude(1, convexity=10)
            intersection() { mp_dettagli_2d(); offset(r=-0.35) mp_corpo_2d(); }
    }
    translate([-3, -sp + 0.2, 0]) cube([6, sp, t_tenone]);
}
mp_c = gioco_manneken/2;
module fessure_manneken() for (s = [-1, 1])
    translate([s*x_manneken - 3 - mp_c, w_fermo_in - t_tenone - mp_c, -1])
        cube([6 + 2*mp_c, t_tenone + 2*mp_c, sp + 2]);
module mannekens_montati() for (s = [-1, 1])
    on_seat() translate([s*x_manneken, w_fermo_in, 0]) rotate([90, 0, 0])
        mirror([s > 0 ? 1 : 0, 0, 0]) manneken();

module fermo() if (mostra_fermo && tipo_fermo == "listello")
    for (s = [-1, 1]) {
        x0 = s > 0 ? luce_fermo/2 : -(xi - 6);
        translate([x0, w_fermo_in - w_fermo, sp - 0.01])
            hull() {                                   // listello con cima tonda
                cube([xi - 6 - luce_fermo/2, w_fermo, 0.01]);
                translate([0, w_fermo/2, h_fermo - w_fermo/2]) rotate([0, 90, 0])
                    cylinder(d=w_fermo, h=xi - 6 - luce_fermo/2);
            }
    }
module seduta() difference() {
    union() { linear_extrude(sp, convexity=10) seduta_2d(); fermo(); }
    if (mostra_fermo && tipo_fermo == "manneken") fessure_manneken();
    if (mostra_frase)
        translate([0, w_front + doga_s/2, sp - 0.8]) linear_extrude(1, convexity=10)
            text(frase, size=3.4, font="Liberation Sans:style=Bold Italic", halign="center", valign="center");
}
module seduta_montata() on_seat() translate([0, 0, -sp]) seduta();

// =====================================================================
// SCHIENALE (coordinate locali x, a). Stampa: faccia anteriore in alto
// =====================================================================
module schienale_2d() difference() {
    union() {
        translate([-xi, -3]) offset(r=3) offset(delta=-3) square([2*xi, h_back + 3]);
        translate([-xi, -3]) square([2*xi, 6]);                      // base dritta
        for (s=[-1,1], a=ling_schienale)
            translate([s > 0 ? xi - 0.5 : -x_out, a - lt/2]) square([sp + 0.65, lt]);
    }
    for (i=[0:len(doghe_b)-2])
        translate([-xi + 4, doghe_b[i][1]]) offset(r=gap_b/2 - 0.01) offset(delta=-(gap_b/2 - 0.01))
            square([2*xi - 8, gap_b]);
}
module targa_2d() offset(r=1.5) offset(delta=-1.5) square([57, 13.4], center=true);
module schienale() difference() {
    linear_extrude(sp, convexity=10) schienale_2d();
    // targa: incavo di 0.6 mm con le scritte in rilievo
    if (mostra_targa) translate([0, (doghe_b[2][0] + h_back)/2, sp - 0.6]) linear_extrude(1, convexity=10)
        difference() {
            targa_2d();
            difference() { offset(delta=-1.0) targa_2d(); offset(delta=-1.8) targa_2d(); }
            translate([0, 2.0]) text(targa_riga1, size=4.0, font="Liberation Sans:style=Bold", halign="center", valign="center");
            translate([0, -3.0]) text(targa_riga2, size=2.9, spacing=1.08, font="Liberation Sans:style=Bold", halign="center", valign="center");
        }
}
// montato: dietro il piano del telefono, rifilato sul piano della seduta
module schienale_montato() intersection() {
    on_back() translate([0, 0, -sp]) schienale();
    on_seat() translate([-100, -100, 0]) cube([200, 300, 200]);
}

// =====================================================================
// FIANCO HORTA (profilo u, z). Due pezzi uguali.
// =====================================================================
r_band = sp/2 + 3.6;     // fasce che portano i fori delle linguette
rs     = 2.6;            // struttura (5.2 mm)
// tratto con raggio che si assottiglia: le linee a frusta
module tr(p, r0, r1=-1) let(r1_ = r1 < 0 ? r0 : r1, k = len(p) - 1)
    for (i=[0:k-1]) hull() {
        translate(p[i])   circle(r0 + (r1_ - r0)*i/k);
        translate(p[i+1]) circle(r0 + (r1_ - r0)*(i+1)/k);
    }
a_arm = (z_arm - z_E + (sp/2)*n[1]) / d[1];       // bracciolo/montante
u_attacco = 66;                                    // la frusta tocca il tavolo
module fianco_2d() difference() {
    union() {
        // fasce di seduta e schienale
        tr([S(w_front + 2, -sp/2), S(w_back + 1, -sp/2)], r_band);
        tr([P(-1, -sp/2), P(h_back - 2, -sp/2)], r_band);
        // GAMBA POSTERIORE: coup de fouet fino al tavolo, poi pattino e ricciolo
        tr(bez3(S(w_back, -sp/2), [20, 38], [36, rs], [u_attacco, rs]), 3.4, rs);
        tr([[u_attacco, rs], [u_coda, rs]], rs);
        tr(spirale([u_coda, rs + 5.5], 5.5, 1.8, -90, 215), rs, 1.2);
        // controvento a frusta dietro lo schienale
        tr(bez3(P(40, -sp - 3), [46, 74], [36, 26], [56, rs]), 2.0, 1.4);
        // GAMBA ANTERIORE leggermente sinuosa + piedino a ricciolo
        tr(bez3([-33, rs], [-29, 22], [-38, 40], [-35.5, z_arm]), rs);
        tr([[-40, rs], [-28, rs]], rs);
        tr(spirale([-40, rs + 4], 4, 1.4, -90, -330), rs, 1.1);
        // BRACCIOLO con voluta
        tr([[-40, z_arm], [P(a_arm, -sp/2)[0], z_arm]], rs);
        tr(spirale([-40, z_arm - 4.4], 4.4, 1.5, 90, 400), rs, 1.2);
        // ornamenti: frusta sotto la seduta e tralcio sotto il bracciolo
        tr(concat(bez3([-32.5, 13], [-10, 0], [-22, 34], [-4, 31]),
                  spirale([-4, 26], 5, 1.8, 90, -200)), 1.7, 1.1);
        tr(concat(bez3([-15, z_arm], [-21, z_arm - 4], [-11, z_E + 6], [-24, z_E + 5]),
                  [S(-26, 3)]), 1.4, 1.1);
    }
    for (w = ling_seduta)
        polygon([S(w-lt/2-c2, -sp-c2), S(w+lt/2+c2, -sp-c2), S(w+lt/2+c2, c2), S(w-lt/2-c2, c2)]);
    for (a = ling_schienale)
        polygon([P(a-lt/2-c2, -sp-c2), P(a+lt/2+c2, -sp-c2), P(a+lt/2+c2, c2), P(a-lt/2-c2, c2)]);
    translate([-200, -50]) square([400, 50]);       // niente sotto il tavolo
}
module fianco() linear_extrude(sp, convexity=10) fianco_2d();
module fianco_montato(s) translate([s > 0 ? x_in : -x_out, 0, 0]) rotate([90,0,90]) fianco();

// =====================================================================
// VISTE
// =====================================================================
module panchina() {
    color("Peru")      seduta_montata();
    color("BurlyWood") schienale_montato();
    color("DarkSlateGray") for (s=[-1,1]) fianco_montato(s);
    if (mostra_fermo && tipo_fermo == "manneken") color("Goldenrod") mannekens_montati();
}
module cavo() on_back() {
    translate([0, inserzione, asse]) rotate([90,0,0]) cylinder(d=4, h=spazio_cavo);
    translate([-5.5, -20, asse-3]) cube([11, 20, 6]);          // overmold
}

if (modalita == "assemblato") {
    panchina();
    if (telefono) %on_back() translate([-38, 0, 0]) cube([76, 165, 9]);
    %cavo();
    %translate([-80, -70, -1]) cube([160, 200, 1]);
}
else if (modalita == "piatto1_fianchi") {
    translate([0, 0, 0]) fianco();
    translate([0, 112, 0]) fianco();
}
else if (modalita == "piatto2_seduta_schienale") {
    translate([0, -w_front, 0]) seduta();
    translate([0, 50, sp]) off_back() schienale_montato();
}
else if (modalita == "manneken") {   // 2 pezzi, stampali col piatto 2
    // destro e sinistro sono speculari (il tenone sta sempre sul lato telefono)
    translate([0, 4, 0]) manneken();
    translate([16, 30, 0]) mirror([1, 0, 0]) manneken();
}
else if (modalita == "seduta")    seduta();
else if (modalita == "schienale") translate([0, 0, sp]) off_back() schienale_montato();
else if (modalita == "fianco")    fianco();
else if (modalita == "test_giunti") test_giunti();   // ugello 0.4, impostazioni definitive
else if (modalita == "check") intersection() { panchina(); cavo(); }

// =====================================================================
// PROVINO DEI GIUNTI (circa 11 g, ~45 min con ugello 0.4)
// A) piastra "fianco" con 7 fori per linguetta, un gioco diverso per foro
// B) linguetta campione, identica a quelle di seduta e schienale
// C) striscia "doga" con 7 fessure per il tenone del Manneken; il bordo
//    davanti alla fessura e' sottile come sulla seduta vera
// Numeri incisi = gioco in centesimi di mm. Il Manneken si prova col pezzo
// vero (modalita = "manneken", ugello 0.2).
// =====================================================================
passo_test = 14;
module etichetta(g) linear_extrude(1, convexity=10)
    text(str(round(g*100)), size=3.4, font="Liberation Sans:style=Bold", halign="center", valign="center");
module test_giunti() {
    n = len(giochi_test);
    W = n*passo_test + 4;
    // A) fori linguetta
    difference() {
        linear_extrude(sp, convexity=10) offset(r=2) offset(delta=-2) square([W, 20]);
        for (i=[0:n-1]) let(g = giochi_test[i], x = 2 + passo_test*(i + 0.5)) {
            translate([x - (sp + g)/2, 11 - (lt + g)/2, -1]) cube([sp + g, lt + g, sp + 2]);
            translate([x, 3.3, sp - 0.6]) etichetta(g);
        }
    }
    // B) linguetta campione con impugnatura
    translate([0, 26, 0]) {
        linear_extrude(sp, convexity=10) offset(r=2) offset(delta=-2) square([18, 14]);
        translate([18 - 0.5, 7 - lt/2, 0]) cube([sp + 0.65, lt, sp]);
    }
    // C) fessure Manneken (bordo anteriore sottile come sulla doga 3)
    bordo = 19.2 + w_fermo_in - t_tenone - gioco_manneken/2;   // ~1.7 mm, come la seduta
    translate([32, 26, 0]) difference() {
        cube([56, 14, sp]);
        for (i=[0:4]) let(g = giochi_test[i], x = 7 + 10.5*i) {
            translate([x - 3 - g/2, bordo, -1]) cube([6 + g, t_tenone + g, sp + 2]);
            translate([x, 9.5, sp - 0.6]) etichetta(g);
        }
    }
}
