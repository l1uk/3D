// =============================================================================
//  PARAMETRIC PRACTICE MUTE PER TROMBA IN Sib (Bb TRUMPET)  -  v2 + VARIANTI FONDELLO
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
// =============================================================================

//  VARIANTI FONDELLO (questo file)
//    Stessa geometria della v2 che hai gia' stampato (il CORPO non cambia, il giunto e' identico).
//    Cambia solo l'uscita del suono, scegliendo cap_variant piu' sotto: "A", "B" o "C".
//    Stampa solo il fondello:  mode = "cap_only".
//
//    FONDELLO FACILE DA SMONTARE (nuovo)
//    Problema della v2: collare liscio a stretto contatto + piastra a filo del corpo
//    -> si chiude bene ma non si riesce piu' ad aprire. Rimedi (tutti SOLO sul fondello):
//      1. lip_trim      : collare un po' piu' stretto (meno attrito su tutta la superficie)
//      2. due nervature a lieve interferenza (ridge_interf): tengono in modo CONTROLLATO
//      3. cap_flange_od : piastra piu' larga del corpo -> bordo da afferrare / fare leva
//    Per tarare l'innesto senza stampare il fondello intero: mode = "lip_test" (anello di
//    prova, ~20 min). Il corpo che hai gia' stampato resta valido.
// =============================================================================

// ── SELETTORE MODALITÀ DI VISUALIZZAZIONE / ESPORTAZIONE ────────────────────
// "assembly"      : Assieme completo montato (+ campana trasparente per riscontro)
// "cross_section" : Spaccato assiale a metà per ispezione camera, tubo e spessori
// "body_only"     : Solo Corpo Superiore (orientato sul piatto per slicing)
// "cap_only"      : Solo Fondello / Base con Tubo Coassiale (orientato per slicing)
// "test_ring"     : Provino rapido calibrato (conicità esatta + base anti-distacco)
// "lip_test"      : Anello di prova del collare (con nervature) per tarare l'innesto: ~20 min
// "fit_test"      : Maschio + femmina affiancati per tarare l'accoppiamento prima del corpo: ~30 min
// "fit_test_female": Solo la femmina (sede del corpo): ci provi il collare del fondello gia' stampato: ~15 min
// "cartuccia"     : Vano imbottitura sospeso (pezzo separato, si infila sullo stelo)
// "cartuccia_lid" : Coperchio della cartuccia
mode = "body_only"; // ["assembly", "cross_section", "body_only", "cap_only", "test_ring", "lip_test", "cartuccia", "cartuccia_lid"]

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
joint_clearance   = 0.4;   // [mm] Gioco radiale innesto maschio-femmina FDM (0.3 -> non entrava: l'ABS rende ~0.3 mm in piu')
lip_height        = 8.0;   // [mm] Altezza collare di innesto tra corpo e fondello

// -- Giunto facile da smontare (solo fondello; il corpo non cambia)
lip_trim          = 0.2;   // [mm] riduzione di raggio del collare (0 = come la v2)
// -- Restringimento della SOLA sede del corpo (femmina), per far mordere le nervature del
//    fondello GIA' stampato. Riguarda solo corpo e fit_test_female; il fondello non cambia.
//    0 = sede standard. 0.3 = sede stretta (imbocco lieve + presa sulle nervature).
recess_tight      = 0.0;   // [mm] di raggio sottratti alla sede del corpo (0.3 e 0.15 ancora stretti: ABS ritira piu' del previsto)
ridge_interf      = 0.05;  // [mm] interferenza radiale delle nervature: 0 = nessuna presa, 0.15 = molto dura (0.08 era un po' dura da aprire)
ridge_count       = 2;     // numero di nervature
ridge_pitch       = 2.5;   // [mm] distanza tra le nervature
ridge_z0          = 2.0;   // [mm] quota della prima nervatura sopra la piastra
ridge_flat        = 0.6;   // [mm] larghezza della cima piatta
cap_flange_od     = 92.0;  // [mm] diametro della piastra del fondello (il corpo e' 84): bordo da afferrare

