// =============================================================================
//  TUBE SQUEEZER PARAMETRICO  (dentifricio / crema mani / tubi larghi)
//  Ricostruzione parametrica e FUNZIONALE del ratchet toothpaste squeezer.
//  Design meccanico:
//    - Corpo a U aperta: lo shaft si appoggia dall'alto nelle sedi, niente
//      da sfilare. Comodo per tubi larghi.
//    - Ratchet a denti ASIMMETRICI (sega): fronte ripido che blocca, dorso
//      inclinato che scorre.
//    - Nottolino (pawl) come PEZZO SEPARATO che ruota su un pernetto del
//      corpo: il becco ingrana sui denti e impedisce lo srotolamento (il
//      "clic" anti-ritorno). Si stampa piatto, robusto, con molla integrata.
//    - Manopola con chiave sagomata passante -> trascina lo shaft.
//    - Ratchet rinforzato (spessore + mozzo) e clearance del foro regolabile
//      per infilarlo senza romperlo.
//
//  PEZZI DA STAMPARE: body, shaft, ratchet, handle, pawl  (1x ciascuno).
//  Monta: shaft nelle sedi a U -> ratchet sulla chiave -> handle -> infila il
//  pawl sul pernetto del corpo (eventualmente con un elastichino sulla codina).
//
//  USO
//    - tube_width = larghezza del tuo tubo (misurata da piatto).
//    - part = pezzo da generare / esportare.
//    - F5 anteprima, F6 render, Export STL. Oppure usa il Customizer.
// =============================================================================

/* [Pezzo da generare] */
part = "assembly"; // [assembly, body, shaft, handle, ratchet, pawl, print_plate]

/* [Tubo] */
// Larghezza del tubo misurato da piatto (dentifricio ~45, crema mani ~60)
tube_width = 60;      // [20:1:130]
// Margine extra di larghezza rispetto al tubo
tube_margin = 8;      // [0:1:30]

/* [Shaft - la barra che arrotola] */
shaft_thickness = 6;  // [3:0.5:10]
shaft_height = 14;    // [8:1:24]
// Larghezza della fessura dove entra il bordo del tubo
slot_width = 2.4;     // [1.0:0.1:5.0]
// Profondita' della fessura
slot_depth = 10;      // [4:1:20]
// Diametro dei perni d'estremita'
pin_dia = 8;          // [5:0.5:14]
// Lunghezza di ciascun perno
pin_len = 10;         // [6:1:18]

/* [Corpo a U] */
body_wall = 4;        // [2:0.5:8]
// Altezza dei montanti (quanto e' alto il telaio)
post_height = 40;     // [24:1:70]
// Gioco dei perni nelle sedi (rotazione fluida)
pin_clearance = 0.4;  // [0.1:0.05:0.8]
// Profondita' della sede a U in cui cade il perno
seat_depth = 6;       // [3:0.5:12]

/* [Ratchet - disco dentato RINFORZATO] */
teeth = 14;           // [8:1:28]
ratchet_dia = 24;     // [14:1:44]
// ROBUSTEZZA: spessore disco (originale 4; piu' alto = piu' forte)
ratchet_thickness = 6;   // [3:0.5:12]
// ROBUSTEZZA: altezza mozzo rinforzato attorno al foro
ratchet_hub = 5;         // [0:0.5:12]
// Diametro del mozzo rinforzato
ratchet_hub_dia = 15;    // [8:1:24]
// TOLLERANZA: gioco del foro sulla chiave (piu' alto = piu' facile infilare)
ratchet_fit_clearance = 0.3; // [0.0:0.05:0.8]
// Altezza (profondita' radiale) del dente
tooth_depth = 2.6;    // [1:0.2:5]

/* [Pawl - lamella elastica a C (molla integrata, pezzo separato)] */
// Spessore del pawl lungo l'asse (= altezza di stampa a plano)
pawl_thickness = 5;    // [3:0.5:10]
// Spessore della lamella elastica (sottile = flette di piu', ma meno forza)
pawl_spring_t = 1.6;   // [0.8:0.1:3.0]
// Distanza dell'arco-molla OLTRE la punta dei denti (sta fuori dal ratchet)
pawl_arc_gap = 2.5;    // [1:0.5:8]
// Apertura dell'arco in gradi (quanto e' lungo l'arco elastico)
pawl_arc_deg = 200;    // [120:5:300]
// Larghezza del becco che cade nella valle dei denti
pawl_beak_w = 3.0;     // [1.5:0.1:5]
// Quanto il becco affonda oltre la cresta dei denti (presa nella valle)
pawl_engage = 1.6;     // [0.5:0.1:3.0]
// Dimensione del blocchetto di ancoraggio fisso al corpo
pawl_anchor = 6;       // [4:0.5:12]
// Gioco fra pawl e pareti dell'alloggiamento (stampa + flessione)
pawl_clear = 0.4;      // [0.2:0.05:0.8]

