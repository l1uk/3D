// ============================================================
//  LEGGIO PARAMETRICO v2 — KORG SP-200
//  Telaio tubolare aperto con perni a L per pannello posteriore,
//  mensolina fermaspartito a filo tastiera e traversa intermedia
//  per massima rigidità strutturale e sostegno fogli.
//
//  Apri con OpenSCAD → F5 anteprima → F6 render → Export STL
// ============================================================

/* ===================== MISURE DA CALIBRO ===================== */

// --- PIOLI DI AGGANCIO (entrano nel pannello verticale posteriore) ---
peg_spacing   = 430;   // distanza centro-centro dei due fori (mm)
peg_width     = 6.6;   // larghezza orizzontale perno (foro 7.0mm, gioco 0.4mm)
peg_thickness = 4.6;   // spessore verticale perno (foro 5.0mm, gioco 0.4mm)
peg_length    = 26;    // profondità inserimento nel retro (foro 28mm)
peg_edge_r    = 0.6;   // arrotondamento spigoli perno (mm)

// --- TELAIO PRINCIPALE ---
stand_height  = 200;   // altezza totale telaio dal centro fori (mm)
stand_width   = 490;   // larghezza totale del telaio (mm) — 245mm per metà: massima larghezza sicura al 100% su Bambu Lab (piatto 256x256)
bar_thickness = 9;     // diametro/sezione tubolari (mm) — 9mm dà ottima rigidità in PLA/PETG

// --- INCLINAZIONE ALL'INDIETRO ---
tilt_angle = 24.0;     // gradi di inclinazione dello schienale (standard pianoforti a coda/orchestra, la gravità tiene i fogli aderenti)

// --- RIENTRANZA CENTRALE SUPERIORE (sagoma a V originale Korg) ---
v_width       = 160;   // larghezza dell'apertura a V in cima (mm)
v_depth       = 35;    // profondità della rientranza verso il basso (mm) — ridotta per dare più appoggio dorsale ai fogli A4
v_bottom_flat = 36;    // tratto orizzontale al fondo della V (mm) — 18mm per lato, alloggia comodamente il foro cieco
                       // (mantiene il foro della spina cieco e 100% annegato nel tubo)

// --- MENSOLINA FERMASPARTITO INFERIORE ---
shelf_y     = 14;      // altezza sopra i fori (mm) — calibrata dal provino reale per adagiarsi radente alla scocca
shelf_depth = 33;      // profondità d'appoggio utile verso il musicista (mm) — accoglie libri spessi e raccoglitori
shelf_t     = 4;       // spessore plastica della mensolina e del bordino (mm)
lip_height  = 10;      // altezza del bordino frontale rialzato (mm)
lip_angle   = 105;     // inclinazione bordino (105° = svasato in avanti per consentire alla pagina di scorrere fluida durante la voltata)

// --- TRAVERSA ORIZZONTALE INTERMEDIA (Rigidità & Anti-caduta fogli) ---
mid_bar_y = 105;       // quota a metà altezza (mm) — lega i montanti e sostiene la schiena dei fogli

// --- SIMULAZIONE PIANOFORTE REALE KORG SP-200 ---
show_piano_preview = false; // true = mostra la carrozzeria reale del piano sotto al leggio in 3D (F5)
                           // false = mostra solo il leggio isolato

// --- SELEZIONE PARTE DA MOSTRARE / STAMPARE ---
part = "both";         // "test"  = PROVINO DI TEST (10 min): stampa solo il perno + angolo mensolina per verificare l'inserimento
                       // "left"  = metà sinistra con fori femmina (per stampante 3D)
                       // "right" = metà destra con fori femmina (per stampante 3D)
                       // "pin"   = 3 spine di giunzione cilindriche a parte
                       // "both"  = telaio completo montato sul pianoforte (anteprima montaggio)
                       // "piano" = SOLO il pianoforte simulato (senza leggio, per ispezione)

