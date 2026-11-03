// =====================================================================
// 04 - TORRE DI TEMPERATURA
// =====================================================================
// Ogni blocco ha: colonna con la temperatura incisa, ponte da 10 mm,
// sbalzo a 45 gradi, spazio tra colonne per vedere i fili (stringing).
// Il blocco piu' in basso e' il piu' caldo.
//
// La temperatura NON cambia da sola: in Cura aggiungi lo script
// "Torre Calibrazione" (vedi tools/TorreCalibrazione.py e README) con:
//     Modalita'       = Temperatura
//     Valore iniziale = t_inizio
//     Passo           = -t_passo
//     Altezza inizio  = h_base
//     Altezza blocco  = h_blocco
//
// Scegli il blocco con il miglior compromesso tra superficie lucida e
// liscia, ponte teso, sbalzo pulito e pochi fili. Con Bambu PLA Basic
// su Ender 3 V2 di solito si finisce tra 200 e 215 gradi.
// =====================================================================

/* [Temperature] */
t_inizio = 230; // [180:5:260]
t_fine   = 190; // [170:5:250]
t_passo  = 5;   // [1:1:10]

/* [Geometria] */
h_blocco = 8;   // [5:1:15]
h_base   = 1.0; // [0.6:0.2:2]

/* [Hidden] */
n        = floor((t_inizio - t_fine) / t_passo) + 1;
prof     = 10;
col_sx   = 10;
luce     = 10;   // luce del ponte
col_dx   = 8;
sbalzo   = 5;    // sporgenza a 45 gradi
sp_ponte = 1.0;
font     = "Liberation Sans:style=Bold";
incisione = 0.6;

larg = col_sx + luce + col_dx;

module blocco(t) {
    H = h_blocco;
    difference() {
        union() {
            cube([col_sx, prof, H]);
            translate([col_sx + luce, 0, 0]) cube([col_dx, prof, H]);
            // ponte
            translate([col_sx, 0, H - sp_ponte]) cube([luce, prof, sp_ponte]);
            // sbalzo a 45 gradi sul lato destro
            translate([0, prof, 0]) rotate([90,0,0])
                linear_extrude(prof)
                    polygon([[larg, H - sbalzo], [larg, H], [larg + sbalzo, H]]);
        }
        // temperatura incisa sul fronte della colonna sinistra
        translate([col_sx/2, incisione, H/2 - 0.5]) rotate([90,0,0])
            linear_extrude(incisione + 0.01)
                text(str(t), size = 4, font = font, halign = "center", valign = "center");
    }
}

// base
translate([-2, -2, 0]) cube([larg + sbalzo + 4, prof + 4, h_base]);

for (i = [0 : n-1])
    translate([0, 0, h_base + i*h_blocco]) blocco(t_inizio - i*t_passo);

echo(str("TORRE TEMPERATURA: ", n, " blocchi, altezza totale ", h_base + n*h_blocco, " mm"));
echo(str("Cura script: inizio=", t_inizio, " passo=", -t_passo, " altezza inizio=", h_base, " altezza blocco=", h_blocco));
