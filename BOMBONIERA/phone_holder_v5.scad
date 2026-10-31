// =====================================================================
// PHONE HOLDER BOMBONIERA DI LAUREA - v5 "CAVALLETTO"
// Redesign completo della v4:
//  - schienale rastremato con cima arrotondata (dietro al telefono non si vede)
//  - grande arco ellittico tra due gambe: il cavo passa sotto e va dietro
//  - due ganci arrotondati con raccordo a 45 gradi, centro libero per il plug
//  - quota dei ganci calcolata dall'altezza REALE sul tavolo (telefono piu' basso)
//  - piede a telaio con tacca passacavo sul retro
// Incastro fessura/linguetta identico alla v4 (stessa clearance e w_fessura).
// Ender 3 V2 - stampa piatta, ZERO supporti - PLA (ok PETG/ABS)
// =====================================================================

/* [Testi] */
riga_sopra  = "LAUREA";
nome        = "LUCA";
riga_sotto  = "BRUXELLES 2026";
motto       = "BIRRA & WAFFLES";
frase       = "Grazie di tutto!";
mostra_tocco   = true;
mostra_cornice = true;

/* [Schienale (mm)] */
larghezza_base   = 72.0;  // ai piedi (stabilita' laterale)
larghezza_cima   = 58.0;  // in alto: resta nascosta dietro al telefono
altezza_stand    = 122.0;
spessore_piastra = 3.6;
r_cima           = 16.0;  // raggio delle spalle superiori
larghezza_gamba  = 12.0;  // gambe dell'arco, al tavolo
margine_arco     = 6.0;   // materiale pieno tra cima dell'arco e fessura

/* [Ganci] */
profondita_culla = 14.5;  // spessore MAX del telefono, cover inclusa
altezza_labbro   = 2.5;   // labbro anti-scivolamento
larghezza_gancio = 12.0;
luce_ganci       = 34.0;  // spazio libero tra i ganci (plug + overmold)
spessore_gancio  = 5.0;
raccordo_gancio  = 2.0;   // raccordo a 45 gradi alla base del gancio

/* [Cavo USB-C] */
spazio_cavo     = 55.0;  // tratto DRITTO: dalla punta del plug a dove si piega
inserzione_plug = 6.5;   // quanto il plug entra nel telefono
asse_porta      = 4.5;   // asse della porta dalla schiena del telefono (cover inclusa)
margine_cavo    = 4.0;   // aria minima tra la piega del cavo e il tavolo

/* [Piede e incastro] */
quota_fessura   = 38.5;  // posizione fessura lungo lo schienale
w_fessura       = 42.0;
lunghezza_piede = 70.0;  // piu' lungo = stand piu' in piedi
w_piede_retro   = 60.0;  // bordo appoggiato al tavolo
w_piede_attacco = 50.0;  // lato linguetta (spalle da 4 mm per parte)
bordo_telaio    = 7.0;   // larghezza dei lati del telaio del piede
tacca_cavo      = true;  // passacavo sul retro del piede

/* [Verifica stabilita'] */
altezza_telefono = 165.0; // telefono grande, per il controllo del baricentro

/* [Tolleranze] */
clearance        = 0.30; // ABS testato a 0.30; in PLA rifai test_incastro (0.25?)
profondita_testo = 0.8;

/* [Vista] */
modalita = "stampa"; // [stampa, assemblato, solo_schienale, solo_piede, test_incastro]

$fn = 72;

// =====================================================================
// CALCOLI
// =====================================================================
mezzo       = spessore_piastra/2;
h_fessura   = spessore_piastra + clearance;
w_linguetta = w_fessura - 2*clearance;
lunghezza_linguetta = spessore_piastra - 0.2;   // a filo, non sporge

// angolo dello schienale sul tavolo (il retro del piede e' smussato)
angolo = atan(lunghezza_piede / (quota_fessura + mezzo));

// quota dei ganci: la piega del cavo deve restare margine_cavo sopra il tavolo.
// Il plug sta davanti alla piastra, quindi parte gia' un po' piu' in alto.
d_asse    = spessore_piastra + asse_porta;
tratto    = spazio_cavo - inserzione_plug;          // sporgenza sotto il telefono
y_ripiano = tratto + (margine_cavo - d_asse*cos(angolo)) / sin(angolo);