// --- SPINE DI GIUNZIONE SEPARATE (a scomparsa totale) ---
pin_diameter     = 4.6;   // diametro spina (mm)
hole_diameter    = 5.4;   // diametro fori femmina (mm) — gioco radiale 0.4mm anti-bloccaggio
hole_depth_top   = 10;    // profondità foro superiore a V per lato (mm)
pin_length_top   = 16;    // lunghezza spina superiore (mm) — entra 8mm per lato, 2mm di aria fondo foro
hole_depth_lower = 18;    // profondità fori traversa intermedia e mensolina per lato (mm)
pin_length_lower = 22;    // lunghezza spine inferiori (mm) — entra 11mm per lato, 7mm di margine aria fondo foro
pin_chamfer      = 1.0;   // smusso d'invito d'estremità a 45° per inserimento guidato senza attrito (mm)


/* ================================================================
   GEOMETRIA 3D — non serve modificare da qui in giù
   ================================================================ */

$fn = 48;
fn_bar = 24;
hb = bar_thickness / 2;
peg_total = peg_length + hb;   // compensazione raccordo sferico del gomito

// ---- Funzioni vettoriali e rotazioni ----
function tilt3d(p) = [p[0], p[1] * cos(tilt_angle), -p[1] * sin(tilt_angle)];
function v_len(v)  = sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]);
function v_unit(v) = let(l = v_len(v)) l > 0 ? v / l : v;

// Coordinata X dei montanti (dritti o rastremati all'altezza Y)
function upright_x(y) = -(stand_width/2 - hb);

// ---- Scheletro del telaio perimetrale (largo 490mm, con montanti agli angoli esterni) ----
frame_skel = [
    [-(stand_width/2 - hb), shelf_y],               // 0  angolo basso SX (quota mensola)
    [-(stand_width/2 - hb), stand_height - hb],     // 1  angolo alto SX
    [-v_width/2, stand_height - hb],                // 2  inizio V superiore
    [-v_bottom_flat/2, stand_height - v_depth + hb],// 3  fondo V sx (tratto piatto)
    [ v_bottom_flat/2, stand_height - v_depth + hb],// 4  fondo V dx (tratto piatto)
    [v_width/2, stand_height - hb],                 // 5  fine V superiore
    [(stand_width/2 - hb), stand_height - hb],      // 6  angolo alto DX
    [(stand_width/2 - hb), shelf_y]                 // 7  angolo basso DX (quota mensola)
];

frame_pts = [for (p = frame_skel) tilt3d(p)];

// Punti di giunzione al centro (x = 0) per i fori delle spine
v_bottom_3d     = tilt3d([0, stand_height - v_depth + hb]);
mid_bar_3d      = tilt3d([0, mid_bar_y]);
shelf_center_3d = tilt3d([0, shelf_y]);

// ---- Moduli costruttivi tubolari 3D ----

// Tubo a sezione tonda tra due punti nello spazio
module bar3d(p1, p2) {
    hull() {
        translate(p1) sphere(d = bar_thickness, $fn = fn_bar);
        translate(p2) sphere(d = bar_thickness, $fn = fn_bar);
    }
}

// Tutte le barre del perimetro
module frame_bars() {
    for (i = [0 : len(frame_pts) - 2])
        bar3d(frame_pts[i], frame_pts[i + 1]);
}

// Traversa inferiore strutturale (quota mensola, tutta la larghezza)
module shelf_crossbar() {
    bar3d(tilt3d([-(stand_width/2 - hb), shelf_y]),
          tilt3d([ (stand_width/2 - hb), shelf_y]));
}

// Traversa intermedia orizzontale (quota 105mm, tutta la larghezza)
module mid_crossbar() {
    bar3d(tilt3d([-(stand_width/2 - hb), mid_bar_y]),
          tilt3d([ (stand_width/2 - hb), mid_bar_y]));
}

// Montanti verticali che collegano i perni alla traversa mensola
module peg_struts() {
    bar3d(tilt3d([-peg_spacing/2, 0]), tilt3d([-peg_spacing/2, shelf_y]));
    bar3d(tilt3d([ peg_spacing/2, 0]), tilt3d([ peg_spacing/2, shelf_y]));
}

// ---- Mensolina fermaspartito con bordino rialzato e cresta svasata/arrotondata ----
shelf_w = stand_width - 2*hb; // 481 mm, raccordata ai montanti laterali

module shelf_profile_2d() {
    lip_dx = lip_height * sin(lip_angle - 90);
    lip_dy = lip_height * cos(lip_angle - 90);
    sd = hb + shelf_depth;       // profondità mensola dal centro tubo
    st = sd + shelf_t;           // spessore bordino
    ch = 1.0;                    // raggio/smusso cresta anti-sfregamento voltata pagine

