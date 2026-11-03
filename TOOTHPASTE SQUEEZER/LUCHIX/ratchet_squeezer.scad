/*
  RATCHET TUBE SQUEEZER v2 - parametrico, stampabile FDM (ABS/PLA, Ender 3, letto 220x220)
  =========================================================================================
  Ricostruito da zero (nessun STL importato). Pezzi: body, shaft, handle, ratchet, pawl.

  SISTEMA DI COORDINATE (assembly)
    X = asse dello shaft (lungo la larghezza del tubo). Piastra 1 a X=0, piastra 2 a X=Xc-cheek_t.
    Y = verso l'alto (il dorso poggia su Y=0). Z = lungo il piano d'appoggio.
    Guardando da +X (lato manopola): Y verso destra, Z verso l'alto, angoli CCW positivi.
    Asse di rotazione in (Y,Z) = (cy,cz) = (13,13).

  USO
    Il piano e' piu' largo dal lato -Z: li' si appoggia il tubo (il suo corpo), con il bordo
    infilato nella fessura dello shaft. Si gira la manopola IN SENSO ORARIO (freccia incisa
    sulla manopola, vista da +X) per avvolgere. Per svolgere: solleva la linguetta del
    nottolino (linguetta rossa sopra al ratchet) e gira indietro.

  VERSO DEL CRICCHETTO (scelta documentata)
      - rotazione ORARIA (CW)      = LIBERA  (i denti salgono la rampa, la lamella si solleva)
      - rotazione ANTIORARIA (CCW) = BLOCCATA (becco contro il fianco ripido, radiale)

  NOTTOLINO (pawl) - ACCESSIBILE E INTERCAMBIABILE
    Piastra con lamella elastica (flette nel piano di stampa), becco e linguetta di rilascio.
    Si incastra a pressione con 2 perni nei fori della piastra 2: si estrae con una pinza e si
    sostituisce. La rigidita' della molla dipende SOLO da arm_t: i pawl con arm_t diversi sono
    intercambiabili (part = "tuning_pawls" stampa morbido / normale / rigido).

  KIT DI TARATURA
    part = "fit_test": 4 blocchetti con foro chiave a gioco 0.1/0.2/0.3/0.4 (1..4 tacche)
                       + un perno chiave: si prova l'accoppiamento in 10 minuti.
    part = "tuning_pawls": 3 pawl (arm_t -0.2, 0, +0.2).

  PARAMETRI DI TARATURA DOPO LA PRIMA STAMPA
    - Gioco chiave/ratchet/manopola/shaft  -> key_clear
    - Gioco shaft nelle piastre            -> journal_clear
    - Presa dei perni del pawl             -> peg_interf (diametrale; piu' alto = piu' stretto)
    - Rigidita' molla                      -> arm_t (+0.2 => ~+40%) oppure arm_len
    - Presa becco/dente                    -> pawl_overlap, beak_clear
*/

/* [Main] */
// pezzo da generare
part = "assembly"; // [assembly, plate_body, plate_small, plate_mech, print_plate, body, shaft, handle, ratchet, pawl, tuning_pawls, fit_test, detail_pawl, chk_beak_ratchet, chk_pawl_body, chk_plate_web, chk_pawl_internal, chk_shaft_internal, chk_handle_internal, chk_ratchet_internal, chk_clash]
// larghezza piatta del tubo [mm]
tube_width = 60; // [20:1:80]
// solo assembly: rotazione dello shaft [deg]
shaft_angle = 0; // [0:1:359]
// solo assembly: mostra la manopola
show_handle = true;
// print_plate: aggiunge pawl piu' morbido e piu' rigido
tuning_pawls = false;

/* [Body] */
cheek_t = 6;       // spessore piastre
cheek_size = 26;   // dimensione base piastra attorno all'asse
web_t = 4;         // spessore del dorso
side_gap = 2;      // gioco tra bordo tubo e piastre (per lato)
plate_r = 5;       // raggio angoli superiori delle piastre
feet = true;       // due incavi sul dorso per strisce adesive antiscivolo
feet_w = 8;
feet_depth = 0.8;

