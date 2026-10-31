// =====================================================================
// CONCEPT B - "SOSPESO"
// Telaio triangolare chiuso, il telefono sta sulla punta anteriore e
// sotto c'e' solo aria: il cavo scende libero, il vuoto diventa voluto.
// Pezzo unico, si stampa DI LATO: zero sbalzi.
// =====================================================================

/* [Testi] */
riga_sopra = "LAUREA";
nome       = "LUCA";
riga_sotto = "BRUXELLES 2026";
motto      = "BIRRA & WAFFLES";
frase      = "Grazie di tutto!";

/* [Forma] */
alpha   = 62;
W       = 40;     // larghezza (= altezza di stampa)
t       = 4;      // spessore delle aste
culla   = 14.5;
L_back  = 72;     // schienale dalla culla alla cima del triangolo
u_front = 16;     // appoggio anteriore sul tavolo
u_rear  = 64;     // appoggio posteriore
r_fin   = 7;      // raccordo interno della finestra

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
module stroke(p) for (i=[0:len(p)-2]) hull() { translate(p[i]) circle(r); translate(p[i+1]) circle(r); }
module on_plane() multmatrix([[1,0,0,0],[0,d[0],n[0],E[0]],[0,d[1],n[1],E[1]],[0,0,0,1]]) children();

cg = (E + (165/2)*d + 4.5*n)[0];
echo(str("B: bordo telefono a ", hE, " mm, baricentro u=", cg, ", appoggio u=", u_front, "..", u_rear));

// vertici (linea media delle aste)
V = [P(-r,-r), [u_front, r], [u_rear, r], P(L_back,-r)];

module profilo() {
    difference() {
        offset(r=r) polygon(V);
        offset(r=r_fin) offset(delta=-r-r_fin) polygon(V);
    }
    stroke([P(-r,-r), P(-r,culla+r), P(5,culla+r)]);       // culla + labbro
}

module stand() difference() {
    rotate([90,0,90]) linear_extrude(W, center=true) profilo();
    on_plane() translate([-7.5, -t-1, 0.8]) cube([15, t+1.5, 7.4]);
    on_plane() translate([0, 0, -0.8]) linear_extrude(0.9) testi();
}

module testi() {
    translate([0, 62]) scale(0.55) tocco();
    translate([0, 52]) text(riga_sopra, size=3.2, spacing=1.3, font="Liberation Sans:style=Bold", halign="center", valign="center");
    translate([0, 43]) text(nome, size=8.5, font="Liberation Sans:style=Bold", halign="center", valign="center");
    translate([0, 33]) text(riga_sotto, size=3.3, font="Liberation Sans:style=Bold", halign="center", valign="center");
    translate([0, 26.5]) text(motto, size=3.0, font="Liberation Sans:style=Bold", halign="center", valign="center");
    translate([0, 19]) text(frase, size=3.2, font="Liberation Sans:style=Bold Italic", halign="center", valign="center");
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
    %translate([-70,-60,-1]) cube([140,160,1]);
}

if (modalita == "assemblato") { color("IndianRed") stand(); fantasmi(); }
else if (modalita == "stampa") translate([0,0,W/2]) rotate([0,-90,0]) stand();
else if (modalita == "check") intersection() { stand(); cavo(); }
