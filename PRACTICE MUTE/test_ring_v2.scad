// =============================================================================
//  TEST RING V2 — Sede Sughero a Quota 65 mm (Conicità Dolce Autobloccante)
//  100% VERO ZERO SUPPORTI — Ottimizzato per Creality Ender-3 V2
// =============================================================================

$fn = $preview ? 64 : 128;

// Profilo campana misurato
bell_profile = [
    [0,   119.0],
    [10,   83.0],
    [20,   69.5],
    [30,   57.0],
    [40,   45.0],
    [70,   35.0],
    [100,  30.0]
];

// Parametri sede sughero a quota 65 mm
cork_depth_target = 65.0;  // [mm] Profondità del centro guarnizione (cono dolce autobloccante)
cork_thick        = 2.0;   // [mm] Spessore striscia sughero
cork_seat_w       = 10.5;  // [mm] Larghezza fondo piano gola (+0.5 mm tolleranza)
cork_seat_d       = 1.1;   // [mm] Profondità gola (il sughero sporge di 0.9 mm a riposo)
cork_compress     = 0.20;  // [mm] Compressione radiale voluta a battuta
cork_chamfer      = cork_seat_d; // [mm] dz = dr = 1.1 mm -> raccordo a 45°

wall_t = 1.6;              // [mm] Spessore parete costante (4 perimetri da 0.4 mm)
h_ring = 26.0;             // [mm] Altezza totale provino

function interp_linear(z, pts, i=0) =
    (i >= len(pts)-1) ? pts[len(pts)-1][1] :
    (z <= pts[0][0]) ? pts[0][1] :
    (z <= pts[i+1][0]) ?
        pts[i][1] + (z - pts[i][0]) * (pts[i+1][1] - pts[i][1]) / (pts[i+1][0] - pts[i][0]) :
        interp_linear(z, pts, i+1);

function bell_dia(z) = interp_linear(z, bell_profile);
function bell_r(z)   = bell_dia(z) / 2;

bell_r_cork = bell_r(cork_depth_target);
cork_protrusion_compressed = (cork_thick - cork_seat_d) - cork_compress; // 0.70 mm
body_r_cork = bell_r_cork - cork_protrusion_compressed;
clearance_plastic_brass = bell_r_cork - body_r_cork; // 0.70 mm costante

z_cork_top    = cork_depth_target + (cork_seat_w / 2);
z_cork_bottom = cork_depth_target - (cork_seat_w / 2);
z_bot         = cork_depth_target - (h_ring / 2);
z_top         = cork_depth_target + (h_ring / 2);

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
    // Appoggio piatto sul bed (senza brim artificiale, si usa il brim di Cura)
    [r_bot_ext,          zm_bot],
    [r_chamfer_bot_ext, zm_chamfer_bot],
    [r_cork_bot_in,     zm_cork_bot],       // rampa 45° interna
    [r_cork_top_in,     zm_cork_top],       // fondo gola piano (10.5 mm)
    [r_chamfer_top_ext, zm_chamfer_top],    // rampa 45° esterna (autoportante)
    [r_top_ext,         zm_top]
];

poly_int = [
    [r_top_ext - wall_t,         zm_top],
    [r_chamfer_top_ext - wall_t, zm_chamfer_top],
    [r_cork_top_in - wall_t,     zm_cork_top],       // parete costante 1.6 mm ovunque
    [r_cork_bot_in - wall_t,     zm_cork_bot],
    [r_chamfer_bot_ext - wall_t, zm_chamfer_bot],
    [r_bot_ext - wall_t,         zm_bot]
];

rotate_extrude()
    polygon(concat(poly_ext, poly_int));
