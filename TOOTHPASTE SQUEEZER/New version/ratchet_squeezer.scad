/*
  RATCHET TUBE SQUEEZER - parametrico, stampabile FDM (PLA, Ender 3, letto 220x220)
  ===============================================================================
  Ricostruito da zero (nessun STL importato). Pezzi: body, shaft, handle, ratchet, pawl.

  SISTEMA DI COORDINATE (assembly)
    X = asse dello shaft (lungo la larghezza del tubo).  Cheek1 a X=0, cheek2 a X=Xc-cheek_t.
    Y,Z = piano delle guance (cheek_size x cheek_size). Asse di rotazione in (Y,Z)=(cy,cz).
    Guardando da +X (lato manopola): Y verso destra, Z verso l'alto, angoli CCW positivi.

  VERSO DEL CRICCHETTO (scelta documentata)
    Visto dal lato manopola (da +X):
      - rotazione ORARIA (CW)      = LIBERA  (i denti salgono la rampa, la lamella si solleva)
      - rotazione ANTIORARIA (CCW) = BLOCCATA (becco contro il fianco ripido, radiale)
    Per invertire: mirror dell'intero ratchet+pawl oppure ruota il verso dello shaft di avvolgimento.

  NOTTOLINO (pawl)
    Piastra PIATTA (stampata sdraiata, spessore = ratchet_t + ratchet_gap) con:
      - lamella elastica curva-dritta (arm) sollecitata a trazione dal blocco in presa,
        flette nel piano della piastra => fibre di stampa lungo la flessione;
      - becco (beak) che entra nella valle del dente e batte sul fianco ripido;
      - blocco di ancoraggio (block) con 2 perni (peg) a interferenza nella "orecchia" (ear)
        della guancia 2: l'orecchia e' stampata/unita nello stesso union() del corpo.
    Niente molle, elastici o viti esterne.

  TARATURA DOPO LA PRIMA STAMPA (vedi anche echo in console)
    - Gioco chiave/ratchet/manopola/shaft  -> key_clear   (aumenta se stretto, diminuisci se lasco)
    - Gioco cuscinetto shaft nelle guance  -> journal_clear
    - Presa dei perni del pawl             -> peg_interf  (diametrale; aumenta = piu' stretto)
    - Rigidita' molla                      -> arm_t (spessore: +0.2 => ~+40% rigidita'), arm_len (lunghezza)
    - Presa becco/dente                    -> pawl_overlap (precarico modellato), beak_clear
*/

/* [Main] */
// pezzo da generare
part = "assembly"; // [assembly, print_plate, body, shaft, handle, ratchet, pawl, detail_pawl, chk_beak_ratchet, chk_pawl_body, chk_ear1_frame, chk_ear_frame, chk_web_cheeks, chk_pawl_internal, chk_shaft_internal, chk_handle_internal, chk_ratchet_internal]
// larghezza piatta del tubo [mm]
tube_width = 60; // [20:1:80]
// solo assembly: rotazione dello shaft [deg]
shaft_angle = 0; // [0:1:359]
// solo assembly: mostra la manopola
show_handle = true;

/* [Body] */
cheek_t = 6;       // spessore guance
cheek_size = 26;   // lato guance (Y e Z)
web_t = 4;         // spessore del dorso
side_gap = 2;      // gioco tra bordo tubo e guance (per lato)
mirror_ear = true; // orecchia gemella (senza pawl) sulla guancia 1: corpo simmetrico
feet = true;       // tacche sul dorso per piedini adesivi in gomma
feet_d = 8;
feet_depth = 1;

/* [Shaft] */
shaft_w = 15;      // larghezza barra
shaft_t = 6;       // spessore barra
slot_w = 1.4;      // fessura per il bordo del tubo
slot_depth = 8;    // profondita' fessura dal bordo
slot_extra = 1.0;  // fessura piu' lunga del tubo di questo valore
journal_clear = 0.35; // gioco radiale perno/foro guancia
bar_gap = 0.4;     // gioco assiale barra/guance
head_t = 2.5;      // spessore testa di arresto
head_w = 22;       // larghezza testa (> diametro foro)

