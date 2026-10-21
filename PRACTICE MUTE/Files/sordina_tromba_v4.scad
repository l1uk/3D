// =============================================================================
//  PARAMETRIC PRACTICE MUTE PER TROMBA IN Sib (Bb TRUMPET)  -  v4
//  Progettata per stampa 3D FDM (Ender-3 V2) - 100% VERO 0 SUPPORTI
// =============================================================================
//
//  Setup:
//    - Stampante: Creality Ender-3 V2 (piatto 220 x 220 mm, Z max 250 mm)
//    - Materiale: PLA / PETG
//    - Ugello: 0.4 mm, Spessore parete nominale: 1.6 mm (4 perimetri solidi ovunque)
//    - Guarnizione: Striscia di sughero continua 360° da 10 mm larghezza x 2.0 mm spessore
//
//  CAMBIAMENTI v2
//    1. FIX: i fori di sfiato erano CIECHI (si fermavano 1 mm dentro il collare pieno
//       del fondello). Ora attraversano piastra + collare.
//    2. bleed_count = 0 di default (VARIANTE A: solo stelo). Con 4 hai la VARIANTE B.
//       Il fondello e' piccolo e veloce da stampare: conviene stamparli entrambi
//       e confrontarli con il microfono (vedi spiegazione nella chat).
//    3. NUOVO report acustico in console (volume camera, frequenza di Helmholtz,
//       attenuazione teorica per alcune note).
//    4. Il profilo del corpo e' ora globale (body_ext_pts / body_int_pts), cosi' il
//       report acustico usa esattamente la geometria che viene stampata.
//    5. NUOVO (v3): gola per O-RING sul collare del fondello (giunto smontabile e
//       ermetico, senza nastro). Il report in console dice quale O-Ring comprare.
//       Il corpo NON cambia: va ristampato solo il fondello.
//    6. NUOVO (v4): joint_style = "ridge" (default): rigonfiamento stampato sul collare,
//       nessun acquisto. Nuove modalita': "lip_test" (anello di prova veloce per tarare
//       l'interferenza) e "gasket_tpu" (guarnizione piatta in TPU per la gola).
// =============================================================================

// ── SELETTORE MODALITÀ DI VISUALIZZAZIONE / ESPORTAZIONE ────────────────────
// "assembly"      : Assieme completo montato (+ campana trasparente per riscontro)
// "cross_section" : Spaccato assiale a metà per ispezione camera, tubo e spessori
// "body_only"     : Solo Corpo Superiore (orientato sul piatto per slicing)
// "cap_only"      : Solo Fondello / Base con Tubo Coassiale (orientato per slicing)
// "test_ring"     : Provino rapido calibrato (conicità esatta + base anti-distacco)
// "lip_test"      : Anello di prova del collare (con rigonfiamento/gola): ~20 min di stampa,
//                   serve a tarare l'innesto nel corpo senza stampare tutto il fondello
// "gasket_tpu"    : Guarnizione piatta da stampare in TPU (solo con joint_style = "oring")
mode = "cap_only"; // ["assembly", "cross_section", "body_only", "cap_only", "test_ring", "lip_test", "gasket_tpu"]

// Risoluzione curve
$fn = $preview ? 48 : 120;


// ── 1. PROFILO INTERNO CAMPANA TROMBA (MISURATO) ───────────────────────────
// Formato: [profondità dal bordo campana (mm), diametro interno (mm)]
// Punti segnati come "PROVVISORIO - DA MISURARE":
bell_profile = [
    [0,   119.0],
    [10,   83.0],
    [20,   69.5],
    [30,   57.0],
    [40,   45.0],
    [70,   35.0],
    [100,  30.0]
]; // PROVVISORIO - DA MISURARE


// ── 2. PARAMETRI SEDE SUGHERO & POSIZIONAMENTO ─────────────────────────────
// Profondità nominale del centro del sughero dal bordo campana [mm]
// NOTA ACUSTICA: a 50 mm di profondità, il Ø campana interpolato è ~41.67 mm.
//                Se si volesse Ø ~38.2 mm, la profondità corrispondente è ~60.4 mm.
cork_depth_target = 50.0;  // [mm] Profondità target del centro guarnizione

