// =====================================================================
//  Dosatore monodose per polvere lavastoviglie  —  v1
//  Principio: cassetto scorrevole con camera dosatrice passante.
//   - Cassetto TIRATO  -> la camera è sotto la tramoggia e si riempie
//   - Cassetto SPINTO  -> la camera è sopra l'uscita e la polvere cade;
//                        il cassetto chiude la tramoggia
//  Stampante: Ender-3 V2 (220x220). Unità: mm.
// =====================================================================

/* [Parte da esportare] */
part = "assembly"; // [assembly, section, body, slider, pin, lid, print_plate, test_tunnels, test_slider, abs_plate, pin_plate]
// Per l'anteprima "assembly": 0 = cassetto tirato (carica), 1 = spinto (eroga)
anim = 0; // [0:0.05:1]

/* [Dose] */
dose_ml      = 25;   // volume della monodose (ml = cm³). Tipico: 20–30 ml
slider_h     = 20;   // spessore del cassetto = altezza della camera

/* [Tolleranze e pareti] */
clr          = 0.35; // gioco per lato tra cassetto e tunnel
wall         = 3;    // pareti del corpo
floor_t      = 3;    // fondo del corpo
roof_t       = 3;    // tetto del tunnel
slider_side  = 6;    // materiale del cassetto ai lati della camera

/* [Serbatoio] */
res_size     = 90;   // lato esterno del serbatoio quadrato
res_h        = 90;   // altezza della parte dritta del serbatoio
funnel_angle = 60;   // pendenza minima pareti tramoggia (gradi da orizzontale)

/* [Fermo cassetto] */
pin_d        = 5;    // perno di fine corsa
pin_clr      = 0.25;
slot_depth   = 4;

$fn = 96;

// ---------------- grandezze derivate ----------------
dose_mm3   = dose_ml * 1000;
chamber_d  = sqrt(4 * dose_mm3 / (PI * slider_h));   // diametro camera
slider_w   = chamber_d + 2 * slider_side;
stroke     = chamber_d + 12;                          // corsa: niente sovrapposizione carico/uscita
margin     = 6;

tun_w      = slider_w + 2 * clr;
tun_h      = slider_h + 2 * clr;
body_w     = tun_w + 2 * wall;
body_h     = floor_t + tun_h + roof_t;

A          = res_size / 2;                 // asse tramoggia (x)
B          = A + stroke;                   // asse uscita (x)
front_solid= stroke + chamber_d / 2 + margin;  // pieno davanti alla camera
x_end      = B + front_solid;              // fondo cieco del tunnel (lato interno)
body_len   = x_end + wall;

slider_len = x_end - 0.5;                  // lunghezza dentro il tunnel (a corsa finita)
handle_len = 30;

pin_x      = 12;                           // posizione perno nel fondo del corpo
// asola nel cassetto, coordinate u = distanza dalla punta
slot_u1    = x_end - stroke - pin_x - pin_d/2 - pin_clr;
slot_u2    = x_end - pin_x + pin_d/2 + pin_clr;

res_in     = res_size - 2 * wall;
funnel_h   = ((res_in - chamber_d) / 2) * tan(funnel_angle);

echo(str("Diametro camera: ", chamber_d, " mm  | corsa: ", stroke,
         " mm | corpo: ", body_len, " x ", res_size, " x ",
         body_h + funnel_h + res_h, " mm | cassetto: ", slider_len + handle_len, " mm"));
echo(str("Capacità serbatoio ~ ", round(res_in*res_in*res_h/1000), " ml"));

// =====================================================================
module body() {
    difference() {
        union() {
            // blocco del tunnel
            translate([0, -body_w/2, 0]) cube([body_len, body_w, body_h]);
            // guscio esterno della tramoggia (pareti esterne a 45°+, stampabili)
            hull() {
                translate([0, -body_w/2, body_h - 0.01]) cube([res_size, body_w, 0.01]);
                translate([0, -res_size/2, body_h + funnel_h]) cube([res_size, res_size, 0.01]);
            }
            // serbatoio
            translate([0, -res_size/2, body_h + funnel_h]) cube([res_size, res_size, res_h]);
        }
        // tunnel del cassetto (aperto in x=0, cieco in fondo)
        translate([-1, -tun_w/2, floor_t]) cube([x_end + 1, tun_w, tun_h]);
        // foro di caduta nel tetto + imbuto interno
        hull() {
            translate([A, 0, body_h - roof_t - 0.5]) cylinder(d = chamber_d - 1, h = 0.01);
            translate([A, 0, body_h]) cylinder(d = chamber_d - 1, h = 0.01);
            translate([A - res_in/2, -res_in/2, body_h + funnel_h]) cube([res_in, res_in, 0.01]);
        }
        // interno serbatoio
        translate([wall, -res_in/2, body_h + funnel_h - 0.01]) cube([res_in, res_in, res_h + 1]);
        // uscita nel fondo, svasata verso il basso (niente sbalzi in stampa)
        translate([B, 0, -0.01]) cylinder(d1 = chamber_d + 2, d2 = chamber_d, h = floor_t + 0.5);
        // foro per il perno di fine corsa
        translate([pin_x, 0, -1]) cylinder(d = pin_d + 2*pin_clr, h = floor_t + 2);
        // freccia "SPINGI" incisa sul fianco
        translate([body_len/2 + 10, -body_w/2 + 0.6, body_h/2])
            rotate([90, 0, 0]) linear_extrude(1)
                text("SPINGI >", size = 6, halign = "center", valign = "center");
    }
}

