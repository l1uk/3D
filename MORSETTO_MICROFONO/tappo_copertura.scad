// =============================================================================
// PROGETTO: TAPPO / SLITTA DI COPERTURA TESTA VITE
// Si inserisce a scorrimento nel canale dopo aver messo la clip a C.
// Copre completamente la testa della vite e la clip, proteggendo il tavolo al 100%.
// =============================================================================

$fn = 100;

// Larghezza della slitta (leggermente inferiore ai 9.8mm del canale per scorrere liscia)
larghezza_slitta = 9.5;

// Diametro della testa tonda della slitta (leggermente inferiore agli 11.2mm della tasca)
diametro_testa = 10.8;

// Lunghezza totale della slitta
lunghezza_slitta = 16.0;

// Spessore del coperchietto (0.6mm = 3 layer da 0.2mm, flessibile, resistente e sottilissimo)
spessore_coperchio = 0.6;

module tappo_slitta() {
    union() {
        // Testa rotonda che copre la tasca centrale e la testa della vite
        cylinder(h = spessore_coperchio, d = diametro_testa);
        
        // Coda rettangolare che riempie il canale d'ingresso
        translate([-larghezza_slitta / 2, 0, 0])
            cube([larghezza_slitta, lunghezza_slitta, spessore_coperchio]);
    }
}

tappo_slitta();