// -- Cestello per l'imbottitura (stampato sul collare, attorno allo stelo): niente collant
//    Parete forata a rombi (sono 0 supporti), bordo di ritenzione inclinato a 45° in cima.
//    L'imbottitura si infila dall'alto, nell'anello tra stelo e parete.
pad_cage          = false;   // (disattivato di default: vedi la cartuccia qui sotto)
pad_r_out         = 38.0;  // [mm] raggio esterno (la camera ha raggio 40.4: restano ~2 mm)
pad_wall          = 1.2;   // [mm] spessore parete (3 perimetri da 0.4)
pad_h             = 28.0;  // [mm] altezza sopra il collare (lascia libero lo sbocco dello stelo)
pad_lip           = 4.0;   // [mm] sporgenza del bordo di ritenzione verso l'interno (45°)
pad_hole          = 8.0;   // [mm] diagonale dei fori a rombo

// -- CARTUCCIA IMBOTTITURA: vano sospeso nella camera, pezzo SEPARATO (nessuna modifica a corpo e fondello)
//    Si infila sullo stelo (che passa nel manicotto centrale), sta centrata nella camera con aria tutt'attorno.
//    Si apre dall'alto, si riempie IN UNA VOLTA con l'imbottitura (anche un blocco unico) e si chiude col
//    coperchio. Si sfila per asciugare/pulire. Modalita': "cartuccia" e "cartuccia_lid".
cart_r_out        = 37.6;  // [mm] raggio esterno (camera 40.4: restano ~2.8 mm di aria)
cart_h            = 26.0;  // [mm] altezza del vano (+1.2 del coperchio): lascia libero lo sbocco dello stelo
cart_wall         = 1.2;   // [mm] spessore pareti
cart_fit          = 0.25;  // [mm] gioco manicotto-stelo (0.15-0.2 = a frizione, 0.35 = libero)
cart_hole         = 8.0;   // [mm] diagonale dei fori a rombo nella parete
cart_lid_h        = 6.0;   // [mm] altezza del bordo del coperchio


// ── 4. PARAMETRI ACUSTICI & CAMERA DI RISONANZA ────────────────────────────
// Camera esterna (fuori dalla campana)
chamber_od        = 84.0;  // [mm] Diametro esterno camera di espansione (max ingombro)
chamber_cyl_h     = 45.0;  // [mm] Altezza della sezione cilindrica inferiore
taper_angle       = 40.0;  // [deg] Angolo cono di raccordo verso il collo (<= 45° per NO supporti)

// VARIANTE DEL FONDELLO: cambia SOLO l'uscita del suono (stelo). Valori teorici del modello:
//   "A" = stelo Ø 9.5 x 48 mm  (quella gia' stampata)  f_H ~110 Hz  massima attenuazione
//   "B" = stelo Ø 12  x 48 mm  (uscita piu' ampia)     f_H ~138 Hz  circa 4-5 dB in meno
//   "C" = stelo Ø 12  x 70 mm  (ampio ma piu' lungo)   f_H ~119 Hz (quasi come A), area 1.6x: separa l'effetto
//                               dell'AREA da quello della MASSA acustica (ma sposta il notch
//                               dell'anello attorno allo stelo verso ~1.2 kHz: vedi report)
cap_variant       = "B";   // ["A", "B", "C"]
assert(cap_variant == "A" || cap_variant == "B" || cap_variant == "C", "cap_variant deve essere A, B o C");

// Tubo coassiale interno (Inlet Stem) = l'UNICA uscita acustica
stem_id           = (cap_variant == "A") ? 9.5 : 12.0;   // [mm] Diametro interno condotto centrale
stem_wall         = 2.0;   // [mm] Spessore parete del condotto (5 perimetri da 0.4). 1.6 si e' spezzato
stem_fillet       = 5.0;   // [mm] raccordo conico alla base dello stelo (45°, 0 supporti): evita la rottura alla base
stem_len          = (cap_variant == "C") ? 70.0 : 48.0;  // [mm] Lunghezza del tubo che entra nella camera dal fondello

