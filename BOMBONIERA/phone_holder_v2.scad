// =====================================================================
// PHONE HOLDER BOMBONIERA DI LAUREA - 2 PEZZI AD INCASTRO (v2)
// Parametrico - Ender 3 V2 - stampa piatta, ZERO supporti
// Pensato per ABS (ok anche PLA/PETG). Ugello 0.4 consigliato.
// =====================================================================

/* [Testi] */
titolo_superiore = "BRUXELLES 2026";
nome_laureato    = "LAUREA LUCA";
corso_o_data     = "BIRRA & WAFFLES";
frase_ricordo    = "Grazie di tutto!";
mostra_tocco_laurea = true;
mostra_cornice_tech = true;

/* [Dimensioni generali (mm)] */
larghezza_stand   = 72.0;
altezza_stand     = 125.0;
spessore_piastra  = 3.6;
profondita_culla  = 14.5;  // spessore MAX del telefono, cover inclusa
altezza_labbro    = 2.5;   // labbro anti-scivolamento (0 = disattivato)
larghezza_ripiano = 60.0;
altezza_ripiano   = 5.0;   // quota del ripiano (solo tipo_dock "nessuno")
luce_cavo_usb     = 24.0;  // larghezza intaglio cavo (solo "nessuno")
h_intaglio_cavo   = 25.0;  // altezza intaglio cavo (solo "nessuno")

/* [Inclinazione e piede] */
quota_z_fessura       = 36.0; // posizione fessura lungo lo schienale
w_fessura             = 42.0;
w_piede_base          = 64.0;
lunghezza_corpo_piede = 56.0; // piu' lungo = stand piu' in piedi
smusso_appoggio       = true; // smussa il retro del piede: appoggia piatto sul tavolo
foro_piede            = true; // alleggerimento centrale

/* [Tolleranze] */
clearance        = 0.30; // ABS: parti da 0.30 e verifica col test_incastro
profondita_testo = 0.8;

/* [Dock di ricarica] */
tipo_dock = "nessuno";        // "nessuno" | "magnetico"
altezza_ripiano_magn  = 24.0; // ripiano rialzato per far stare punta + cavo
diametro_punta        = 8.0;  // diametro punta magnetica del cavo (CALIPRO)
lunghezza_punta       = 12.0; // lunghezza punta magnetica del cavo
diametro_cavo         = 4.0;
lunghezza_adattatore  = 6.0;  // quanto sporge l'adattatore magnetico sotto il telefono
quota_asse_porta      = 5.0;  // asse della porta dalla schiena del telefono (cover inclusa)
gioco_dock            = 0.5;  // gioco radiale della sede

/* [Vista] */
modalita = "stampa"; // "stampa" | "assemblato" | "solo_schienale" | "solo_piede" | "test_dock" | "test_incastro"

$fn = 60;

// =====================================================================
// CALCOLI DERIVATI
// =====================================================================
dock_magn   = (tipo_dock == "magnetico");
y_ripiano   = dock_magn ? altezza_ripiano_magn : altezza_ripiano;
z_culla     = spessore_piastra + profondita_culla;      // inizio del labbro
z_tot       = z_culla + altezza_labbro;                 // altezza totale del pezzo

h_fessura   = spessore_piastra + clearance;
w_linguetta = w_fessura - 2*clearance;
lunghezza_linguetta = spessore_piastra - 0.2;           // a filo, non sporge
mezzo       = spessore_piastra/2;

// angolo di appoggio dello stand (gradi dall'orizzontale)
angolo = atan(lunghezza_corpo_piede /
              (quota_z_fessura + (smusso_appoggio ? mezzo : -mezzo)));

r_punta   = (diametro_punta + 2*gioco_dock)/2;
r_cavo    = (diametro_cavo + 2*gioco_dock)/2;
y_gradino = y_ripiano - lunghezza_adattatore - 0.5 - lunghezza_punta;
z_asse    = spessore_piastra + quota_asse_porta;

assert(!dock_magn || y_gradino >= 3, "Dock magnetico: punta+adattatore troppo lunghi, alza altezza_ripiano_magn");
assert(!dock_magn || z_asse - r_punta >= 2, "Dock magnetico: quota_asse_porta troppo bassa");
assert(r_cavo < r_punta, "Il cavo deve essere piu' sottile della punta");
assert(y_ripiano + altezza_labbro < quota_z_fessura - h_fessura/2 - 2, "Ripiano troppo alto: tocca la fessura");

