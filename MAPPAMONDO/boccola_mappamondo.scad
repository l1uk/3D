// =====================================================================
// BOCCOLA DI SUPPORTO PER MAPPAMONDO (Polo Superiore con Scanalatura)
// =====================================================================
// Misure verificate dai rilievi:
// - Altezza totale al centro: 13.5 mm
// - Spessore totale ai bordi della flangia: 11.0 mm (bombatura = 2.5 mm)
// - Diametro flangia esterna: 37.5 mm
// - Diametro collare interno: 32.0 mm (foro globo 32.5 mm)
// - Altezza collare: 10.0 mm
// - Perno a croce: 11.0 mm + 0.5 mm tolleranza di rotazione = 11.5 mm
// - Gradino / scanalatura di centraggio sul bordo del collare
// =====================================================================

/* [Dettagli Rendering] */
$fn = 120; // Risoluzione curve

/* [Dimensioni Principali] */
// Diametro esterno della flangia di battuta
diametro_flangia = 37.5; // [35.0:0.5:42.0]

// Altezza complessiva misurata al vertice centrale della cupola
altezza_totale = 13.5;   // [12.0:0.1:16.0]

// Altezza complessiva misurata al bordo esterno della flangia
spessore_bordo = 11.0;   // [9.0:0.1:13.0]

// Diametro esterno del collare principale (foro mappamondo = 32.5 mm)
diametro_collare = 32.0; // [30.0:0.1:32.5]

// Lunghezza del collare che entra nel globo
altezza_collare = 10.0;  // [8.0:0.5:12.0]

/* [Scanalatura / Gradino Superiore del Collare] */
// Diametro esterno del gradino ribassato in cima al collare
diametro_gradino = 30.4;  // [28.0:0.2:32.0]

// Altezza/profondità dello scalino di centraggio
altezza_gradino = 1.6;    // [0.5:0.1:3.0]

// Smusso invito in punta per facilitare l'innesto nel mappamondo
smusso_punta = 0.8;       // [0.0:0.2:1.5]

/* [Sede Centrale per Perno a Croce] */
// Diametro del perno misurato sul supporto
diametro_perno = 11.0;    // [9.0:0.1:13.0]

// Gioco di rotazione libera per il perno (consigliato 0.4 - 0.6 mm)
gioco_rotazione = 0.5;    // [0.2:0.05:1.0]

// Svasatura sulla cupola per inserire facilmente il perno
svasatura_imbocco = 1.0;  // [0.0:0.2:2.0]

/* [Dettagli Stampa 3D] */
// Raccordo a 45° sotto la flangia (permette di stampare a sbalzo senza supporti)
raccordo_sotto_flangia = 1.5; // [0.0:0.5:2.5]

// =====================================================================
// CALCOLO GEOMETRIA SFERICA
// =====================================================================
// Bombatura (freccia dell'arco sferico) = 13.5 - 11.0 = 2.5 mm
bombatura = altezza_totale - spessore_bordo;
raggio_flangia = diametro_flangia / 2;

// Raggio della sfera: R = (r^2 + h^2) / (2*h)
raggio_sfera = (pow(raggio_flangia, 2) + pow(bombatura, 2)) / (2 * bombatura);
z_centro_sfera = altezza_totale - raggio_sfera;

// Diametro effettivo del foro perno
diametro_foro = diametro_perno + gioco_rotazione;

echo(str("========================================"));
echo(str("Raggio sfera cupola: ", raggio_sfera, " mm (bombatura: ", bombatura, " mm)"));
echo(str("Gradino collare: Ø ", diametro_gradino, " mm x altezza ", altezza_gradino, " mm"));
echo(str("Foro centrale perno: Ø ", diametro_foro, " mm"));
echo(str("========================================"));

// =====================================================================
// MODULO MODELLAZIONE
// =====================================================================
module boccola_con_scanalatura() {
    difference() {
        union() {
            // --- 1. COLLARE CHE ENTRA NEL GLOBO ---
            // A) Sezione a gradino / scanalata in punta (Z da 0 ad altezza_gradino)
            if (smusso_punta > 0) {
                // Invito iniziale smussato
                cylinder(h = smusso_punta, 
                         d1 = diametro_gradino - (smusso_punta * 2), 
                         d2 = diametro_gradino);
                // Corpo del gradino
                translate([0, 0, smusso_punta])
                    cylinder(h = altezza_gradino - smusso_punta, d = diametro_gradino);
            } else {
                cylinder(h = altezza_gradino, d = diametro_gradino);
            }

            // B) Corpo principale del collare (diametro 32.0 mm)
            translate([0, 0, altezza_gradino])
                cylinder(h = altezza_collare - altezza_gradino, d = diametro_collare);

            // C) Raccordo a 45° sotto la flangia (per stampa a sbalzo senza supporti)
            if (raccordo_sotto_flangia > 0) {
                translate([0, 0, altezza_collare - raccordo_sotto_flangia])
                    cylinder(h = raccordo_sotto_flangia, 
                             d1 = diametro_collare, 
                             d2 = min(diametro_flangia, diametro_collare + raccordo_sotto_flangia * 2));
            }

            // --- 2. FLANGIA ESTERNA BOMBATA (SFERICA) ---
            intersection() {
                // Cilindro di contenimento diametro flangia
                translate([0, 0, altezza_collare])
                    cylinder(h = altezza_totale - altezza_collare + 2, d = diametro_flangia);
                
                // Calotta sferica reale
                translate([0, 0, z_centro_sfera])
                    sphere(r = raggio_sfera);
            }
        }

        // --- 3. FORO PASSANTE PER IL PERNO A CROCE (Ø 11.5 mm) ---
        translate([0, 0, -1])
            cylinder(h = altezza_totale + 2, d = diametro_foro);

        // --- 4. SVASATURA D'INGRESSO SULLA CUPOLA ---
        if (svasatura_imbocco > 0) {
            translate([0, 0, altezza_totale - svasatura_imbocco + 0.01])
                cylinder(h = svasatura_imbocco + 0.1, 
                         d1 = diametro_foro, 
                         d2 = diametro_foro + (svasatura_imbocco * 2));
        }
    }
}

// Genera il pezzo
boccola_con_scanalatura();