z_culla = spessore_piastra + profondita_culla;
z_tot   = z_culla + altezza_labbro;
y0_gancio = y_ripiano - spessore_gancio;
x_gancio  = (luce_ganci + larghezza_gancio)/2;

y_fessura_bot = quota_fessura - h_fessura/2;
y_fessura_top = quota_fessura + h_fessura/2;
h_arco = y_fessura_bot - margine_arco;
w_arco = larghezza_base - 2*larghezza_gamba;

// stabilita' (in orizzontale dal bordo anteriore verso il retro)
base_appoggio = (quota_fessura + mezzo)*cos(angolo) + lunghezza_piede*sin(angolo);
cg_telefono   = (y_ripiano + altezza_telefono/2)*cos(angolo)
                - (spessore_piastra + 4)*sin(angolo);
h_piega = (y_ripiano - tratto)*sin(angolo) + d_asse*cos(angolo);
h_bordo_telefono = y_ripiano*sin(angolo) + spessore_piastra*cos(angolo);

assert(y0_gancio - raccordo_gancio >= y_fessura_top + 0.5,
       "Ganci troppo bassi: toccano la fessura. Abbassa quota_fessura");
assert(h_arco > 15, "Arco troppo basso");
assert(x_gancio + larghezza_gancio/2 < larghezza_base/2 - 3, "Ganci troppo larghi per lo schienale");
assert(w_piede_attacco >= w_fessura + 6, "Spalle del piede troppo strette");
assert(cg_telefono < base_appoggio - 15, "Instabile: allunga il piede o alza la fessura");

echo(str("Angolo: ", angolo, " gradi"));
echo(str("Ganci a ", y_ripiano, " mm lungo lo schienale, bordo telefono a ", h_bordo_telefono, " mm dal tavolo"));
echo(str("Piega del cavo a ", h_piega, " mm dal tavolo"));
echo(str("Base d'appoggio ", base_appoggio, " mm, baricentro telefono a ", cg_telefono, " mm"));

// =====================================================================
// VISTE
// =====================================================================
if (modalita == "stampa") {
    translate([-larghezza_base/2 - 4, 0, 0]) schienale();
    translate([w_piede_retro/2 + 4, 0, 0]) piede();
}
else if (modalita == "assemblato") {
    %translate([-70, -40, -1]) cube([140, 160, 1]);   // tavolo
    rotate([angolo, 0, 0]) {
        schienale();
        translate([0, quota_fessura + mezzo, -lunghezza_piede])
            rotate([90, 0, 0]) piede();
        // telefono e cavo fantasma
        %translate([-38, y_ripiano, spessore_piastra]) cube([76, altezza_telefono, 9]);
        %translate([0, y_ripiano + inserzione_plug, d_asse])
            rotate([90, 0, 0]) cylinder(d=6, h=spazio_cavo);
    }
}
else if (modalita == "solo_schienale") schienale();
else if (modalita == "solo_piede") piede();
else if (modalita == "test_incastro") {
    // provino: fascia dello schienale con la fessura + punta del piede
    translate([-larghezza_base/2 - 4, 0, 0]) intersection() {
        schienale();
        translate([-50, quota_fessura - 5, -1]) cube([100, 9, spessore_piastra + 1]);
    }
    translate([w_piede_retro/2 + 4, 0, 0]) intersection() {
        piede();
        translate([-50, lunghezza_piede - 12, -1]) cube([100, 30, spessore_piastra + 2]);
    }
}

// =====================================================================
// SCHIENALE
// =====================================================================
module sagoma_schienale() {
    r_b = 4;
    offset(r=1.5) offset(delta=-1.5)      // raccorda gli spigoli vivi
    difference() {
        hull() for (s = [-1, 1]) {
            translate([s*(larghezza_base/2 - r_b), r_b]) circle(r=r_b);
            translate([s*(larghezza_cima/2 - r_cima), altezza_stand - r_cima]) circle(r=r_cima);
        }
        scale([w_arco/2, h_arco]) circle(r=1, $fn=144);
    }
}

module schienale() {
    difference() {
        union() {
            difference() {
                linear_extrude(spessore_piastra) sagoma_schienale();
                translate([0, 0, spessore_piastra - profondita_testo])
                    linear_extrude(profondita_testo + 0.1) incisioni();
            }
            for (s = [-1, 1]) gancio(s*x_gancio);
        }
        // fessura del piede
        translate([-w_fessura/2, y_fessura_bot, -1])
            cube([w_fessura, h_fessura, spessore_piastra + 2]);
    }
}

