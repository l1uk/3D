// =====================================================================
// PHONE HOLDER BOMBONIERA DI LAUREA - v6 "PANCHINA"
// Una panchina da parco in miniatura: il telefono si siede.
//  - seduta alta quanto serve al cavo USB-C dritto, inclinata di 6 gradi
//    all'indietro: il telefono scivola nell'angolo e resta li'
//  - il plug passa tra le doghe (foro centrale) ed esce davanti
//  - targhetta "commemorativa" sullo schienale, come sulle panchine vere
//  - frase sulla doga anteriore: resta visibile col telefono appoggiato
// 4 pezzi piatti (2 fianchi uguali, seduta, schienale): seduta e schienale
// hanno linguette alle estremita' che entrano nei fianchi, a filo.
// Ender 3 V2 - PLA - stampa piatta, ZERO supporti
// =====================================================================

/* [Testi] */
targa_riga1 = "DOTT. LUCA";
targa_riga2 = "BRUXELLES · MMXXVI";
frase       = "Grazie di esserci stati.";
mostra_targa = true;
mostra_frase = true;

/* [Panchina (mm)] */
alpha      = 65;    // inclinazione schienale = telefono
beta       = 6;     // inclinazione all'indietro della seduta
sp         = 3.2;   // spessore pannelli
L_in       = 92;    // luce tra i fianchi (telefoni fino a ~86 mm con cover)
w_front    = -36;   // bordo anteriore seduta (dall'angolo seduta/schienale)
w_back     = 4.3;   // la seduta passa sotto lo schienale
h_back     = 46;    // altezza schienale lungo l'inclinazione
bracciolo  = 18;    // altezza braccioli sopra la seduta
clearance  = 0.3;   // gioco totale linguetta/foro (PLA: prova test_incastro)

/* [Cavo USB-C] */
spazio_cavo = 55;   // tratto dritto: dalla punta del plug a dove si piega
inserzione  = 6.5;
asse        = 4.5;  // asse della porta dalla schiena del telefono
margine     = 4;    // aria tra la piega del cavo e il tavolo

/* [Vista] */
modalita = "assemblato"; // [assemblato, stampa, seduta, schienale, fianco, test_incastro, check]
telefono = true;
$fn = 48;

// =====================================================================
// GEOMETRIA
// =====================================================================
d = [cos(alpha), sin(alpha)];        // lungo lo schienale, verso l'alto
n = [-sin(alpha), cos(alpha)];       // normale schienale, verso il davanti
g = [cos(beta), -sin(beta)];         // lungo la seduta, verso il retro
m = [sin(beta), cos(beta)];          // normale seduta, verso l'alto
tratto = spazio_cavo - inserzione;
z_E = margine + tratto*sin(alpha) - asse*cos(alpha);   // angolo seduta/schienale
E = [0, z_E];
function P(a, b) = E + a*d + b*n;    // piano schienale
function S(w, h) = E + w*g + h*m;    // piano seduta
function bez(p0, p1, p2, k=16) = [for (i=[0:k]) let(t=i/k) (1-t)*(1-t)*p0 + 2*(1-t)*t*p1 + t*t*p2];

module on_back() multmatrix([[1,0,0,0],[0,d[0],n[0],E[0]],[0,d[1],n[1],E[1]],[0,0,0,1]]) children();
module off_back() multmatrix([[1,0,0,0],[0,d[0],d[1],-(d*E)],[0,n[0],n[1],-(n*E)],[0,0,0,1]]) children();
module on_seat() multmatrix([[1,0,0,0],[0,g[0],m[0],E[0]],[0,g[1],m[1],E[1]],[0,0,0,1]]) children();

x_in  = L_in/2;          // faccia interna fianco
x_out = x_in + sp;       // faccia esterna fianco
xi    = x_in - 0.15;     // fine di seduta/schienale
c2    = clearance/2;
lt    = 9;               // lunghezza linguette
ling_seduta    = [-26, -4];     // posizioni (w)
ling_schienale = [6.5, 38];     // posizioni (a)
z_arm = z_E + bracciolo;

// doghe
gap_s = 1.6;  n_s = 5;
doga_s = (w_back - w_front - (n_s-1)*gap_s) / n_s;
gap_b = 2.4;
doghe_b = [[0, 13], [15.4, 28.5], [30.9, h_back]];   // [inizio, fine] lungo a

cg = (E + (165/2)*d + 4.5*n)[0];
echo(str("Seduta a ", z_E, " mm, baricentro telefono u=", cg, " (appoggio -38..56)"));
echo(str("Ingombro panchina: ", 2*x_out, " mm di larghezza"));
assert(cg < 56 - 15, "Instabile: allunga la gamba posteriore");

// =====================================================================
// SEDUTA (coordinate locali x, w; w verso il retro). Stampa: faccia sopra in alto
// =====================================================================
module seduta_2d() difference() {
    union() {
        translate([-xi, w_front]) offset(r=1.2) offset(delta=-1.2) square([2*xi, w_back - w_front]);
        for (s=[-1,1], w=ling_seduta)
            translate([s > 0 ? xi - 0.5 : -x_out, w - lt/2]) square([sp + 0.65, lt]);
    }
    for (i=[1:n_s-1]) let(w0 = w_front + i*doga_s + (i-1)*gap_s)
        translate([-xi + 4, w0]) offset(r=gap_s/2 - 0.01) offset(delta=-(gap_s/2 - 0.01))
            square([2*xi - 8, gap_s]);
    hull() for (w=[-10.5+3, -0.3-3]) translate([0, w]) offset(r=3) square([9, 0.01], center=true);
}
module seduta() difference() {
    linear_extrude(sp, convexity=10) seduta_2d();
    if (mostra_frase)
        translate([0, w_front + doga_s/2, sp - 0.8]) linear_extrude(1, convexity=10)
            text(frase, size=3.4, font="Liberation Sans:style=Bold Italic", halign="center", valign="center");
}
module seduta_montata() on_seat() translate([0, 0, -sp]) seduta();