/* [Key / chiave] */
key_w = 8.3;
key_h = 6.3;
key_clear = 0.25;  // gioco totale per dimensione (fori/tasche = chiave + key_clear)
sock_d = 5;        // profondita' presa della chiave nel perno shaft

/* [Ratchet] */
teeth = 10;
ratchet_tip_r = 11;     // raggio punte (Ø22)
tooth_depth = 2.2;
ratchet_t = 8;          // spessore disco (era 4)
ratchet_gap = 0.5;      // distanza dal fianco della guancia
hub_d = 14;             // mozzo attorno al foro
hub_h = 4;              // altezza mozzo
lead_in = 0.6;          // smusso d'invito del foro

/* [Pawl] */
pawl_angle = 0;         // posizione del becco sul ratchet (0 = lato +Y)
arm_t = 1.6;            // spessore lamella
arm_len = 21;           // lunghezza lamella
arm_gap = 0.6;          // distanza lamella-punte
beak_w = 2.2;
beak_clear = 0.35;      // gioco becco-fondo valle
pawl_overlap = 0.2;     // compenetrazione modellata becco/fianco (precarico)
relief = 0.4;           // lamella/becco piu' sottili verso la guancia (niente attrito)
blk_w = 10;             // larghezza blocco di ancoraggio
peg_d = 5;
peg_len = 4;
peg_interf = 0.2;       // interferenza diametrale perno/foro

/* [Handle] */
knob_len = 44;
knob_w = 14;
boss_d = 20;
knob_t = 8;

/* [Hidden] */
$fn = 72;
eps = 0.01;

// ---------- derivati ----------
cy = cheek_size/2;  cz = cheek_size/2;
inner = tube_width + 2*side_gap;
x1 = cheek_t;  x2 = x1 + inner;  Xc = x2 + cheek_t;
Rt = ratchet_tip_r;  Rr = Rt - tooth_depth;  pitch = 360/teeth;
plate_t = ratchet_gap + ratchet_t;
journal_d = sqrt(shaft_w*shaft_w + shaft_t*shaft_t) + 0.24;
hole_d = journal_d + 2*journal_clear;
xk = Xc + ratchet_gap + ratchet_t + hub_h;      // faccia interna manopola
stub_len = xk - (Xc - sock_d);

// ---------- pawl: geometria locale (becco in alto, theta=90deg; arm verso +u) ----------
pa = pawl_angle - 90;
function pol(r,a) = [r*cos(a), r*sin(a)];
function rot(p,a) = [p[0]*cos(a)-p[1]*sin(a), p[0]*sin(a)+p[1]*cos(a)];
function g2(p) = rot(p,pa) + [cy,cz];           // locale -> globale (Y,Z)

va0 = Rt + arm_gap;                              // fondo lamella
draw = pol(Rt, 90+pitch) - [0,Rr];
dvec = draw/norm(draw);
Q1 = [pawl_overlap, Rr + beak_clear];
Q3 = Q1 + (beak_w/abs(dvec[0]))*dvec;
beak_top = va0 + 0.6;
u_l = pawl_overlap - beak_w - 0.4;
u_r = u_l + arm_len;
blk_u0 = u_r - 1;  blk_u1 = u_r + blk_w;
blk_v0 = 0;  blk_v1 = va0 + arm_t + 3.5;   // blocco basso: a quella distanza dal ratchet non c'e' ingombro
peg_loc = [[(blk_u0+blk_u1)/2, blk_v0+3.5], [(blk_u0+blk_u1)/2, blk_v1-3.5]];
peg_glb = [for (p = peg_loc) g2(p)];
ear_u0 = cheek_size/2 - 3;  ear_u1 = blk_u1 + 1.5;
ear_v0 = -cheek_size/2;     ear_v1 = blk_v1 + 1.0;   // v0 fino al letto di stampa (Y=0): niente sbalzi

