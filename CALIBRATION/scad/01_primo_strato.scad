// =====================================================================
// 01 - TEST PRIMO STRATO (Ender 3 V2, piatto 220x220)
// =====================================================================
// 5 quadrati da UN SOLO layer: centro + 4 angoli.
// Serve per regolare livellamento e Z-offset (babystep) mentre stampa.
//
// In Cura:
//  - Altezza primo strato = 'spessore' qui sotto (default 0.2)
//  - Adesione: Skirt (NON brim), Top/Bottom pattern: Lines
//  - NON spostare il modello: deve restare centrato sul piatto
//
// Lettura:
//  - linee separate / tonde / si staccano  -> ugello troppo ALTO
//  - superficie trasparente, creste, raschia -> ugello troppo BASSO
//  - giusto: linee schiacciate, unite, superficie liscia e opaca
// =====================================================================

/* [Piatto] */
lato_piatto = 220;   // [200:1:235]
// Distanza del bordo dei pad dal bordo piatto (evita le clip del vetro)
margine     = 25;    // [10:1:40]

/* [Pad] */
lato_pad    = 30;    // [15:1:40]
// = altezza primo strato in Cura
spessore    = 0.2;   // [0.12:0.04:0.32]

offset_c = lato_piatto/2 - margine - lato_pad/2;

posizioni = [
    [0, 0],
    [-offset_c, -offset_c], [ offset_c, -offset_c],
    [-offset_c,  offset_c], [ offset_c,  offset_c]
];

for (p = posizioni)
    translate([p[0] - lato_pad/2, p[1] - lato_pad/2, 0])
        cube([lato_pad, lato_pad, spessore]);