// Fori di sfiato sul fondello (ora PASSANTI).
// ATTENZIONE: ogni foro aperto aggiunge un percorso d'uscita per il suono, alza la
// frequenza di Helmholtz e riduce l'attenuazione (vedi report in console).
bleed_count       = 0;     // 0 = nessun foro (variante A)  |  4 = variante B
bleed_dia         = 3.2;   // [mm] Diametro singoli fori di sfiato
bleed_pitch_dia   = 40.0;  // [mm] Diametro di circonferenza fori


// ── valori derivati del giunto (dopo chamber_od: OpenSCAD valuta le variabili in ordine) ──
lip_r_eff = (chamber_od/2) - (wall_t/2) - (joint_clearance/2) - lip_trim;   // raggio del collare
ridge_h   = joint_clearance + lip_trim + ridge_interf;                      // sporgenza nervature
assert(ridge_z0 + (ridge_count - 1) * ridge_pitch + 2 * ridge_h + ridge_flat <= lip_height - 1.2,
       "Nervature troppo alte sul collare: riduci ridge_count, ridge_pitch o ridge_z0");
assert(!pad_cage || pad_h <= (stem_len - lip_height) - 8,
       "Cestello troppo alto: deve restare libero lo sbocco dello stelo (riduci pad_h)");
assert(!pad_cage || pad_r_out <= chamber_od/2 - wall_t - 1.5,
       "Cestello troppo largo per la camera: riduci pad_r_out");
assert(cart_h + cart_wall <= (stem_len - lip_height) - 10,
       "Cartuccia troppo alta: deve restare libero lo sbocco dello stelo (riduci cart_h)");
assert(cart_r_out <= chamber_od/2 - wall_t - 1.5, "Cartuccia troppo larga per la camera: riduci cart_r_out");

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
cap_recess_r = (chamber_od/2) - (wall_t/2) + (joint_clearance/2) - recess_tight;

// FIX parete sede fondello: nei primi lip_height mm la sede interna e' a r = cap_recess_r
// (41.4) e l'esterno a chamber_od/2 (42.0) -> parete di soli 0.6 mm (1.5 estrusioni), contro
// i 1.6 mm dichiarati. Sede, chamber_od e camera interna sono vincolati dal giunto/acustica,
// quindi si ispessisce SOLO l'esterno con un anello di rinforzo di seat_boost mm, che rientra
// a 45° (faccia rivolta verso l'alto: nessun sbalzo) fino al diametro nominale.
// seat_boost = 1.0 -> parete 1.6 mm = wall_t.   seat_boost = 0 -> geometria originale.
seat_boost = cap_recess_r + wall_t - chamber_od/2;   // = 1.0 mm: porta la parete della sede a wall_t
assert(seat_boost >= 0, "seat_boost negativo");
assert(z_joint_step + lip_height + seat_boost < z_chamber_cyl_top, "rinforzo sede troppo alto");

// Profilo esterno: transizioni a 45° per 0 supporti
body_ext_pts = concat(
    (seat_boost > 0) ? [
        [chamber_od/2 + seat_boost,             z_joint_step],
        [chamber_od/2 + seat_boost,             z_joint_step + lip_height],
        [chamber_od/2,                          z_joint_step + lip_height + seat_boost]   // rientro 45°
    ] : [
        [chamber_od/2,                          z_joint_step]
    ],
  [
    [chamber_od/2,                          z_chamber_cyl_top],
    [neck_r_base,                           z_taper_top],
    [body_r(zbell_ch_bot),                  bell_z_to_mute_z(zbell_ch_bot)],
    [body_r(zbell_ck_bot) - cork_seat_d,    bell_z_to_mute_z(zbell_ck_bot)],  // rampa 45° verso l'interno
    [body_r(zbell_ck_top) - cork_seat_d,    bell_z_to_mute_z(zbell_ck_top)],  // fondo piano conico della gola
    [body_r(zbell_ch_top),                  bell_z_to_mute_z(zbell_ch_top)],  // rampa 45° verso l'esterno
    [body_r(zbell_tip),                     bell_z_to_mute_z(zbell_tip)]
  ]
);

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
echo(str("Giunto: collare Ø ", round(2 * lip_r_eff * 100) / 100, " mm (gioco radiale ", joint_clearance + lip_trim,
         " mm), ", ridge_count, " nervature con interferenza ", ridge_interf, " mm, flangia Ø ", cap_flange_od, " mm"));
