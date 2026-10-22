// =============================================================================
// PROGETTO: PRESSORE A BASSO PROFILO CON CANALE GUIDA PER BLOCCO A C
// CALIBRATO AL DECIMO DI MILLIMETRO SULLE MISURE REALI FORNITE:
// - Linguetta a C: larghezza max 9.0mm, apertura 4.0mm, spessore 0.8mm
// - Vite: scavo ("fosso") 4.5mm, testa ~6.0-6.2mm, filetto M8
// =============================================================================

$fn = 120;

/* [Dimensioni Piattello] */
// Diametro d'appoggio sulla scrivania
diametro_piattello = 32.0;

// Spessore totale piattello (2.4mm: garantisce passaggio su scrivania da 51mm in cast da 54mm)
spessore_totale = 2.4;

// Smusso perimetrale superiore anti-graffio
raggio_smusso = 0.6;

/* [Passaggio Perno Vite] */
// Diametro foro passante: 6.6mm (permette alla testa da ~6.0-6.2mm di passare libera, 
// lasciando 1.2mm di solido dente di battuta per la clip da 9.0mm)
diametro_foro_passante = 6.6;

// Spessore della base d'appoggio per la clip (battuta)
spessore_battuta = 1.3;

/* [Tasca e Canale per la Linguetta a C] */
// Diametro tasca centrale: 11.2mm (la clip da 9mm ha spazio per allargarsi durante lo scatto)
diametro_tasca_clip = 11.2;

// Larghezza del canale di scorrimento laterale: 9.8mm (la clip da 9.0mm scivola senza attrito)
larghezza_canale_clip = 9.8;

// Profondita della tasca/canale: 1.1mm (la clip da 0.8mm resta incassata di 0.3mm sotto il piano)
profondita_tasca = spessore_totale - spessore_battuta; // 1.1mm


module pressore_calibrato() {
    difference() {
        // 1. Corpo esterno del piattello
        union() {
            // Smusso a contatto con il legno
            cylinder(h = raggio_smusso, d1 = diametro_piattello - 2 * raggio_smusso, d2 = diametro_piattello);
            
            // Corpo cilindrico
            translate([0, 0, raggio_smusso])
                cylinder(h = spessore_totale - raggio_smusso, d = diametro_piattello);
        }
        
        // 2. Foro passante per la vite (da Z=0 a salire fino alla tasca)
        translate([0, 0, -0.1])
            cylinder(h = spessore_battuta + 0.2, d = diametro_foro_passante);
            
        // 3. Tasca centrale per alloggiare la clip
        translate([0, 0, spessore_battuta])
            cylinder(h = profondita_tasca + 0.5, d = diametro_tasca_clip);
            
        // 4. Canale di scorrimento laterale dal bordo fino al centro
        translate([0, diametro_piattello / 4, spessore_battuta + (profondita_tasca + 0.5) / 2])
            cube([larghezza_canale_clip, diametro_piattello / 2 + 1, profondita_tasca + 0.5], center = true);
            
        // 5. Invito svasato per agevolare l'ingresso della vite dal basso
        translate([0, 0, -0.1])
            cylinder(h = 0.4, d1 = diametro_foro_passante + 1.0, d2 = diametro_foro_passante);
            
        // 6. Invito d'ingresso per la clip sul bordo esterno
        translate([0, diametro_piattello / 2 - 1.5, spessore_battuta + (profondita_tasca + 0.5) / 2])
            cylinder(h = profondita_tasca + 0.5, d = larghezza_canale_clip + 2.0, center = true);
    }
}

// Visualizzazione orientata per la stampa (senza supporti)
pressore_calibrato();