    polygon([
        [0,               0],              // A  dorso superiore
        [sd,              0],              // B  base interna bordino
        [sd + lip_dx,     lip_dy - ch],    // C  invito interno cresta
        [sd + lip_dx + ch, lip_dy],        // C2 cresta superiore interna
        [st + lip_dx - ch, lip_dy],        // D2 cresta superiore esterna
        [st + lip_dx,     lip_dy - ch],    // D  invito esterno cresta
        [st,              0],              // E  base esterna bordino
        [st,             -shelf_t],        // F  fondo inferiore
        [0,              -shelf_t]         // G  fondo posteriore
    ]);
}

module shelf_geometry() {
    rotate([-tilt_angle, 0, 0])
        translate([0, shelf_y, 0])
            rotate([0, -90, 0])
                linear_extrude(height = shelf_w, center = true, convexity = 4)
                    shelf_profile_2d();
}

// ---- Perni di aggancio a gomito a L (retro tastiera) ----
// Il perno deve essere completamente liscio e libero da alette/gusset
// per poter scorrere liberamente dentro il foro del pianoforte per tutti i suoi 26mm.
module peg_at(x_pos) {
    er = peg_edge_r;

    // Corpo perno orizzontale rettangolare arrotondato (scorre dentro il foro da z = hb a z = hb + peg_length)
    translate([
        x_pos - peg_width/2 + er,
        -peg_thickness/2 + er,
        hb + er])
        minkowski() {
            cube([
                peg_width - 2*er,
                peg_thickness - 2*er,
                peg_length - 2*er]);
            sphere(r = er, $fn = 16);
        }

    // Battuta e raccordo al gomito: la sfera di giunzione a z=0 tocca a filo la scocca a z=hb
    hull() {
        translate([x_pos, 0, 0])
            sphere(d = bar_thickness, $fn = fn_bar);
        translate([x_pos, 0, hb])
            cube([peg_width, peg_thickness, 0.01], center = true);
    }
}

// ---- Leggio intero completo ----
module leggio_full() {
    frame_bars();
    shelf_crossbar();
    mid_crossbar();
    peg_struts();
    shelf_geometry();
    peg_at(-peg_spacing/2);
    peg_at( peg_spacing/2);
}

// ---- Fori femmina di centraggio (3 fori perfettamente annegati e ciechi) ----
module alignment_holes_left() {
    // 1. Foro superiore (linea a V, profondo 10mm in -X)
    translate(v_bottom_3d)
        rotate([0, -90, 0])
            translate([0, 0, -0.01])
                cylinder(d = hole_diameter, h = hole_depth_top + 0.01, $fn = 32);

    // 2. Fori inferiori (traversa intermedia e mensolina, profondi 18mm in -X)
    for (pos = [mid_bar_3d, shelf_center_3d])
        translate(pos)
            rotate([0, -90, 0])
                translate([0, 0, -0.01])
                    cylinder(d = hole_diameter, h = hole_depth_lower + 0.01, $fn = 32);
}

module alignment_holes_right() {
    // 1. Foro superiore (linea a V, profondo 10mm in +X)
    translate(v_bottom_3d)
        rotate([0, 90, 0])
            translate([0, 0, -0.01])
                cylinder(d = hole_diameter, h = hole_depth_top + 0.01, $fn = 32);

    // 2. Fori inferiori (traversa intermedia e mensolina, profondi 18mm in +X)
    for (pos = [mid_bar_3d, shelf_center_3d])
        translate(pos)
            rotate([0, 90, 0])
                translate([0, 0, -0.01])
                    cylinder(d = hole_diameter, h = hole_depth_lower + 0.01, $fn = 32);
}

// ---- Modulo spine di giunzione stampabili ----
module single_pin(length) {
    ch = pin_chamfer;
    body = length - 2*ch;

    translate([0, 0, ch])
        cylinder(d = pin_diameter, h = body, $fn = 32);
    cylinder(d1 = pin_diameter - 2*ch, d2 = pin_diameter, h = ch, $fn = 32);
    translate([0, 0, ch + body])
        cylinder(d1 = pin_diameter, d2 = pin_diameter - 2*ch, h = ch, $fn = 32);
}

