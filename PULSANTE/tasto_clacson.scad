// =====================================================================
//  Copritasto clacson con 4 clip a scatto  —  ricostruzione parametrica
//  Misure dallo schizzo (mm). Le voci "STIMA" vanno verificate col calibro.
//
//  Sistema di riferimento:
//    X = lato lungo (0 = lato sinistro, quello basso/stretto)
//    Y = lato corto (0 = lato dritto in basso nella vista dall'alto)
//    Z = altezza (0 = bordo inferiore del guscio; le clip scendono sotto)
// =====================================================================

/* [Pianta (vista dall'alto)] */
L        = 38.92;  // lunghezza totale
H_right  = 23.85;  // altezza lato destro (alto)
H_left   = 20.56;  // altezza lato sinistro (basso)
wall     = 1.78;   // spessore parete

// Raggi degli angoli in pianta. Scelti perche' i tratti dritti
// tornino con lo schizzo: sotto 38.92-r_BL-r_BR = 25.32, sopra ~23.36
r_BL = 7.0;   // basso-sinistra        (STIMA)
r_BR = 6.6;   // basso-destra          (STIMA)
r_TR = 6.5;   // alto-destra           (STIMA)
r_TL = 9.2;   // alto-sinistra (il piu' tondo)  (STIMA)

/* [Altezze del corpo (senza clip)] */
z_FL = 6.84;   // angolo davanti-sinistra
z_FR = 10.08;  // angolo davanti-destra
z_BR = 8.51;   // angolo dietro-destra
// Il quarto angolo (dietro-sinistra) esce dal piano: ~5.27 mm,
// compatibile con i 4.9 / 5.9 dello schizzo.

top_thk  = 1.6;   // spessore del cielo   (STIMA - manca)
r_fillet = 2.0;   // raggio arrotondamento bordo superiore (STIMA)

/* [Clip a scatto] */
clip_len     = 9.0;   // lunghezza gamba sotto il corpo
clip_w_top   = 4.3;   // larghezza gamba all'attacco
clip_w_bot   = 3.17;  // larghezza gamba in punta
clip_thk     = 2.12;  // spessore gamba
clip_depth   = 3.11;  // profondita' totale gamba + dente
hook_h       = 2.54;  // altezza del dente
hook_flat    = 0.6;   // tratto dritto in cima al dente (il resto e' curvo)
// Angolo (gradi) verso cui guarda il dente di ogni clip: BL, BR, TR, TL
clip_ang     = [225, 315, 45, 135];   // (STIMA - diagonali)
clip_inset   = 0.0;   // sposta le clip verso l'interno (mm)
clip_r       = 0.4;   // raggio di arrotondamento spigoli clip

/* [Pulsantino centrale interno] */
boss       = true;
boss_d     = 8.0;    // (STIMA - manca)
boss_h     = 3.0;    // quanto sporge dal cielo verso il basso (STIMA - manca)
boss_pos   = [20, 11];

/* [Decorazioni sopra] */
domes      = true;
dome_d     = 3.8;    // diametro bollini   (STIMA - manca)
dome_h     = 0.7;    // altezza bollini    (STIMA - manca)
horn       = true;   // simbolo clacson inciso
horn_depth = 0.4;

$fn = 64;

// ---------------------------------------------------------------------
// Derivati
// ---------------------------------------------------------------------
ax = (z_FR - z_FL) / L;        // pendenza in X
by = (z_BR - z_FR) / H_right;  // pendenza in Y
function zt(x, y) = z_FL + ax * x + by * y;   // quota del piano superiore

// centri degli angoli: [x, y, r]
corners = [
  [r_BL,      r_BL,          r_BL],
  [L - r_BR,  r_BR,          r_BR],
  [L - r_TR,  H_right - r_TR, r_TR],
  [r_TL,      H_left - r_TL, r_TL]
];

base_off = -6;               // il solido parte sotto z=0 e viene tagliato
Hbig     = z_FL - base_off;  // altezza "dritta" prima della cesoia

// cesoia: z' = z + ax*x + by*y  -> il top piatto diventa il piano inclinato
module shear() {
  multmatrix([[1,0,0,0],[0,1,0,0],[ax,by,1,base_off],[0,0,0,1]]) children();
}

// blocco convesso con bordo superiore arrotondato
module rounded_block(off, h, rf) {
  hull() for (c = corners) {
    r = c[2] - off;
    translate([c[0], c[1], 0]) cylinder(r = r, h = h - rf);
    translate([c[0], c[1], h - rf])
      rotate_extrude() translate([r - rf, 0]) circle(r = rf);
  }
}