ear_pts = [for (p=[[ear_u0,ear_v0],[ear_u1,ear_v0],[ear_u0,ear_v1],[ear_u1,ear_v1]]) g2(p)];
zmin_b = min(0, min([for (p=ear_pts) p[1]]));
zmax_b = max(cheek_size, max([for (p=ear_pts) p[1]]));
pw_pts = [for (p=[Q1,Q3,[Q1[0],beak_top],[Q3[0],beak_top],[u_l,va0],[u_r,va0],[u_l,va0+arm_t],[u_r,va0+arm_t],
                  [blk_u0,blk_v0],[blk_u1,blk_v0],[blk_u0,blk_v1],[blk_u1,blk_v1]]) g2(p)];
pY0 = min([for (p=pw_pts) p[0]]);  pY1 = max([for (p=pw_pts) p[0]]);
pZ0 = min([for (p=pw_pts) p[1]]);  pZ1 = max([for (p=pw_pts) p[1]]);

lift = tooth_depth - beak_clear + 0.3;
echo(str("Lock: CCW blocked / CW free (vista da +X). Shaft length = ", Xc+head_t, " mm"));
echo(str("Spring: arm ", arm_len, " x ", arm_t, " mm, lift ", lift, " mm => bending strain ~",
         round(1000*3*arm_t*lift/(2*arm_len*arm_len))/10, " % (PLA ok se < ~1.5 %)"));

// ---------- helper ----------
module yz(x0,t){ translate([x0,0,0]) rotate([90,0,90]) linear_extrude(height=t) children(); }
module pl(){ translate([cy,cz]) rotate(pa) children(); }
module rrect(w,h,r=1){ hull() for (sx=[-1,1],sy=[-1,1]) translate([sx*(w/2-r), sy*(h/2-r)]) circle(r=r,$fn=24); }

// ---------- 2D ----------
module ratchet2d(){
  polygon([for (k=[0:teeth-1]) each [pol(Rr,pawl_angle+k*pitch), pol(Rt,pawl_angle+(k+1)*pitch)]]);
}
module beak2d(){ polygon([Q1, [Q1[0],beak_top], [Q3[0],beak_top], Q3]); }
module arm2d(){ translate([u_l,va0]) square([u_r-u_l, arm_t]); }
module block2d(){ translate([blk_u0,blk_v0]) square([blk_u1-blk_u0, blk_v1-blk_v0]); }
module ear2d(){ pl() translate([ear_u0,ear_v0]) square([ear_u1-ear_u0, ear_v1-ear_v0]); }
module knob2d(){
  // ali lungo Z (orizzontali quando il corpo poggia sul dorso: non toccano il piano)
  rotate(90) hull() for (s=[-1,1]) translate([s*(knob_len/2-knob_w/2),0]) circle(d=knob_w);
  circle(d=boss_d);
}

// ---------- BODY ----------
module frame_asm(){   // telaio: cheek1 + cheek2 (quadrata) + dorso
  union(){
    yz(0,cheek_t) square(cheek_size);
    yz(x2,cheek_t) square(cheek_size);
    cube([Xc, web_t, cheek_size]);
  }
}
module ear_asm(){ yz(x2,cheek_t) ear2d(); }   // alloggiamento del pawl
module ear1_asm(){ yz(0,cheek_t) ear2d(); }   // orecchia gemella (bilanciamento)
module body_asm(){
  difference(){
    union(){ frame_asm(); ear_asm(); if (mirror_ear) ear1_asm(); }
    if (feet) for (fx=[12, Xc-12], fz=[6.5, cheek_size-6.5])
      translate([fx,-eps,fz]) rotate([-90,0,0]) cylinder(d=feet_d, h=feet_depth+eps);
    translate([-1,cy,cz]) rotate([0,90,0]) cylinder(d=hole_d, h=Xc+2);
    for (p = peg_glb) translate([Xc-peg_len-0.4, p[0], p[1]]) rotate([0,90,0])
      cylinder(d=peg_d-peg_interf, h=peg_len+0.4+eps, $fn=32);
  }
}

