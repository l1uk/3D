// =====================================================================
// PHONE HOLDER BOMBONIERA DI LAUREA - 2 PEZZI AD INCASTRO (v4)
// v3: ripiano rialzato per far passare un cavo USB-C dritto (spazio_cavo)
// v4: due ganci laterali al posto della mensola + arco sotto lo schienale
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
spessore_ripiano  = 5.0;   // spessore della mensola su cui appoggia il telefono
luce_cavo_usb     = 24.0;  // fessura nel ripiano (solo dock magnetico / ganci=false)

/* [Ganci e arco (v4, solo tipo_dock "nessuno")] */
usa_ganci        = true;  // due ganci laterali invece della mensola piena
larghezza_gancio = 12.0;  // ogni gancio; distanza interna = larghezza_ripiano - 2*questo
usa_arco         = true;  // arco sotto la fessura: due gambe, il cavo passa in mezzo
larghezza_gamba  = 13.0;  // gambe dell'arco
margine_arco     = 4.0;   // materiale pieno tra la cima dell'arco e la fessura

/* [Spazio per il cavo (solo tipo_dock "nessuno")] */
spazio_cavo     = 55.0; // tratto DRITTO del cavo: dalla punta del plug a dove si piega
inserzione_plug = 6.5;  // quanto il plug entra nel telefono (USB-C ~6.5)
margine_cavo    = 4.0;  // aria extra sotto la piega
larghezza_passaggio = 14.0; // tacca per il cavo (solo se usa_arco = false)
altezza_passaggio   = 12.0;

/* [Inclinazione e piede] */
// v3: fessura piu' alta e piede piu' lungo -> stand piu' in piedi (~62 gradi)
// e base piu' profonda, perche' il telefono ora sta piu' in alto.
quota_z_fessura       = 40.0; // posizione fessura lungo lo schienale
w_fessura             = 42.0;
w_piede_base          = 64.0;
lunghezza_corpo_piede = 76.0; // piu' lungo = stand piu' in piedi

/* [Verifica stabilita'] */
altezza_telefono = 165.0; // telefono grande, per il controllo del baricentro
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
altezza_ripiano = spazio_cavo - inserzione_plug + margine_cavo;
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
// il ripiano (mensola o blocco magnetico) non deve toccare la fessura
y_base_ripiano = dock_magn ? 0 : y_ripiano - spessore_ripiano;
ganci  = usa_ganci && !dock_magn;
arco   = usa_arco  && !dock_magn;
w_arco = larghezza_stand - 2*larghezza_gamba;
h_arco = quota_z_fessura - h_fessura/2 - margine_arco;   // cima dell'arco
assert(!arco || h_arco > w_arco*0.55/2 + 5, "Arco troppo basso: riduci w_arco o alza la fessura");
assert(!ganci || larghezza_ripiano - 2*larghezza_gancio >= 20, "Ganci troppo larghi: non resta spazio per il plug");
assert(dock_magn
       ? y_ripiano + altezza_labbro < quota_z_fessura - h_fessura/2 - 2
       : y_base_ripiano > quota_z_fessura + h_fessura/2 + 1,
       "Ripiano e fessura si sovrappongono: cambia quota_z_fessura o spazio_cavo");
assert(y_ripiano + altezza_labbro + 20 < altezza_stand, "Ripiano troppo vicino alla cima: aumenta altezza_stand");

// stabilita': baricentro del telefono vs base d'appoggio (in orizzontale,
// da bordo anteriore dello schienale verso il retro)
base_appoggio = quota_z_fessura * cos(angolo) + lunghezza_corpo_piede * sin(angolo);
cg_telefono   = (y_ripiano + altezza_telefono/2) * cos(angolo)
                - (spessore_piastra + 4) * sin(angolo);
assert(cg_telefono < base_appoggio - 15, "Instabile: il telefono si ribalta all'indietro, allunga il piede");

echo(str("Angolo di appoggio: ", angolo, " gradi"));
echo(str("Ripiano a ", y_ripiano, " mm lungo lo schienale"));
echo(str("Base d'appoggio: ", base_appoggio, " mm, baricentro telefono a ", cg_telefono, " mm"));

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
        // telefono e plug fantasma (solo anteprima)
        %translate([-37, y_ripiano, spessore_piastra]) cube([74, altezza_telefono, 9]);
        %translate([0, y_ripiano + inserzione_plug, spessore_piastra + 4.5])
            rotate([90, 0, 0]) cylinder(d=6, h=spazio_cavo);
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
        translate([-40, quota_z_fessura - 6, -1]) cube([80, 12, 10]);
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
// "nessuno": mensola sottile alta y_ripiano, sotto resta vuoto per il plug.
// "magnetico": blocco pieno dal fondo (serve per la sede della punta).
module ripiano() {
    lab = altezza_labbro;
    y0  = y_base_ripiano;
    pts = lab > 0
        ? [[y0,0], [y_ripiano,0], [y_ripiano,z_culla], [y_ripiano+lab, z_culla+lab], [y0, z_culla+lab]]
        : [[y0,0], [y_ripiano,0], [y_ripiano,z_culla], [y0,z_culla]];
    if (ganci)
        for (s = [-1, 1])
            translate([s * (larghezza_ripiano - larghezza_gancio)/2, 0, 0])
                profilo_ripiano(pts, larghezza_gancio);
    else
        profilo_ripiano(pts, larghezza_ripiano);
}

module profilo_ripiano(pts, w) {
    rotate([90, 0, 90])
        linear_extrude(height=w, center=true)
            polygon(pts);
}

// Arco 2D (coordinate della piastra): rettangolo dal fondo + cima tonda
module arco_2d(off = 0) {
    offset(delta = off) {
        translate([-w_arco/2, -10]) square([w_arco, h_arco - w_arco/2 + 10]);
        translate([0, h_arco - w_arco/2]) scale([1, 0.55]) circle(d = w_arco);
    }
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
        // fessura nella mensola (con i ganci il centro e' gia' libero)
        if (!ganci)
            translate([-luce_cavo_usb/2, y_base_ripiano - 1, spessore_piastra - 0.01])
                cube([luce_cavo_usb, spessore_ripiano + altezza_labbro + 2, z_tot + 2]);
        if (arco)
            translate([0, 0, -1]) linear_extrude(spessore_piastra + 2) arco_2d();
        else
            // tacca in fondo allo schienale: il cavo passa dietro lo stand
            translate([-larghezza_passaggio/2, -1, -1])
                cube([larghezza_passaggio, altezza_passaggio + 1, spessore_piastra + 2]);
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
        if (mostra_cornice_tech) difference() {
          union() {
            // v4: la cornice segue anche il profilo dell'arco
            if (arco) difference() { arco_2d(3.7); arco_2d(2.5); }
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
          if (arco) arco_2d(2.5);
        }
        translate([0, altezza_stand - 35])
            text(titolo_superiore, size=4.4, font="Liberation Sans:style=Bold", halign="center", valign="center");
        translate([0, altezza_stand - 45])
            text(nome_laureato, size=5.6, font="Liberation Sans:style=Bold", halign="center", valign="center");
        translate([0, altezza_stand - 54])
            text(corso_o_data, size=3.6, font="Liberation Sans", halign="center", valign="center");
        translate([0, y_ripiano + altezza_labbro + 7])
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
