// =====================================================================
// CONCEPT D - "POLTRONCINA"
// Il telefono "si siede": la seduta e' alta quanto serve al cavo, il plug
// scende in un foro nella seduta ed esce davanti tra le gambe.
// Flat-pack: 4 pezzi piatti (2 fianchi uguali, seduta, schienale a doghe)
// uniti a tenone e mortasa, si stampano piatti senza supporti.
// "Grazie di tutto!" sulla seduta resta visibile anche col telefono.
// =====================================================================

/* [Testi] */
riga_sopra = "LAUREA";
nome       = "LUCA";
riga_sotto = "BRUXELLES 2026";
motto      = "BIRRA & WAFFLES";
frase      = "Grazie di tutto!";

/* [Forma] */
alpha    = 65;     // inclinazione schienale/telefono
sp       = 3.6;    // spessore dei pannelli
W_tot    = 71.2;   // larghezza seduta e schienale
x_fianco = 30;     // asse dei fianchi
u_front  = -34;    // bordo anteriore seduta
u_back   = 4.3;    // bordo posteriore seduta
L_back   = 88;     // altezza schienale lungo l'inclinazione
clearance = 0.3;

/* [Cavo USB-C] */
spazio_cavo = 55;  inserzione = 6.5;  asse = 4.5;  margine = 4;

modalita = "assemblato"; // [assemblato, stampa, check]
telefono = true;         // fantasma del telefono nella vista assemblata
$fn = 48;

// ---------------------------------------------------------------------
d = [cos(alpha), sin(alpha)];
n = [-sin(alpha), cos(alpha)];
tratto = spazio_cavo - inserzione;
z_seat = margine + tratto*sin(alpha) - asse*cos(alpha);   // piano seduta
E  = [0, z_seat];
function P(a, b) = E + a*d + b*n;
module on_plane() multmatrix([[1,0,0,0],[0,d[0],n[0],E[0]],[0,d[1],n[1],E[1]],[0,0,0,1]]) children();
module off_plane() multmatrix([[1,0,0,0],[0,d[0],d[1],-(d*E)],[0,n[0],n[1],-(n*E)],[0,0,0,1]]) children();

cg = (E + (165/2)*d + 4.5*n)[0];
echo(str("D: seduta a ", z_seat, " mm, baricentro u=", cg, ", appoggio u=-31..54"));

tenoni_seduta   = [-24, -6];   // posizioni (u) dei tenoni sotto la seduta
tenoni_schienale = [18, 58];   // posizioni (a) dei tenoni dietro lo schienale
lt = 12;                        // lunghezza tenone

// ---------------- SEDUTA (piatta, coordinate x,u) ----------------
module seduta_2d() difference() {
    offset(r=4) offset(delta=-4) translate([-W_tot/2, u_front]) square([W_tot, u_back - u_front]);
    hull() for (u = [-10.5+3, -0.3-3]) translate([0, u]) offset(r=3) square([15-6, 0.01], center=true); // foro plug
    for (s=[-1,1], u=tenoni_seduta)
        translate([s*x_fianco, u]) square([sp+clearance, lt+clearance], center=true);
}
module seduta() {
    difference() {
        linear_extrude(sp) seduta_2d();
        translate([0, -26, sp-0.8]) linear_extrude(1) text(frase, size=4.2,
            font="Liberation Sans:style=Bold Italic", halign="center", valign="center");
    }
    // listello ferma-telefono (davanti a qualsiasi telefono fino a 14.5 mm)
    translate([-28, -17.3, 0]) cube([56, 2.6, sp+1.6]);
}

