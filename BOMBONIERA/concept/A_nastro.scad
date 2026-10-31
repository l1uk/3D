// =====================================================================
// CONCEPT A - "NASTRO"
// Un pezzo unico: una striscia continua che fa schienale, culla, gamba,
// base e coda. Si stampa DI LATO (profilo sul piatto): zero sbalzi.
// Il telefono (76 mm) sporge ai lati: lo stand sparisce dietro.
// =====================================================================

/* [Testi] */
riga_sopra = "LAUREA";
nome       = "LUCA";
riga_sotto = "BRUXELLES 2026";
motto      = "BIRRA & WAFFLES";
frase      = "Grazie di tutto!";

/* [Forma] */
alpha    = 62;    // inclinazione del telefono dall'orizzontale
W        = 50;    // larghezza (= altezza di stampa)
t        = 3.6;   // spessore della striscia
culla    = 14.5;  // spessore max telefono + cover
L_back   = 60;    // lunghezza schienale dalla culla
R_gamba  = 10;    // raggio del piede anteriore
u_gamba  = 3.8;   // gamba verticale, dietro al cavo
u_base   = 55;    // fine della base (stabilita')

/* [Cavo USB-C] */
spazio_cavo = 55;  inserzione = 6.5;  asse = 4.5;  margine = 4;

modalita = "assemblato"; // [assemblato, stampa, check]
telefono = true;         // fantasma del telefono nella vista assemblata
$fn = 48;

// ---------------------------------------------------------------------
r = t/2;
d = [cos(alpha), sin(alpha)];       // lungo il telefono, verso l'alto
n = [-sin(alpha), cos(alpha)];      // normale, verso il davanti
tratto = spazio_cavo - inserzione;
hE = margine + tratto*sin(alpha) - asse*cos(alpha);  // bordo inferiore telefono
E  = [0, hE];
function P(a, b) = E + a*d + b*n;
function arc(c, R, a0, a1, k=12) = [for (i=[0:k]) c + R*[cos(a0+(a1-a0)*i/k), sin(a0+(a1-a0)*i/k)]];
module stroke(p) for (i=[0:len(p)-2]) hull() { translate(p[i]) circle(r); translate(p[i+1]) circle(r); }
module on_plane() multmatrix([[1,0,0,0],[0,d[0],n[0],E[0]],[0,d[1],n[1],E[1]],[0,0,0,1]]) children();

cg = (E + (165/2)*d + 4.5*n)[0];   // baricentro di un telefono da 165 mm
echo(str("A: bordo telefono a ", hE, " mm, baricentro u=", cg, ", appoggio u=", u_gamba+R_gamba-3, "..", u_base));

module profilo() {
    stroke([P(0,-r), P(L_back,-r)]);                       // schienale
    stroke([P(-r,-r), P(-r,culla+r), P(5,culla+r)]);       // culla + labbro
    stroke(concat([P(-r,-r), [u_gamba, hE-8]],             // gamba, base, coda
                  arc([u_gamba+R_gamba, r+R_gamba], R_gamba, 180, 270),
                  arc([u_base, r+6], 6, 270, 360)));
}

module stand() difference() {
    rotate([90,0,90]) linear_extrude(W, center=true) profilo();
    on_plane() translate([-7.5, -t-1, 0.8]) cube([15, t+1.5, 7.4]);   // passaggio plug
    on_plane() translate([0, 0, -0.8]) linear_extrude(0.9) testi();
}

module testi() {
    translate([0, 51]) scale(0.6) tocco();
    translate([0, 41]) text(riga_sopra, size=3.4, spacing=1.3, font="Liberation Sans:style=Bold", halign="center", valign="center");
    translate([0, 32]) text(nome, size=9, font="Liberation Sans:style=Bold", halign="center", valign="center");
    translate([0, 22]) text(riga_sotto, size=3.6, font="Liberation Sans:style=Bold", halign="center", valign="center");
    translate([0, 15.5]) text(motto, size=3.2, font="Liberation Sans:style=Bold", halign="center", valign="center");
    translate([0, 9]) text(frase, size=3.4, font="Liberation Sans:style=Bold Italic", halign="center", valign="center");
}
module tocco() {
    rotate(45) square([15,15], center=true);
    translate([0,-5.5]) scale([1.3,0.7]) circle(r=5);
    polygon([[0,0],[6,-3],[8,-10],[6.5,-10],[4.5,-3]]);
}

module cavo() on_plane() {
    translate([0, inserzione, asse]) rotate([90,0,0]) cylinder(d=4, h=spazio_cavo);
    translate([-5.5, -20, asse-3]) cube([11, 20, 6]);      // overmold
}
module fantasmi() {
    if (telefono) %on_plane() translate([-38,0,0]) cube([76,165,9]);
    %cavo();
    %translate([-70,-60,-1]) cube([140,160,1]);
}

if (modalita == "assemblato") { color("SteelBlue") stand(); fantasmi(); }
else if (modalita == "stampa") translate([0,0,W/2]) rotate([0,-90,0]) stand();
else if (modalita == "check") intersection() { stand(); cavo(); }