/* [Shaft] */
shaft_w = 15;      // larghezza barra
shaft_t = 6;       // spessore barra
slot_w = 1.4;      // fessura per il bordo del tubo
slot_depth = 8;    // profondita' fessura
slot_extra = 1.0;  // fessura piu' lunga del tubo
journal_clear = 0.35; // gioco radiale perno/foro piastra
bar_gap = 0.4;     // gioco assiale barra/piastre
head_t = 2.5;      // spessore testa di arresto
head_w = 22;       // larghezza testa
head_r = 4;        // raggio angoli testa
head_gap = 0.3;    // gioco assiale testa/piastra 1
shaft_ears = true; // orecchie sacrificali da 0.4 mm sotto lo shaft in stampa (anti-warping), da strappare a stampa finita
ear_d = 16;
ear_h = 0.4;

/* [Key / chiave] */
key_w = 8.3;
key_h = 6.3;
key_clear = 0.2;   // gioco totale per dimensione (scelto con fit_test in ABS: blocchetto a 2 tacche)
sock_d = 5;        // profondita' presa chiave nel perno dello shaft
socket_clear = 0.35; // gioco della tasca nello shaft (stampa con l'asse in orizzontale: viene piu' stretta)
stub_trim = 0.1;   // il perno della manopola e' piu' piccolo del nominale di questo valore (gioco extra)

/* [Ratchet] */
teeth = 10;
ratchet_tip_r = 11;
tooth_depth = 2.2;
ratchet_t = 8;
ratchet_gap = 0.5;
hub_d = 14;
hub_h = 4;
lead_in = 0.6;

/* [Pawl] */
arm_t = 1.6;            // spessore lamella (rigidita')
arm_len = 21;           // lunghezza lamella
arm_gap = 0.6;
beak_w = 2.2;
beak_clear = 0.35;
pawl_overlap = 0.2;
relief = 0.4;
blk_w = 10;
peg_d = 5;
peg_len = 4;
peg_interf = 0.2;
tab_w = 5;              // linguetta di rilascio
tab_h = 4;

/* [Handle] */
knob_len = 44;          // apertura totale
knob_w = 13;            // larghezza ali
boss_d = 20;            // disco centrale
knob_t = 8;
knob_blend = 4;         // raccordo tra disco e ali
arrow = true;           // freccia di rotazione incisa

/* [Hidden] */
$fn = 72;
eps = 0.01;
pawl_angle = 0;         // non modificare: la geometria di piastra e pawl e' calcolata per 0

// ---------- derivati ----------
cy = cheek_size/2;  cz = cheek_size/2;
inner = tube_width + 2*side_gap;
x1 = cheek_t;  x2 = x1 + inner;  Xc = x2 + cheek_t;
Rt = ratchet_tip_r;  Rr = Rt - tooth_depth;  pitch = 360/teeth;
plate_t = ratchet_gap + ratchet_t;
journal_d = sqrt(shaft_w*shaft_w + shaft_t*shaft_t) + 0.24;
hole_d = journal_d + 2*journal_clear;
xk = Xc + ratchet_gap + ratchet_t + hub_h;
stub_len = xk - (Xc - sock_d);
sw = key_w - stub_trim;  sh = key_h - stub_trim;   // sezione effettiva del perno della manopola

// ---------- pawl: geometria locale (becco in alto; lamella verso +u) ----------
pa = pawl_angle - 90;
function pol(r,a) = [r*cos(a), r*sin(a)];
function rot(p,a) = [p[0]*cos(a)-p[1]*sin(a), p[0]*sin(a)+p[1]*cos(a)];
function g2(p) = rot(p,pa) + [cy,cz];

va0 = Rt + arm_gap;
draw = pol(Rt, 90+pitch) - [0,Rr];
dvec = draw/norm(draw);
Q1 = [pawl_overlap, Rr + beak_clear];
Q3 = Q1 + (beak_w/abs(dvec[0]))*dvec;
beak_top = va0 + 0.6;
u_l = pawl_overlap - beak_w - 0.4;
u_r = u_l + arm_len;
// blocco di ancoraggio: indipendente da arm_t => i pawl con arm_t diverso sono intercambiabili
blk_u0 = u_r - 1;  blk_u1 = u_r + blk_w;
blk_v0 = 0;        blk_v1 = va0 + 5.1;
peg_loc = [[(blk_u0+blk_u1)/2, blk_v0+3.5], [(blk_u0+blk_u1)/2, blk_v1-3.5]];
peg_glb = [for (p = peg_loc) g2(p)];
// linguetta di rilascio
tab_u0 = u_l + 5;
tab_top = va0 + 2.0 + tab_h;

