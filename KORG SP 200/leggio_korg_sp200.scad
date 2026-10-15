// ============================================================
//  LEGGIO PARAMETRICO — KORG SP-200
//  Telaio tubolare aperto con perno L a gomito e mensolina
//  fermaspartito con bordino frontale rialzato.
//  Apri con OpenSCAD → F5 anteprima → F6 render → Export STL
// ============================================================

/* ===================== MISURE DA CALIBRO ===================== */

// --- PIOLI DI AGGANCIO ---
// Sezione rettangolare, entrano ORIZZONTALI nel pannello posteriore
// (fori a ~40mm sotto il bordo superiore del pianoforte).
peg_spacing   = 430;   // distanza centro-centro (mm)
peg_width     = 6.6;   // larghezza perno (alloggiamento 7mm, gioco 0.4mm)
peg_thickness = 4.6;   // spessore perno (alloggiamento 5mm, gioco 0.4mm)
peg_length    = 26;    // inserimento effettivo (foro 28mm, battuta precisa)
peg_edge_r    = 0.6;   // arrotondamento spigoli perno (mm)

// --- TELAIO ---
stand_height  = 200;   // altezza totale telaio (mm) — ~160mm utili sopra il piano
stand_width   = 450;   // larghezza totale (mm)
bar_thickness = 9;     // diametro sezione tubolari (mm)

// --- INCLINAZIONE ALL'INDIETRO ---
tilt_angle = 14;       // gradi da verticale

// --- RIENTRANZA CENTRALE (V nella traversa superiore) ---
v_width = 160;         // larghezza dell'apertura V (mm)
v_depth = 55;          // profondità della rientranza (mm)
v_bottom_flat = 30;    // tratto piatto orizzontale al fondo della V (mm)
                       // — tiene i fori delle spine completamente annegati nel tubo

// --- GOMITO RINFORZATO ---
elbow_gusset_len = 18; // lunghezza rinforzo triangolare (mm)

// --- MENSOLINA FERMASPARTITO ---
shelf_y     = 40;      // altezza sopra i perni (mm) — a filo col piano tastiera
shelf_depth = 25;      // profondità d'appoggio verso il musicista (mm)
shelf_t     = 4;       // spessore plastica mensolina e bordino (mm)
lip_height  = 12;      // altezza bordino frontale rialzato (mm)
lip_angle   = 95;      // angolo bordino (90=verticale, >90=inclinato avanti)

// --- DIVISIONE IN DUE METÀ ---
part = "left    ";         // "left"  = metà sinistra (foro femmina)
                       // "right" = metà destra   (foro femmina)
                       // "both"  = telaio intero  (anteprima)
                       // "pin"   = spine di giunzione separate (da incollare)

// --- SPINE DI CENTRAGGIO SEPARATE (foro femmina su entrambi i lati) ---
pin_diameter  = 5;     // diametro spina (mm)
pin_clearance = 0.2;   // gioco diametrale per lato (mm) → foro = 5.4mm
hole_depth    = 15;    // profondità foro femmina per lato (mm)
pin_total     = 28;    // lunghezza totale spina (mm) — 14mm per lato, 1mm aria per colla
pin_chamfer   = 0.8;   // smusso estremità spina per inserimento facile (mm)

/* ================================================================
   GEOMETRIA — non serve modificare da qui in giù
   ================================================================ */

$fn = 48;
fn_bar = 24;
hb = bar_thickness / 2;
peg_total = peg_length + hb;   // compensazione raccordo sferico

// ---- Funzioni ----

function tilt3d(p) = [p[0], p[1] * cos(tilt_angle), -p[1] * sin(tilt_angle)];
function v_len(v)  = sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]);
function v_unit(v) = let(l = v_len(v)) l > 0 ? v / l : v;

// ---- Scheletro del telaio ----

frame_skel = [
    [-peg_spacing/2, 0],                            // 0  base montante SX
    [-(stand_width/2 - hb), stand_height - hb],     // 1  angolo alto SX
    [-v_width/2, stand_height - hb],                // 2  inizio V
    [-v_bottom_flat/2, stand_height - v_depth + hb],// 3  fondo V sx
    [ v_bottom_flat/2, stand_height - v_depth + hb],// 4  fondo V dx (tratto piatto)
    [v_width/2, stand_height - hb],                 // 5  fine V
    [(stand_width/2 - hb), stand_height - hb],      // 6  angolo alto DX
    [peg_spacing/2, 0]                               // 7  base montante DX
];

frame_pts = [for (p = frame_skel) tilt3d(p)];

// Centro del tratto piatto (x=0) per i fori delle spine
v_bottom_3d     = tilt3d([0, stand_height - v_depth + hb]);
shelf_center_3d = tilt3d([0, shelf_y]);

// ---- Moduli geometrici ----

module bar3d(p1, p2) {
    hull() {
        translate(p1) sphere(d = bar_thickness, $fn = fn_bar);
        translate(p2) sphere(d = bar_thickness, $fn = fn_bar);
    }
}

module frame_bars() {
    for (i = [0 : len(frame_pts) - 2])
        bar3d(frame_pts[i], frame_pts[i + 1]);
}

// Traversa strutturale alla quota della mensola (sezione tonda)
module shelf_crossbar() {
    bar3d(tilt3d([-peg_spacing/2, shelf_y]),
          tilt3d([ peg_spacing/2, shelf_y]));
}

