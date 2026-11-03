// =====================================================================
// 03 - TEST DIAMETRI (fori e cilindri esterni)
// =====================================================================
// Fila dietro: FORI da 2 a 12 mm + sede esagonale per dado M3.
// Fila davanti: CILINDRI esterni da 4, 8, 12 mm + quadrato 15x15.
//
// Misura col calibro (fori piccoli: prova con le punte da trapano).
// In Cura:
//  - fori troppo piccoli   -> "Hole Horizontal Expansion" (+ media errore/2)
//  - esterni troppo grandi -> "Horizontal Expansion"      (- media errore/2)
//  - se sono sbagliati di una % costante su tutto (es. 1%) -> e' il flusso
//    o lo shrink, NON gli steps X/Y (cinghie GT2 = precise).
// Esempio: foro 10 misura 9.80 -> errore 0.20 sul diametro -> +0.10 di
// Hole Horizontal Expansion.
// =====================================================================

/* [Piastra] */
spessore = 4;   // [3:0.5:8]
smusso   = 0.4; // [0:0.1:1]
// Chiave del dado M3 (5.5 nominale) senza gioco: il gioco lo dice il test
chiave_m3 = 5.5;

/* [Hidden] */
$fn = 96;
fori     = [2, 3, 4, 5, 6, 8, 10, 12];
cilindri = [4, 8, 12];
lato_q   = 15;
h_cil    = 6;
spazio   = 4;
bordo    = 3;
font     = "Liberation Sans:style=Bold";
incisione = 0.6;

// somma dei primi n elementi di un vettore
function somma(v, n) = n <= 0 ? 0 : v[n-1] + somma(v, n-1);
// centro x dell'i-esimo foro
function cx(v, i) = bordo + somma(v, i) + i*spazio + v[i]/2;

lung_fori = bordo*2 + somma(fori, len(fori)) + (len(fori))*spazio + chiave_m3/cos(30);
larghezza = lung_fori;
riga_fori_y = 20;          // centro dei fori
profondita  = riga_fori_y + 12/2 + 7;

module foro(d) {
    translate([0,0,-0.01]) cylinder(d = d, h = spessore + 0.02);
    translate([0,0,-0.01]) cylinder(d1 = d + 2*smusso, d2 = d, h = smusso + 0.01);
    translate([0,0,spessore - smusso]) cylinder(d1 = d, d2 = d + 2*smusso, h = smusso + 0.01);
}

module etichetta(t, x, y) {
    translate([x, y, spessore - incisione])
        linear_extrude(incisione + 0.01)
            text(t, size = 2.6, font = font, halign = "center", valign = "center");
}

difference() {
    cube([larghezza, profondita, spessore]);
    for (i = [0 : len(fori)-1]) {
        translate([cx(fori, i), riga_fori_y, 0]) foro(fori[i]);
        etichetta(str(fori[i]), cx(fori, i), riga_fori_y + 12/2 + 3.5);
    }
    // sede esagonale M3 (misurata tra le facce piane)
    x_hex = bordo + somma(fori, len(fori)) + len(fori)*spazio + chiave_m3/cos(30)/2;
    translate([x_hex, riga_fori_y, -0.01])
        rotate([0,0,30]) cylinder(d = chiave_m3/cos(30), h = spessore + 0.02, $fn = 6);
    etichetta("M3", x_hex, riga_fori_y + 12/2 + 3.5);
}

// cilindri esterni e quadrato, davanti alla piastra
translate([0, -lato_q - 4, 0]) {
    cube([larghezza, lato_q + 4, 1.2]);   // basetta
    for (i = [0 : len(cilindri)-1])
        translate([cx(cilindri, i) + 2, (lato_q + 4)/2, 1.2]) cylinder(d = cilindri[i], h = h_cil);
    translate([larghezza - bordo - lato_q, 2, 1.2]) cube([lato_q, lato_q, h_cil]);
}