module slider() {
    // il cassetto è modellato con la punta in u=0 e la maniglia in u=slider_len
    difference() {
        union() {
            translate([0, -slider_w/2, 0]) cube([slider_len, slider_w, slider_h]);
            // maniglia (fa anche da fine corsa contro il corpo)
            translate([slider_len, -body_w/2 - 4, 0])
                cube([handle_len, body_w + 8, slider_h]);
        }
        // camera dosatrice passante
        translate([front_solid, 0, -1]) cylinder(d = chamber_d, h = slider_h + 2);
        // asola di fine corsa sul lato inferiore
        hull() {
            translate([slot_u1, 0, -1]) cylinder(d = pin_d + 2*pin_clr + 0.4, h = slot_depth + 1);
            translate([slot_u2, 0, -1]) cylinder(d = pin_d + 2*pin_clr + 0.4, h = slot_depth + 1);
        }
        // presa per le dita nella maniglia
        translate([slider_len + handle_len/2, 0, -1])
            cylinder(d = 20, h = slider_h + 2);
        // etichetta dose
        translate([slider_len + handle_len/2, body_w/2 - 2, slider_h - 0.8])
            linear_extrude(1) text(str(dose_ml, " ml"), size = 5, halign = "center", valign = "center");
    }
}

module pin() {
    // perno da inserire dal basso dopo aver infilato il cassetto (incollare)
    cylinder(d = pin_d, h = floor_t + slot_depth - 0.6);
}

module lid() {
    lip = 8; c = 0.3;
    translate([0, 0, 0]) cube([res_size, res_size, 2.4]);
    translate([wall + c, wall + c, 2.3]) difference() {
        cube([res_in - 2*c, res_in - 2*c, lip]);
        translate([1.6, 1.6, -1]) cube([res_in - 2*c - 3.2, res_in - 2*c - 3.2, lip + 2]);
    }
}

// =====================================================================
if (part == "body") body();
else if (part == "slider") slider();
else if (part == "pin") pin();
else if (part == "lid") lid();
else if (part == "print_plate") {
    body();
    translate([0, res_size/2 + 10 + body_w/2 + 4, 0]) slider();
}
else if (part == "section") {   // spaccato a metà per vedere il funzionamento
    difference() { assembly(); translate([-50, -200, -10]) cube([400, 200, 400]); }
}
else if (part == "test_tunnels") {
    // 3 anelli di tunnel con giochi diversi: 0.25 / 0.35 / 0.45 mm per lato
    cl = [0.25, 0.35, 0.45];
    for (i = [0:2]) translate([0, i * (slider_w + 2*wall + 10), 0]) test_tunnel(cl[i]);
}
else if (part == "test_slider") test_slider();
else if (part == "abs_plate") abs_plate();
else if (part == "pin_plate") pin_plate();
else assembly();

// Spezzone di tunnel lungo 20 mm (stampare in piedi, come il corpo: il tetto è un ponte)
module test_tunnel(c) {
    tw = slider_w + 2*c; th = slider_h + 2*c;
    bw = tw + 2*wall;    bh = floor_t + th + roof_t;
    difference() {
        translate([0, -bw/2, 0]) cube([20, bw, bh]);
        translate([-1, -tw/2, floor_t]) cube([22, tw, th]);
        translate([10, 0, bh - 0.6]) linear_extrude(1)
            text(str(c), size = 5, halign = "center", valign = "center");
    }
}

// Spezzone di cassetto con la camera vera: serve sia per il gioco sia per tarare la dose
module test_slider() {
    L = chamber_d + 2*slider_side + 20;
    difference() {
        translate([0, -slider_w/2, 0]) cube([L, slider_w, slider_h]);
        translate([slider_side + chamber_d/2, 0, -1]) cylinder(d = chamber_d, h = slider_h + 2);
        translate([L - 10, 0, slider_h - 0.6]) linear_extrude(1)
            text(str(dose_ml), size = 6, halign = "center", valign = "center");
    }
}

module assembly() {
    tip = x_end - stroke * (1 - anim);   // posizione della punta del cassetto
    color("lightsteelblue", 0.55) body();
    color("tomato") translate([tip, 0, floor_t + clr]) mirror([1, 0, 0]) slider();
    color("gold") translate([pin_x, 0, 0]) pin();
    color("white", 0.4) translate([0, res_size/2, body_h + funnel_h + res_h + 2.4 + 12])
        rotate([180, 0, 0]) lid();
}

// Perno stampato coricato: gli strati corrono lungo l'asse, così il taglio
// non cade tra uno strato e l'altro. Piccolo piatto sotto per l'adesione.
module pin_lying() {
    L = floor_t + slot_depth - 0.6;
    translate([0, 0, pin_d/2 - 0.4]) difference() {
        rotate([0, 90, 0]) cylinder(d = pin_d, h = L, $fn = 48);
        translate([-1, -pin_d, -pin_d/2 - 1 + 0.4]) cube([L + 2, 2*pin_d, 1]);
    }
}

// Piatto ABS per la Ender-3 V2 (220x220): cassetto in diagonale (lascia spazio al brim),
// spezzone di prova e 3 perni (2 di scorta) negli angoli liberi.
module abs_plate() {
    translate([110, 110, 0]) rotate([0, 0, 45])
        translate([-(slider_len + handle_len)/2, 0, 0]) slider();
    translate([138, 10 + slider_w/2, 0]) test_slider();
}

// 3 perni (2 di scorta), da stampare a parte
module pin_plate() { for (i = [0:2]) translate([0, i * 10, 0]) pin_lying(); }