/* [Chiave manopola <-> ratchet/shaft] */
// Lato lungo del profilo chiave
key_long = 8.3;       // [5:0.1:14]
// Lato corto del profilo chiave
key_short = 6.3;      // [4:0.1:12]

/* [Qualita'] */
$fn = 72;

// ---------------------------------------------------------------------------
eps = 0.02;
roll_len     = tube_width + tube_margin;        // luce utile dello shaft
span         = roll_len + 2*body_wall + 2*pin_clearance; // fra interni montanti
body_outer_w = span + 2*body_wall;
shaft_axis_z = post_height - seat_depth/2;      // quota dell'asse di rotazione
key_h_full   = ratchet_thickness + ratchet_hub; // lunghezza chiave dentro ratchet

// profilo rettangolo arrotondato centrato (w lungo X, h lungo Y)
module rrect(w, h, r=1.5) {
    hull() for (sx=[-1,1], sy=[-1,1])
        translate([sx*(w/2-r), sy*(h/2-r)]) circle(r=r);
}
// profilo chiave (rettangolo stondato) centrato
module key2d(a, b) { offset(r=1) offset(r=-1) square([a,b], center=true); }

// ===========================================================================
//  SHAFT  (asse di rotazione = X)
// ===========================================================================
module shaft() {
    color("SteelBlue") {
        difference() {
            // barra centrale
            translate([-roll_len/2,0,0]) rotate([0,90,0])
                linear_extrude(roll_len) rrect(shaft_height, shaft_thickness, 1.5);
            // fessura per il bordo del tubo
            cube([roll_len+eps, slot_width, slot_depth*2], center=true);
        }
        // perno liscio sinistro
        translate([-roll_len/2-pin_len,0,0]) rotate([0,90,0])
            cylinder(d=pin_dia, h=pin_len+eps);
        // perno destro + prolunga con CHIAVE sagomata per manopola e ratchet
        translate([roll_len/2,0,0]) rotate([0,90,0])
            cylinder(d=pin_dia, h=pin_len+eps);
        // moncone-chiave oltre il perno destro
        translate([roll_len/2+pin_len,0,0]) rotate([0,90,0])
            linear_extrude(key_h_full + 6) key2d(key_short, key_long);
    }
}

// ===========================================================================
//  CORPO a U  + sede perni + LAMELLA anti-ritorno
// ===========================================================================
// ---- Posizioni chiave lungo l'asse X (coerenti con assembly) --------------
ratchet_cx    = roll_len/2 + pin_len;              // X dove inizia il ratchet
ratchet_mid_x = ratchet_cx + ratchet_thickness/2;  // X piano medio del ratchet
post_outer_x  = span/2 + body_wall;                // faccia esterna montante dx

// ===========================================================================
//  LAMELLA ELASTICA a C (molla integrata) + suo alloggiamento
//
//  Geometria nel piano del ratchet (u = world Y, v = world Z - shaft_axis_z),
//  centro del ratchet nell'origine (u,v)=(0,0).
//    - r_out = raggio punta denti.
//    - Il BECCO cade a un certo angolo beak_a, affondando pawl_engage nella
//      valle: appoggia contro il fianco ripido del dente -> blocca.
//    - La MOLLA e' un ARCO lungo (raggio pawl_arc_r, apertura pawl_arc_deg)
//      concentrico al ratchet: flette dolcemente, poco stress, non si rompe.
//    - L'ANCORAGGIO e' un blocchetto all'altra estremita' dell'arco, incastrato
//      in una tasca del corpo: e' il riscontro fisso della molla.
//    - Tutto vive in un ALLOGGIAMENTO (tasca) ricavato nel supporto del corpo,
//      con gioco pawl_clear per lasciar flettere la lamella.
// ===========================================================================
r_out      = ratchet_dia/2;                   // raggio punta denti
// L'arco-molla sta SEMPRE fuori dalla circonferenza dei denti:
pawl_arc_r = r_out + pawl_arc_gap + pawl_spring_t/2; // raggio medio arco
pawl_x0     = ratchet_cx + ratchet_thickness;  // X faccia esterna del ratchet
// angoli (nel piano u-v) di becco e ancoraggio dell'arco
beak_a     = 90;                              // becco in cima al ratchet
anchor_a   = beak_a + pawl_arc_deg;           // altro capo dell'arco