// ---------- SHAFT ----------
module shaft_asm(){
  slit_len = tube_width + slot_extra;
  difference(){
    union(){
      translate([x1+bar_gap, cy-shaft_t/2, cz-shaft_w/2]) cube([inner-2*bar_gap, shaft_t, shaft_w]);
      intersection(){
        union(){
          translate([-eps,cy,cz]) rotate([0,90,0]) cylinder(d=journal_d, h=x1+bar_gap+0.2+eps);
          translate([x2-bar_gap-0.2,cy,cz]) rotate([0,90,0]) cylinder(d=journal_d, h=cheek_t+bar_gap+0.2);
        }
        translate([-5, cy-20, cz-shaft_w/2]) cube([Xc+10, 40, shaft_w]);
      }
      translate([-head_t, cy-head_w/2, cz-shaft_w/2]) cube([head_t+0.2, head_w, shaft_w]);
    }
    translate([x1+(inner-slit_len)/2, cy-slot_w/2, cz+shaft_w/2-slot_depth]) cube([slit_len, slot_w, slot_depth+1]);
    yz(Xc-sock_d-0.6, sock_d+0.6+eps) translate([cy,cz]) rrect(key_w+key_clear, key_h+key_clear);
  }
}

// ---------- RATCHET ----------
module ratchet_asm(){
  xr = Xc + ratchet_gap;
  difference(){
    union(){
      yz(xr, ratchet_t) translate([cy,cz]) ratchet2d();
      yz(xr+ratchet_t-2, hub_h+2) translate([cy,cz]) circle(d=hub_d);   // mozzo compenetra il disco di 2 mm
    }
    yz(xr-1, ratchet_t+hub_h+2) translate([cy,cz]) rrect(key_w+key_clear, key_h+key_clear);
    // smussi d'invito (entrambe le facce)
    hull(){ yz(xr-eps, eps) translate([cy,cz]) rrect(key_w+key_clear+2*lead_in, key_h+key_clear+2*lead_in);
            yz(xr+lead_in, eps) translate([cy,cz]) rrect(key_w+key_clear, key_h+key_clear); }
    hull(){ yz(xr+ratchet_t+hub_h-lead_in, eps) translate([cy,cz]) rrect(key_w+key_clear, key_h+key_clear);
            yz(xr+ratchet_t+hub_h, eps) translate([cy,cz]) rrect(key_w+key_clear+2*lead_in, key_h+key_clear+2*lead_in); }
  }
}

// ---------- PAWL ----------
module beak_asm(){ yz(Xc+relief, plate_t-relief) pl() beak2d(); }
module arm_asm(){ yz(Xc+relief, plate_t-relief) pl() arm2d(); }
module block_asm(){ yz(Xc, plate_t) pl() block2d(); }
module pegs_asm(){
  for (p = peg_glb) translate([Xc-peg_len, p[0], p[1]]) rotate([0,90,0]) cylinder(d=peg_d, h=peg_len+1, $fn=32);
}
module pawl_asm(){ union(){ block_asm(); arm_asm(); beak_asm(); pegs_asm(); } }

// ---------- HANDLE ----------
module handle_asm(){
  union(){
    yz(xk, knob_t) translate([cy,cz]) knob2d();
    yz(xk-stub_len, stub_len+3) translate([cy,cz]) rrect(key_w, key_h);   // stub compenetra la manopola di 3 mm
  }
}

// ---------- ASSEMBLY ----------
module assembly(){
  color("lightsteelblue") body_asm();
  color("orange") translate([0,cy,cz]) rotate([shaft_angle,0,0]) translate([0,-cy,-cz]) shaft_asm();
  color("seagreen") ratchet_asm();
  color("crimson") pawl_asm();
  if (show_handle) color("gold") translate([0,cy,cz]) rotate([shaft_angle,0,0]) translate([0,-cy,-cz]) handle_asm();
}

