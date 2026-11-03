// =====================================================================
// 07 - TEST SBALZI E PONTI (raffreddamento)
// =====================================================================
// Davanti: sbalzi a 30, 40, 50, 60, 70 gradi dalla verticale.
// Dietro:  ponti con luce 10, 20, 30, 40 mm.
// Stampa SENZA supporti.
//
// Lettura:
//  - sbalzi arricciati gia' a 45-50 gradi -> poca ventola o troppo caldo
//  - ponti cadenti -> abbassa temperatura, ventola 100%, in Cura
//    "Bridge Settings": velocita' ponte 25-30 mm/s, flusso ponte 90-95%
// Riferimento PLA ben tarato: sbalzi puliti fino a 55-60 gradi,
// ponti puliti fino a 30-40 mm.
// =====================================================================

/* [Hidden] */
angoli  = [30, 40, 50, 60, 70];
luci    = [10, 20, 30, 40];
h_sb    = 8;    // altezza sbalzi
muro    = 4;    // spessore muro sbalzi
largh   = 10;   // larghezza segmento
pilastro = 5;
h_ponte = 6;
sp_ponte = 1.0;
riga    = 9;    // passo tra le file dei ponti
font    = "Liberation Sans:style=Bold";
incisione = 0.6;
base    = 1.0;

lung_sb = len(angoli) * largh;
lung_pt = max(luci) + 2*pilastro;
lung    = max(lung_sb, lung_pt);

// base unica
translate([0, -len(luci)*riga - 2, 0])
    cube([lung, len(luci)*riga + 2 + muro + h_sb*tan(max(angoli)) + 1, base]);

// --- SBALZI (sporgono verso +Y, cioe' verso il fronte del piatto) ---
translate([0, 0, base])
for (i = [0 : len(angoli)-1]) {
    a = angoli[i];
    translate([i*largh, 0, 0])
    difference() {
        // profilo in YZ estruso lungo X
        rotate([90,0,90]) linear_extrude(largh)
            polygon([[0,0], [muro,0], [muro + h_sb*tan(a), h_sb], [0, h_sb]]);
        // angolo inciso sul retro (faccia y=0)
        translate([largh/2, incisione, h_sb/2]) rotate([90,0,0])
            linear_extrude(incisione + 0.01)
                text(str(a), size = 3.5, font = font, halign = "center", valign = "center");
    }
}

// --- PONTI (dietro) ---
translate([0, 0, base])
for (j = [0 : len(luci)-1]) {
    L = luci[j];
    y = -(j+1)*riga;
    translate([0, y, 0]) {
        cube([pilastro, pilastro, h_ponte]);
        translate([pilastro + L, 0, 0]) cube([pilastro, pilastro, h_ponte]);
        translate([pilastro, 0, h_ponte - sp_ponte]) cube([L, pilastro, sp_ponte]);
        // luce incisa sul pilastro sinistro, in alto
        translate([pilastro/2, pilastro/2, h_ponte - incisione])
            linear_extrude(incisione + 0.01)
                text(str(L), size = 2.6, font = font, halign = "center", valign = "center");
    }
}
