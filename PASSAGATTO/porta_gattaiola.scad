// =====================================================================
//  Porta basculante per gattaiola — modello parametrico (OpenSCAD)
//  v4: struttura a nervature (lastra da 2 mm + muretti da 2 mm)
//
//  Riferimento:
//    X = larghezza, centrata (x = 0 sull'asse di simmetria)
//    Y = altezza    (0 = fondo arrotondato, H = bordo superiore coi perni)
//    Z = spessore   (0 .. T, piano medio a T/2; il pezzo e' simmetrico in Z)
// =====================================================================

$fn = 72;
eps = 0.01;

// ---------------------------------------------------------------------
//  STAMPA
// ---------------------------------------------------------------------
// "meta"   : mezza porta tagliata sul piano medio, faccia di taglio sul
//            piatto -> nessun supporto. Se ne stampano DUE uguali, una si
//            ribalta e si saldano (ASA + acetone).
// "intera" : pezzo intero, come l'originale (serve supporto)
modo = "meta";
anima_perno = false; // true = canale per un tondino d'acciaio da 3 mm nei perni (rinforzo)
d_anima     = 3.2;
l_anima     = 14;    // lunghezza del canale dalla punta del perno
d_spina     = 1.9;   // fori per spinette di allineamento (filamento 1.75)
p_spina     = 3;

// ---------------------------------------------------------------------
//  CONTORNO
// ---------------------------------------------------------------------
H       = 152.5;  // altezza totale
W_bot   = 146;    // larghezza della parte bassa arrotondata
rx_bot  = 38;     // angolo in basso: estensione orizzontale
ry_bot  = 45;     // angolo in basso: estensione verticale
W_body  = 134;    // larghezza del corpo nel tratto della calamita
gioco_contorno = 0.3;

// ---------------------------------------------------------------------
//  LASTRA E NERVATURE
// ---------------------------------------------------------------------
T       = 9.5;    // altezza delle nervature (spessore massimo)
t_pan   = 2;      // lastra / pannello
t_nerv  = 2;      // spessore di ogni nervatura
g_nerv  = 2.5;    // vuoto tra nervatura esterna e interna
h_bar   = 17.5;   // dal bordo superiore al bordo inferiore della nervatura bassa della barra
t_bar   = 5;      // spessore della nervatura sul bordo superiore (l'unica che rientra)

// ---------------------------------------------------------------------
//  LINGUETTA PER LA CALAMITA (misure dal bordo superiore)
// ---------------------------------------------------------------------
lin_da   = 17;
lin_a    = 108.5;
fin_out  = 1;      // sporgenza della pinna oltre il fianco
dentini  = [[17, 10], [50, 6], [71, 6], [97, 10]];  // [inizio, lunghezza]
dent_out = 3;      // sporgenza dei dentini dal fianco
dent_w   = 6;      // larghezza dei dentini nello spessore
dent_smusso = 1;
dent_testa  = 1;   // spessore della testa a fungo

mag_l     = 90;    // lunghezza della calamita
gioco_mag_y = 2.5; // gioco in lunghezza della calamita montata (misurato sull'originale)
mag_h     = 5;     // calamita a U (solo controlli)
mag_depth = 2;
mag_open  = 7;

// ---------------------------------------------------------------------
//  PERNI
// ---------------------------------------------------------------------
pin_d      = 6;
pin_len    = 7.5;
pin_top    = 3;     // dal bordo superiore al bordo del perno (misurato)
col_d      = 12;
col_len    = 3;
col_h      = 12;    // altezza del collarino dal bordo superiore al lato opposto (12 = cerchio intero)
                    // il piatto e' a filo col bordo superiore della porta
pin_oltre_dentini = 10;   // dalla punta dei dentini alla punta del perno
gambo_w    = 9;     // spessore del gambo sotto il collarino
gambo_oltre = 2;    // il gambo sporge oltre la punta dei dentini
telaio_W   = 147;   // larghezza interna del telaio all'altezza dei fori
gioco_perno = 0;    // il foro del telaio (cupola 8 x 7) lascia gia' gioco
smusso_punta = 0.5;

