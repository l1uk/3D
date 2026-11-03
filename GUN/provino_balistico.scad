// =====================================================================
// PROVINO BALISTICO - revolver giocattolo
// Una sola camera, niente tamburo: serve a tarare trattenuta del bossolo,
// corsa del percussore e forma del proiettile, e a misurare la gittata.
//
// Funzionamento:
//   1. metti il bossolo (con proiettile o pallino) nel blocco camera
//   2. infila il blocco camera nella feritoia dall'alto
//   3. tira indietro il pomolo e giralo di lato nella tacca (armato)
//   4. riportalo in alto: la molla spinge il percussore e spara
//
// Montaggio: percussore dal retro, molla sull'asta, tappo + perno in
// filamento 1.75 nel foro verticale. Il pomolo si infila dall'alto nella
// fessura e va a pressione nel collare. La canna va a pressione nel telaio.
// Il tappo arancione si infila sulla volata.
//
// Munizioni provabili con lo stesso telaio:
//   - bossolo + proiettile cal. 8 (blocco "camera", canna_8)
//   - bossolo + pallino 6 mm      (blocco "camera", canna_6)
//   - cartuccia intera che parte  (blocco "camera_c", canna_c): si infila
//     dal retro del blocco finche' e' a filo, la tiene la fascia ad attrito
// =====================================================================
include <params.scad>
include <lib.scad>

/* [Vista] */
modalita = "assemblato"; // [assemblato, sezione, check, parte]
stato    = "armato";     // [armato, sparato]
munizione = "diabolo";   // [diabolo, volano, ogiva, bb, cart_chiusa, cart_aperta, cart_corta]
parte    = "telaio";     // [telaio, camera, percussore, pomolo, tappo, bossolo_8, bossolo_6, proiettile_diabolo, proiettile_volano, proiettile_ogiva, canna_8, canna_6, volata, camera_c, cartuccia_chiusa, cartuccia_aperta, cartuccia_corta, canna_c]
variante = 0;            // indice dell'interferenza di bossolo o camera_c (0,1,2)

/* [Telaio provino] */
W       = 24;    // larghezza telaio
H       = 22;    // altezza telaio
zb      = 11;    // quota asse canna
L_tappo = 8;     // tratto del tappo dentro il telaio
t_sc    = 3;     // scudo tra percussore e camera
g_tamb  = 0.3;   // gioco camera/scudo e camera/canna (come il tamburo)
t_sp    = 1.5;   // spalla di battuta della canna
L_sede  = 20;    // tratto di canna dentro il telaio
cam_W   = 16;    // blocco camera
cam_H   = 26;
cam_zb  = 9;     // asse rispetto al fondo del blocco camera
cam_L   = 22;    // deve contenere la cartuccia intera

$fn = 64;
eps = 0.01;

// ---------------- Grandezze derivate ----------------
m_Di  = molla_Di(molla_d, molla_De);
m_na  = molla_n_att(molla_n_tot, molla_n_morte);
m_Lp  = molla_L_pacco(molla_d, molla_n_tot);
m_k   = molla_k(molla_d, molla_De, m_na, molla_G);
L1    = molla_L0 - precarico;                        // molla a percussore avanti
corsa = min(corsa_max, L1 - (m_Lp + margine_pacco));
L2    = L1 - corsa;                                  // molla ad armato
E_mJ  = molla_E(m_k, precarico, precarico + corsa);

x_cr_f  = L_tappo + L1;              // retro collare, percussore avanti
x_sc    = x_cr_f + perc_col_L;       // retro scudo (battuta del collare)
x_cam   = x_sc + t_sc + g_tamb;      // retro blocco camera = fondo bossolo
x_spal  = x_cam + cam_L + g_tamb;
x_sede  = x_spal + t_sp;
L_tel   = x_sede + L_sede;

punta_L = t_sc - 0.5 + corsa;        // ad armato la punta resta 0.5 dentro lo scudo
spinta  = corsa - 0.5 - g_tamb - boss_fondo;   // tratto in cui il proiettile e' spinto
spinta_c = corsa - 0.5 - g_tamb;               // la cartuccia e' spinta dal fondello
is_cart = (munizione == "cart_chiusa" || munizione == "cart_aperta" || munizione == "cart_corta");
function cart_L_tot(Lb) = Lb + cart_ogiva_L + cart_punta_L;
asta_d  = m_Di - 0.3;
borch_h = 2;                          // borchia di centraggio sul tappo
asta_L  = L2 - borch_h - 1.5;
boss_L  = boss_fondo + boss_prof;
w_fes   = pomolo_d + 0.6;            // fessura del pomolo
x_pom_f = x_cr_f + perc_col_L/2;     // pomolo a percussore avanti
x_pom_a = x_pom_f - corsa;           // pomolo ad armato
r_pom0  = perc_col_D/2 - 3.5;        // il pomolo entra 3.5 mm nel collare
pom_L   = max(H - zb, W/2) + 0.8 - r_pom0;   // gambo fino a fuori dal telaio
testa_D = 6; testa_h = 4;

