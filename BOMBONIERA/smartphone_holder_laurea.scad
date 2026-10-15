// =====================================================================
// SMARTPHONE HOLDER BOMBONIERA DI LAUREA - 2 PEZZI AD INCASTRO
// Ottimizzato per Creality Ender 3 V2 - Stampa Piatta ZERO Supporti
// =====================================================================

/* [Personalizzazione Testo (Audience Generalista)] */
titolo_superiore = "LUCA 2026";
nome_laureato    = "BRUXELLES";
corso_o_data = "";
frase_ricordo    = "Gianotti Family";

/* [Icona e Decorazione] */
mostra_tocco_laurea = true;
mostra_cornice_tech = true; // Elegante cornice geometrica ai bordi

/* [Dimensioni Generali (mm)] */
larghezza_stand  = 72.0; // Larghezza schienale (ottima stabilità per tutti gli smartphone)
altezza_stand    = 125.0; // Altezza schienale
spessore_piastra = 3.6;  // Spessore solido e anti-flessione (18 layer da 0.2mm)
profondita_culla = 14.5; // Spazio utile per il telefono (compatibile con cover)
altezza_becco    = 14.0; // Altezza del gancio frontale ferma-telefono
luce_cavo_usb    = 24.0; // Larghezza intaglio centrale per cavetto di ricarica

/* [Tolleranze Incastro Ender 3 V2] */
clearance        = 0.40; // Gioco meccanico (0.35-0.45mm ideale per scorrimento senza gioco)
profondita_testo = 0.80; // Profondità incisione testo (4 layer da 0.2mm, ottima visibilità)

/* [Modalità di Visualizzazione] */
modalita = "stampa"; // ["stampa", "assemblato", "solo_schienale", "solo_piede"]

$fn = 60;

// =====================================================================
// CALCOLI E PARAMETRI INTERNI
// =====================================================================
h_fessura = spessore_piastra + clearance;
w_fessura = 42.0;
quota_z_fessura = 36.0; // Posizione della fessura sullo schienale

w_piede_base = 64.0;
lunghezza_corpo_piede = 56.0;
lunghezza_linguetta = 20.0;
w_linguetta = w_fessura - clearance*2; // 41.2 mm

// =====================================================================
// SELETTORE VISTA PRINCIPALE
// =====================================================================
if (modalita == "stampa") {
    // Entrambi i pezzi affiancati piatti sul piatto di stampa (Ender 3 V2: 220x220mm)
    translate([-larghezza_stand/2 - 6, 0, 0])
        schienale();
        
    translate([w_piede_base/2 + 6, 0, 0])
        piede();
}
else if (modalita == "assemblato") {
    // Vista assemblata in posizione d'uso a ~68° di inclinazione
    angolo_schienale = 68;
    
    // Posiziona schienale
    rotate([90 - angolo_schienale, 0, 0])
        schienale();
        
    // Posiziona il piede ad incastro perfetto
    translate([0, quota_z_fessura * cos(angolo_schienale), quota_z_fessura * sin(angolo_schienale)])
        rotate([-32, 0, 0])
        translate([0, -lunghezza_corpo_piede, -spessore_piastra/2])
        piede();
}
else if (modalita == "solo_schienale") {
    schienale();
}
else if (modalita == "solo_piede") {
    piede();
}

// =====================================================================
// MODULO 1: SCHIENALE PRINCIPALE (Con ganci per telefono e incisioni)
// =====================================================================
module schienale() {
    difference() {
        union() {
            // Piastra base con angoli superiori arrotondati
            hull() {
                translate([-larghezza_stand/2 + 6, 6, 0])
                    cylinder(r=6, h=spessore_piastra);
                translate([larghezza_stand/2 - 6, 6, 0])
                    cylinder(r=6, h=spessore_piastra);
                translate([-larghezza_stand/2 + 8, altezza_stand - 8, 0])
                    cylinder(r=8, h=spessore_piastra);
                translate([larghezza_stand/2 - 8, altezza_stand - 8, 0])
                    cylinder(r=8, h=spessore_piastra);
            }
            
            // Ganci frontali reggi-telefono (stampati in verticale in Z, zero supporti!)
            ganci_frontali();
        }
        
        // Fessura rettangolare per incastro del piede
        translate([-w_fessura/2, quota_z_fessura - h_fessura/2, -1])
            cube([w_fessura, h_fessura, spessore_piastra + 2]);
            
        // Finestra intaglio centrale per passaggio cavetto di ricarica
        translate([-luce_cavo_usb/2, -1, -1])
            cube([luce_cavo_usb, 26, spessore_piastra + 2]);
            
        // Incisioni grafiche e testi
        translate([0, 0, spessore_piastra - profondita_testo])
            incisioni_schienale();
    }
}

// Ganci laterali simmetrici che tengono lo smartphone in posizione
module ganci_frontali() {
    w_gancio = (larghezza_stand - luce_cavo_usb) / 2;
    
    // Modulo singolo gancio (lato destro: da X = luce_cavo_usb/2 a larghezza_stand/2)
    module un_gancio() {
        translate([luce_cavo_usb/2, 0, 0])
        rotate([0, -90, 0])
        translate([-altezza_becco, 0, -w_gancio])
        linear_extrude(w_gancio)
        polygon([
            [0, 0],
            [altezza_becco, 0],
            [altezza_becco, 4.0],
            [5.0, 4.0],
            [5.0, profondita_culla + 4.0],
            [altezza_becco, profondita_culla + 4.0],
            [altezza_becco, profondita_culla + 7.5],
            [2.0, profondita_culla + 7.5],
            [0, 10.0]
        ]);
    }
    