module printable_pins() {
    // 3 spine adagiate orizzontalmente sul piatto lungo l'asse X, distanziate lungo Y
    // Spina 1: superiore corta per rientranza a V (16mm)
    translate([0, -15, pin_diameter/2])
        rotate([0, 90, 0])
            translate([0, 0, -pin_length_top/2])
                single_pin(pin_length_top);

    // Spina 2: traversa intermedia (22mm)
    translate([0, 0, pin_diameter/2])
        rotate([0, 90, 0])
            translate([0, 0, -pin_length_lower/2])
                single_pin(pin_length_lower);

    // Spina 3: mensolina inferiore (22mm)
    translate([0, 15, pin_diameter/2])
        rotate([0, 90, 0])
            translate([0, 0, -pin_length_lower/2])
                single_pin(pin_length_lower);
}

// ---- Scatole di taglio piano x = 0 ----
module left_box() {
    translate([-1000, -500, -500])
        cube([1000, 1500, 1500]);
}

module right_box() {
    translate([0, -500, -500])
        cube([1000, 1500, 1500]);
}

// ---- Modulo simulazione 3D della scocca reale Korg SP-200 ----
module piano_simulation() {
    piano_w = 520; // larghezza porzione simulata del pianoforte (mm)

    // Sagoma 2D della carrozzeria (coordinate: u = profondità in Z, v = altezza in Y)
    module piano_casing_2d() {
        hull() {
            // Curva 1 posteriore (raggio 5mm)
            translate([11, 10]) circle(r = 5, $fn = 32);
            // Curva 2 anteriore (raggio 5mm) dopo il tratto piatto di 15mm
            translate([26, 10]) circle(r = 5, $fn = 32);
            // Fondo posteriore
            translate([6, -60]) square([0.1, 0.1]);
            // Fondo anteriore
            translate([150, -60]) square([0.1, 0.1]);
            // Fine piano inclinato comandi (discesa verso i tasti)
            translate([150, -20]) square([0.1, 0.1]);
        }
    }

    // Carrozzeria semitrasparente grigio grafite con fori di alloggiamento
    color([0.25, 0.25, 0.28, 0.5]) {
        difference() {
            rotate([0, 90, 0])
                mirror([1, 0, 0])
                    translate([0, 0, -piano_w/2])
                        linear_extrude(height = piano_w, convexity = 4)
                            piano_casing_2d();

            // Due fori rettangolari 7x5 mm profondi 28mm nel retro
            for (xs = [-peg_spacing/2, peg_spacing/2]) {
                translate([xs, 0, 4.5 + 14])
                    cube([7.0, 5.0, 28.1], center = true);
            }
        }
    }

    // Boccole Korg originali (collare plastico nero che sporge 1.5mm dal retro)
    color([0.12, 0.12, 0.14, 0.95]) {
        for (xs = [-peg_spacing/2, peg_spacing/2]) {
            difference() {
                translate([xs, 0, (4.5 + 6.0)/2])
                    cube([12, 9, 6.0 - 4.5], center = true);
                translate([xs, 0, 4.5 + 14])
                    cube([7.0, 5.0, 30], center = true);
            }
        }
    }

    // Viti metalliche laterali che fissano le boccole (come nella tua foto reale)
    color([0.65, 0.55, 0.45]) {
        for (xs = [-peg_spacing/2, peg_spacing/2]) {
            for (dx = [-11, 11]) {
                translate([xs + dx, 0, 5.8])
                    rotate([90, 0, 0])
                        cylinder(d = 5.5, h = 1.0, center = true, $fn = 20);
            }
        }
    }
}

// ---- Scatola per provino rapido di test (perno + 5cm di mensolina) ----
module test_box() {
    translate([-peg_spacing/2 - 35, -25, -60])
        cube([90, shelf_y + 45, 120]);
}

// ---- Render della parte selezionata ----
module render_part() {
    if (part == "test") {
        intersection() {
            leggio_full();
            test_box();
        }
    } else if (part == "piano") {
        piano_simulation();
    } else if (part == "both") {
        leggio_full();
        if (show_piano_preview) {
            piano_simulation();
        }
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