if (pad_cage) {
    pad_vol = PI * (pow(pad_r_out - pad_wall, 2) - pow(stem_id/2 + stem_wall, 2)) * pad_h / 1000;   // cm³ (stima)
    echo(str("Cestello imbottitura: volume utile ~", round(pad_vol), " cm³ -> circa ", round(pad_vol * 0.02 * 10) / 10,
             " g a riempimento morbido (20 g/L), ", round(pad_vol * 0.04 * 10) / 10, " g sodo (40 g/L), ",
             round(pad_vol * 0.06 * 10) / 10, " g molto sodo (60 g/L)"));
}
echo(str("Cartuccia imbottitura: volume utile ~",
         round(PI * (pow(cart_r_out - cart_wall, 2) - pow(stem_id/2 + stem_wall + cart_fit + cart_wall, 2)) * cart_h / 1000), " cm³",
         " -> ~2-3 g (morbido), ~5 g (sodo), ~7 g (molto sodo); altezza totale con coperchio ", cart_h + cart_wall, " mm"));
echo(str("Variante fondello          : ", cap_variant, "  (stelo Ø ", stem_id, " x ", stem_len, " mm)"));
echo(str("Aperture d'uscita          : ", bleed_count > 0 ? str("stelo + ", bleed_count, " fori da ", bleed_dia, " mm") : "solo stelo"));
echo(str("Frequenza di Helmholtz f_H : ", round(f_helm), " Hz"));
echo(str("Notch 1/4 d'onda (anello stelo-parete): ~", round(f_notch_ann), " Hz (indicativo, nella realtà più basso)"));
for (f = [165, 233, 349, 466, 698, 932])
    echo(str("  attenuazione teorica a ", f, " Hz: ", round(tl_db(f) * 10) / 10, " dB"));
echo("(Limite superiore: pareti, giunto e fughe limitano l'attenuazione reale a ~15-20 dB)");
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
// ── Cartuccia imbottitura (pezzo separato) ─────────────────────────────────
// z locale 0 = sommita' del collare del fondello (la cartuccia appoggia li' attorno allo stelo)
module cartuccia() {
    r_si = stem_id/2 + stem_wall + cart_fit;      // foro del manicotto
    r_so = r_si + cart_wall;
    r_o  = cart_r_out;  r_i = r_o - cart_wall;
    r_m  = (r_so + r_i) / 2;
    nrow = floor((cart_h - cart_wall - 2) / (cart_hole + 2));
    stem_or = stem_id/2 + stem_wall;                       // raggio esterno dello stelo
    rc0     = stem_or + stem_fillet + 0.35 + 1.8;          // raggio del colletto conico alla base
    zc      = rc0 - r_so;                                  // altezza a cui il colletto si fonde col manicotto
    difference() {
        cylinder(r = r_o, h = cart_h);
        // vano anulare tra manicotto e parete (aperto in alto); il colletto conico resta pieno
        translate([0, 0, cart_wall])
            difference() {
                cylinder(r = r_i, h = cart_h);
                translate([0, 0, -1]) cylinder(r = r_so, h = cart_h + 2);
                translate([0, 0, -cart_wall]) rotate_extrude()
                    polygon([[0, -0.01], [rc0, -0.01], [r_so, zc], [0, zc]]);
            }
        // foro per lo stelo + cavita' conica che accoglie il raccordo (gioco 0.35 mm)
        translate([0, 0, -1]) cylinder(r = r_si, h = cart_h + 2);
        rotate_extrude()
            polygon([[0, -1], [stem_or + stem_fillet + 0.35 + 1, -1], [stem_or + 0.35, stem_fillet], [0, stem_fillet]]);
        // fori del fondo (cerchi: il fondo si stampa sul piatto)
        for (a = [0 : 11]) {
            rotate([0, 0, a * 30])        translate([r_m,     0, -1]) cylinder(d = 7, h = cart_wall + 2, $fn = 24);
            rotate([0, 0, a * 30 + 15])   translate([r_m + 8, 0, -1]) cylinder(d = 7, h = cart_wall + 2, $fn = 24);
        }
        // fori a rombo sulla parete esterna (fianchi a 45°: 0 supporti), file sfalsate
        for (j = [0 : nrow - 1])
            for (i = [0 : 23])
                rotate([0, 0, (i + (j % 2) * 0.5) * 360 / 24])
                    translate([r_i - 2, 0, cart_wall + 1 + cart_hole/2 + j * (cart_hole + 2)])
                        rotate([0, 90, 0]) cylinder(r = cart_hole/2, h = cart_wall + 4, $fn = 4);
    }
}