// ingombro della piastra (calcolato dal blocco del pawl)
pb_pts = [for (p=[[blk_u0,blk_v0],[blk_u1,blk_v0],[blk_u0,blk_v1],[blk_u1,blk_v1]]) g2(p)];
plate_zlo = min(0, min([for (p=pb_pts) p[1]]) - 2.0);
plate_zhi = cheek_size;
plate_yhi = max(cheek_size, max([for (p=pb_pts) p[0]]) + 1.5);

pw_pts = [for (p=[Q1,Q3,[Q1[0],beak_top],[Q3[0],beak_top],[u_l,va0],[u_r,va0],[u_l,va0+arm_t],[u_r,va0+arm_t],
                  [blk_u0,blk_v0],[blk_u1,blk_v0],[blk_u0,blk_v1],[blk_u1,blk_v1],
                  [tab_u0,tab_top],[tab_u0+tab_w,tab_top]]) g2(p)];
pY0 = min([for (p=pw_pts) p[0]]);  pY1 = max([for (p=pw_pts) p[0]]);
pZ0 = min([for (p=pw_pts) p[1]]);  pZ1 = max([for (p=pw_pts) p[1]]);

lift = tooth_depth - beak_clear + 0.3;
echo(str("Lock: CCW blocked / CW free (vista da +X). Shaft length = ", Xc+head_t+head_gap, " mm"));
echo(str("Body: ", Xc, " x ", plate_zhi-plate_zlo, " x ", plate_yhi, " mm (X x Z x Y)"));
echo(str("Spring: arm ", arm_len, " x ", arm_t, " mm, lift ", lift, " mm => bending strain ~",
         round(1000*3*arm_t*lift/(2*arm_len*arm_len))/10, " % (PLA ok se < ~1.5 %)"));

// ---------- helper ----------
module yz(x0,t){ translate([x0,0,0]) rotate([90,0,90]) linear_extrude(height=t) children(); }
module pl(){ translate([cy,cz]) rotate(pa) children(); }
module rrect(w,h,r=1){ hull() for (sx=[-1,1],sy=[-1,1]) translate([sx*(w/2-r), sy*(h/2-r)]) circle(r=r,$fn=24); }

// ---------- 2D ----------
// piastra: angoli superiori (Y alto) arrotondati, base (Y=0) piatta per la stampa
module plate2d(){
  hull(){
    translate([0,plate_zlo]) square([eps, plate_zhi-plate_zlo]);
    for (z=[plate_zlo+plate_r, plate_zhi-plate_r]) translate([plate_yhi-plate_r, z]) circle(r=plate_r);
  }
}
// foro asse a goccia (apice verso Y alto = verso l'alto in stampa: niente ponte)
module hole2d(){ translate([cy,cz]) hull(){ circle(d=hole_d); translate([hole_d/2*1.4142,0]) circle(d=0.02,$fn=6); } }
module ratchet2d(){
  polygon([for (k=[0:teeth-1]) each [pol(Rr,pawl_angle+k*pitch), pol(Rt,pawl_angle+(k+1)*pitch)]]);
}
module beak2d(){ polygon([Q1, [Q1[0],beak_top], [Q3[0],beak_top], Q3]); }
module arm2d(t=arm_t){ translate([u_l,va0]) square([u_r-u_l, t]); }
module block2d(){ translate([blk_u0,blk_v0]) square([blk_u1-blk_u0, blk_v1-blk_v0]); }
module tab2d(){ hull(){ translate([tab_u0,va0]) square([tab_w,1]); translate([tab_u0+tab_w/2, tab_top-tab_w/2]) circle(d=tab_w,$fn=36); } }
// manopola a osso: disco centrale + ali lungo Z, raccordate (chiusura morfologica)
module knob2d(){
  offset(r=-knob_blend) offset(r=knob_blend) union(){
    circle(d=boss_d);
    hull() for (s=[-1,1]) translate([0, s*(knob_len/2-knob_w/2)]) circle(d=knob_w);
  }
}
// freccia oraria (vista da +X): arco con punta
module arrow2d(){
  ra=6; w=1.4; a0=150; a1=40;
  polygon(concat([for (a=[a1:5:a0]) pol(ra+w/2,a)], [for (a=[a0:-5:a1]) pol(ra-w/2,a)]));
  P=pol(ra,a1); T=[sin(a1),-cos(a1)]; N=[cos(a1),sin(a1)];
  polygon([P+T*4.2, P-T*0.8+N*2.4, P-T*0.8-N*2.4]);   // base della punta sovrapposta all'arco
}