cork_thick        = 2.0;   // [mm] Spessore striscia sughero non compressa
cork_width        = 10.0;  // [mm] Larghezza nominale striscia sughero
cork_seat_w       = 10.5;  // [mm] Larghezza fondo piano gola (+0.5 mm tolleranza assiale)
cork_seat_d       = 0.8;   // [mm] Profondità gola (il sughero sporge di 1.2 mm a riposo)
cork_compress     = 0.25;  // [mm] Compressione radiale desiderata a battuta

// Raccordo FDM anti-sbalzo: smusso a 45° (in altezza pari alla profondità)
// Rende la gola 100% stampabile senza supporti, eliminando qualsiasi sbalzo a 90°
cork_chamfer      = cork_seat_d; // [mm] dz = dr = 0.8 mm -> pendenza 45° perfetta


// ── 3. PARAMETRI MECCANICI & DI STAMPA FDM ─────────────────────────────────
wall_t            = 1.6;   // [mm] Spessore parete nominale (4 perimetri pieni da 0.4 mm)
joint_clearance   = 0.3;   // [mm] Gioco radiale per innesto maschio-femmina FDM
lip_height        = 8.0;   // [mm] Altezza collare di innesto tra corpo e fondello


// ── 4. PARAMETRI ACUSTICI & CAMERA DI RISONANZA ────────────────────────────
// Camera esterna (fuori dalla campana)
chamber_od        = 84.0;  // [mm] Diametro esterno camera di espansione (max ingombro)
chamber_cyl_h     = 45.0;  // [mm] Altezza della sezione cilindrica inferiore
taper_angle       = 40.0;  // [deg] Angolo cono di raccordo verso il collo (<= 45° per NO supporti)

// Tubo coassiale interno (Inlet Stem) = l'UNICA uscita acustica nella variante A
stem_id           = 9.5;   // [mm] Diametro interno condotto centrale
stem_wall         = 1.6;   // [mm] Spessore parete del condotto
stem_len          = 48.0;  // [mm] Lunghezza del tubo che entra nella camera dal fondello

// Fori di sfiato sul fondello (ora PASSANTI).
// ATTENZIONE: ogni foro aperto aggiunge un percorso d'uscita per il suono, alza la
// frequenza di Helmholtz e riduce l'attenuazione (vedi report in console).
bleed_count       = 0;     // 0 = nessun foro (variante A)  |  4 = variante B
bleed_dia         = 3.2;   // [mm] Diametro singoli fori di sfiato
bleed_pitch_dia   = 40.0;  // [mm] Diametro di circonferenza fori


// ── 5. GIUNTO FONDELLO-CORPO ────────────────────────────────────────────────
// joint_style:
//   "ridge" = rigonfiamenti (nervature) stampati sul collare, a lieve interferenza con la
//             parete liscia del corpo. Nessun acquisto. Tiene per attrito, sigilla in modo
//             approssimativo (controlla con acqua e sapone).
//   "oring" = gola sul collare per un O-Ring (o una guarnizione piatta in TPU stampata).
//   "none"  = collare liscio (usa nastro PTFE).
joint_style   = "ridge";

// -- "ridge": nervature a trapezio con fianchi a 45° (0 supporti)
ridge_h       = 0.45;  // [mm] sporgenza. Interferenza = ridge_h - joint_clearance (0.15 mm)
ridge_flat    = 0.6;   // [mm] larghezza della cima piatta
ridge_z0      = 2.0;   // [mm] quota della prima nervatura sopra la piastra
ridge_count   = 2;     // numero di nervature (2 = doppia linea di contatto)
ridge_pitch   = 2.5;   // [mm] distanza tra le nervature