// Coperchio: si stampa a piastra in basso (bordo in su); si monta capovolto sul bordo della cartuccia
module cartuccia_lid() {
    r_si = stem_id/2 + stem_wall + cart_fit + 0.6;   // gioco largo attorno allo stelo
    r_o  = cart_r_out;
    rim_in  = r_o + 0.2;
    rim_out = rim_in + cart_wall;
    r_so = stem_id/2 + stem_wall + cart_fit + cart_wall;
    r_i  = r_o - cart_wall;
    r_m  = (r_so + r_i) / 2;
    difference() {
        union() {
            cylinder(r = rim_out, h = cart_wall);
            difference() {
                cylinder(r = rim_out, h = cart_lid_h);
                translate([0, 0, -1]) cylinder(r = rim_in, h = cart_lid_h + 2);
            }
            // 3 tacche a frizione sul bordo interno (interferenza ~0.1 mm con la parete della cartuccia)
            for (a = [0, 120, 240])
                rotate([0, 0, a]) translate([rim_in - 0.3, -1.5, 0]) cube([0.31, 3, cart_lid_h]);
        }
        translate([0, 0, -1]) cylinder(r = r_si, h = cart_lid_h + 2);
        for (a = [0 : 11]) {
            rotate([0, 0, a * 30])        translate([r_m,     0, -1]) cylinder(d = 7, h = cart_wall + 2, $fn = 24);
            rotate([0, 0, a * 30 + 15])   translate([r_m + 8, 0, -1]) cylinder(d = 7, h = cart_wall + 2, $fn = 24);
        }
    }
}

// Cestello dell'imbottitura. z locale 0 = sommita' del collare (si fonde 0.3 mm nel collare)
module pad_cage() {
    r_in  = pad_r_out - pad_wall;
    nrow  = floor((pad_h - pad_lip - 1) / (pad_hole + 2));
    nang  = 24;
    difference() {
        rotate_extrude()
            polygon([
                [r_in,           -0.3],
                [pad_r_out,      -0.3],
                [pad_r_out,      pad_h],
                [r_in - pad_lip, pad_h],      // bordo di ritenzione: sotto inclinato a 45°
                [r_in,           pad_h - pad_lip]
            ]);
        // fori a rombo (vertici in alto/in basso -> fianchi a 45°, autoportanti), file sfalsate
        for (j = [0 : nrow - 1])
            for (i = [0 : nang - 1])
                rotate([0, 0, (i + (j % 2) * 0.5) * 360 / nang])
                    translate([r_in - 2, 0, 1 + pad_hole/2 + j * (pad_hole + 2)])
                        rotate([0, 90, 0])
                            cylinder(r = pad_hole/2, h = pad_wall + 4, $fn = 4);
    }
}

// Nervature di attrito sul collare: trapezio con fianchi a 45° (0 supporti). r0 = raggio del collare
module lip_ridges(r0) {
    if (ridge_count > 0) for (k = [0 : ridge_count - 1]) {
        z = ridge_z0 + k * ridge_pitch;
        rotate_extrude()
            polygon([
                [r0 - 0.3,       z],
                [r0,             z],
                [r0 + ridge_h,   z + ridge_h],
                [r0 + ridge_h,   z + ridge_h + ridge_flat],
                [r0,             z + 2 * ridge_h + ridge_flat],
                [r0 - 0.3,       z + 2 * ridge_h + ridge_flat]
            ]);
    }
}