// ---------- BODY ----------
module web_asm(){ translate([0,0,plate_zlo]) cube([Xc, web_t, plate_zhi-plate_zlo]); }
module frame_asm(){ union(){ yz(0,cheek_t) plate2d(); yz(x2,cheek_t) plate2d(); web_asm(); } }
module body_asm(){
  difference(){
    frame_asm();
    yz(-1, Xc+2) hole2d();
    for (p = peg_glb) translate([Xc-peg_len-0.4, p[0], p[1]]) rotate([0,90,0])
      cylinder(d=peg_d-peg_interf, h=peg_len+0.4+eps, $fn=32);
    if (feet) for (zc=[plate_zlo+9, plate_zhi-9]) hull() for (fx=[10+feet_w/2, Xc-10-feet_w/2])
      translate([fx,-eps,zc]) rotate([-90,0,0]) cylinder(d=feet_w, h=feet_depth+eps, $fn=32);
  }
}

// ---------- SHAFT ----------
module bar_asm(){ translate([x1+bar_gap, cy-shaft_t/2, cz-shaft_w/2]) cube([inner-2*bar_gap, shaft_t, shaft_w]); }
module head_asm(){ yz(-head_t-head_gap, head_t) translate([cy,cz]) rrect(head_w, shaft_w, head_r); }
// perni di scorrimento nelle piastre (compenetrano la testa e la barra)
module journal1_asm(){ intersection(){
  translate([-head_gap-1,cy,cz]) rotate([0,90,0]) cylinder(d=journal_d, h=x1+bar_gap+0.2+head_gap+1);
  translate([-5, cy-20, cz-shaft_w/2]) cube([Xc+10, 40, shaft_w]); } }
module journal2_asm(){ intersection(){
  translate([x2-bar_gap-0.2,cy,cz]) rotate([0,90,0]) cylinder(d=journal_d, h=cheek_t+bar_gap+0.2);
  translate([-5, cy-20, cz-shaft_w/2]) cube([Xc+10, 40, shaft_w]); } }
module shaft_asm(){
  slit_len = tube_width + slot_extra;
  difference(){
    union(){ bar_asm(); journal1_asm(); journal2_asm(); head_asm(); }
    translate([x1+(inner-slit_len)/2, cy-slot_w/2, cz+shaft_w/2-slot_depth]) cube([slit_len, slot_w, slot_depth+1]);
    yz(Xc-sock_d-0.6, sock_d+0.6+eps) translate([cy,cz]) rrect(key_w+socket_clear, key_h+socket_clear);
  }
}
module shaft_rot(){ translate([0,cy,cz]) rotate([shaft_angle,0,0]) translate([0,-cy,-cz]) children(); }

// ---------- RATCHET ----------
module ratchet_asm(){
  xr = Xc + ratchet_gap;
  difference(){
    union(){
      yz(xr, ratchet_t) translate([cy,cz]) ratchet2d();
      yz(xr+ratchet_t-2, hub_h+2) translate([cy,cz]) circle(d=hub_d);   // mozzo compenetra il disco di 2 mm
    }
    yz(xr-1, ratchet_t+hub_h+2) translate([cy,cz]) rrect(key_w+key_clear, key_h+key_clear);
    hull(){ yz(xr-eps, eps) translate([cy,cz]) rrect(key_w+key_clear+2*lead_in, key_h+key_clear+2*lead_in);
            yz(xr+lead_in, eps) translate([cy,cz]) rrect(key_w+key_clear, key_h+key_clear); }
    hull(){ yz(xr+ratchet_t+hub_h-lead_in, eps) translate([cy,cz]) rrect(key_w+key_clear, key_h+key_clear);
            yz(xr+ratchet_t+hub_h, eps) translate([cy,cz]) rrect(key_w+key_clear+2*lead_in, key_h+key_clear+2*lead_in); }
  }
}

// ---------- PAWL ----------
module beak_asm(){ yz(Xc+relief, plate_t-relief) pl() beak2d(); }
module arm_asm(t=arm_t){ yz(Xc+relief, plate_t-relief) pl() arm2d(t); }
module tab_asm(){ yz(Xc+relief, plate_t-relief) pl() tab2d(); }
module block_asm(){ yz(Xc, plate_t) pl() block2d(); }
module pegs_asm(){
  for (p = peg_glb) translate([Xc-peg_len, p[0], p[1]]) rotate([0,90,0]) cylinder(d=peg_d, h=peg_len+1, $fn=32);
}
module pawl_asm(t=arm_t){ union(){ block_asm(); arm_asm(t); beak_asm(); tab_asm(); pegs_asm(); } }

