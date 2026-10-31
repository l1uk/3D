// =====================================================================
// CONCEPT C - "PODIO" (il leggio della discussione di tesi)
// Il telefono sta su un piccolo podio: la facciata frontale resta
// SEMPRE visibile, anche col telefono in carica, e porta il nome.
// Il cavo scende dentro il podio ed esce da un archetto davanti
// (o di lato, il profilo e' aperto).
// Pezzo unico, si stampa DI LATO: zero sbalzi, gli archetti sono ponti corti.
// =====================================================================

/* [Testi] */
riga_sopra = "LAUREA";
nome       = "LUCA";
riga_sotto = "BRUXELLES 2026";
motto      = "BIRRA & WAFFLES";
frase      = "Grazie di tutto!";

/* [Forma] */
alpha    = 62;
W        = 56;    // larghezza (= altezza di stampa)
t        = 3.2;
culla    = 14.5;
L_back   = 60;
u_fronte = -37;   // piede della facciata
u_retro  = 3.6;   // parete posteriore (dietro al cavo)
u_base   = 55;

/* [Cavo USB-C] */
spazio_cavo = 55;  inserzione = 6.5;  asse = 4.5;  margine = 4;

modalita = "assemblato"; // [assemblato, stampa, check]
telefono = true;         // fantasma del telefono nella vista assemblata
$fn = 48;

// ---------------------------------------------------------------------
r = t/2;
d = [cos(alpha), sin(alpha)];
n = [-sin(alpha), cos(alpha)];
tratto = spazio_cavo - inserzione;
hE = margine + tratto*sin(alpha) - asse*cos(alpha);
E  = [0, hE];
function P(a, b) = E + a*d + b*n;
function arc(c, R, a0, a1, k=12) = [for (i=[0:k]) c + R*[cos(a0+(a1-a0)*i/k), sin(a0+(a1-a0)*i/k)]];
module stroke(p) for (i=[0:len(p)-2]) hull() { translate(p[i]) circle(r); translate(p[i+1]) circle(r); }
module on_plane() multmatrix([[1,0,0,0],[0,d[0],n[0],E[0]],[0,d[1],n[1],E[1]],[0,0,0,1]]) children();

cg = (E + (165/2)*d + 4.5*n)[0];
echo(str("C: bordo telefono a ", hE, " mm, baricentro u=", cg, ", appoggio u=", u_fronte, "..", u_base));

F_top  = P(-r, culla+r);                 // fronte della culla
z_deck = F_top[1];
B0 = [u_fronte, r];                      // facciata: piede
B1 = [u_fronte + 2.5, z_deck];           // facciata: cima (leggermente inclinata)
v  = (B1 - B0) / norm(B1 - B0);
nf = [-v[1], v[0]];                      // normale della facciata, verso il davanti

module profilo() {
    stroke([P(0,-r), P(L_back,-r)]);                         // schienale
    stroke([P(-r,-r), F_top, P(5,culla+r)]);                 // culla + labbro
    stroke([F_top, B1, B1 + [-2.2, 0]]);                     // piano + cornice
    stroke([B1, B0]);                                         // facciata
    stroke(concat([P(-r,-r), [u_retro, hE-8]],               // parete post. + base
                  arc([u_retro+6, r+6], 6, 180, 270),
                  arc([u_base, r+6], 6, 270, 360)));
}

module stand() difference() {
    rotate([90,0,90]) linear_extrude(W, center=true) profilo();
    on_plane() translate([-7.5, -t-1, 0.8]) cube([15, t+1.5, 7.4]);
    // archetti passacavo: davanti e dietro
    for (u = [u_fronte - 3, u_retro - 3]) translate([0, u, 0]) archetto(10);
    // incisioni
    multmatrix([[1,0,0,0],[0,v[0],nf[0],B0[0]+r*nf[0]],[0,v[1],nf[1],B0[1]+r*nf[1]],[0,0,0,1]])
        translate([0, 0, -0.8]) linear_extrude(0.9) testi_facciata();
    on_plane() translate([0, 0, -0.8]) linear_extrude(0.9) testi_schienale();
}
module archetto(l) {
    rotate([-90,0,0]) linear_extrude(l) hull() {
        translate([-8, 1]) square([16, 1]);
        translate([0, -4]) circle(r=7);   // arco alto ~11 mm
    }
}

module testi_facciata() {
    translate([0, 40]) text(riga_sopra, size=4, spacing=1.35, font="Liberation Sans:style=Bold", halign="center", valign="center");
    translate([0, 28.5]) text(nome, size=11, font="Liberation Sans:style=Bold", halign="center", valign="center");
    translate([0, 17]) text(riga_sotto, size=4, font="Liberation Sans:style=Bold", halign="center", valign="center");
}
module testi_schienale() {
    translate([0, 44]) scale(0.8) tocco();
    translate([0, 26]) text(motto, size=3.6, font="Liberation Sans:style=Bold", halign="center", valign="center");
    translate([0, 17]) text(frase, size=4, font="Liberation Sans:style=Bold Italic", halign="center", valign="center");
}
module tocco() {
    rotate(45) square([15,15], center=true);
    translate([0,-5.5]) scale([1.3,0.7]) circle(r=5);
    polygon([[0,0],[6,-3],[8,-10],[6.5,-10],[4.5,-3]]);
}

module cavo() on_plane() {
    translate([0, inserzione, asse]) rotate([90,0,0]) cylinder(d=4, h=spazio_cavo);
    translate([-5.5, -20, asse-3]) cube([11, 20, 6]);
}
module fantasmi() {
    if (telefono) %on_plane() translate([-38,0,0]) cube([76,165,9]);
    %cavo();
    %translate([-70,-70,-1]) cube([140,170,1]);
}

if (modalita == "assemblato") { color("Goldenrod") stand(); fantasmi(); }
else if (modalita == "stampa") translate([0,0,W/2]) rotate([0,-90,0]) stand();
else if (modalita == "check") intersection() { stand(); cavo(); }