// ---------- PRINT ORIENTATION ----------
module body_print(){   translate([0, zmax_b, 0]) rotate([90,0,0]) body_asm(); }
module shaft_print(){  translate([head_t, -(cy-head_w/2), -(cz-shaft_w/2)]) shaft_asm(); }
module pawl_print(){   translate([-pZ0, -pY0, Xc+plate_t]) rotate([0,90,0]) pawl_asm(); }
module ratchet_print(){ translate([cz+Rt, -(cy-Rt), -(Xc+ratchet_gap)]) rotate([0,-90,0]) ratchet_asm(); }
module handle_print(){ ky=max(knob_w,boss_d); translate([-(cz-knob_len/2), -(cy-ky/2), xk+knob_t]) rotate([0,90,0]) handle_asm(); }

module print_plate(){
  g = 6;
  yB = (zmax_b - zmin_b) + g;
  yC = yB + head_w + g;
  body_print();
  translate([0,yB,0]) shaft_print();
  translate([0,yC,0]) ratchet_print();
  translate([2*Rt+g,yC,0]) pawl_print();
  translate([2*Rt+g+(pZ1-pZ0)+g,yC,0]) handle_print();
}

// ---------- VERIFICHE: intersezioni (volume > 0 = connessi) ----------
module chk_beak_ratchet(){ intersection(){ beak_asm(); ratchet_asm(); } }
// perni del pawl (a interferenza) nei fori dell'orecchia; la piastra appoggia poi a filo sulla faccia della guancia
module chk_pawl_body(){ intersection(){ pegs_asm(); body_asm(); } }
module chk_ear_frame(){ intersection(){ ear_asm(); frame_asm(); } }
module chk_ear1_frame(){ intersection(){ ear1_asm(); frame_asm(); } }
module chk_web_cheeks(){ intersection(){ cube([Xc, web_t, cheek_size]); union(){ yz(0,cheek_t) square(cheek_size); yz(x2,cheek_t) square(cheek_size);} } }
module chk_pawl_internal(){ union(){ intersection(){ beak_asm(); arm_asm(); } intersection(){ arm_asm(); block_asm(); } intersection(){ block_asm(); pegs_asm(); } } }
module chk_shaft_internal(){ intersection(){ shaft_asm(); union(){ translate([x1-0.5,cy-9,cz-9]) cube([1.0,18,18]); translate([x2-0.5,cy-9,cz-9]) cube([1.0,18,18]); translate([-0.5,cy-12,cz-8]) cube([1.0,24,16]); } } }
module chk_handle_internal(){ intersection(){ yz(xk, knob_t) translate([cy,cz]) knob2d(); yz(xk-stub_len, stub_len+3) translate([cy,cz]) rrect(key_w,key_h); } }
module chk_ratchet_internal(){ intersection(){ yz(Xc+ratchet_gap, ratchet_t) translate([cy,cz]) ratchet2d(); yz(Xc+ratchet_gap+ratchet_t-2, hub_h+2) translate([cy,cz]) circle(d=hub_d); } }

// ---------- DISPATCH ----------
if      (part == "assembly")      assembly();
else if (part == "print_plate")   print_plate();
else if (part == "body")          body_print();
else if (part == "shaft")         shaft_print();
else if (part == "handle")        handle_print();
else if (part == "ratchet")       ratchet_print();
else if (part == "pawl")          pawl_print();
else if (part == "detail_pawl")   { color("lightsteelblue") ear_asm(); color("lightsteelblue") yz(x2,cheek_t) square(cheek_size); color("seagreen") ratchet_asm(); color("crimson") pawl_asm(); }
else if (part == "chk_beak_ratchet")    chk_beak_ratchet();
else if (part == "chk_pawl_body")       chk_pawl_body();
else if (part == "chk_ear_frame")       chk_ear_frame();
else if (part == "chk_ear1_frame")      chk_ear1_frame();
else if (part == "chk_web_cheeks")      chk_web_cheeks();
else if (part == "chk_pawl_internal")   chk_pawl_internal();
else if (part == "chk_shaft_internal")  chk_shaft_internal();
else if (part == "chk_handle_internal") chk_handle_internal();
else if (part == "chk_ratchet_internal") chk_ratchet_internal();
