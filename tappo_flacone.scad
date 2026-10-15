// =====================================================================
// TAPPO FEMMINA PER FLACONE - VERSIONE FINALE OTTIMIZZATA (V3)
// Con Modifiche A & B Anti-Cross-Threading e Misure 2/20" (2.54 mm)
// =====================================================================

/* [Misure Flacone Verificate] */
neck_d_crest    = 32.50; // Diametro cresta filetto maschio (mm)
neck_d_root     = 31.00; // Diametro tubo liscio (mm)
spire_pitch     = 2.54;  // Distanza Cresta-Cresta tra le due linee = 2/20" (2.54 mm)
starts          = 2;     // 2 principi opposti a 180°
neck_height     = 8.00;  // Altezza utile del collo (mm)

/* [Tolleranze Stampa 3D FDM] */
clearance_radial = 0.40; // Gioco radiale (+0.80mm sul diametro, compensa ritiro fori FDM)

/* [Dimensioni Tappo] */
wall_thickness   = 2.3;  // Spessore parete esterna (mm)
top_thickness    = 2.4;  // Spessore fondo/cielo (mm)
internal_depth   = 8.8;  // Profondità cavità interna (mm)
knurl_count      = 28;   // Scanalature esterne zigrinatura
knurl_depth      = 0.5;  // Profondità zigrinatura (mm)
profile_w        = 1.60; // Larghezza della gola (dente maschio = 1.27mm / 1/20")

/* [Modalità e Vista] */
mode = "full"; // ["full", "test"]
show_section = false; // [true, false]

/* Calcoli derivati */
lead       = spire_pitch * starts;                          // Avanzamento a 360° = 5.08 mm (5 TPI)
r_bore     = (neck_d_root / 2) + clearance_radial;          // 15.90 mm (D_foro = 31.8 mm)
r_groove   = (neck_d_crest / 2) + clearance_radial + 0.15;  // 16.80 mm (D_gola = 33.6 mm)
cap_r_ext  = r_groove + wall_thickness;                     // 19.10 mm (D_esterno = 38.2 mm)
total_h    = internal_depth + top_thickness;                // 11.20 mm

// Modulo fresa filetto (Modifica B: parte a quota z=0.3, niente ingressi sotto zero)
module selective_thread_cutter(r_base, r_tip, z_start, z_top, lead, starts=2, profile_w=1.60, steps_per_turn=48) {
    total_z = z_top - z_start;
    total_deg = (total_z / lead) * 360;
    n_steps = floor((total_deg / 360) * steps_per_turn);
    d_th = total_deg / n_steps;
    dz = total_z / n_steps;
    
    for (s = [0:starts-1]) {
        th0 = s * (360 / starts);
        
        pts = [
            for (i = [0:n_steps])
                let(
                    th = th0 + i * d_th,
                    z = z_start + i * dz
                )
                each [
                    [r_base * cos(th), r_base * sin(th), z - profile_w * 0.5],
                    [r_tip  * cos(th), r_tip  * sin(th), z - profile_w * 0.22],
                    [r_tip  * cos(th), r_tip  * sin(th), z + profile_w * 0.22],
                    [r_base * cos(th), r_base * sin(th), z + profile_w * 0.5]
                ]
        ];
        
        faces = concat(
            [[0, 1, 2], [0, 2, 3]],
            [[n_steps*4 + 0, n_steps*4 + 2, n_steps*4 + 1], [n_steps*4 + 0, n_steps*4 + 3, n_steps*4 + 2]],
            [
                for (i = [0:n_steps-1])
                    for (k = [0:3])
                        let(
                            k_next = (k + 1) % 4,
                            v0 = i * 4 + k,
                            v1 = i * 4 + k_next,
                            v2 = (i + 1) * 4 + k_next,
                            v3 = (i + 1) * 4 + k
                        )
                        each [
                            [v0, v3, v2],
                            [v0, v2, v1]
                        ]
            ]
        );
        polyhedron(points=pts, faces=faces);
    }
}

// Modifica A: Tasche di ingresso selettive SOLO a 0° e 180° (Anti-Cross-Threading)
module entry_pockets(r_bore, r_groove, starts=2, pocket_angle=30, pocket_h=1.2) {
    for (s = [0:starts-1]) {
        rotate([0, 0, s * (360 / starts)])
            rotate([0, 0, -pocket_angle/2])
            rotate_extrude(angle=pocket_angle, $fn=80)
                polygon([
                    [r_bore - 0.5, -0.1],
                    [r_groove + 0.3, -0.1],
                    [r_groove, pocket_h],
                    [r_bore, pocket_h]
                ]);
    }
}

// Corpo con zigrinatura esterna
module cap_body(h, r_out, knurls=28, k_depth=0.5) {
    difference() {
        union() {
            cylinder(r=r_out, h=h - 1.0, $fn=80);
            translate([0,0,h - 1.0])
                cylinder(r1=r_out, r2=r_out - 1.0, h=1.0, $fn=80);
        }
        for (a = [0:knurls-1]) {
            rotate([0, 0, a * (360 / knurls)])
                translate([r_out, 0, -0.5])
                cylinder(r=k_depth, h=h + 1, $fn=16);
        }
    }
}

// Assieme
module make_cap(is_test=false) {
    h_cap = is_test ? 6.0 : total_h;
    depth = is_test ? 7.0 : internal_depth;
    
    difference() {
        cap_body(h=h_cap, r_out=cap_r_ext, knurls=knurl_count, k_depth=knurl_depth);
        
        // Foro centrale
        translate([0, 0, -0.5])
            cylinder(r=r_bore, h=depth + 0.5, $fn=80);
            
        // Gole filetto (Modifica B: partenza a z=0.3)
        selective_thread_cutter(
            r_base=r_bore - 0.2,
            r_tip=r_groove,
            z_start=0.3,
            z_top=depth + 0.5,
            lead=lead,
            starts=starts,
            profile_w=profile_w,
            steps_per_turn=48
        );
        
        // Modifica A: Tasche d'ingresso uniche a 0° e 180°
        entry_pockets(r_bore=r_bore, r_groove=r_groove, starts=starts, pocket_angle=30, pocket_h=1.2);
    }
}

module render_selected() {
    render() {
        if (mode == "full") {
            make_cap(is_test=false);
        } else {
            make_cap(is_test=true);
        }
    }
}

if (show_section) {
    difference() {
        render_selected();
        translate([0, -50, -5]) cube([60, 100, 30]);
    }
} else {
    render_selected();
}