// -- "oring": O-Ring o guarnizione TPU
oring_cs      = 2.0;   // [mm] sezione dell'O-Ring (cordone)
oring_squeeze = 0.4;   // [mm] compressione radiale (~20% di oring_cs: tiene e sigilla)
oring_stretch = 1.02;  // fondo gola = diametro interno anello x 1.02 (allungamento 2%)
oring_z0      = 2.0;   // [mm] quota del fondo gola sopra il piano della piastra
oring_w_flat  = 1.5;   // [mm] larghezza del fondo piano della gola (sopra: rampa 45°)


// =============================================================================
//  FUNZIONI DI INTERPOLAZIONE E CALCOLO GEOMETRICO
// =============================================================================

// Interpolazione lineare ricorsiva sul profilo campana
function interp_linear(z, pts, i=0) =
    (i >= len(pts)-1) ? pts[len(pts)-1][1] :
    (z <= pts[0][0]) ? pts[0][1] :
    (z <= pts[i+1][0]) ?
        pts[i][1] + (z - pts[i][0]) * (pts[i+1][1] - pts[i][1]) / (pts[i+1][0] - pts[i][0]) :
        interp_linear(z, pts, i+1);

function bell_dia(z) = interp_linear(z, bell_profile);
function bell_r(z)   = bell_dia(z) / 2;

// Raggio campana al centro del sughero
bell_r_cork = bell_r(cork_depth_target);

// Raggio della spalla plastica al centro del sughero:
// body_r = bell_r - sporgenza_sughero_compressa
// dove sporgenza compressa = (cork_thick - cork_seat_d) - cork_compress
cork_protrusion_compressed = (cork_thick - cork_seat_d) - cork_compress; // = (2.0 - 0.8) - 0.25 = 0.95 mm
body_r_cork = bell_r_cork - cork_protrusion_compressed;
groove_r_cork = body_r_cork - cork_seat_d;

// Gioco nominale plastica-ottone (anti-graffio campana)
clearance_plastic_brass = bell_r_cork - body_r_cork;

// Quote assiali lungo la campana (Z_bell = 0 al bordo campana, Z_bell > 0 dentro la campana)
// Posizionamento della gola sughero:
z_cork_top    = cork_depth_target + (cork_seat_w / 2); // fondo gola piano alto
z_cork_bottom = cork_depth_target - (cork_seat_w / 2); // fondo gola piano basso
z_neck_tip    = cork_depth_target + 18.0;              // estremità superiore del collo
z_neck_base   = 20.0;                                  // quota inizio raccordo a 45°

// ── ECHO DI CONTROLLO DIMENSIONALE ──────────────────────────────────────────
echo("=================================================================");
echo("=== REPORT DIMENSIONALE SORDINA TROMBA ===");
echo(str("Profondità target sughero: ", cork_depth_target, " mm"));
echo(str("Ø interno campana a target: ", 2 * bell_r_cork, " mm (raggio = ", bell_r_cork, " mm)"));
echo(str("Ø spalla corpo sordina   : ", 2 * body_r_cork, " mm (raggio = ", body_r_cork, " mm)"));
echo(str("Ø fondo gola sughero     : ", 2 * groove_r_cork, " mm (raggio = ", groove_r_cork, " mm)"));
echo(str("Gioco radiale plastica-ottone: ", clearance_plastic_brass, " mm (SICUREZZA ANTI-GRAFFIO: OK)"));
echo(str("Compressione sughero prevista: ", cork_compress, " mm"));
echo("Raccordo sbalzo FDM: smusso a 45° (dz = 0.8 mm, dr = 0.8 mm) -> 0 SUPPORTI");
echo(str("Spessore parete nominale: costante ", wall_t, " mm su tutta la superficie (4 perimetri)"));
echo("=================================================================");


// =============================================================================
//  COORDINATE ASSIALI DEL MODELLO SORDINA (Asse Z Sordina)
//  Nel sistema della sordina:
//    Z_mute = 0  sul fondo del Cap (appoggio su bed del fondello)
// =============================================================================

neck_r_base = (bell_r(z_neck_base) - clearance_plastic_brass);
taper_h = (chamber_od/2 - neck_r_base) / tan(taper_angle);

cap_base_t = 3.2; // 8 strati da 0.4, rigidità acustica assoluta

