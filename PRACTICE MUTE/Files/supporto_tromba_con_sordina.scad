// =============================================================================
//  SUPPORTO UNIVERSALE PER TROMBA (con o senza sordina)  -  100% stampabile, 0 supporti
// =============================================================================
//
//  Idea: la sordina ha un fondello piatto (Ø 92 mm): la tromba sta in piedi, CAMPANA IN GIU',
//  appoggiata sul fondello dentro un alloggio. Il pavimento dell'alloggio e' inclinato
//  all'indietro (lean), cosi' la tromba pende leggermente verso un montante posteriore e si
//  appoggia con la campana su una forcella (sella) regolabile in altezza. Lo stelo di uscita
//  della sordina NON viene chiuso (foro di sfogo sotto), la campana e la sordina non sono toccate
//  se non dalla sella.
//
//  USO UNIVERSALE (uso = "sordina" oppure "aperta"):
//    - con sordina: la tromba sta sul fondello nell'alloggio (come descritto sopra)
//    - senza sordina: il bordo della campana (Ø 120-127 mm) appoggia sull'anello piano attorno
//      all'alloggio; il bordo di ritenzione lo tiene in posizione. Il montante e la sella sono
//      gli stessi: cambia solo il foro del perno (il report dice quale).
//    Rifodera l'anello con feltro. Per un'altra tromba rimisura rest_h e rest_d.
//
//  Pezzi da stampare:  "base" (base + alloggio + montante, un solo pezzo),  "clip" (la sella
//  scorrevole),  "pin" (perno: va bene anche un chiodo/vite da 4 mm).
//  Foderare l'alloggio e la sella con feltro o nastro in gomma/espanso (2 mm) per non graffiare.
//
//  DOVE REGOLARE (misura con la tromba in piedi sul fondello):
//    rest_h = quota (mm) sopra il fondello a cui appoggiare la campana (dove e' liscia e tonda)
//    rest_d = diametro ESTERNO della campana a quella quota (mm)
//  Il report in console dice quale foro del montante usare.
// =============================================================================

mode = "assembly";   // ["assembly", "base", "clip", "pin", "ghost", "clip_placed", "pin_placed"]
uso  = "sordina";    // ["sordina", "aperta"]  -> con o senza sordina nella campana

$fn = $preview ? 48 : 96;

// ── Sordina / fondello ──────────────────────────────────────────────────────
flange_od     = 92.0;   // [mm] diametro della piastra del fondello (cap_flange_od della sordina)
mute_rim_z    = 38.0;   // [mm] quota del bordo campana sopra il fondello quando c'e' la sordina

// ── Alloggio inclinato ──────────────────────────────────────────────────────
lean          = 10.0;   // [deg] inclinazione della tromba all'indietro
pocket_clear  = 1.0;    // [mm] gioco radiale del fondello nell'alloggio
pocket_depth  = 7.0;    // [mm] altezza del bordo dell'alloggio
bell_seat_r   = 64.5;   // [mm] raggio interno del bordo di ritenzione (sede del bordo campana senza sordina: Ø 129)
seat_lip_t    = 3.0;    // [mm] spessore del bordo di ritenzione
seat_lip_h    = 5.0;    // [mm] altezza del bordo di ritenzione sopra l'anello
relief_d      = 28.0;   // [mm] foro di sfogo sotto lo stelo (non chiude l'uscita)

// ── Base ────────────────────────────────────────────────────────────────────
base_t        = 8.0;    // [mm]
base_x_front  = 82.0;   // [mm] sporgenza davanti all'asse della tromba
base_x_rear   = 112.0;  // [mm] sporgenza dietro
base_w        = 200.0;  // [mm] larghezza (stabilita' laterale)

// ── Montante (parallelo all'asse della tromba) ──────────────────────────────
post_w        = 22.0;   // [mm] larghezza (laterale)
post_t        = 14.0;   // [mm] spessore (avanti-dietro)
post_x        = 80.0;   // [mm] distanza dell'asse del montante dall'asse della tromba
post_h        = 190.0;  // [mm] altezza lungo il montante
hole_d        = 4.4;    // [mm] fori per il perno
hole_z0       = 40.0;   // [mm] quota del primo foro
hole_pitch    = 10.0;   // [mm]
hole_n        = 14;
pin_d         = 4.0;    // [mm]

