// =====================================================================
// 05 - TORRE DI RETRAZIONE
// =====================================================================
// Due colonne distanti 'distanza' mm: ad ogni layer l'ugello viaggia
// a vuoto tra le due, quindi i fili mostrano quanto bene retrae.
// Ogni blocco e' separato da una tacca e ha il valore inciso.
//
// Due passate consigliate (stesso modello, cambi solo le etichette):
//  1) LUNGHEZZA a velocita' fissa 45 mm/s: valori 2,3,4,5,6,7 (passo 1)
//  2) VELOCITA' alla lunghezza scelta: valori 30,35,40,45,50,55 (passo 5)
//
// In Cura aggiungi lo script "Torre Calibrazione" con:
//     Modalita'       = Retrazione lunghezza  (oppure velocita')
//     Valore iniziale = valore_iniziale
//     Passo           = passo
//     Altezza inizio  = h_base
//     Altezza blocco  = h_blocco
// e in Cura disattiva "Combing" per questa stampa (altrimenti l'ugello
// evita di retrarre).
//
// Scegli il valore PIU' BASSO che non fa fili: piu' retrazione del
// necessario sui Bowden porta a intasamenti e buchi a inizio linea.
// =====================================================================

/* [Valori] */
valore_iniziale = 2;  // [0:0.5:60]
passo           = 1;  // [0.25:0.25:10]
n_blocchi       = 6;  // [3:1:10]
// unita' mostrata sulla base
unita = "mm"; // [mm, mm/s]

/* [Geometria] */
h_blocco = 8;    // [5:1:15]
h_base   = 1.0;  // [0.6:0.2:2]
lato     = 8;    // [5:1:12]
distanza = 40;   // [20:5:80]

/* [Hidden] */
font = "Liberation Sans:style=Bold";
incisione = 0.6;
tacca = 0.6;   // altezza tacca tra i blocchi

module colonna(con_testo) {
    difference() {
        cube([lato, lato, n_blocchi*h_blocco]);
        for (i = [1 : n_blocchi-1])
            // tacca orizzontale su tutti i lati
            translate([0, 0, i*h_blocco - tacca/2])
                difference() {
                    translate([-1, -1, 0]) cube([lato + 2, lato + 2, tacca]);
                    translate([0.5, 0.5, -0.01]) cube([lato - 1, lato - 1, tacca + 0.02]);
                }
        if (con_testo)
            for (i = [0 : n_blocchi-1])
                translate([lato/2, incisione, i*h_blocco + h_blocco/2]) rotate([90,0,0])
                    linear_extrude(incisione + 0.01)
                        text(str(valore_iniziale + i*passo), size = 3.2, font = font,
                             halign = "center", valign = "center");
    }
}

// base che unisce le colonne
translate([-3, -3, 0]) cube([distanza + lato + 6, lato + 6, h_base]);
translate([0, 0, h_base]) colonna(true);
translate([distanza, 0, h_base]) colonna(false);
// unita' sulla base, in mezzo
translate([lato + distanza/2 - lato/2, lato/2, h_base])
    linear_extrude(0.6)
        text(unita, size = 4, font = font, halign = "center", valign = "center");

echo(str("TORRE RETRAZIONE: ", n_blocchi, " blocchi da ", valore_iniziale, " passo ", passo,
         " | altezza inizio=", h_base, " altezza blocco=", h_blocco));