// massa percussore (pieno, PLA 1.24 g/cm3) per la stima di velocita'
V_perc = PI/4*(asta_d*asta_d*asta_L + perc_col_D*perc_col_D*perc_col_L
         + perc_punta_d*perc_punta_d*punta_L);
m_perc = V_perc * 1.24e-3;

echo(str("MOLLA: d=", molla_d, " Di=", m_Di, " spire attive=", m_na,
         " pacco=", m_Lp, " k=", m_k, " N/mm"));
echo(str("MOLLA: L1=", L1, " L2=", L2, " corsa=", corsa,
         " F_max=", m_k*(precarico+corsa), " N  energia=", E_mJ, " mJ"));
echo(str("PERCUSSORE: spinta sul proiettile=", spinta, " mm, massa ~", m_perc, " g"));
echo(str("CARTUCCIA: spinta=", spinta_c, " mm, lunghezza ", cart_L_tot(cart_bossolo_L[0]),
         " / corta ", cart_L_tot(cart_bossolo_L[1]), " mm"));
echo(str("TELAIO: lunghezza ", L_tel, " mm, totale con canna ", L_tel - L_sede + canna_L, " mm"));

assert(corsa > 3, "Corsa troppo corta: molla troppo vicina al pacco");
assert(L2 >= m_Lp + margine_pacco, "La molla arriva a pacco");
assert(asta_L > 3 && asta_d > 1.2, "Asta guida molla troppo piccola");
assert(spinta > 2, "Spinta sul proiettile troppo corta");
assert(cam_L >= boss_fondo + 14 + 0.5, "Blocco camera troppo corto per il proiettile");
assert(cam_L >= cart_L_tot(max(cart_bossolo_L)) + 0.5, "Blocco camera troppo corto per la cartuccia");

// =====================================================================
// PROIETTILI (asse Z, fondo a z=0, punta in alto = come si stampano)
// Tutti: fascia posteriore piena da cal. 1.2 mm (trattenuta nel bossolo),
// perno centrale a filo del fondo (spinta del percussore).
// =====================================================================
c = cal_proiettile/2;
perno_r = 1.3;
function arco(r, z0, h, n=12) = [for (i=[1:n]) let(t=90*i/n) [r*cos(t), z0 + h*sin(t)]];

module proiettile(tipo) {
    if (tipo == "diabolo") {
        union() {
            difference() {
                rotate_extrude() polygon(concat([[0,0],[c,0],[c,1.2],[c-1,5],[c,6],[c,7.5]],
                                                arco(c, 7.5, 4)));
                rotate_extrude() polygon([[0,-eps],[c-0.8,-eps],[c-0.8,1.2],[c-1.8,5],[0,5]]);
            }
            cylinder(r=perno_r, h=5.2);
        }
    } else if (tipo == "volano") {
        union() {
            difference() {
                rotate_extrude() polygon(concat([[0,0],[c,0],[c,1.2],[c-0.6,8],[c,8.6],[c,10]],
                                                arco(c, 10, 4)));
                rotate_extrude() polygon([[0,-eps],[c-0.8,-eps],[c-0.8,1.2],[c-1.4,8],[0,8]]);
            }
            cylinder(r=perno_r, h=8.2);
        }
    } else if (tipo == "ogiva") {
        union() {
            difference() {
                rotate_extrude() polygon(concat([[0,0],[c,0],[c,7]], arco(c, 7, 6)));
                rotate_extrude() polygon([[0,-eps],[2.5,-eps],[2.5,4],[0,6.5]]);
            }
            cylinder(r=perno_r, h=6);
        }
    }
}