echo(str("Angolo di appoggio: ", angolo, " gradi"));

// =====================================================================
// VISTE
// =====================================================================
if (modalita == "stampa") {
    translate([-larghezza_stand/2 - 6, 0, 0]) schienale();
    translate([w_piede_base/2 + 6, 0, 0]) piede();
}
else if (modalita == "assemblato") {
    // tavolo fantasma
    %translate([-60, -60, -1]) cube([120, 200, 1]);
    rotate([angolo, 0, 0]) {
        schienale();
        translate([0, quota_z_fessura + mezzo, -lunghezza_corpo_piede])
            rotate([90, 0, 0]) piede();
    }
}
else if (modalita == "solo_schienale") schienale();
else if (modalita == "solo_piede") piede();
else if (modalita == "test_dock") {
    y_test = min(quota_z_fessura - h_fessura/2 - 1, y_ripiano + altezza_labbro + 10);
    intersection() {
        schienale();
        translate([-40, -5, -1]) cube([80, y_test + 5, z_tot + 5]);
    }
}
else if (modalita == "test_incastro") {
    translate([-60, 0, 0]) intersection() {
        schienale();
        translate([-40, quota_z_fessura - 8, -1]) cube([80, 16, 10]);
    }
    translate([20, 0, 0]) intersection() {
        piede();
        translate([-40, lunghezza_corpo_piede - 14, -1]) cube([80, 40, 10]);
    }
}

// =====================================================================
// SCHIENALE
// =====================================================================
module schienale() {
    difference() {
        union() {
            piastra_incisa();
            ripiano();
        }
        fessura_piede();
        taglio_cavo();
    }
}

module piastra() {
    hull() {
        translate([-larghezza_stand/2 + 6, 6, 0]) cylinder(r=6, h=spessore_piastra);
        translate([ larghezza_stand/2 - 6, 6, 0]) cylinder(r=6, h=spessore_piastra);
        translate([-larghezza_stand/2 + 8, altezza_stand - 8, 0]) cylinder(r=8, h=spessore_piastra);
        translate([ larghezza_stand/2 - 8, altezza_stand - 8, 0]) cylinder(r=8, h=spessore_piastra);
    }
}

// le incisioni tagliano SOLO la piastra (non il ripiano)
module piastra_incisa() {
    difference() {
        piastra();
        translate([0, 0, spessore_piastra - profondita_testo]) incisioni_schienale();
    }
}

module fessura_piede() {
    translate([-w_fessura/2, quota_z_fessura - h_fessura/2, -1])
        cube([w_fessura, h_fessura, spessore_piastra + 2]);
}

// Ripiano: profilo (y,z) estruso in X. Nessun overhang: il labbro ha
// il sottosquadro a 45 gradi.
module ripiano() {
    lab = altezza_labbro;
    pts = lab > 0
        ? [[0,0], [y_ripiano,0], [y_ripiano,z_culla], [y_ripiano+lab, z_culla+lab], [0, z_culla+lab]]
        : [[0,0], [y_ripiano,0], [y_ripiano,z_culla], [0,z_culla]];
    rotate([90, 0, 90])
        linear_extrude(height=larghezza_ripiano, center=true)
            polygon(pts);
}

// Intaglio cavo (attraversa tutto: piastra + ripiano)
module taglio_cavo() {
    if (dock_magn) {
        len_sede = y_ripiano - y_gradino + altezza_labbro + 2;
        // gola stretta per il cavo, sotto il gradino
        translate([-r_cavo, -1, -1])
            cube([2*r_cavo, y_gradino + 1.01, z_tot + 2]);
        // sede della punta: cilindro + apertura verso l'alto (a U)
        translate([0, y_gradino, z_asse]) rotate([-90, 0, 0])
            cylinder(r=r_punta, h=len_sede);
        translate([-r_punta, y_gradino, z_asse])
            cube([2*r_punta, len_sede, z_tot]);
    } else {
        translate([-luce_cavo_usb/2, -1, -1])
            cube([luce_cavo_usb, h_intaglio_cavo + 1, z_tot + 2]);
    }
}