module outer() { shear() rounded_block(0, Hbig, r_fillet); }
module inner() {
  shear() translate([0,0,-1])
    rounded_block(wall, Hbig - top_thk + 1, max(r_fillet - wall, 0.4));
}

// ---------------------------------------------------------------------
// Bollini (posizioni misurate sulla foto, da verificare)
// ---------------------------------------------------------------------
dome_pos = [
  [7.6,16.4],[13.2,17.4],[19.0,17.4],[24.8,16.8],[30.6,15.9],
  [6.0,11.0],[26.4,11.2],[32.6,10.6],
  [8.6,5.2],[14.8,4.6],[21.0,4.6],[27.2,4.6],[33.2,5.0]
];
R_dome = (dome_d*dome_d/4 + dome_h*dome_h) / (2*dome_h);

module domes_add() {
  for (p = dome_pos)
    intersection() {
      translate([p[0], p[1], zt(p[0],p[1]) + dome_h - R_dome]) sphere(r = R_dome);
      translate([p[0]-dome_d, p[1]-dome_d, zt(p[0],p[1]) - 1]) cube([2*dome_d, 2*dome_d, 5]);
    }
}

// simbolo clacson stilizzato (bocchino a sinistra, campana a destra)
module horn_2d() {
  translate([10.3, 12.2]) {
    translate([0, -2]) square([1.0, 4.0]);                   // bocchino
    translate([0.9, -0.6]) square([5.6, 1.2]);               // canna
    polygon([[6.3,-0.8],[10.2,-3.0],[10.2,3.0],[6.3,0.8]]);  // campana
  }
}
module horn_cut() {
  shear() translate([0,0,Hbig - horn_depth])
    linear_extrude(horn_depth + 1) horn_2d();
}

// ---------------------------------------------------------------------
// Clip
// ---------------------------------------------------------------------
// gamba centrata in Y locale; il dente sporge verso +X locale (esterno)
// Tutti gli spigoli sono arrotondati con raggio clip_r (minkowski con sfera).
module clip() {
  r = clip_r;
  p = clip_depth - clip_thk;
  // gamba rastremata
  minkowski() {
    hull() {
      translate([-clip_thk + r, -clip_w_top/2 + r, -0.5])
        cube([clip_thk - 2*r, clip_w_top - 2*r, 3.5]);
      translate([-clip_thk + r, -clip_w_bot/2 + r, -clip_len + r])
        cube([clip_thk - 2*r, clip_w_bot - 2*r, 0.01]);
    }
    sphere(r = r, $fn = 16);
  }
  // dente
  minkowski() {
    translate([0, clip_w_bot/2 - r, -clip_len])
      rotate([90,0,0])
        linear_extrude(clip_w_bot - 2*r)
          offset(delta = -r)
            hook_profile(p);
    sphere(r = r, $fn = 16);
  }
}

// profilo laterale del dente: esterno curvo (quarto di ellisse) che parte
// dal fondo della gamba e arriva in cima con un piccolo tratto dritto,
// cosi' la faccia di aggancio superiore resta piatta
module hook_profile(p) {
  hb = hook_h - hook_flat;
  polygon(concat(
    [[-clip_thk, 0]],
    [for (t = [0:5:90]) [p * sin(t), hb - hb * cos(t)]],
    [[p, hook_h], [-clip_thk, hook_h]]
  ));
}

module clips() {
  for (i = [0:3]) {
    c = corners[i];
    a = clip_ang[i];
    translate([c[0], c[1], 0])
      rotate([0,0,a])
        translate([c[2] - clip_inset, 0, 0])
          clip();
  }
}

// ---------------------------------------------------------------------
// Assemblaggio
// ---------------------------------------------------------------------
module boss_add() {
  if (boss) intersection() {
    translate([boss_pos[0], boss_pos[1], zt(boss_pos[0],boss_pos[1]) - top_thk - boss_h])
      cylinder(d = boss_d, h = boss_h + 0.5);
    inner();
  }
}

module tasto() {
  difference() {
    union() {
      intersection() {
        outer();
        translate([-5,-5,0]) cube([L+10, H_right+10, 30]);   // taglio fondo a z=0
      }
      if (domes) domes_add();
    }
    difference() {                                           // cavita'
      intersection() { inner(); translate([-5,-5,-1]) cube([L+10, H_right+10, 30]); }
      boss_add();
    }
    if (horn) horn_cut();
  }
  // clip aggiunte dopo la cavita'; sopra z=0 vengono rifilate dentro il
  // guscio, cosi' non sporgono spigoli vivi sulla parete curva
  intersection() {
    clips();
    union() {
      outer();
      translate([-20, -20, -30]) cube([L + 40, H_right + 40, 30]);
    }
  }
}

tasto();
