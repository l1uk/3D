// =============================================================================
// PROGETTO: MORSETTO A C COMPLETO PER BRACCIO MICROFONO (ALTERNATIVE COMPLETA)
// Progettato per essere stampato sdraiato sul fianco (massima resistenza meccanica)
// =============================================================================

$fn = 80;

/* [Dimensioni Generali Morsetto] */
// Apertura della bocca (spazio utile per la scrivania)
apertura_scrivania = 62.0; // Adatto per tavoli fino a 58-60mm

// Profondita utile della gola del morsetto
profondita_gola = 45.0;

// Spessore delle pareti portanti a C (minimo 12-14mm per reggere la flessione)
spessore_struttura = 15.0;

// Larghezza complessiva del morsetto (estrusione)
larghezza_morsetto = 40.0;

// Raggio di raccordo interno agli angoli (fondamentale contro le rotture)
raggio_raccordo_interno = 8.0;

/* [Alloggiamento Perno Braccio Microfonico] */
// Diametro perno braccio (standard 12.0mm + tolleranza)
diametro_perno_braccio = 12.4;
profondita_foro_braccio = 38.0;

/* [Filettatura / Dado M8 per la Vite] */
// Diametro foro per barra filettata M8
diametro_foro_vite = 8.5;
// Sede esagonale per dado standard M8 (chiave 13mm -> diametro circoscritto ~14.8mm)
diametro_dado_m8 = 15.0;
spessore_dado_m8 = 7.0;

module morsetto_2d() {
    difference() {
        // Profilo esterno
        offset(r = 3) offset(r = -3)
        square([profondita_gola + spessore_struttura + 25, apertura_scrivania + 2 * spessore_struttura]);
        
        // Vano gola interna
        translate([spessore_struttura, spessore_struttura])
            square([profondita_gola + 30, apertura_scrivania]);
    }
}

module morsetto_3d() {
    difference() {
        union() {
            // Estrusione del profilo
            linear_extrude(height = larghezza_morsetto)
                morsetto_2d();
                
            // Raccordo interno d'angolo inferiore
            translate([spessore_struttura, spessore_struttura, 0])
                cylinder(r = raggio_raccordo_interno, h = larghezza_morsetto);
                
            // Raccordo interno d'angolo superiore
            translate([spessore_struttura, spessore_struttura + apertura_scrivania, 0])
                cylinder(r = raggio_raccordo_interno, h = larghezza_morsetto);
        }
        
        // Foro verticale per il perno del braccio microfonico (sul blocco posteriore/superiore)
        translate([spessore_struttura / 2 + 3, spessore_struttura + apertura_scrivania + spessore_struttura - profondita_foro_braccio, larghezza_morsetto / 2])
            rotate([-90, 0, 0])
                cylinder(d = diametro_perno_braccio, h = profondita_foro_braccio + 10);
                
        // Foro passante per la vite M8 di serraggio (sul braccio inferiore)
        translate([spessore_struttura + 22, -5, larghezza_morsetto / 2])
            rotate([-90, 0, 0])
                cylinder(d = diametro_foro_vite, h = spessore_struttura + 10);
                
        // Tasca esagonale per incassare un dado M8 sotto la base
        translate([spessore_struttura + 22, spessore_struttura - spessore_dado_m8, larghezza_morsetto / 2])
            rotate([-90, 0, 0])
                cylinder(d = diametro_dado_m8, h = spessore_dado_m8 + 0.1, $fn = 6);
    }
}

// Visualizzazione per stampa: sdraiato sul fianco per orientare i layer parallelamente al carico
morsetto_3d();