// util: punto (u,v) a raggio r e angolo a
function uv(r,a) = [r*cos(a), r*sin(a)];

// Profilo 2D della lamella (nel piano u-v): arco-molla + becco + ancoraggio.
// IL BECCO E' RICAVATO PER SOTTRAZIONE del profilo denti dal tab terminale,
// cosi' la faccia che ingrana e' per costruzione il negativo del dente:
// si incastra sempre perfettamente nella valle, senza calcoli di angoli.
beak_span = 360/teeth * 1.2;   // ampiezza angolare del tab del becco
module pawl_lamella_2d() {
    difference() {
        union() {
            // 1) arco-molla: corona circolare settoriale [beak_a .. anchor_a]
            intersection() {
                difference() {
                    circle(r = pawl_arc_r + pawl_spring_t/2);
                    circle(r = pawl_arc_r - pawl_spring_t/2);
                }
                pie_slice(beak_a, anchor_a, pawl_arc_r + pawl_spring_t);
            }
            // 2) TAB del becco: all'estremita' beak_a, un settore pieno che
            //    va dall'arco fin DENTRO il cerchio dei denti.
            intersection() {
                difference() {
                    circle(r = pawl_arc_r + pawl_spring_t/2);
                    circle(r = r_out - pawl_engage);   // scende dentro la valle
                }
                pie_slice(beak_a, beak_a + beak_span, pawl_arc_r + pawl_spring_t);
            }
            // 3) ancoraggio al corpo (capo opposto)
            translate(uv(pawl_arc_r, anchor_a))
                rotate(anchor_a)
                    square([pawl_anchor, pawl_anchor], center=true);
        }
        // 4) SOTTRAI i denti (ingranditi del gioco) -> il tab prende la forma
        //    esatta per incastrarsi nella valle lasciando scorrere la rampa.
        offset(r = pawl_clear) ratchet_profile2d();
    }
}

// settore circolare (pie) da a0 a a1
module pie_slice(a0, a1, r) {
    pts = [ [0,0], for (a=[a0:2:a1]) uv(r,a), uv(r,a1) ];
    polygon(pts);
}

// Supporto sul corpo: blocco che tiene l'ancoraggio della lamella e forma
// l'alloggiamento (la tasca dove la lamella flette). Sta fuori dal montante dx.
module pawl_mount() {
    // blocco di base attorno all'ancoraggio
    plate_t = pawl_thickness + 2;
    translate([pawl_x0 - eps, 0, shaft_axis_z])
        rotate([0,-90,0])
            // nel piano u-v: un blocco attorno al punto di ancoraggio
            linear_extrude(plate_t)
                translate(uv(pawl_arc_r, anchor_a))
                    rotate(anchor_a)
                        square([pawl_anchor + 4, pawl_anchor + 4], center=true);
}

module post(side) {
    // side = -1 sinistra, +1 destra. Montante con sede a U aperta in alto.
    x = side*(span/2 + body_wall/2);
    difference() {
        translate([x,0,post_height/2])
            cube([body_wall, shaft_height+2*body_wall, post_height], center=true);
        // sede a U: semicerchio + taglio verticale fino in cima
        translate([x, 0, shaft_axis_z]) rotate([0,90,0])
            cylinder(d=pin_dia+2*pin_clearance, h=body_wall+2*eps, center=true);
        translate([x, 0, shaft_axis_z + seat_depth/2])
            cube([body_wall+2*eps, pin_dia+2*pin_clearance, seat_depth], center=true);
    }
}

module base() {
    translate([0,0,body_wall/2])
        cube([body_outer_w, shaft_height+2*body_wall, body_wall], center=true);
}

module body() {
    color("Khaki") {
        base();
        post(-1);
        post(+1);
        pawl_mount();    // supporto + pernetto del nottolino (pezzo separato)
    }
}

// ===========================================================================
//  MANOPOLA  (chiave passante -> trascina lo shaft; leva per girare)
// ===========================================================================
module handle() {
    color("IndianRed")
    difference() {
        union() {
            // mozzo + leva
            hull() {
                cylinder(d=pin_dia+10, h=shaft_thickness+3);
                translate([ratchet_dia*1.5,0,0]) cylinder(d=11, h=shaft_thickness+3);
            }
        }
        // foro chiave passante (con un filo di gioco per assemblaggio)
        translate([0,0,-eps]) rotate([0,0,0])
            linear_extrude(shaft_thickness+3+2*eps)
                key2d(key_short+0.3, key_long+0.3);
    }
}