// ---------------- SCHIENALE (piatto, coordinate x,a) ----------------
module schienale_2d() difference() {
    hull() {
        translate([-W_tot/2, -4]) square([W_tot, 1]);
        for (s=[-1,1]) translate([s*(W_tot/2-10), L_back-10]) circle(r=10);
    }
    for (x=[-19,-7,7,19]) hull() for (a=[8,44]) translate([x, a]) circle(r=2.5);   // doghe
    for (s=[-1,1], a=tenoni_schienale)
        translate([s*x_fianco, a]) square([sp+clearance, lt+clearance], center=true);
}
module schienale_testi() {
    translate([0, 80]) scale(0.55) tocco();
    translate([0, 70]) text(riga_sopra, size=3.6, spacing=1.35, font="Liberation Sans:style=Bold", halign="center", valign="center");
    translate([0, 60.5]) text(nome, size=9, font="Liberation Sans:style=Bold", halign="center", valign="center");
    translate([0, 51.5]) text(riga_sotto, size=3.6, font="Liberation Sans:style=Bold", halign="center", valign="center");
    translate([0, 3]) text(motto, size=3.2, font="Liberation Sans:style=Bold", halign="center", valign="center");
}
// schienale montato: piastra dietro il piano del telefono, tagliata sul piano seduta
module schienale_montato() intersection() {
    on_plane() difference() {
        translate([0,0,-sp]) linear_extrude(sp) schienale_2d();
        translate([0,0,-0.8]) linear_extrude(0.9) schienale_testi();
    }
    translate([-50, -50, z_seat]) cube([100, 200, 200]);
}

// ---------------- FIANCO (piatto, coordinate u,z) ----------------
rr = 3.5;
module st(p) for (i=[0:len(p)-2]) hull() { translate(p[i]) circle(rr); translate(p[i+1]) circle(rr); }
function Q(s) = E - n*(sp + rr) + d*s;   // asse del montante dietro lo schienale
z_rail = z_seat - sp - rr;
module fianco_2d() {
    difference() {
        union() {
            st([[-31, rr], [-28, rr], [-28, z_rail], [u_back - 2, z_rail]]);    // gamba ant. + traverso
            st([[u_back - 2, z_rail], Q(78)]);                                    // montante
            st([[u_back - 2, z_rail], [48, rr], [55, rr]]);                       // gamba posteriore
        }
        // spazio per seduta e schienale (con gioco)
        translate([u_front - 5, z_seat - sp - 0.25]) square([u_back - u_front + 5.25, 30]);
        intersection() {
            polygon([P(-10, 0.25), P(100, 0.25), P(100, -sp-0.25), P(-10, -sp-0.25)]);
            translate([-100, z_seat - 0.25]) square([300, 300]);
        }
    }
    // tenoni
    for (u = tenoni_seduta) translate([u - lt/2, z_seat - sp - 0.5]) square([lt, sp + 0.3]);
    for (a = tenoni_schienale)
        polygon([P(a-lt/2, -sp-0.5), P(a+lt/2, -sp-0.5), P(a+lt/2, -0.2), P(a-lt/2, -0.2)]);
}
module fianco_montato(s) translate([s*x_fianco - sp/2, 0, 0]) rotate([90,0,90]) linear_extrude(sp) fianco_2d();

module tocco() {
    rotate(45) square([15,15], center=true);
    translate([0,-5.5]) scale([1.3,0.7]) circle(r=5);
    polygon([[0,0],[6,-3],[8,-10],[6.5,-10],[4.5,-3]]);
}

module stand() {
    color("Sienna") translate([0, 0, z_seat - sp]) seduta();
    color("Peru") schienale_montato();
    color("SaddleBrown") for (s=[-1,1]) fianco_montato(s);
}

module cavo() on_plane() {
    translate([0, inserzione, asse]) rotate([90,0,0]) cylinder(d=4, h=spazio_cavo);
    translate([-5.5, -20, asse-3]) cube([11, 20, 6]);
}
module fantasmi() {
    if (telefono) %on_plane() translate([-38,0,0]) cube([76,165,9]);
    %cavo();
    %translate([-70,-60,-1]) cube([140,160,1]);
}

if (modalita == "assemblato") { stand(); fantasmi(); }
else if (modalita == "stampa") {
    // layout per piatto 220x220 (ingombro ~195 x 191)
    translate([40.6, 0.5, 0]) seduta();
    translate([40.6, 10, sp]) off_plane() schienale_montato();
    for (i=[0,1]) translate([0, i*98, 0]) rotate(90) linear_extrude(sp) fianco_2d();
}
else if (modalita == "check") intersection() { stand(); cavo(); }