// ── Sella (forcella che regge la campana) ───────────────────────────────────
rest_h        = 95.0;   // [mm] quota del contatto sopra il fondello CON la sordina (senza sordina il codice la abbassa da solo)
rest_d        = 42.0;   // [mm] diametro ESTERNO della campana alla quota (rest_h - saddle_h/2), cioe' dove la sella e' piu' larga
saddle_clear  = 2.5;    // [mm] gioco per lato (spazio per il feltro)
saddle_wall   = 3.5;    // [mm]
saddle_h      = 12.0;   // [mm]
clip_wall     = 4.0;    // [mm] pareti del manicotto
clip_h        = 32.0;   // [mm]
sleeve_clear  = 0.35;   // [mm] gioco manicotto/montante
arm_t         = 10.0;   // [mm] spessore del braccio (sta sul piatto: nessun sbalzo)
pin_local_z   = 20.0;   // [mm] quota del foro del perno nella sella (dal fondo della sella)

// ── Valori derivati ─────────────────────────────────────────────────────────
R_pocket = flange_od/2 + pocket_clear;           // raggio dell'alloggio
R_cup    = bell_seat_r + seat_lip_t;             // raggio esterno dell'anello di appoggio
bell_rim_z = (uso == "sordina") ? mute_rim_z : pocket_depth;   // quota del bordo campana sopra il piano dell'alloggio
rest_h_eff = rest_h - (mute_rim_z - bell_rim_z);                 // quota del contatto in questo uso (stessa profondita' di campana)
r_u      = rest_d/2 + saddle_clear;              // raggio interno della sella
// quota di riferimento del piano dell'alloggio (il punto piu' basso del pavimento sta a 2 mm sopra la base)
z0       = base_t + 2 + R_pocket * sin(lean);
// foro del montante da usare: la sella ha il centro a (z_perno - pin_local_z + saddle_h/2)
k_hole   = max(0, min(hole_n - 1, round((rest_h_eff + pin_local_z - saddle_h/2 - hole_z0) / hole_pitch)));
z_pin    = hole_z0 + k_hole * hole_pitch;
z_clip0  = z_pin - pin_local_z;                  // quota (asse tromba) del fondo della sella

echo("=================================================================");
echo("=== SUPPORTO TROMBA CON SORDINA ===");
echo(str("Uso: ", uso, " | inclinazione ", lean, " deg | foro n. ", k_hole + 1, " (di ", hole_n, ") -> centro sella a ",
         z_clip0 + saddle_h/2, " mm sopra il piano dell'alloggio (richiesti ", rest_h_eff, ")"));
echo(str("Sella: apertura interna Ø ", 2 * r_u, " mm per una campana Ø ", rest_d, " mm (gioco ", saddle_clear, " mm per lato: feltro)"));
echo(str("Ingombro base: ", base_x_front + base_x_rear, " x ", base_w, " mm"));
echo("=================================================================");

// ── sistema di riferimento della tromba: Z' = asse (inclinato), origine al centro del fondello ──
module T() { translate([0, 0, z0]) rotate([0, -lean, 0]) children(); }

// ── ghost: fondello + campana (solo per visualizzazione / controllo collisioni) ──
bell_prof = [[0,119.0],[10,83.0],[20,69.5],[30,57.0],[40,45.0],[70,35.0],[100,30.0],[300,12.0]];
module ghost_solid() {
    // fondello della sordina + corpo cilindrico (solo con la sordina)
    if (uso == "sordina") {
        cylinder(r = flange_od/2, h = 3.2);
        cylinder(r = 42, h = 48.2);
    }
    // campana (diametro esterno = interno + 1 mm), dal bordo (z' = bell_rim_z) verso la gola
    rotate_extrude()
        polygon(concat(
            [[0, bell_rim_z]],
            [ for (p = bell_prof) [p[1]/2 + 0.5, bell_rim_z + p[0]] ],
            [[0, bell_rim_z + bell_prof[len(bell_prof)-1][0]]]
        ));
}

// ── base + alloggio + montante (un solo pezzo) ──────────────────────────────
module post_solid() {
    translate([-post_x - post_t/2, -post_w/2, -60]) cube([post_t, post_w, post_h + 60]);
}