// ===========================================================================
//  RATCHET  (denti asimmetrici + mozzo rinforzato + clearance)
// ===========================================================================
// Profilo 2D del ratchet a denti ASIMMETRICI (vero profilo a sega).
// Ogni dente: fronte radiale ripido (blocca), dorso tangenziale inclinato
// (lascia scorrere). Il verso di blocco dipende da RATCHET_CW.
RATCHET_CW = true;  // true = blocca la rotazione oraria vista dal lato denti
module ratchet_profile2d() {
    r_out = ratchet_dia/2;
    r_in  = r_out - tooth_depth;
    pitch = 360/teeth;
    dir = RATCHET_CW ? 1 : -1;
    points = [ for (i=[0:teeth-1])
                 let(a0 = i*pitch, a1 = (i+1)*pitch)
                 each [
                    // punta del dente (raggio esterno) all'inizio del passo
                    [r_out*cos(dir*a0), r_out*sin(dir*a0)],
                    // scende al raggio interno appena prima: fronte ripido
                    [r_in *cos(dir*a1), r_in *sin(dir*a1)]
                 ]
             ];
    polygon(points);
}

module ratchet() {
    color("SeaGreen")
    difference() {
        union() {
            // disco dentato (profilo a sega asimmetrico)
            linear_extrude(ratchet_thickness) ratchet_profile2d();
            // mozzo rinforzato attorno al foro
            if (ratchet_hub > 0) cylinder(d=ratchet_hub_dia, h=ratchet_thickness+ratchet_hub);
        }
        // foro chiave passante con clearance regolabile (facile da infilare)
        translate([0,0,-eps])
            linear_extrude(ratchet_thickness+ratchet_hub+2*eps)
                key2d(key_short+2*ratchet_fit_clearance, key_long+2*ratchet_fit_clearance);
    }
}

// ===========================================================================
//  PAWL  -> da estrusione del profilo lamella (vedi pawl_lamella_2d sopra).
// ===========================================================================
// La lamella come pezzo 3D: estrusione del profilo u-v lungo lo spessore.
module pawl() {
    color("DarkOrange")
        linear_extrude(pawl_thickness) pawl_lamella_2d();
}

// Porta la lamella nel piano del ratchet (world Y-Z), spessore lungo world X.
// Mappa: local X(u) -> world Y ; local Y(v) -> world Z-shaft_axis_z ;
//        local Z (spessore) -> world X, a partire dalla faccia esterna ratchet.
module pawl_placed() {
    multmatrix([
        [0, 0, 1, pawl_x0],          // world X = local Z + faccia ratchet
        [1, 0, 0, 0],                // world Y = local X (u)
        [0, 1, 0, shaft_axis_z],     // world Z = local Y (v) + centro ratchet
        [0, 0, 0, 1]
    ]) pawl();
}

// ===========================================================================
//  LAYOUT
// ===========================================================================
module assembly() {
    body();
    // shaft appoggiato nelle sedi
    translate([0,0,shaft_axis_z]) shaft();
    // ratchet calettato sulla chiave, lato destro
    translate([roll_len/2+pin_len, 0, shaft_axis_z]) rotate([0,90,0]) ratchet();
    // manopola oltre il ratchet
    translate([roll_len/2+pin_len+key_h_full+1, 0, shaft_axis_z]) rotate([0,90,0]) handle();
    // nottolino in presa sui denti
    pawl_placed();
}

module print_plate() {
    // tutto appoggiato sul piano, orientato per stampa senza supporti
    translate([0, 0, 0]) body();
    translate([0, shaft_height+2*body_wall+15, shaft_thickness/2]) rotate([90,0,0]) shaft();
    translate([-ratchet_dia, -ratchet_dia-10, 0]) ratchet();
    translate([ ratchet_dia, -ratchet_dia-10, 0]) handle();
    translate([0, -ratchet_dia-20, 0]) pawl();
}

// ===========================================================================
//  DISPATCH
// ===========================================================================
if      (part == "assembly")    assembly();
else if (part == "body")        body();
else if (part == "shaft")       shaft();
else if (part == "handle")      handle();
else if (part == "ratchet")     ratchet();
else if (part == "pawl")        pawl();
else if (part == "pawl_test") {
    // solo ratchet + nottolino, per tarare la presa
    translate([roll_len/2+pin_len, 0, shaft_axis_z]) rotate([0,90,0]) ratchet();
    pawl_placed();
}
else if (part == "pawl_test2d") {
    // overlay 2D nel piano u-v: profilo denti + lamella (per tarare la presa)
    color("SeaGreen", 0.55)   linear_extrude(1) ratchet_profile2d();
    color("DarkOrange", 0.9)  linear_extrude(2) pawl_lamella_2d();
}
else if (part == "print_plate") print_plate();
