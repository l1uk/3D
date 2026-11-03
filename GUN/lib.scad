// =====================================================================
// LIBRERIA: molle e utilita' di stampa
// =====================================================================

// ---------- Molla di compressione ----------
function molla_Dm(d, De)            = De - d;                 // diametro medio
function molla_Di(d, De)            = De - 2*d;               // diametro interno
function molla_n_att(nt, nm)        = nt - nm;                // spire attive
function molla_L_pacco(d, nt)       = nt * d;                 // lunghezza a pacco
function molla_k(d, De, na, G)      = G * pow(d,4) / (8 * pow(De-d,3) * na); // [N/mm]
function molla_E(k, x1, x2)         = 0.5 * k * (x2*x2 - x1*x1);  // [mJ] da x1 a x2

// ---------- Fori orizzontali stampabili (goccia) ----------
// Foro lungo l'asse X, punta verso +Z: niente sbalzi sopra i 45 gradi.
module goccia_x(d, L) {
    rotate([0, 90, 0]) linear_extrude(L)
        rotate(180) goccia_2d(d);   // +X del 2D finisce in -Z: giro di 180
}
module goccia_2d(d) {
    r = d/2;
    hull() {
        circle(r);
        // punta a 45 gradi (verso +X nel 2D, ruotata poi in +Z)
        translate([r*sqrt(2), 0]) square(0.01, center=true);
    }
}

// Tacche sull'orlo per numerare le varianti (n tacche).
module tacche(n, R, h) {
    if (n > 0) for (i = [0 : n-1])
        rotate(i * 25) translate([R, 0, -0.01]) cylinder(d=0.9, h=h+0.02, $fn=12);
}
