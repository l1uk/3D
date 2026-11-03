// =====================================================================
// 02 - CALIBRO DI TOLLERANZE (gioco perno/foro)
// =====================================================================
// Piastra con 10 fori per un perno da 6.00 mm.
// Il numero inciso e' il GIOCO DIAMETRALE in mm:
//     diametro foro = diametro perno + gioco
// (stessa convenzione dei tuoi .scad, es. "11.0 + 0.5 tolleranza")
//
// Stampa piastra e perno insieme, in piano, con le impostazioni
// che userai per i pezzi veri (stesse pareti, velocita', flusso).
//
// Lettura:
//  - primo foro dove il perno ENTRA con forza    -> accoppiamento a pressione
//  - primo foro dove il perno SCORRE senza gioco -> accoppiamento scorrevole
//  - primo foro dove il perno GIRA libero        -> accoppiamento rotante
// Usa quei valori come tolleranze nei tuoi progetti.
// =====================================================================

/* [Selezione] */
parte = "tutto"; // [tutto, piastra, perno]

/* [Perno] */
d_perno     = 6.0;  // [3:0.5:12]
h_perno     = 10;   // [6:1:20]

/* [Piastra] */
spessore    = 5;    // [3:0.5:10]
// Smusso ai bordi dei fori (elimina l'effetto del piede d'elefante)
smusso      = 0.4;  // [0:0.1:1]

/* [Hidden] */
$fn = 96;
giochi    = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50];
etichette = [".05", ".10", ".15", ".20", ".25", ".30", ".35", ".40", ".45", ".50"];
colonne   = 5;
cella_x   = d_perno + 6.5;
cella_y   = d_perno + 10;
bordo     = 3;
font      = "Liberation Sans:style=Bold";
incisione = 0.6;

larghezza = colonne * cella_x + 2*bordo;
profondita = ceil(len(giochi)/colonne) * cella_y + 2*bordo;

module foro(d) {
    translate([0,0,-0.01]) cylinder(d = d, h = spessore + 0.02);
    // smussi sopra e sotto
    translate([0,0,-0.01]) cylinder(d1 = d + 2*smusso, d2 = d, h = smusso + 0.01);
    translate([0,0,spessore - smusso]) cylinder(d1 = d, d2 = d + 2*smusso, h = smusso + 0.01);
}

module piastra() {
    difference() {
        cube([larghezza, profondita, spessore]);
        for (i = [0 : len(giochi)-1]) {
            col = i % colonne;
            riga = floor(i / colonne);
            cx = bordo + col*cella_x + cella_x/2;
            // riga 0 in alto (dietro), cosi' si legge da sinistra a destra, dall'alto in basso
            cy = profondita - bordo - riga*cella_y - cella_y/2;
            translate([cx, cy + 2, 0]) foro(d_perno + giochi[i]);
            translate([cx, cy - d_perno/2 - 1.8, spessore - incisione])
                linear_extrude(incisione + 0.01)
                    text(etichette[i], size = 3, font = font, halign = "center", valign = "center");
        }
    }
}

module perno() {
    base = d_perno + 8;
    difference() {
        translate([-base/2, -base/2, 0]) cube([base, base, 3]);
        translate([0, -base/2 + 2, 3 - incisione])
            linear_extrude(incisione + 0.01)
                text(str(d_perno), size = 2.5, font = font, halign = "center", valign = "center");
    }
    translate([0,0,3]) {
        cylinder(d = d_perno, h = h_perno - 0.5);
        translate([0,0,h_perno - 0.5]) cylinder(d1 = d_perno, d2 = d_perno - 1, h = 0.5);
    }
}

if (parte == "tutto" || parte == "piastra") piastra();
if (parte == "tutto" || parte == "perno")
    translate([larghezza + (d_perno + 8)/2 + 5, profondita/2, 0]) perno();
