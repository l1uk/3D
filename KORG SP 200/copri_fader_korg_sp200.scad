// ============================================================
//  COPRI-FADER PARAMETRICO — KORG SP-200
//  Misure reali prese con calibro dal pezzo originale.
//  Apri con OpenSCAD → F5 anteprima → F6 render → Export STL
// ============================================================

/* ===================== MISURE DA CALIBRO ===================== */

// --- STELO DEL FADER (lamina metallica che sporge dallo slider) ---
stem_thickness    = 1.5;   // spessore della lamina metallica (mm)
stem_width        = 4.0;   // larghezza della lamina metallica (mm)
stem_insert_depth = 5.5;   // profondità di innesto nel tappo (mm)
clearance         = 0.2;   // tolleranza stampa 3D per incastro (mm)

// --- FORMA ESTERNA DEL TAPPO ---
cap_length    = 12.0;  // lunghezza (mm) — direzione di scorrimento del fader
cap_width     = 5.5;   // larghezza (mm) — trasversale allo scorrimento
cap_height    = 6.5;   // altezza totale (mm)
corner_radius = 1.0;   // raggio angoli arrotondati (mm)

// --- INTERNO A CROCE (crea le alette a molla) ---
slit_width = 1.0;      // larghezza dell'intaglio trasversale (mm)
slit_depth = 5.0;      // profondità dell'intaglio dal basso (mm) — più profondo = più elastico
wall_min   = 1.0;      // parete minima tra intaglio e bordo esterno (mm)

// --- SMUSSO ANTI-ZAMPA D'ELEFANTE ---
chamfer = 0.7;         // invito svasato all'imboccatura inferiore (mm)

// --- ERGONOMIA SUPERIORE ---
finger_concavity = 0.4;    // profondità incavo concavo per il dito (mm)
finger_radius    = 25;     // raggio sfera per l'incavo (mm) — più grande = più dolce
indicator_width  = 0.8;    // larghezza tacca indicatrice (mm)
indicator_depth  = 0.5;    // profondità tacca indicatrice (mm)

/* ================================================================
   GEOMETRIA — non serve modificare da qui in giù
   ================================================================ */

$fn = 48;

// Dimensioni calcolate della cavità
sw = stem_thickness + clearance;   // apertura cavità in X (spessore + gioco)
sl = stem_width + clearance;       // apertura cavità in Y (larghezza + gioco)
slit_len = cap_width - 2*wall_min; // lunghezza dell'intaglio trasversale

// Corpo esterno: rettangolo arrotondato centrato in XY, da z=0 a z=h
module rounded_box(w, l, h, r) {
    hull() {
        for (x = [-w/2 + r, w/2 - r])
            for (y = [-l/2 + r, l/2 - r])
                translate([x, y, 0])
                    cylinder(h = h, r = r);
    }
}

// Cavità interna a croce + smusso
module cross_cavity() {
    // ---- Fessura orizzontale (alloggiamento lamina, lungo cap_length/Y) ----
    translate([-sw/2, -sl/2, -0.1])
        cube([sw, sl, stem_insert_depth + 0.1]);

    // ---- Intaglio verticale passante (crea le due alette a molla) ----
    // Corre lungo X (trasversale alla lamina), dividendo il materiale in due dita
    // elastiche che stringono la lamina per attrito.
    translate([-slit_len/2, -slit_width/2, -0.1])
        cube([slit_len, slit_width, slit_depth + 0.1]);

    // ---- Smusso/invito svasato all'imboccatura (anti elephant's foot) ----
    // Piramide tronca: larga in basso (z=0), si restringe alla misura della cavità
    hull() {
        translate([-(sw/2 + chamfer), -(sl/2 + chamfer), -0.1])
            cube([sw + 2*chamfer, sl + 2*chamfer, 0.01]);
        translate([-sw/2, -sl/2, chamfer])
            cube([sw, sl, 0.01]);
    }
}

module fader_cap() {
    difference() {
        // Corpo esterno arrotondato
        rounded_box(cap_width, cap_length, cap_height, corner_radius);

        // Cavità interna a croce con smusso
        cross_cavity();

        // Incavo concavo per il dito (sfera tangente alla sommità)
        translate([0, 0, cap_height + finger_radius - finger_concavity])
            sphere(r = finger_radius);

        // Tacca indicatrice (fessura trasversale sulla faccia superiore)
        translate([-(cap_width/2 + 0.5), -indicator_width/2, cap_height - indicator_depth])
            cube([cap_width + 1, indicator_width, indicator_depth + 0.1]);
    }
}

fader_cap();