// ---------- HANDLE ----------
module handle_asm(){
  union(){
    difference(){
      yz(xk, knob_t) translate([cy,cz]) knob2d();
      if (arrow) yz(xk+knob_t-0.6, 0.7) translate([cy,cz]) arrow2d();
    }
    stub_asm();
  }
}
// perno chiave: compenetra la manopola di 3 mm; raccordo conico alla base (0.6 mm, entro lo smusso d'invito del mozzo)
module stub_asm(){
  yz(xk-stub_len, stub_len+3) translate([cy,cz]) rrect(sw, sh);
  hull(){
    yz(xk-0.6, eps) translate([cy,cz]) rrect(sw, sh);
    yz(xk, 0.5) translate([cy,cz]) rrect(sw+1.2, sh+1.2);
  }
}

// ---------- ASSEMBLY ----------
module assembly(){
  color("lightsteelblue") body_asm();
  color("orange") shaft_rot() shaft_asm();
  color("seagreen") shaft_rot() ratchet_asm();   // il ratchet e' calettato sulla chiave: gira con lo shaft
  color("crimson") pawl_asm();
  if (show_handle) color("gold") shaft_rot() handle_asm();
}

// ---------- ORIENTAMENTO DI STAMPA ----------
module body_print(){   translate([0, plate_zhi, 0]) rotate([90,0,0]) body_asm(); }
module shaft_print(){
  translate([head_t+head_gap, -(cy-head_w/2), -(cz-shaft_w/2)]) union(){
    shaft_asm();
    if (shaft_ears) for (x=[x1+6, x1+inner/3, x1+2*inner/3, x2-6])
      translate([x, cy, cz-shaft_w/2]) cylinder(d=ear_d, h=ear_h);
  }
}
module pawl_print(t=arm_t){ translate([-pZ0, -pY0, Xc+plate_t]) rotate([0,90,0]) pawl_asm(t); }
module ratchet_print(){ translate([cz+Rt, -(cy-Rt), -(Xc+ratchet_gap)]) rotate([0,-90,0]) ratchet_asm(); }
module handle_print(){ ky=max(knob_w,boss_d); translate([-(cz-knob_len/2), -(cy-ky/2), xk+knob_t]) rotate([0,90,0]) handle_asm(); }

module print_plate(){
  g = 6;  pw = pZ1 - pZ0;
  yB = (plate_zhi - plate_zlo) + g;
  yC = yB + head_w + g;
  yD = yC + 2*Rt + g;
  body_print();
  translate([0,yB,0]) shaft_print();
  translate([0,yC,0]) ratchet_print();
  translate([2*Rt+g,yC,0]) pawl_print();
  translate([2*Rt+g+pw+g,yC,0]) handle_print();
  if (tuning_pawls) {
    translate([2*Rt+g,yD,0]) pawl_print(arm_t-0.2);
    translate([2*Rt+g+pw+g,yD,0]) pawl_print(arm_t+0.2);
  }
}
// due piatti separati (consigliati in ABS): corpo da solo, e meccanismo (shaft, ratchet, pawl, manopola)
module plate_body(){ body_print(); }
module plate_mech(){
  g = 6;  pw = pZ1 - pZ0;
  yC = head_w + g;
  yD = yC + 2*Rt + g;
  shaft_print();
  translate([0,yC,0]) ratchet_print();
  translate([2*Rt+g,yC,0]) pawl_print();
  translate([2*Rt+g+pw+g,yC,0]) handle_print();
  if (tuning_pawls) {
    translate([2*Rt+g,yD,0]) pawl_print(arm_t-0.2);
    translate([2*Rt+g+pw+g,yD,0]) pawl_print(arm_t+0.2);
  }
}
// ratchet + 3 pawl (morbido/normale/rigido): tutti alti ~12 mm, quindi stampano nelle stesse condizioni
module plate_small(){
  g = 6;  pw = pZ1 - pZ0;
  ratchet_print();
  translate([2*Rt+g,0,0]) pawl_print(arm_t-0.2);
  translate([2*Rt+g+pw+g,0,0]) pawl_print(arm_t);
  translate([2*Rt+g+2*(pw+g),0,0]) pawl_print(arm_t+0.2);
}
module tuning_set(){
  pw = pZ1 - pZ0;
  pawl_print(arm_t-0.2);
  translate([pw+6,0,0]) pawl_print(arm_t);
  translate([2*(pw+6),0,0]) pawl_print(arm_t+0.2);
}
// 4 blocchetti con foro chiave a gioco crescente (1..4 tacche) + perno chiave
module fit_test(){
  for (i=[0:3]) translate([i*17,0,0]) difference(){
    translate([-7.5,-6.5,0]) cube([15,13,5]);
    translate([0,0,-1]) linear_extrude(7) rrect(key_w+0.1*(i+1), key_h+0.1*(i+1));
    for (n=[0:i]) translate([-5.5+n*3.2,-6.5-eps,-1]) cube([1.6,1.2,7]);
  }
  translate([0,20,0]) {
    translate([-8,-7,0]) cube([16,14,2]);
    linear_extrude(15) rrect(key_w,key_h);
  }
}