// Anello di prova: solo il collare (anello largo 4 mm) con le stesse nervature del fondello
module lip_test() {
    difference() {
        union() {
            cylinder(r = lip_r_eff, h = lip_height);
            lip_ridges(lip_r_eff);
        }
        translate([0, 0, -1]) cylinder(r = lip_r_eff - 4, h = lip_height + 2);
        translate([0, 0, lip_height - 1.0])
            difference() {
                cylinder(r = lip_r_eff + 1, h = 2);
                cylinder(r1 = lip_r_eff, r2 = lip_r_eff - 1.0, h = 2);
            }
    }
}

// FEMMINA di prova: solo l'anello che riproduce la SEDE del corpo (foro = cap_recess_r).
// Serve se hai GIA' il fondello stampato: ci provi dentro il collare vero del fondello.
//   entra con lieve pressione e tiene -> il corpo nuovo andra' bene
//   troppo duro  -> aumenta joint_clearance | lasco -> riducilo (o alza ridge_interf)
module fit_test_female() {
    h = lip_height + 2;
    difference() {
        cylinder(r = cap_recess_r + wall_t + 1.5, h = h);
        translate([0, 0, -1]) cylinder(r = cap_recess_r, h = h + 2);
    }
}

// FIT TEST: maschio (collare+nervature, come il fondello) + femmina (sede, come il corpo),
// stampati affiancati. Serve a tarare l'accoppiamento reale in ABS in ~30 min, PRIMA di
// stampare il corpo intero. Si prova a infilare il maschio nella femmina:
//   troppo duro -> aumenta joint_clearance (p.es. 0.4) o riduci ridge_interf
//   lasco       -> riduci joint_clearance o aumenta ridge_interf
module fit_test() {
    h = lip_height + 2;
    // MASCHIO (come il collare del fondello)
    translate([-lip_r_eff - 3, 0, 0])
        difference() {
            union() {
                cylinder(r = lip_r_eff, h = h);
                lip_ridges(lip_r_eff);
            }
            translate([0, 0, -1]) cylinder(r = lip_r_eff - 4, h = h + 2);
        }
    // FEMMINA (come la sede del corpo): anello con foro interno = cap_recess_r
    translate([ cap_recess_r + 3 + 3, 0, 0])
        fit_test_female();
}

module cap_base() {
    cap_lip_r = lip_r_eff;   // collare ridotto di lip_trim

    difference() {
        union() {
            // Piatto di base esterno = FLANGIA piu' larga del corpo (presa per smontare)
            cylinder(r = cap_flange_od/2, h = cap_base_t);

            // Collare maschio di inserimento nella camera (PIENO)
            translate([0, 0, cap_base_t])
                cylinder(r = cap_lip_r, h = lip_height);

            // Nervature di attrito sul collare (interferenza controllata)
            translate([0, 0, cap_base_t]) lip_ridges(cap_lip_r);

            // Raccordo conico alla base dello stelo (rinforza il punto dove si e' spezzato)
            translate([0, 0, cap_base_t + lip_height])
                rotate_extrude()
                    polygon([
                        [stem_id/2 + stem_wall - 0.5, -0.3],
                        [stem_id/2 + stem_wall + stem_fillet, -0.3],
                        [stem_id/2 + stem_wall + stem_fillet, 0],
                        [stem_id/2 + stem_wall, stem_fillet],
                        [stem_id/2 + stem_wall - 0.5, stem_fillet]
                    ]);

            // Cestello per l'imbottitura attorno allo stelo
            if (pad_cage)
                translate([0, 0, cap_base_t + lip_height]) pad_cage();

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
else if (mode == "fit_test") {
    // Maschio + femmina affiancati: tara l'accoppiamento reale prima di stampare il corpo (~30 min)
    fit_test();
}
else if (mode == "fit_test_female") {
    // Solo la femmina (sede del corpo): ci provi dentro il collare del fondello che hai gia' (~15 min)
    fit_test_female();
}
else if (mode == "cartuccia") { cartuccia(); }
else if (mode == "cartuccia_lid") { cartuccia_lid(); }
else if (mode == "cartuccia_montata") {      // solo per controlli: fondello + cartuccia + coperchio
    cap_base();
    translate([0, 0, cap_base_t + lip_height]) cartuccia();
    translate([0, 0, cap_base_t + lip_height + cart_h + cart_wall]) mirror([0, 0, 1]) cartuccia_lid();
}