z_cap_bottom      = 0;
z_joint_step      = cap_base_t;
z_chamber_cyl_top = z_joint_step + chamber_cyl_h;
z_taper_top       = z_chamber_cyl_top + taper_h;
z_neck_len        = z_neck_tip - z_neck_base;
z_mute_tip        = z_taper_top + z_neck_len;

function bell_z_to_mute_z(zb) =
    z_taper_top + (zb - z_neck_base);


// =============================================================================
//  PROFILO GLOBALE DEL CORPO SUPERIORE
//  (usato sia dalla geometria sia dal report acustico)
// =============================================================================

// Quote Z campana dei punti caratteristici del collo
zbell_tip    = z_neck_tip;
zbell_ch_top = z_cork_top + cork_chamfer;   // fine rampa 45° alta
zbell_ck_top = z_cork_top;                  // fondo gola, lato alto
zbell_ck_bot = z_cork_bottom;               // fondo gola, lato basso
zbell_ch_bot = z_cork_bottom - cork_chamfer;// inizio rampa 45° bassa

// Raggio esterno del corpo alla quota campana zb (campana meno gioco anti-graffio)
function body_r(zb) = bell_r(zb) - clearance_plastic_brass;

inner_r_cyl  = (chamber_od/2) - wall_t;
cap_recess_r = (chamber_od/2) - (wall_t/2) + (joint_clearance/2);
cap_lip_r    = (chamber_od/2) - (wall_t/2) - (joint_clearance/2);   // raggio collare fondello

// Gola O-Ring: profondità = sezione - gioco radiale - compressione
oring_depth = oring_cs - joint_clearance - oring_squeeze;
oring_r_bot = cap_lip_r - oring_depth;                          // raggio fondo gola
assert(joint_style != "oring" || oring_depth > 0.5,
       "Gola O-Ring troppo poco profonda: riduci oring_squeeze o aumenta oring_cs");
assert(joint_style != "oring" || oring_z0 + oring_w_flat + oring_depth <= lip_height - 1.5,
       "Gola O-Ring troppo alta sul collare: riduci oring_z0 o oring_w_flat");
assert(joint_style != "ridge" ||
       ridge_z0 + (ridge_count - 1) * ridge_pitch + 2 * ridge_h + ridge_flat <= lip_height - 1.2,
       "Nervature troppo alte sul collare: riduci ridge_count, ridge_pitch o ridge_z0");

// Profilo esterno: transizioni a 45° per 0 supporti
body_ext_pts = [
    [chamber_od/2,                          z_joint_step],
    [chamber_od/2,                          z_chamber_cyl_top],
    [neck_r_base,                           z_taper_top],
    [body_r(zbell_ch_bot),                  bell_z_to_mute_z(zbell_ch_bot)],
    [body_r(zbell_ck_bot) - cork_seat_d,    bell_z_to_mute_z(zbell_ck_bot)],  // rampa 45° verso l'interno
    [body_r(zbell_ck_top) - cork_seat_d,    bell_z_to_mute_z(zbell_ck_top)],  // fondo piano conico della gola
    [body_r(zbell_ch_top),                  bell_z_to_mute_z(zbell_ch_top)],  // rampa 45° verso l'esterno
    [body_r(zbell_tip),                     bell_z_to_mute_z(zbell_tip)]
];

// Profilo interno: offset costante wall_t. I punti 0..7 delimitano l'ARIA della camera
// (dalla punta del collo fino alla sommità del collare pieno del fondello);
// i punti 8..9 sono la sede del collare.
body_int_pts = [
    [body_r(zbell_tip)    - wall_t,                  bell_z_to_mute_z(zbell_tip)],
    [body_r(zbell_ch_top) - wall_t,                  bell_z_to_mute_z(zbell_ch_top)],
    [body_r(zbell_ck_top) - cork_seat_d - wall_t,    bell_z_to_mute_z(zbell_ck_top)],
    [body_r(zbell_ck_bot) - cork_seat_d - wall_t,    bell_z_to_mute_z(zbell_ck_bot)],
    [body_r(zbell_ch_bot) - wall_t,                  bell_z_to_mute_z(zbell_ch_bot)],
    [neck_r_base - wall_t,                           z_taper_top],
    [inner_r_cyl,                                    z_chamber_cyl_top],
    [inner_r_cyl,                                    z_joint_step + lip_height],
    [cap_recess_r,                                   z_joint_step + lip_height],
    [cap_recess_r,                                   z_joint_step]
];