// =====================================================================
// CARTUCCIA INTERA (asse Z, fondello a z=0, punta in alto = stampa)
// Bossolo cavo a parete sottile + palla piena: baricentro in avanti.
//   chiusa: fondello pieno con innesco decorativo
//   aperta: retro aperto (frena dietro e stabilizza), il perno centrale
//           fa da innesco e riceve la spinta del percussore
//   corta : come aperta ma bossolo piu' corto (piu' leggera, piu' "di punta")
// Fasce di contatto da cart_D solo davanti e dietro, il resto e' scaricato.
// =====================================================================
module cartuccia(tipo) {
    Lb = (tipo == "corta") ? cart_bossolo_L[1] : cart_bossolo_L[0];
    R  = cart_D/2; Rc = cart_D_corpo/2; Rg = cart_gola_D/2; Ro = cart_ogiva_D/2;
    f  = cart_fascia; g0 = f; g1 = f + 0.8;          // gola di estrazione
    ri_g = Rg - cart_parete;                          // cavita' all'altezza della gola
    ri   = Rc - cart_parete;                          // cavita' nel corpo
    fondo = (tipo == "chiusa") ? 1.2 : -eps;
    profilo = concat(
        [[0,0],[R,0],[R,g0],[Rg,g0],[Rg,g1],[Rc,g1 + (Rc-Rg)],
         [Rc,Lb-f],[R,Lb-f],[R,Lb],[Ro,Lb],[Ro,Lb+cart_ogiva_L]],
        arco(Ro, Lb + cart_ogiva_L, cart_punta_L));
    // cavita': stretta alla gola, larga nel corpo, tetto a cono 45 gradi
    cavita = [[0,fondo],[ri_g,fondo],[ri_g,g1+0.5],[ri,g1+0.5+(ri-ri_g)],
              [ri,Lb-ri],[0,Lb]];
    difference() {
        rotate_extrude() polygon(profilo);
        rotate_extrude() polygon(cavita);
        if (tipo == "chiusa")   // innesco decorativo
            translate([0,0,-eps]) difference() { cylinder(r=1.8, h=0.3); cylinder(r=1.4, h=0.3); }
    }
    if (tipo != "chiusa") cylinder(r=1.5, h=Lb - 1.4);   // perno/innesco
}

// =====================================================================
// BOSSOLO (asse Z, orlo a z=0)
// =====================================================================
module bossolo(tipo, interf, n_tacche) {
    difference() {
        union() {
            cylinder(d=boss_D, h=boss_L);
            cylinder(d=boss_orlo_D, h=boss_orlo_h);
        }
        // foro del percussore nel fondello
        translate([0,0,-eps]) cylinder(d=boss_foro + comp_foro_v, h=boss_fondo + 2*eps);
        if (tipo == "8") {
            // fascia di trattenuta sul fondo (stringe la fascia posteriore)
            translate([0,0,boss_fondo-eps])
                cylinder(d=cal_proiettile - interf + comp_foro_v, h=1.2 + 2*eps);
            translate([0,0,boss_fondo+1.2])
                cylinder(d=cal_proiettile + 0.1 + comp_foro_v, h=boss_prof);
            translate([0,0,boss_L-0.4])
                cylinder(d1=cal_proiettile + 0.1 + comp_foro_v, d2=cal_proiettile + 0.9, h=0.4+eps);
        } else {
            // pallino: siede sul foro del fondello, l'equatore cade nella fascia
            translate([0,0,boss_fondo-eps])
                cylinder(d=bb_d - interf + comp_foro_v, h=1.6 + 2*eps);
            translate([0,0,boss_fondo+1.6])
                cylinder(d=bb_d + 0.05 + comp_foro_v, h=boss_prof);
            translate([0,0,boss_L-0.4])
                cylinder(d1=bb_d + 0.05 + comp_foro_v, d2=bb_d + 0.85, h=0.4+eps);
        }
        // tacche sul bordo dell'orlo = numero della variante
        tacche(n_tacche, boss_orlo_D/2, boss_orlo_h);
    }
}

// =====================================================================
// CANNA (asse Z, ingresso con invito a z=0) e TAPPO ARANCIONE
// =====================================================================
module canna(anima) {
    difference() {
        cylinder(d=canna_D, h=canna_L);
        translate([0,0,-eps]) cylinder(d=anima + comp_foro_v, h=canna_L + 2*eps);
        translate([0,0,-eps]) cylinder(d1=anima + 1.6, d2=anima + comp_foro_v, h=invito_L);
    }
}
module volata() {   // da stampare arancione, labbro sul piatto
    difference() {
        cylinder(d=canna_D + 4, h=8);
        translate([0,0,1.5]) cylinder(d=canna_D + gioco_press, h=8);
        translate([0,0,-eps]) cylinder(d=canna_d_c + 1, h=2);
    }
}