    // Gancio destro
    un_gancio();
    
    // Gancio sinistro: simmetria perfetta rispetto all'asse X
    mirror([1, 0, 0])
        un_gancio();
}

// Decorazioni e testi incisi sulla superficie superiore
module incisioni_schienale() {
    linear_extrude(profondita_testo + 0.2) {
        
        // Icona Tocco di Laurea stilizzato
        if (mostra_tocco_laurea) {
            translate([0, altezza_stand - 20]) {
                // Cappello quadrato a losanga
                rotate([0, 0, 45])
                    square([15, 15], center=true);
                // Calotta inferiore
                translate([0, -5.5])
                    scale([1.3, 0.7])
                    circle(r=5);
                // Bottone centrale
                circle(r=1.3);
                // Nappina laterale
                polygon([
                    [0, 0],
                    [6, -3],
                    [8, -10],
                    [6.5, -10],
                    [4.5, -3]
                ]);
            }
        }
        
        // Cornice elegante perimetrale (discreta e moderna)
        if (mostra_cornice_tech) {
            difference() {
                hull() {
                    translate([-larghezza_stand/2 + 5, 8]) circle(r=3);
                    translate([larghezza_stand/2 - 5, 8]) circle(r=3);
                    translate([-larghezza_stand/2 + 6, altezza_stand - 6]) circle(r=4);
                    translate([larghezza_stand/2 - 6, altezza_stand - 6]) circle(r=4);
                }
                hull() {
                    translate([-larghezza_stand/2 + 6.2, 9.2]) circle(r=2.5);
                    translate([larghezza_stand/2 - 6.2, 9.2]) circle(r=2.5);
                    translate([-larghezza_stand/2 + 7.2, altezza_stand - 7.2]) circle(r=3.5);
                    translate([larghezza_stand/2 - 7.2, altezza_stand - 7.2]) circle(r=3.5);
                }
                // Tagli geometrici decorativi agli angoli
                translate([-larghezza_stand/2 + 5, altezza_stand - 18]) square([3, 10], center=true);
                translate([larghezza_stand/2 - 5, altezza_stand - 18]) square([3, 10], center=true);
            }
        }
        
        // Riga 1: Titolo Laurea
        translate([0, altezza_stand - 35])
            text(titolo_superiore, size=4.4, font="Liberation Sans:style=Bold", halign="center", valign="center");
            
        // Riga 2: Nome e Cognome del Festeggiato
        translate([0, altezza_stand - 45])
            text(nome_laureato, size=5.6, font="Liberation Sans:style=Bold", halign="center", valign="center");
            
        // Riga 3: Corso / Anno
        translate([0, altezza_stand - 54])
            text(corso_o_data, size=3.6, font="Liberation Sans", halign="center", valign="center");
            
        // Riga 4: Frase ricordo / ringraziamento (sopra la fessura)
        translate([0, quota_z_fessura + 12])
            text(frase_ricordo, size=3.2, font="Liberation Sans:style=Italic", halign="center", valign="center");
    }
}

// =====================================================================
// MODULO 2: PIEDE POSTERIORE (Cavalletto di supporto antiribaltamento)
// UNICO PEZZO SOLIDO E CONTINUO
// =====================================================================
module piede() {
    difference() {
        linear_extrude(spessore_piastra) {
            union() {
                // 1. Corpo largo del cavalletto (appoggio stabile sul tavolo)
                hull() {
                    translate([-w_piede_base/2 + 6, 6])
                        circle(r=6);
                    translate([w_piede_base/2 - 6, 6])
                        circle(r=6);
                    translate([-w_piede_base/2 + 4, lunghezza_corpo_piede - 4])
                        circle(r=4);
                    translate([w_piede_base/2 - 4, lunghezza_corpo_piede - 4])
                        circle(r=4);
                }
                
                // 2. Linguetta di inserimento frontale (continua e solida)
                // Forma due spalle di arresto a quota Y = lunghezza_corpo_piede
                hull() {
                    translate([-w_linguetta/2 + 3, lunghezza_corpo_piede])
                        circle(r=3);
                    translate([w_linguetta/2 - 3, lunghezza_corpo_piede])
                        circle(r=3);
                    translate([-w_linguetta/2 + 3, lunghezza_corpo_piede + lunghezza_linguetta - 3])
                        circle(r=3);
                    translate([w_linguetta/2 - 3, lunghezza_corpo_piede + lunghezza_linguetta - 3])
                        circle(r=3);
                }
            }
        }
        
        // Smusso di invito a 45 gradi sulla punta della linguetta per facilitare l'inserimento
        translate([-w_linguetta/2 - 1, lunghezza_corpo_piede + lunghezza_linguetta - 1.5, spessore_piastra - 1.5])
            rotate([45, 0, 0])
            cube([w_linguetta + 2, 6, 6]);
            
        // Intaglio estetico centrale sul corpo (riduce materiale e tempi senza perdere forza)
        translate([0, 24, -1])
            linear_extrude(spessore_piastra + 2)
            hull() {
                translate([0, 0]) circle(r=10);
                translate([0, 16]) circle(r=6);
            }
    }
}