// Gancio: profilo (y,z) estruso in X, intersecato con un'impronta arrotondata.
// Sottosquadro del labbro e raccordo alla base a 45 gradi: niente supporti.
module gancio(xc) {
    lab = altezza_labbro;
    g   = raccordo_gancio;
    y0  = y0_gancio;
    pts = [[y0 - g, 0], [y_ripiano, 0], [y_ripiano, z_culla],
           [y_ripiano + lab, z_tot], [y0, z_tot],
           [y0, spessore_piastra + g], [y0 - g, spessore_piastra]];
    intersection() {
        translate([xc, 0, 0]) rotate([90, 0, 90])
            linear_extrude(height=larghezza_gancio, center=true) polygon(pts);
        linear_extrude(z_tot + 1)
            translate([xc, 0]) offset(r=2) offset(delta=-2)
                translate([-larghezza_gancio/2, y0 - g])
                    square([larghezza_gancio, y_ripiano + lab - y0 + g]);
    }
}

module tocco() {
    rotate(45) square([15, 15], center=true);
    translate([0, -5.5]) scale([1.3, 0.7]) circle(r=5);
    polygon([[0,0], [6,-3], [8,-10], [6.5,-10], [4.5,-3]]);
}

module incisioni() {
    H = altezza_stand;
    if (mostra_cornice) difference() {
        offset(r=-2.2) sagoma_schienale();
        offset(r=-3.2) sagoma_schienale();
    }
    if (mostra_tocco) translate([0, H - 15]) scale(0.8) tocco();
    translate([0, H - 31]) text(riga_sopra, size=4.0, spacing=1.35,
        font="Liberation Sans:style=Bold", halign="center", valign="center");
    translate([0, H - 42]) text(nome, size=11,
        font="Liberation Sans:style=Bold", halign="center", valign="center");
    translate([0, H - 53]) text(riga_sotto, size=4.0,
        font="Liberation Sans:style=Bold", halign="center", valign="center");
    translate([0, H - 60]) text(motto, size=3.6,
        font="Liberation Sans:style=Bold", halign="center", valign="center");
    translate([0, H - 67.5]) text(frase, size=3.8,
        font="Liberation Sans:style=Bold Italic", halign="center", valign="center");
}

// =====================================================================
// PIEDE (telaio)
// y=0: retro appoggiato al tavolo; y=lunghezza_piede: spalle contro lo
// schienale; la linguetta entra nella fessura a filo.
// =====================================================================
module sagoma_piede() {
    L = lunghezza_piede;
    hull() for (s = [-1, 1]) {
        translate([s*(w_piede_retro/2 - 5), 5]) circle(r=5);
        translate([s*(w_piede_attacco/2 - 3), L - 3]) circle(r=3);
    }
}

module piede() {
    L  = lunghezza_piede;
    tt = tan(angolo);
    difference() {
        linear_extrude(spessore_piastra) {
            sagoma_piede();
            // linguetta trapezoidale (invito laterale 0.8 mm), come v4
            polygon([[-w_linguetta/2, L - 0.01], [w_linguetta/2, L - 0.01],
                     [ w_linguetta/2 - 0.8, L + lunghezza_linguetta],
                     [-w_linguetta/2 + 0.8, L + lunghezza_linguetta]]);
        }
        // finestra del telaio
        translate([0, 0, -1]) linear_extrude(spessore_piastra + 2)
            offset(r=4) offset(delta=-4)
            intersection() {
                offset(delta=-bordo_telaio) sagoma_piede();
                translate([-50, 11]) square([100, L - 11 - 8]);
            }
        // passacavo sul bordo che tocca il tavolo
        if (tacca_cavo)
            translate([0, 0, -1]) linear_extrude(spessore_piastra + 2)
                hull() { translate([0, 1.5]) circle(r=3.5); translate([-3.5, -2]) square([7, 1]); }
        // smusso: il retro appoggia piatto sul tavolo (nessun overhang)
        rotate([90, 0, 90])
            linear_extrude(height=w_piede_retro + 2, center=true)
                polygon([[-2, -1], [-tt, -1],
                         [(spessore_piastra + 1)*tt, spessore_piastra + 1],
                         [-2, spessore_piastra + 1]]);
    }
}