// =====================================================================
// PERCUSSORE (asse X, retro collare a x=0) - si stampa con l'asta in basso
// =====================================================================
module percussore() {
    sm = 1.1;   // smusso del collare
    difference() {
        union() {
            translate([-asta_L,0,0]) rotate([0,90,0]) cylinder(d=asta_d, h=asta_L + eps);
            rotate([0,90,0]) {
                // retro: appoggio piano per la molla poi smusso 45 gradi
                cylinder(d=molla_De + 0.4, h=sm);
                translate([0,0,0]) cylinder(d1=molla_De + 0.4, d2=perc_col_D, h=(perc_col_D - molla_De - 0.4)/2);
                translate([0,0,(perc_col_D - molla_De - 0.4)/2])
                    cylinder(d=perc_col_D, h=perc_col_L - (perc_col_D - molla_De - 0.4)/2 - sm);
                translate([0,0,perc_col_L - sm]) cylinder(d1=perc_col_D, d2=perc_col_D - 2*sm, h=sm);
            }
            translate([perc_col_L - eps,0,0]) rotate([0,90,0]) cylinder(d=perc_punta_d, h=punta_L + eps);
        }
        // foro del pomolo (verso +Z)
        translate([perc_col_L/2, 0, r_pom0]) cylinder(d=pomolo_d + gioco_press, h=perc_col_D);
    }
}
module pomolo() {   // asse Z, si stampa in piedi
    cylinder(d=pomolo_d, h=pom_L + eps);
    translate([0,0,pom_L]) cylinder(d=testa_D, h=testa_h);
}

// =====================================================================
// TAPPO POSTERIORE (asse X, faccia della molla a x=0, verso -X il resto)
// =====================================================================
module tappo() {
    difference() {
        union() {
            translate([-L_tappo,0,0]) rotate([0,90,0]) cylinder(d=canale_D - 0.2, h=L_tappo);
            translate([-L_tappo-1.55,0,0]) rotate([0,90,0]) cylinder(d=canale_D + 3, h=1.5);
            rotate([0,90,0]) cylinder(d=asta_d, h=borch_h);    // borchia centra-molla
        }
        // foro perno: verticale nel telaio (asse Z)
        translate([-L_tappo/2,0,-canale_D]) cylinder(d=foro_perno, h=2*canale_D, $fn=16);
        // tacca di allineamento sulla flangia, in alto
        translate([-L_tappo-1.5-eps, -0.5, canale_D/2]) cube([1, 1, 2]);
    }
}

// =====================================================================
// BLOCCO CAMERA (asse X, retro a x=0, fondo a z=0)
// Si stampa in piedi sul retro: fori rotondi.
// =====================================================================
module camera() {
    difference() {
        translate([0,-cam_W/2,0]) cube([cam_L, cam_W, cam_H]);
        translate([0,0,cam_zb]) rotate([0,90,0]) {
            translate([0,0,-eps]) cylinder(d=boss_orlo_D + 0.4 + comp_foro_v, h=boss_orlo_h + eps);
            translate([0,0,-eps]) cylinder(d=boss_D + gioco + comp_foro_v, h=boss_L + eps);
            cylinder(d=canna_d_8 + 0.1 + comp_foro_v, h=cam_L + eps);
        }
        // presa per le dita sopra il telaio
        for (s=[-1,1]) translate([cam_L/2, s*(cam_W/2+0.5), cam_H-3])
            rotate([0,90,0]) cylinder(d=4, h=cam_L+1, center=true);
    }
}

// Blocco camera per la cartuccia intera: foro passante con invito sul
// retro e fascia di trattenuta dove arriva la fascia posteriore.
// Le tacche sopra indicano la variante di interferenza.
module camera_c(interf, n_tacche) {
    difference() {
        translate([0,-cam_W/2,0]) cube([cam_L, cam_W, cam_H]);
        translate([0,0,cam_zb]) rotate([0,90,0]) {
            translate([0,0,-eps]) cylinder(d=cart_D - interf + comp_foro_v, h=cam_L + 2*eps);
            // dopo la fascia di trattenuta il foro si allarga
            translate([0,0,cart_fascia + 0.5]) cylinder(d=cart_D + 0.25 + comp_foro_v, h=cam_L);
            translate([0,0,-eps]) cylinder(d1=cart_D + 0.8, d2=cart_D - interf + comp_foro_v, h=0.5);
        }
        for (s=[-1,1]) translate([cam_L/2, s*(cam_W/2+0.5), cam_H-3])
            rotate([0,90,0]) cylinder(d=4, h=cam_L+1, center=true);
        if (n_tacche > 0) for (i=[0:n_tacche-1])
            translate([cam_L/2 + (i-(n_tacche-1)/2)*3, 0, cam_H-0.6]) cylinder(d=1.5, h=1);
    }
}