module stand_base() {
    difference() {
        union() {
            linear_extrude(base_t)
                offset(r = 10) offset(delta = -10)
                    translate([-base_x_rear, -base_w/2]) square([base_x_rear + base_x_front, base_w]);
            T() {
                translate([0, 0, -60]) cylinder(r = R_cup, h = 60 + pocket_depth);
                // bordo di ritenzione attorno all'anello (tiene il bordo campana senza sordina)
                translate([0, 0, pocket_depth])
                    difference() {
                        cylinder(r = R_cup, h = seat_lip_h);
                        translate([0, 0, -1]) cylinder(r = bell_seat_r, h = seat_lip_h + 2);
                    }
                post_solid();
            }
        }
        T() {
            // alloggio del fondello
            cylinder(r = R_pocket, h = pocket_depth + 5);
            // foro di sfogo lungo l'asse: lo stelo non viene chiuso
            translate([0, 0, -200]) cylinder(d = relief_d, h = 201);
            // fori per il perno del montante
            for (k = [0 : hole_n - 1])
                translate([-post_x, 0, hole_z0 + k * hole_pitch])
                    rotate([90, 0, 0]) cylinder(d = hole_d, h = post_w + 2, center = true, $fn = 24);
        }
        // tutto cio' che e' sotto il piano del tavolo
        translate([-400, -400, -400]) cube([800, 800, 400]);
    }
}

// ── sella scorrevole (stampata con il fondo del braccio sul piatto) ──────────
module clip_part() {
    sx   = (post_t + sleeve_clear)/2;           // semi-spessore interno del manicotto (x')
    sy   = (post_w + sleeve_clear)/2;
    x_pc = -post_x;                              // asse del montante
    x_front = x_pc + sx + clip_wall;             // faccia anteriore del manicotto
    x_back_u = -(r_u + saddle_wall);             // dorso della sella
    open_w = rest_d + 3;                         // apertura della forcella (la campana entra da davanti)
    difference() {
        union() {
            // manicotto sul montante
            translate([x_pc - sx - clip_wall, -(sy + clip_wall), 0])
                cube([2 * (sx + clip_wall), 2 * (sy + clip_wall), clip_h]);
            // braccio piatto (sul piano di stampa)
            translate([x_front - 1, -9, 0]) cube([(x_back_u + 3) - (x_front - 1), 18, arm_t]);
            // sella ad anello
            cylinder(r = r_u + saddle_wall, h = saddle_h);
        }
        // passaggio del montante
        translate([x_pc - sx, -sy, -1]) cube([2 * sx, 2 * sy, clip_h + 2]);
        // interno della sella
        translate([0, 0, -1]) cylinder(r = r_u, h = saddle_h + 2);
        // apertura anteriore (la campana entra da davanti)
        translate([0, -open_w/2, -1]) cube([r_u + saddle_wall + 5, open_w, saddle_h + 2]);
        // foro del perno
        translate([x_pc, 0, pin_local_z]) rotate([90, 0, 0])
            cylinder(d = hole_d, h = 2 * (sy + clip_wall) + 2, center = true, $fn = 24);
    }
}

module pin_part() {
    L = post_w + 2 * (clip_wall + sleeve_clear) + 6;
    rotate([0, 90, 0]) {
        cylinder(d = pin_d, h = L, $fn = 24);
        cylinder(d = pin_d + 4, h = 2.5, $fn = 24);
    }
}

// ── render ──────────────────────────────────────────────────────────────────
if (mode == "assembly") {
    color([0.55, 0.55, 0.58]) stand_base();
    color([0.25, 0.45, 0.85]) T() translate([0, 0, z_clip0]) clip_part();
    color([0.15, 0.15, 0.15]) T() translate([-post_x, 0, z_pin])
        rotate([90, 0, 0]) cylinder(d = pin_d, h = post_w + 2 * clip_wall + 8, center = true, $fn = 24);
    %T() ghost_solid();
}
else if (mode == "base") { stand_base(); }
else if (mode == "clip") { clip_part(); }
else if (mode == "pin")  { translate([0, 0, (pin_d + 4)/2]) pin_part(); }
else if (mode == "ghost") { T() ghost_solid(); }
else if (mode == "clip_placed") { T() translate([0, 0, z_clip0]) clip_part(); }   // solo per controlli
else if (mode == "pin_placed") { T() translate([-post_x, 0, z_pin]) rotate([90, 0, 0]) cylinder(d = pin_d, h = post_w + 2 * clip_wall + 8, center = true, $fn = 24); }   // solo per controlli