// ---- Mensolina + bordino ----
// Profilo unico 2D (poligono singolo → nessuna faccia coplanare).
// Coordinate profilo:
//   X = distanza dal centro-barra verso il musicista
//   Y = altezza relativa alla superficie della mensola (0 = piano d'appoggio)
module shelf_profile_2d() {
    lip_dx = lip_height * sin(lip_angle - 90);
    lip_dy = lip_height * cos(lip_angle - 90);
    sd = hb + shelf_depth;       // bordo mensola
    st = sd + shelf_t;           // bordo esterno bordino

    polygon([
        [0,          0],              // A  dorso superiore (centro barra)
        [sd,         0],              // B  bordo mensola (base interna bordino)
        [sd + lip_dx, lip_dy],        // C  sommità bordino, faccia interna
        [st + lip_dx, lip_dy],        // D  sommità bordino, faccia esterna
        [st,         0],              // E  base esterna bordino
        [st,        -shelf_t],        // F  fondo anteriore
        [0,         -shelf_t]         // G  fondo posteriore
    ]);
}

// Estrusione del profilo lungo la larghezza, poi tilt
module shelf_geometry() {
    rotate([-tilt_angle, 0, 0])
        translate([0, shelf_y, 0])
            rotate([0, -90, 0])
                linear_extrude(height = peg_spacing, center = true, convexity = 4)
                    shelf_profile_2d();
}

// ---- Perni di aggancio ----

module peg_at(x_pos) {
    er = peg_edge_r;
    translate([
        x_pos - peg_width/2 + er,
        -peg_thickness/2 + er,
        er])
        minkowski() {
            cube([
                peg_width - 2*er,
                peg_thickness - 2*er,
                peg_total - 2*er]);
            sphere(r = er, $fn = 16);
        }

    hull() {
        translate([x_pos, 0, 0])
            sphere(d = bar_thickness, $fn = fn_bar);
        translate([x_pos, 0, hb + 3])
            cube([peg_width, peg_thickness, 0.01], center = true);
    }
}

module elbow_gusset(x_pos, frame_next_pt) {
    dir_up = v_unit(frame_next_pt - [x_pos, 0, 0]);
    p_up   = [x_pos, 0, 0] + dir_up * elbow_gusset_len;
    p_peg  = [x_pos, 0, elbow_gusset_len];

    hull() {
        translate([x_pos, 0, 0])
            sphere(d = bar_thickness, $fn = fn_bar);
        translate(p_up)
            sphere(d = bar_thickness * 0.55, $fn = fn_bar);
        translate(p_peg)
            sphere(d = bar_thickness * 0.55, $fn = fn_bar);
    }
}

// ---- Leggio completo ----

module leggio_full() {
    frame_bars();
    shelf_crossbar();
    shelf_geometry();
    peg_at(-peg_spacing/2);
    peg_at( peg_spacing/2);
    elbow_gusset(-peg_spacing/2, frame_pts[1]);
    elbow_gusset( peg_spacing/2, frame_pts[6]);
}

// ---- Fori femmina (uguali su entrambe le metà) ----

hole_d = pin_diameter + 2 * pin_clearance;   // 5.4mm

module alignment_holes_left() {
    // Fori che penetrano nella metà sinistra (in -X dal piano di taglio)
    for (pos = [v_bottom_3d, shelf_center_3d])
        translate(pos)
            rotate([0, -90, 0])   // fora in -X
                translate([0, 0, -0.01])
                    cylinder(d = hole_d, h = hole_depth + 0.01, $fn = 32);
}

module alignment_holes_right() {
    // Fori che penetrano nella metà destra (in +X dal piano di taglio)
    for (pos = [v_bottom_3d, shelf_center_3d])
        translate(pos)
            rotate([0, 90, 0])    // fora in +X
                translate([0, 0, -0.01])
                    cylinder(d = hole_d, h = hole_depth + 0.01, $fn = 32);
}

// ---- Spine di giunzione stampabili ----

module single_pin() {
    // Cilindro con smussi alle estremità per inserimento facilitato
    ch = pin_chamfer;
    body = pin_total - 2*ch;

    // Corpo centrale
    translate([0, 0, ch])
        cylinder(d = pin_diameter, h = body, $fn = 32);
    // Smusso inferiore
    cylinder(d1 = pin_diameter - 2*ch, d2 = pin_diameter, h = ch, $fn = 32);
    // Smusso superiore
    translate([0, 0, ch + body])
        cylinder(d1 = pin_diameter, d2 = pin_diameter - 2*ch, h = ch, $fn = 32);
}

module printable_pins() {
    // 2 spine adagiate sul piano di stampa, distanziate 15mm
    translate([-10, 0, pin_diameter/2])
        rotate([0, 90, 0]) single_pin();
    translate([ 10, 0, pin_diameter/2])
        rotate([0, 90, 0]) single_pin();
}

// ---- Divisione ----

module left_box() {
    translate([-1000, -500, -500])
        cube([1000, 1500, 1500]);
}

module right_box() {
    translate([0, -500, -500])
        cube([1000, 1500, 1500]);
}

module render_part() {
    if (part == "both") {
        leggio_full();
    } else if (part == "left") {
        difference() {
            intersection() { leggio_full(); left_box(); }
            alignment_holes_left();
        }
    } else if (part == "right") {
        difference() {
            intersection() { leggio_full(); right_box(); }
            alignment_holes_right();
        }
    } else if (part == "pin") {
        printable_pins();
    }
}

render_part();