// =====================================================================
// TELAIO (asse X, retro a x=0, fondo a z=0) - si stampa cosi' com'e'
// =====================================================================
module spicchio_pomolo(x) {   // tacca a 90 gradi da +Z a +Y per tenere armato
    translate([x,0,zb]) rotate([0,-90,0]) {
        rotate_extrude(angle=90) translate([0,-w_fes/2]) square([zb + 8, w_fes]);
        rotate_extrude(angle=90) translate([r_pom0 + pom_L - 0.5, -(testa_D+0.8)/2])
            square([10, testa_D + 0.8]);
    }
    // tratto dritto verso +Y: il pomolo armato sta tutto qui dentro
    translate([x - w_fes/2, 0, zb - w_fes/2]) cube([w_fes, W, w_fes]);
}
module telaio() {
    difference() {
        translate([0,-W/2,0]) cube([L_tel, W, H]);
        // canale percussore + molla + tappo
        translate([-eps,0,zb]) goccia_x(canale_D, x_sc + eps);
        // foro della punta nello scudo
        translate([x_sc - eps,0,zb]) goccia_x(perc_punta_d + 0.4, t_sc + 2*eps);
        // feritoia del blocco camera
        translate([x_sc + t_sc, -(cam_W + gioco)/2, zb - cam_zb])
            cube([x_spal - x_sc - t_sc, cam_W + gioco, H]);
        // passaggio nella spalla e sede canna
        translate([x_spal - eps,0,zb]) goccia_x(canna_d_c + 0.6, t_sp + 2*eps);
        translate([x_sede,0,zb]) goccia_x(canna_D + gioco_press, L_sede + eps);
        // fessura del pomolo sopra il canale
        translate([x_pom_a - w_fes/2, -w_fes/2, zb])
            cube([x_pom_f - x_pom_a + w_fes + 1, w_fes, H]);
        spicchio_pomolo(x_pom_a);
        // perno in filamento del tappo
        translate([L_tappo/2, 0, -eps]) cylinder(d=foro_perno, h=H + 2*eps, $fn=16);
    }
}

// =====================================================================
// ASSIEME
// =====================================================================
x_cr = (stato == "armato") ? x_cr_f - corsa : x_cr_f;
proj_x = (stato == "armato") ? 0 : (is_cart ? spinta_c : spinta);   // avanzamento munizione
tipo_cart = munizione == "cart_chiusa" ? "chiusa" : munizione == "cart_corta" ? "corta" : "aperta";

module molla_vis(L) {   // elica indicativa, solo per la vista
    rotate([0,90,0]) linear_extrude(height=L, twist=-360*(m_na + 2), $fn=24)
        translate([(molla_De - molla_d)/2, 0]) circle(d=molla_d, $fn=8);
}
module munizione_in_camera() {
    if (is_cart) translate([x_cam + proj_x, 0, zb]) rotate([0,90,0]) color("gold") cartuccia(tipo_cart);
    else translate([x_cam, 0, zb]) rotate([0,90,0]) {
        color("gold") bossolo(munizione == "bb" ? "6" : "8", 0, 0);
        translate([0,0,proj_x + boss_fondo]) {
            if (munizione == "bb") color("white") translate([0,0,bb_d/2 - 0.97]) sphere(d=bb_d);
            else color("orangered") proiettile(munizione);
        }
    }
}
module p_percussore() translate([x_cr,0,zb]) color("khaki") percussore();
module p_pomolo() translate([x_cr + perc_col_L/2, 0, zb])
    rotate([stato == "armato" ? -90 : 0, 0, 0]) translate([0,0,r_pom0]) color("tomato") pomolo();
module p_tappo() translate([L_tappo,0,zb]) color("dimgray") tappo();
// in assieme la camera_c ha 0.1 di gioco al posto dell'interferenza, per il controllo
module p_camera() translate([x_cam,0,zb - cam_zb]) color("steelblue")
    if (is_cart) camera_c(-0.1, 0); else camera();