// ---------------------------------------------------------------------
//  Derivate
// ---------------------------------------------------------------------
zm      = T / 2;
xb      = W_bot / 2 - gioco_contorno;
xs      = W_body / 2;
x_dent  = xs + dent_out;
col_out = x_dent + pin_oltre_dentini - pin_len;
x_gambo = x_dent + gambo_oltre;
y_bar   = H - h_bar;
// il tratto libero per la calamita va dalla barra alla nervatura del gradino:
// calamita + gioco (sostituisce la misura lin_a)
y_step  = y_bar - (mag_l + gioco_mag_y);
ryb     = min(ry_bot, y_step);
y_pin   = H - pin_top - pin_d / 2;
y_lin   = H - lin_da;            // inizio linguetta (in alto)
H_top   = y_pin - col_d / 2 + col_h;   // bordo superiore: a filo col piatto dei collarini
d_int   = t_nerv + g_nerv;       // distanza della nervatura interna dal bordo
x_col_in = x_dent - dent_testa;  // collarino e collo iniziano dove inizia la testa dei dentini

assert(2 * col_out < telaio_W, "i collarini non entrano nel telaio");
assert(dent_w < mag_open, "i dentini non entrano nella U della calamita");
assert(abs((x_dent + mag_h - mag_depth) - W_bot / 2) < 1.01,
       "la calamita montata non arriva a filo con la parte bassa");

// =====================================================================
//  2D
// =====================================================================
module fondo_largo(off = 0) {   // parte bassa allargata, prolungata in alto
    offset(delta = -off) hull() {
        for (s = [-1, 1])
            translate([s * (xb - rx_bot), ryb]) scale([rx_bot, ryb]) circle(1);
        translate([-xb, H - 1]) square([2 * xb, 1]);
    }
}

module contorno() {
    intersection() { fondo_largo(); translate([-xb - 1, 0]) square([2 * xb + 2, y_step + eps]); }
    translate([-xs, y_step]) square([2 * xs, H_top - y_step]);
}

// anello della nervatura interna: corre lungo il fondo e sui fianchi
// (dove la sua faccia esterna coincide col fianco del corpo)
// faccia esterna della nervatura interna: sui fianchi coincide col fianco
// del corpo e sotto il gradino curva subito, senza tratto dritto
module anello_esterno_sagoma() {
    xc = xb - rx_bot;                       // stessi centri dell'angolo esterno
    hull() {
        for (s = [-1, 1])
            translate([s * xc, ryb]) scale([xs - xc, ryb - d_int]) circle(1);
        translate([-xs, H - 1]) square([2 * xs, 1]);
    }
}
module nervatura_interna_2d() {   // aperta in alto: si innesta nella barra
    intersection() {
        difference() { anello_esterno_sagoma(); offset(delta = -t_nerv) anello_esterno_sagoma(); }
        translate([-xs - 1, -1]) square([2 * xs + 2, y_bar + 1]);
    }
}

// nervatura esterna lungo la parte bassa (bordo del pezzo)
module nervatura_esterna_2d() {
    intersection() {
        difference() { fondo_largo(); fondo_largo(t_nerv); }
        translate([-xb - 1, -1]) square([2 * xb + 2, y_step + 1]);
    }
}

// barra: nervatura sul bordo superiore (spessa t_bar) e sul bordo inferiore (a tutta altezza T)
module barra_alta_2d()  { translate([-xs, H_top - t_nerv]) square([2 * xs, t_nerv]); }
module barra_bassa_2d() { translate([-x_gambo, y_bar]) square([2 * x_gambo, t_nerv]); }  // dritta fino al blocco sotto il perno

r_racc = 1.5;   // raccordo tra collo e cerchio del collarino
module collo() { translate([y_bar, zm - gambo_w / 2]) square([y_pin - y_bar, gambo_w]); }
module serratura() {
    offset(delta = -r_racc) offset(r = r_racc) {
        translate([y_pin, zm]) circle(d = col_d);
        collo();
    }
}

module lungo_x(x0, len) {
    translate([x0, 0, 0]) rotate([90, 0, 90]) linear_extrude(len) children();
}