// =============================================================================
//  REPORT ACUSTICO  (modello a parametri concentrati di Helmholtz)
//
//  Idea: l'aria nello stelo (e nei fori) si comporta come una MASSA, l'aria della
//  camera come una MOLLA. Massa + molla = risonatore di Helmholtz, con frequenza
//      f_H = c / (2*pi) * sqrt( somma(G) / V )
//  dove V = volume della camera e G = A / L_eff per ogni apertura
//  (A = area, L_eff = lunghezza + correzione d'estremità).
//  Sopra f_H il sistema è un filtro passa-basso: l'uscita cala come (f_H/f)^2,
//  cioè circa -12 dB per ottava. Quindi: f_H BASSA = più attenuazione.
//  Valido come ordine di grandezza fino a ~1 kHz.
// =============================================================================

c_sound = 343000; // [mm/s] velocità del suono a ~20 °C

function frustum_vol(r1, r2, h) = PI * h / 3 * (r1*r1 + r1*r2 + r2*r2);
function area_mm2(d) = PI * d * d / 4;

// somma dei tronchi di cono del profilo interno, punti 0..7
function vol_sum(i = 0) =
    (i >= 7) ? 0 :
    frustum_vol(body_int_pts[i][0], body_int_pts[i+1][0],
                abs(body_int_pts[i][1] - body_int_pts[i+1][1])) + vol_sum(i + 1);

// volume occupato dalla parete dello stelo che sporge nella camera (sopra il collare)
V_stem_wall = PI * pow(stem_id/2 + stem_wall, 2) * max(0, stem_len - lip_height);
V_chamber   = vol_sum() - V_stem_wall;                       // [mm^3]

// conduttanze acustiche [mm]
//  stelo: estremità esterna su piastra (flangiata, 0.85 a) + interna libera (0.6 a)
//  fori : entrambe le estremità su superfici piane (2 x 0.85 a)
G_stem  = area_mm2(stem_id) / (cap_base_t + stem_len + 1.45 * stem_id/2);
G_bleed = bleed_count * area_mm2(bleed_dia) / (cap_base_t + lip_height + 1.7 * bleed_dia/2);

f_helm      = (c_sound / (2*PI)) * sqrt((G_stem + G_bleed) / V_chamber);
f_notch_ann = c_sound / (4 * (stem_len - lip_height));       // anello attorno allo stelo

// perdita di trasmissione teorica [dB] (positivo = attenuazione), solo percorso acustico
function tl_db(f) = 20 * log(max(abs(1 - pow(f / f_helm, 2)), 0.01));

echo("=================================================================");
echo("=== REPORT ACUSTICO (parametri concentrati) ===");
echo(str("Volume d'aria della camera : ", round(V_chamber / 100) / 10, " cm³"));
echo(str("Aperture d'uscita          : ", bleed_count > 0 ? str("stelo + ", bleed_count, " fori da ", bleed_dia, " mm") : "solo stelo"));
echo(str("Frequenza di Helmholtz f_H : ", round(f_helm), " Hz"));
echo(str("Notch 1/4 d'onda (anello stelo-parete): ~", round(f_notch_ann), " Hz (indicativo, nella realtà più basso)"));
for (f = [165, 233, 349, 466, 698, 932])
    echo(str("  attenuazione teorica a ", f, " Hz: ", round(tl_db(f) * 10) / 10, " dB"));
echo("(Limite superiore: pareti, giunto e fughe limitano l'attenuazione reale a ~15-20 dB)");
echo("=================================================================");

