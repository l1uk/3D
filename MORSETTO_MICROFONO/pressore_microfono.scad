// =============================================================================
// PROGETTO: PRESSORE A BASSO PROFILO CON SERRAGGIO TRAMITE BLOCCO A C ORIGINALE
// - Il foro e' largo (5.2mm): la vite entra libera e senza forzature (NO lock-in)
// - Si blocca/serra con il blocco a C originale (la E-clip in metallo)
// - La clip alloggia in una tasca centrale a scomparsa (non tocca la scrivania)
// - Spessore totale 2.4mm: perfetto per far entrare la scrivania da 51mm
// =============================================================================

$fn = 120;

/* [Dimensioni Piattello] */
// Diametro del piattello di appoggio sulla scrivania
diametro_piattello = 32.0;

// Spessore totale del piattello
spessore_totale = 2.4;

// Smusso perimetrale esterno per non graffiare la scrivania
raggio_smusso = 0.6;

/* [Passaggio Perno Vite] */
// Diametro foro centrale (vite ~4.5mm -> foro 5.2mm per ingresso immediato e liscio)
diametro_foro_passante = 5.2;

// Spessore del collarino interno su cui appoggia la clip
spessore_battuta = 1.2;

/* [Tasca Incassata per Blocco a C (E-Clip)] */
// Diametro della tasca superiore che accoglie la clip a C (clip ~8.5mm -> tasca 10.5mm)
diametro_tasca_clip = 10.5;

// Profondita della tasca (clip spessa 0.8mm -> profondita 1.2mm, cosi la clip resta incassata sotto il piano)
profondita_tasca_clip = spessore_totale - spessore_battuta; // 1.2mm


module pressore_con_blocco_c() {
    difference() {
        // 1. Corpo principale del piattello
        union() {
            // Cilindro base
            cylinder(h = spessore_totale - raggio_smusso, d = diametro_piattello);
            
            // Smusso superiore verso la scrivania
            translate([0, 0, spessore_totale - raggio_smusso])
                cylinder(h = raggio_smusso, d1 = diametro_piattello, d2 = diametro_piattello - 2 * raggio_smusso);
        }
        
        // 2. Foro passante largo per la punta della vite (da Z=0 a salire)
        translate([0, 0, -0.1])
            cylinder(h = spessore_battuta + 0.2, d = diametro_foro_passante);
            
        // 3. Tasca centrale superiore incassata per il blocco a C (E-clip)
        // La clip entra qui dentro, si innesta nella scanalatura della vite e blocca il piattello
        translate([0, 0, spessore_battuta])
            cylinder(h = profondita_tasca_clip + 0.5, d = diametro_tasca_clip);
            
        // Smusso d'invito all'ingresso inferiore della vite
        translate([0, 0, -0.1])
            cylinder(h = 0.5, d1 = diametro_foro_passante + 1.0, d2 = diametro_foro_passante);
    }
}

// Visualizzazione orientata per la stampa:
// - Piatto a Z=0
// - La tasca per la clip e' in alto, stampa pulitissima senza supporti!
pressore_con_blocco_c();