// =====================================================================
// SCHIENALE (coordinate locali x, a). Stampa: faccia anteriore in alto
// =====================================================================
module schienale_2d() difference() {
    union() {
        translate([-xi, -3]) offset(r=3) offset(delta=-3) square([2*xi, h_back + 3]);
        translate([-xi, -3]) square([2*xi, 6]);                      // base dritta
        for (s=[-1,1], a=ling_schienale)
            translate([s > 0 ? xi - 0.5 : -x_out, a - lt/2]) square([sp + 0.65, lt]);
    }
    for (i=[0:len(doghe_b)-2])
        translate([-xi + 4, doghe_b[i][1]]) offset(r=gap_b/2 - 0.01) offset(delta=-(gap_b/2 - 0.01))
            square([2*xi - 8, gap_b]);
}
module targa_2d() offset(r=1.5) offset(delta=-1.5) square([57, 13.4], center=true);
module schienale() difference() {
    linear_extrude(sp, convexity=10) schienale_2d();
    // targa: incavo di 0.6 mm con le scritte in rilievo
    if (mostra_targa) translate([0, (doghe_b[2][0] + h_back)/2, sp - 0.6]) linear_extrude(1, convexity=10)
        difference() {
            targa_2d();
            difference() { offset(delta=-1.0) targa_2d(); offset(delta=-1.8) targa_2d(); }  // bordino in rilievo
            translate([0, 2.0]) text(targa_riga1, size=4.0, font="Liberation Sans:style=Bold", halign="center", valign="center");
            translate([0, -3.0]) text(targa_riga2, size=2.9, spacing=1.08, font="Liberation Sans:style=Bold", halign="center", valign="center");
        }
}
// montato: dietro il piano del telefono, rifilato sul piano della seduta
module schienale_montato() intersection() {
    on_back() translate([0, 0, -sp]) schienale();
    on_seat() translate([-100, -100, 0]) cube([200, 300, 200]);
}

// =====================================================================
// FIANCO (profilo u, z). Due pezzi uguali.
// =====================================================================
r_band = sp/2 + 3.6;
module st(p, r) for (i=[0:len(p)-2]) hull() { translate(p[i]) circle(r); translate(p[i+1]) circle(r); }
a_arm = (z_arm - z_E + (sp/2)*n[1]) / d[1];          // dove il bracciolo incontra il montante
module fianco_2d() difference() {
    union() {
        st([S(w_front + 2, -sp/2), S(w_back + 1, -sp/2)], r_band);       // traversa seduta
        st([P(-1, -sp/2), P(h_back - 2, -sp/2)], r_band);                // montante schienale
        st([[-33.5, 3], [-35.5, z_arm]], 3);                             // gamba anteriore
        st([[-39, z_arm], [P(a_arm, -sp/2)[0], z_arm]], 3);              // bracciolo
        translate([-39, z_arm]) circle(4.2);                             // pomello
        st(bez(S(w_back, -sp/2), [24, 34], [52, 3]), 3);                 // gamba posteriore
        st([[-39, 3], [-29, 3]], 3);                                     // piedini
        st([[46, 3], [56, 3]], 3);
    }
    for (w = ling_seduta)
        polygon([S(w-lt/2-c2, -sp-c2), S(w+lt/2+c2, -sp-c2), S(w+lt/2+c2, c2), S(w-lt/2-c2, c2)]);
    for (a = ling_schienale)
        polygon([P(a-lt/2-c2, -sp-c2), P(a+lt/2+c2, -sp-c2), P(a+lt/2+c2, c2), P(a-lt/2-c2, c2)]);
}
module fianco() linear_extrude(sp, convexity=10) fianco_2d();
module fianco_montato(s) translate([s > 0 ? x_in : -x_out, 0, 0]) rotate([90,0,90]) fianco();

// =====================================================================
// VISTE
// =====================================================================
module panchina() {
    color("Peru")        seduta_montata();
    color("BurlyWood")   schienale_montato();
    color("SaddleBrown") for (s=[-1,1]) fianco_montato(s);
}
module cavo() on_back() {
    translate([0, inserzione, asse]) rotate([90,0,0]) cylinder(d=4, h=spazio_cavo);
    translate([-5.5, -20, asse-3]) cube([11, 20, 6]);          // overmold
}

if (modalita == "assemblato") {
    panchina();
    if (telefono) %on_back() translate([-38, 0, 0]) cube([76, 165, 9]);
    %cavo();
    %translate([-80, -70, -1]) cube([160, 170, 1]);
}
else if (modalita == "stampa") {   // piatto 220x220: ingombro ~214 x 191
    translate([0, -w_front, 0]) seduta();
    translate([0, 47, sp]) off_back() schienale_montato();
    for (i=[0,1]) translate([i == 0 ? -64.5 : 46.5, -98, 0]) fianco();
}
else if (modalita == "seduta")    seduta();
else if (modalita == "schienale") translate([0, 0, sp]) off_back() schienale_montato();
else if (modalita == "fianco")    fianco();
else if (modalita == "test_incastro") {
    // un angolo di seduta con una linguetta + il pezzo di fianco col suo foro
    intersection() { seduta(); translate([x_in - 12, ling_seduta[0] - 8, -1]) cube([20, 16, 10]); }
    translate([75, 0, 0]) linear_extrude(sp, convexity=10) intersection() {
        fianco_2d(); translate(S(ling_seduta[0], -sp/2)) circle(r=11);
    }
}
else if (modalita == "check") intersection() { panchina(); cavo(); }