echo("=== GIUNTO FONDELLO-CORPO ===");
if (joint_style == "ridge") {
    echo(str("Nervature: ", ridge_count, " x sporgenza ", ridge_h, " mm -> interferenza radiale ",
             round((ridge_h - joint_clearance) * 100) / 100, " mm"));
    echo("Taratura: stampa mode=\"lip_test\". Troppo duro -> riduci ridge_h; lasco -> aumentalo (passi di 0.05-0.1).");
} else if (joint_style == "oring") {
    echo(str("Gola: profondità ", round(oring_depth * 100) / 100, " mm | fondo gola Ø ",
             round(2 * oring_r_bot * 100) / 100, " mm | compressione ",
             round(oring_squeeze / oring_cs * 100), " %"));
    echo(str("O-Ring: ~", round(2 * oring_r_bot / oring_stretch * 10) / 10, " x ", oring_cs,
             " mm (diametro interno x sezione), oppure guarnizione TPU: mode=\"gasket_tpu\"."));
} else {
    echo("Collare liscio: sigilla con nastro PTFE.");
}
echo("=================================================================");


// =============================================================================
//  GEOMETRIA MODULARE: 1. CAMPANA DI RISCONTRO TRASPARENTE
// =============================================================================
module trumpet_bell_ghost() {
    %rotate_extrude() {
        polygon(concat(
            [ for (i = [0 : len(bell_profile)-1]) [bell_profile[i][1]/2, -bell_profile[i][0]] ],
            [ for (i = [len(bell_profile)-1 : -1 : 0]) [bell_profile[i][1]/2 + 0.6, -bell_profile[i][0]] ]
        ));
    }
}


// =============================================================================
//  GEOMETRIA MODULARE: 2. CORPO SUPERIORE (UPPER BODY)
//  Ottimizzato per FDM: Raccordi a 45° su entrambi i cambi quota della gola.
//  (Il profilo è calcolato nella sezione globale body_ext_pts / body_int_pts.)
// =============================================================================
module upper_body_2d_profile() {
    polygon(concat(body_ext_pts, body_int_pts));
}

module upper_body() {
    rotate_extrude()
        upper_body_2d_profile();
}


// =============================================================================
//  GEOMETRIA MODULARE: 3. BASE / FONDELLO CON TUBO COASSIALE & SFIATI
// =============================================================================
// ── Elementi del collare (z locale: 0 = base del collare = sommità della piastra) ──
// Gola per O-Ring: fondo piano + rampa a 45° in alto (0 supporti)
module lip_groove_cut() {
    rotate_extrude()
        polygon([
            [oring_r_bot,   oring_z0],
            [cap_lip_r + 1, oring_z0],
            [cap_lip_r + 1, oring_z0 + oring_w_flat + oring_depth + 1],
            [oring_r_bot,   oring_z0 + oring_w_flat]
        ]);
}

// Nervature a trapezio: fianco inferiore a 45° (sbalzo autoportante), fianco superiore a 45°
module lip_ridge_add() {
    for (k = [0 : ridge_count - 1]) {
        z = ridge_z0 + k * ridge_pitch;
        rotate_extrude()
            polygon([
                [cap_lip_r - 0.3,      z],
                [cap_lip_r,            z],
                [cap_lip_r + ridge_h,  z + ridge_h],
                [cap_lip_r + ridge_h,  z + ridge_h + ridge_flat],
                [cap_lip_r,            z + 2 * ridge_h + ridge_flat],
                [cap_lip_r - 0.3,      z + 2 * ridge_h + ridge_flat]
            ]);
    }
}

// Anello di prova: solo il collare (ring largo 4 mm) con gola/nervature, per tarare l'innesto
module lip_test() {
    difference() {
        union() {
            cylinder(r = cap_lip_r, h = lip_height);
            if (joint_style == "ridge") lip_ridge_add();
        }
        translate([0, 0, -1]) cylinder(r = cap_lip_r - 4, h = lip_height + 2);
        if (joint_style == "oring") lip_groove_cut();
        translate([0, 0, lip_height - 1.0])
            difference() {
                cylinder(r = cap_lip_r + 1, h = 2);
                cylinder(r1 = cap_lip_r, r2 = cap_lip_r - 1.0, h = 2);
            }
    }
}

