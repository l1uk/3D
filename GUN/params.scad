// =====================================================================
// REVOLVER GIOCATTOLO - PARAMETRI CONDIVISI
// Tutte le misure in mm. Usato da provino e (in futuro) dal revolver.
// Munizioni: sistema bossolo + proiettile (cal. 8 stampato in PLA)
// oppure bossolo per pallino softair 6 mm (BB). Il bossolo ha lo stesso
// esterno in entrambi i casi: cambia solo l'interno e la canna.
// =====================================================================

/* [Tolleranze di stampa] */
gioco        = 0.25;  // gioco generico tra parti scorrevoli (diametro)
gioco_press  = 0.10;  // gioco per accoppiamenti a pressione leggera
comp_foro_v  = 0.10;  // compensazione fori stampati in verticale (escono piccoli)
filamento_d  = 1.75;  // perni ricavati da spezzoni di filamento
foro_perno   = 1.95;  // foro per perno in filamento

/* [Calibro e canna] */
cal_proiettile = 8.0;   // diametro fasce del proiettile stampato
canna_d_8      = 8.3;   // anima canna per proiettile cal. 8
bb_d           = 5.95;  // pallino softair commerciale
canna_d_6      = 6.10;  // anima canna per pallino 6 mm
canna_D        = 15.0;  // diametro esterno canna (uguale per tutte le canne)
canna_L        = 60;    // lunghezza canna
invito_L       = 2.0;   // cono d'invito all'ingresso canna

/* [Bossolo] */
boss_D        = 10.5;  // diametro esterno corpo
boss_orlo_D   = 12.0;  // diametro orlo (collarino)
boss_orlo_h   = 1.2;   // spessore orlo
boss_fondo    = 1.2;   // spessore fondello
boss_foro     = 4.4;   // foro nel fondello per il percussore
boss_prof     = 8.0;   // profondita' interna (dove siede il proiettile)
boss_tratt_L  = 1.2;   // lunghezza della fascia di trattenuta alla bocca
// interferenza (sul diametro) della fascia di trattenuta: si stampano piu'
// varianti e si tiene quella che trattiene senza frenare troppo
interf_8 = [0.05, 0.10, 0.15];
interf_6 = [0.02, 0.05, 0.10];

/* [Percussore] */
perc_punta_d = 4.0;   // punta che entra nel fondello
perc_col_D   = 7.6;   // collare che scorre nel canale (leggero = piu' energia al proiettile)
perc_col_L   = 6.0;
canale_D     = 8.0;   // canale del percussore nel telaio
pomolo_d     = 3.5;   // perno di armamento (provino)

/* [Molla di propulsione] */
// Molla grande attuale: L0 29, De 5, ~26 spire, 10 spire ravvicinate.
// d = filo: misurare la lunghezza a pacco e dividere per le spire totali.
molla_d       = 0.6;   // diametro filo
molla_De      = 5.0;   // diametro esterno
molla_L0      = 29;    // lunghezza libera
molla_n_tot   = 26;    // spire totali
molla_n_morte = 10;    // spire ravvicinate (non lavorano)
molla_G       = 80000; // modulo di taglio acciaio armonico [MPa]
precarico     = 2.0;   // compressione a percussore avanti [mm]
corsa_max     = 9.0;   // corsa desiderata del percussore [mm]
margine_pacco = 1.5;   // la molla non deve mai arrivare a pacco

/* [Cartuccia intera (parte tutta)] */
// Senza orlo sporgente: passa nella canna. In camera la tiene solo
// una fascia ad attrito; dietro la ferma lo scudo del telaio.
cart_D        = 10.5;  // fasce di contatto (davanti e dietro)
cart_D_corpo  = 10.2;  // corpo scaricato tra le fasce: meno attrito
cart_fascia   = 1.5;   // altezza di ciascuna fascia
cart_gola_D   = 9.3;   // gola di estrazione decorativa
cart_parete   = 0.8;   // parete del corpo cavo (2 perimetri da 0.4)
cart_ogiva_D  = 8.6;   // "palla" che sporge dal bossolo
cart_ogiva_L  = 3.0;   // tratto cilindrico della palla
cart_punta_L  = 5.0;   // lunghezza della punta arrotondata
cart_bossolo_L = [13, 9];  // lunghezza del bossolo: normale, corta
canna_d_c     = 10.8;  // anima canna per la cartuccia
// interferenza (sul diametro) della fascia di trattenuta in camera
interf_c = [0.05, 0.10, 0.15];

/* [Revolver: corpo (GUN/corpo, build123d)] */
// Nomi nuovi, non usati dal provino. Le quote derivate stanno in
// GUN/corpo/meccanica.py con gli stessi nomi del provino.
n_camere       = 6;     // camere del tamburo [5:1:6]
corsa_riserva  = 3.0;   // corsa in piu' disponibile nel canale (molle future)
gioco_rot      = 0.5;   // gioco diametrale per rotazione libera (tamburo, perni)
parete_min     = 1.6;   // parete minima (4 linee da 0.42)
tamb_par_est   = 2.6;   // parete esterna del tamburo (ospita le tacche del fermo)
tamb_asse_d    = 6.0;   // perno del tamburo (stampato, sfilabile per caricare)
cricc_h        = 1.5;   // profondita' denti del cricchetto
cricc_L        = 4.0;   // fascia del cricchetto sul retro del tamburo
tacca_fermo    = 1.0;   // profondita' tacche del fermo tamburo
spessore_guscio = 2.4;  // parete laterale dei gusci del telaio