// ---------- VERIFICHE ----------
module chk_beak_ratchet(){ intersection(){ beak_asm(); ratchet_asm(); } }
module chk_pawl_body(){ intersection(){ pegs_asm(); body_asm(); } }
module chk_plate_web(){ intersection(){ web_asm(); union(){ yz(0,cheek_t) plate2d(); yz(x2,cheek_t) plate2d(); } } }
module chk_pawl_internal(){ union(){ intersection(){ beak_asm(); arm_asm(); } intersection(){ arm_asm(); block_asm(); } intersection(){ block_asm(); pegs_asm(); } intersection(){ tab_asm(); arm_asm(); } } }
// giunzioni dello shaft: testa↔perno1, perno1↔barra, barra↔perno2 (volume > 0 = pezzo unico connesso)
module chk_shaft_internal(){ union(){ intersection(){ head_asm(); journal1_asm(); } intersection(){ journal1_asm(); bar_asm(); } intersection(){ bar_asm(); journal2_asm(); } } }
module chk_handle_internal(){ intersection(){ yz(xk, knob_t) translate([cy,cz]) knob2d(); stub_asm(); } }
module chk_ratchet_internal(){ intersection(){ yz(Xc+ratchet_gap, ratchet_t) translate([cy,cz]) ratchet2d(); yz(Xc+ratchet_gap+ratchet_t-2, hub_h+2) translate([cy,cz]) circle(d=hub_d); } }
// coppie che NON devono toccarsi: il risultato deve essere vuoto
module chk_clash(){
  union(){
    shaft_rot() intersection(){ shaft_asm(); body_asm(); }
    intersection(){ shaft_rot() shaft_asm(); shaft_rot() ratchet_asm(); }
    intersection(){ shaft_rot() shaft_asm(); pawl_asm(); }
    intersection(){ shaft_rot() shaft_asm(); shaft_rot() handle_asm(); }   // perno nella tasca: nessun contatto
    intersection(){ shaft_rot() handle_asm(); body_asm(); }
    intersection(){ shaft_rot() handle_asm(); pawl_asm(); }
    intersection(){ shaft_rot() handle_asm(); shaft_rot() ratchet_asm(); }
    intersection(){ shaft_rot() ratchet_asm(); body_asm(); }
    // becco/denti: contatto voluto, verificato a parte con chk_beak_ratchet a shaft_angle=0
  }
}

// ---------- DISPATCH ----------
if      (part == "assembly")      assembly();
else if (part == "print_plate")   print_plate();
else if (part == "plate_body")    plate_body();
else if (part == "plate_mech")    plate_mech();
else if (part == "plate_small")   plate_small();
else if (part == "body")          body_print();
else if (part == "shaft")         shaft_print();
else if (part == "handle")        handle_print();
else if (part == "ratchet")       ratchet_print();
else if (part == "pawl")          pawl_print();
else if (part == "tuning_pawls")  tuning_set();
else if (part == "fit_test")      fit_test();
else if (part == "detail_pawl")   { color("lightsteelblue") yz(x2,cheek_t) plate2d(); color("seagreen") ratchet_asm(); color("crimson") pawl_asm(); }
else if (part == "chk_beak_ratchet")    chk_beak_ratchet();
else if (part == "chk_pawl_body")       chk_pawl_body();
else if (part == "chk_plate_web")       chk_plate_web();
else if (part == "chk_pawl_internal")   chk_pawl_internal();
else if (part == "chk_shaft_internal")  chk_shaft_internal();
else if (part == "chk_handle_internal") chk_handle_internal();
else if (part == "chk_ratchet_internal") chk_ratchet_internal();
else if (part == "chk_clash")           chk_clash();