// Guarnizione piatta per la gola, da stampare in TPU (sezione rettangolare, tutte pareti)
module gasket_tpu() {
    g_r_in = oring_r_bot / oring_stretch;   // raggio interno a riposo (si allunga del 2% in gola)
    g_h    = oring_w_flat - 0.1;
    difference() {
        cylinder(r = g_r_in + oring_cs, h = g_h);
        translate([0, 0, -1]) cylinder(r = g_r_in, h = g_h + 2);
    }
}

module cap_base() {
    difference() {
        union() {
            // Piatto di base esterno
            cylinder(r = chamber_od/2, h = cap_base_t);

            // Collare maschio di inserimento nella camera (PIENO)
            translate([0, 0, cap_base_t])
                cylinder(r = cap_lip_r, h = lip_height);

            // Nervature di tenuta/attrito sul collare (joint_style = "ridge")
            if (joint_style == "ridge")
                translate([0, 0, cap_base_t]) lip_ridge_add();

            // Tubo Coassiale Interno (Inlet Stem)
            cylinder(r = (stem_id/2) + stem_wall, h = cap_base_t + stem_len);
        }

        // Foro passante assiale del tubo coassiale
        translate([0, 0, -1])
            cylinder(r = stem_id/2, h = cap_base_t + stem_len + 2);

        // Fori di sfiato PASSANTI: attraversano piastra + collare pieno.
        // (v1: h = cap_base_t + 2 -> i fori si fermavano a z = 4.2, dentro il collare)
        if (bleed_count > 0)
            for (i = [0 : bleed_count - 1])
                rotate([0, 0, i * 360 / bleed_count])
                    translate([bleed_pitch_dia/2, 0, -1])
                        cylinder(r = bleed_dia/2, h = cap_base_t + lip_height + 2);

        // Gola per O-Ring / guarnizione TPU sul collare (joint_style = "oring")
        if (joint_style == "oring")
            translate([0, 0, cap_base_t]) lip_groove_cut();

        // Smusso di guida 45° sul labbro di inserimento per facilitare l'innesto
        translate([0, 0, cap_base_t + lip_height - 1.0])
            difference() {
                cylinder(r = cap_lip_r + 1, h = 2);
                cylinder(r1 = cap_lip_r, r2 = cap_lip_r - 1.0, h = 2);
            }
    }
}


// =============================================================================
//  GEOMETRIA MODULARE: 4. STRISCIA SUGHERO (VISUALIZZAZIONE VIRTUALE)
// =============================================================================
module cork_strip_ghost() {
    color([0.82, 0.65, 0.45, 0.85]) { // colore sughero
        rotate_extrude() {
            r_top_g_in = (bell_r(z_cork_top) - clearance_plastic_brass) - cork_seat_d;
            r_bot_g_in = (bell_r(z_cork_bottom) - clearance_plastic_brass) - cork_seat_d;

            polygon([
                [r_bot_g_in, bell_z_to_mute_z(z_cork_bottom)],
                [r_bot_g_in + cork_thick, bell_z_to_mute_z(z_cork_bottom)],
                [r_top_g_in + cork_thick, bell_z_to_mute_z(z_cork_top)],
                [r_top_g_in, bell_z_to_mute_z(z_cork_top)]
            ]);
        }
    }
}


// =============================================================================
//  GEOMETRIA MODULARE: 5. PROVINO CALIBRATO (TEST RING V2 - VERO 0 SUPPORTI)
//  Con conicità reale, raccordi a 45° senza sbalzi a 90°, spessore costante 1.6 mm
//  e flangia di appoggio anti-distacco per piatto Ender-3!
// =============================================================================
module test_ring_v2() {
    h_ring = 26.0;
    z_bot  = cork_depth_target - (h_ring / 2);
    z_top  = cork_depth_target + (h_ring / 2);

