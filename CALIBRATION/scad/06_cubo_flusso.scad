// =====================================================================
// 06 - CUBO PER IL FLUSSO (Flow)
// =====================================================================
// Da fare DOPO e-steps e temperatura.
//
// In Cura, solo per questa stampa:
//  - Wall Line Count = 2, Line Width = 0.42 (o quella che usi)
//  - Top Layers = 0, Infill = 0%, Bottom Layers = 3
//  - Ironing off, velocita' parete esterna = interna
//
// Misura lo spessore delle pareti col calibro in 8 punti (2 per lato,
// a meta' altezza, non sugli spigoli) e fai la media:
//     atteso = 2 * line_width             (0.84 con 0.42)
//     nuovo Flow % = Flow attuale * atteso / misurato
// Esempio: 100% * 0.84 / 0.87 = 96.6%  -> Flow 96.5 %
//
// Verifica visiva: stampa poi un cubo 20 mm pieno e guarda il top:
// deve essere chiuso, senza solchi (sotto) ne' creste (sopra).
// =====================================================================

lato    = 20;  // [15:1:40]
altezza = 15;  // [10:1:30]

cube([lato, lato, altezza]);