// =====================================================================
// INCISIONI (invariate)
// =====================================================================
module incisioni_schienale() {
    linear_extrude(profondita_testo + 0.2) {
        if (mostra_tocco_laurea) {
            translate([0, altezza_stand - 20]) {
                rotate([0, 0, 45]) square([15, 15], center=true);
                translate([0, -5.5]) scale([1.3, 0.7]) circle(r=5);
                circle(r=1.3);
                polygon([[0,0],[6,-3],[8,-10],[6.5,-10],[4.5,-3]]);
            }
        }
        if (mostra_cornice_tech) {
            difference() {
                hull() {
                    translate([-larghezza_stand/2 + 5, 8]) circle(r=3);
                    translate([ larghezza_stand/2 - 5, 8]) circle(r=3);
                    translate([-larghezza_stand/2 + 6, altezza_stand - 6]) circle(r=4);
                    translate([ larghezza_stand/2 - 6, altezza_stand - 6]) circle(r=4);
                }
                hull() {
                    translate([-larghezza_stand/2 + 6.2, 9.2]) circle(r=2.5);
                    translate([ larghezza_stand/2 - 6.2, 9.2]) circle(r=2.5);
                    translate([-larghezza_stand/2 + 7.2, altezza_stand - 7.2]) circle(r=3.5);
                    translate([ larghezza_stand/2 - 7.2, altezza_stand - 7.2]) circle(r=3.5);
                }
                translate([-larghezza_stand/2 + 5, altezza_stand - 18]) square([3, 10], center=true);
                translate([ larghezza_stand/2 - 5, altezza_stand - 18]) square([3, 10], center=true);
            }
        }
        translate([0, altezza_stand - 35])
            text(titolo_superiore, size=4.4, font="Liberation Sans:style=Bold", halign="center", valign="center");
        translate([0, altezza_stand - 45])
            text(nome_laureato, size=5.6, font="Liberation Sans:style=Bold", halign="center", valign="center");
        translate([0, altezza_stand - 54])
            text(corso_o_data, size=3.6, font="Liberation Sans", halign="center", valign="center");
        translate([0, quota_z_fessura + 12])
            text(frase_ricordo, size=3.2, font="Liberation Sans:style=Italic", halign="center", valign="center");
    }
}

// =====================================================================
// PIEDE
// Si stampa piatto. Il retro (y=0) appoggia sul tavolo, la linguetta
// entra nella fessura dello schienale a filo e il carico lavora in
// compressione sulle spalle.
// =====================================================================
module piede() {
    tt = tan(angolo);
    difference() {
        linear_extrude(spessore_piastra) {
            union() {
                hull() {
                    translate([-w_piede_base/2 + 6, 6]) circle(r=6);
                    translate([ w_piede_base/2 - 6, 6]) circle(r=6);
                    translate([-w_piede_base/2 + 4, lunghezza_corpo_piede - 4]) circle(r=4);
                    translate([ w_piede_base/2 - 4, lunghezza_corpo_piede - 4]) circle(r=4);
                }
                // linguetta trapezoidale (invito laterale di 0.8 mm)
                polygon([
                    [-w_linguetta/2,       lunghezza_corpo_piede - 0.01],
                    [ w_linguetta/2,       lunghezza_corpo_piede - 0.01],
                    [ w_linguetta/2 - 0.8, lunghezza_corpo_piede + lunghezza_linguetta],
                    [-w_linguetta/2 + 0.8, lunghezza_corpo_piede + lunghezza_linguetta]
                ]);
            }
        }
        if (foro_piede)
            translate([0, 0, -1]) linear_extrude(spessore_piastra + 2)
                hull() {
                    translate([0, 24]) circle(r=10);
                    translate([0, 40]) circle(r=6);
                }
        // smusso retro: la faccia sul piatto resta lunga, la superiore si accorcia
        // (nessun overhang) e a stand montato il retro appoggia piatto sul tavolo
        if (smusso_appoggio)
            rotate([90, 0, 90])
                linear_extrude(height=w_piede_base + 2, center=true)
                    polygon([[-2, -1], [-tt, -1],
                             [(spessore_piastra + 1)*tt, spessore_piastra + 1],
                             [-2, spessore_piastra + 1]]);
    }
}