module p_canna() translate([x_spal + t_sp,0,zb]) rotate([0,90,0])
    color("silver") canna(is_cart ? canna_d_c : munizione == "bb" ? canna_d_6 : canna_d_8);
module p_volata() translate([x_spal + t_sp + canna_L + 1.5,0,zb]) rotate([0,-90,0])
    color("darkorange") volata();
module p_molla() translate([L_tappo,0,zb]) color("lightgray") molla_vis(x_cr - L_tappo);

module assieme() {
    color("dimgray", 0.35) telaio();
    p_percussore(); p_pomolo(); p_tappo(); p_camera(); p_canna(); p_volata(); p_molla();
    munizione_in_camera();
}

// Controllo collisioni: deve risultare VUOTO.
// (il proiettile nel bossolo e' a pressione per progetto: escluso)
module collisioni() {
    intersection() { telaio(); p_percussore(); }
    intersection() { telaio(); p_pomolo(); }
    intersection() { telaio(); p_tappo(); }
    intersection() { telaio(); p_camera(); }
    intersection() { telaio(); p_canna(); }
    intersection() { p_camera(); munizione_in_camera(); }
    intersection() { p_percussore(); p_camera(); }
    intersection() { p_percussore(); munizione_in_camera_bossolo(); }
    intersection() { p_percussore(); p_tappo(); }
}
module munizione_in_camera_proiettile()
    if (!is_cart) translate([x_cam, 0, zb]) rotate([0,90,0]) translate([0,0,proj_x + boss_fondo]) {
        if (munizione == "bb") translate([0,0,bb_d/2 - 0.97]) sphere(d=bb_d);
        else proiettile(munizione);
    }
module munizione_in_camera_bossolo()
    if (is_cart) translate([x_cam + proj_x, 0, zb]) rotate([0,90,0]) cartuccia(tipo_cart);
    else translate([x_cam, 0, zb]) rotate([0,90,0]) bossolo(munizione == "bb" ? "6" : "8", 0, 0);

// =====================================================================
// PARTI SINGOLE, orientate per la stampa
// =====================================================================
module parte_stampa(p) {
    if      (p == "telaio")     telaio();
    else if (p == "camera")     rotate([0,-90,0]) camera();          // retro sul piatto
    else if (p == "percussore") translate([0,0,asta_L]) rotate([0,-90,0]) percussore();
    else if (p == "pomolo")     pomolo();
    else if (p == "tappo")      translate([0,0,L_tappo+1.5]) rotate([0,-90,0]) tappo();
    else if (p == "bossolo_8")  bossolo("8", interf_8[variante], variante + 1);
    else if (p == "bossolo_6")  bossolo("6", interf_6[variante], variante + 1);
    else if (p == "proiettile_diabolo") proiettile("diabolo");
    else if (p == "proiettile_volano")  proiettile("volano");
    else if (p == "proiettile_ogiva")   proiettile("ogiva");
    else if (p == "canna_8")    canna(canna_d_8);
    else if (p == "canna_6")    canna(canna_d_6);
    else if (p == "volata")     volata();
    else if (p == "camera_c")   rotate([0,-90,0]) camera_c(interf_c[variante], variante + 1);
    else if (p == "cartuccia_chiusa") cartuccia("chiusa");
    else if (p == "cartuccia_aperta") cartuccia("aperta");
    else if (p == "cartuccia_corta")  cartuccia("corta");
    else if (p == "canna_c")    canna(canna_d_c);
}

// taglio a y=0 pezzo per pezzo, cosi' ogni sezione resta del suo colore
module taglio(col) color(col) render() intersection() {
    children(); translate([-20, 0, -30]) cube([300, 50, 90]);
}

if (modalita == "assemblato") assieme();
else if (modalita == "sezione") {
    taglio("gainsboro") telaio();
    taglio("khaki") p_percussore();
    taglio("tomato") p_pomolo();
    taglio("dimgray") p_tappo();
    taglio("steelblue") p_camera();
    taglio("silver") p_canna();
    taglio("darkorange") p_volata();
    taglio("gray") p_molla();
    taglio("gold") munizione_in_camera_bossolo();
    taglio(munizione == "bb" ? "white" : "orangered") munizione_in_camera_proiettile();
}
else if (modalita == "check") collisioni();
else if (modalita == "parte") parte_stampa(parte);