// =====================================================================
//  3D — dettagli del lato destro (x > 0)
// =====================================================================
module lato_destro() {
    // pinna (lastra che esce oltre il fianco)
    translate([xs - eps, y_step, zm - t_pan / 2])
        cube([fin_out + eps, y_bar - y_step, t_pan]);
    // chiusura del gradino in basso e in alto della linguetta (nervatura trasversale)
    translate([xs - t_nerv, y_step - t_nerv, 0]) cube([xb - xs + t_nerv, t_nerv, T]);
    // dentini a fungo: nervatura esterna "a tratti"
    for (i = [0 : len(dentini) - 1]) {
        d  = dentini[i];
        // il primo e l'ultimo dentino entrano nella nervatura trasversale:
        // l'invito resta nascosto e il dentino arriva "pieno" contro la nervatura
        y1 = (i == 0) ? max(H - d[0], y_bar) + dent_smusso : H - d[0];
        y0 = (i == len(dentini) - 1) ? min(H - d[0] - d[1], y_step - dent_smusso)
                                     : H - d[0] - d[1];
        translate([xs - eps, y0, zm - t_pan / 2]) cube([dent_out + eps, y1 - y0, t_pan]);
        xt = x_dent - dent_testa;
        hull() {
            translate([xt, y0 + dent_smusso, zm - dent_w / 2])
                cube([dent_testa, y1 - y0 - 2 * dent_smusso, dent_w]);
            translate([xt, y0, zm - t_pan / 2]) cube([dent_testa, y1 - y0, t_pan]);
        }
    }
    // lato corto del rettangolo superiore: prosegue la nervatura interna del
    // fianco dalla barra bassa fino alla nervatura del bordo superiore
    // in alto e' arrotondata come il cerchio del collarino (stesso profilo visto in testa)
    lungo_x(xs - t_nerv, t_nerv) intersection() {
        translate([y_bar, 0]) square([H_top - t_nerv - y_bar + eps, T]);
        union() {
            translate([y_pin, zm]) circle(d = col_d);
            translate([y_bar - 1, -1]) square([y_pin - y_bar + 1, T + 2]);
        }
    }
    // tra la nervatura e il collarino c'e' lo stesso scavo dei fianchi:
    // solo la lastra da 2 mm, come tra la nervatura e i dentini
    translate([xs - eps, y_bar, zm - t_pan / 2])
        cube([x_col_in - xs + 2 * eps, H_top - y_bar, t_pan]);
    // collarino + gambo: profilo "a serratura" (cerchio da 12 + collo largo
    // gambo_w che scende fino alla barra), raccordato senza spigoli vivi.
    // Sopra l'asse c'e' solo il cerchio del collarino.
    lungo_x(x_col_in, col_out - col_len - x_col_in + eps) serratura();
    lungo_x(col_out - col_len, col_len) translate([y_pin, zm]) circle(d = col_d);
    // il collo sporge fino a 2 mm oltre la punta dei dentini
    lungo_x(col_out - col_len, x_gambo - col_out + col_len) collo();
    // perno
    translate([col_out - eps, y_pin, zm]) rotate([0, 90, 0]) {
        dp = pin_d - gioco_perno;
        cylinder(d = dp, h = pin_len - smusso_punta + eps);
        translate([0, 0, pin_len - smusso_punta])
            cylinder(d1 = dp, d2 = dp - 2 * smusso_punta, h = smusso_punta);
    }
}

module porta_intera() {
    difference() {
        union() {
            // lastra
            translate([0, 0, zm - t_pan / 2]) linear_extrude(t_pan) contorno();
            // nervature a tutta altezza
            linear_extrude(T) { nervatura_interna_2d(); nervatura_esterna_2d(); }
            // barra superiore
            translate([0, 0, zm - t_bar / 2]) linear_extrude(t_bar) barra_alta_2d();
            linear_extrude(T) barra_bassa_2d();
            lato_destro();
            mirror([1, 0, 0]) lato_destro();
        }
        if (anima_perno) for (s = [-1, 1])
            translate([s * (col_out + pin_len + 1), y_pin, zm])
                rotate([0, s * -90, 0]) cylinder(d = d_anima, h = l_anima + 1);
    }
}

// spinette di allineamento nei collarini (12 mm), simmetriche in X
spine = [[col_out - col_len / 2, y_pin - 4.5], [-(col_out - col_len / 2), y_pin - 4.5]];

module mezza_porta() {
    translate([0, 0, -zm]) difference() {
        intersection() {
            porta_intera();
            translate([-200, -10, zm]) cube([400, 400, 50]);
        }
        for (p = spine)
            translate([p[0], p[1], zm - eps]) cylinder(d = d_spina, h = p_spina + eps, $fn = 24);
    }
}

if (modo == "meta") mezza_porta();
else porta_intera();

echo(str("Tratto libero per la calamita: ", y_bar - y_step, " mm (fine linguetta a ", H - y_step, " dal bordo)"));
echo(str("Altezza totale (cima collarini/barra): ", H_top, " mm"));
echo(str("Gioco collarino-telaio per lato: ", (telaio_W - 2 * col_out) / 2, " mm"));
echo(str("Ingombro perno-perno: ", 2 * (col_out + pin_len), " mm"));