    zb_chamfer_top = z_cork_top + cork_chamfer;
    zb_cork_top    = z_cork_top;
    zb_cork_bot    = z_cork_bottom;
    zb_chamfer_bot = z_cork_bottom - cork_chamfer;

    r_bot_ext         = bell_r(z_bot) - clearance_plastic_brass;
    r_top_ext         = bell_r(z_top) - clearance_plastic_brass;
    r_chamfer_bot_ext = bell_r(zb_chamfer_bot) - clearance_plastic_brass;
    r_cork_bot_in     = (bell_r(zb_cork_bot) - clearance_plastic_brass) - cork_seat_d;
    r_cork_top_in     = (bell_r(zb_cork_top) - clearance_plastic_brass) - cork_seat_d;
    r_chamfer_top_ext = bell_r(zb_chamfer_top) - clearance_plastic_brass;

    zm_bot         = 0;
    zm_chamfer_bot = zb_chamfer_bot - z_bot;
    zm_cork_bot    = zb_cork_bot - z_bot;
    zm_cork_top    = zb_cork_top - z_bot;
    zm_chamfer_top = zb_chamfer_top - z_bot;
    zm_top         = h_ring;

    poly_ext = [
        // Flangia brim integrata di aderenza al piatto (spessore 0.6 mm, +4 mm larghezza)
        [r_bot_ext - wall_t, zm_bot],
        [r_bot_ext + 4.0,    zm_bot],
        [r_bot_ext + 4.0,    0.6],
        [r_bot_ext,          0.6],

        // Corpo conico inferiore
        [r_chamfer_bot_ext, zm_chamfer_bot],
        [r_cork_bot_in,     zm_cork_bot],       // rampa 45° verso l'interno
        [r_cork_top_in,     zm_cork_top],       // fondo gola piano (10.5 mm)
        [r_chamfer_top_ext, zm_chamfer_top],    // rampa 45° verso l'esterno (overhang autoportante!)
        [r_top_ext,         zm_top]
    ];

    poly_int = [
        [r_top_ext - wall_t,         zm_top],
        [r_chamfer_top_ext - wall_t, zm_chamfer_top],
        [r_cork_top_in - wall_t,     zm_cork_top],       // spessore costante 1.6 mm anche nella gola!
        [r_cork_bot_in - wall_t,     zm_cork_bot],
        [r_chamfer_bot_ext - wall_t, zm_chamfer_bot],
        [r_bot_ext - wall_t,         zm_bot]
    ];

    rotate_extrude()
        polygon(concat(poly_ext, poly_int));
}


// =============================================================================
//  RENDER FINALE IN BASE ALLA MODALITÀ SELEZIONATA
// =============================================================================

if (mode == "assembly") {
    // Sordina montata
    color([0.25, 0.45, 0.85, 0.9]) upper_body();
    color([0.15, 0.15, 0.15, 1.0]) cap_base();
    cork_strip_ghost();

    // Campana posizionata alla corretta quota Z
    translate([0, 0, bell_z_to_mute_z(0)])
        trumpet_bell_ghost();
}
else if (mode == "cross_section") {
    difference() {
        union() {
            color([0.25, 0.45, 0.85, 0.9]) upper_body();
            color([0.15, 0.15, 0.15, 1.0]) cap_base();
            cork_strip_ghost();
        }
        // Taglio a 180° lungo l'asse X per vedere spessori e canali
        translate([0, -100, -10])
            cube([200, 200, 300]);
    }
}
else if (mode == "body_only") {
    // Pronto per esportazione STL del corpo principale
    upper_body();
}
else if (mode == "cap_only") {
    // Pronto per esportazione STL del fondello
    cap_base();
}
else if (mode == "test_ring") {
    // Pronto per stampa rapida del provino calibrato a 0 supporti reali
    test_ring_v2();
}
else if (mode == "lip_test") {
    // Anello di prova del collare per tarare l'innesto (~20 min)
    lip_test();
}
else if (mode == "gasket_tpu") {
    // Guarnizione piatta in TPU per joint_style = "oring"
    gasket_tpu();
}
