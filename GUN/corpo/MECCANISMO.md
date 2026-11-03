# MECCANISMO - revolver giocattolo GUN, molla verticale nel manico (versione finale)

Generato da `concept_molla_verticale_final.py` (non modificare a mano i numeri: rilanciare lo script).
Coordinate di `build.py`: X asse canna (verso la volata), Z alto, Y laterale (y = 0 piano dei gusci), mm.

## 1. La molla: cosa comprare e come tagliarla

- **Filo di molla inox AISI 304** (1.4301/1.4310), **diametro esterno 8 mm, filo 1.0 mm**, passo ~3 mm (molla di compressione lunga da tagliare). G = 68000 MPa, Dm 7, indice C 7.
- **Tagliare 20 spire = ~60 mm** (non 45): contare le spire, poi chiudere a pinza l'ultima spira di ogni capo (appoggio piano, 2 spire non attive). Spire attive ~18, **k ~1.38 N/mm** (stima: tolleranza +-30%).
- Perche' 60 e non 45: con 45 mm (k 1.91) i vostri 10 mm di precarico danno 40 N a cane armato e ~42 N al grilletto; e anche con precarico quasi nullo k x corsa (10.8 mm) fa gia' 21 N: non resta spazio per caricarla. La 60 da' 4.0 m con 23.2 N.
- Montaggio nominale: sede 58 mm, **distanziale 4 mm** (dischi 4), molla montata a 54 mm: precarico 6.0 mm (8.3 N), armata 43.2 mm (23.2 N), pacco 21 mm, tau 501/810 MPa.
- Resa simulata: 166 mJ nella molla -> 41 mJ nella cartuccia da 1.13 g (25%), 8.6 m/s, **~4.0 m di tiro teso**. Pollice ~11 N, grilletto ~24 N.
- Limite onesto: con la corsa di 10 mm e 25 N la molla non puo' superare 259 mJ: 5 m tesi (~66 mJ nella cartuccia) richiedono ~30 N di molla (distanziale +4: 4.7 m, grilletto 30 N).
- Non comprimerla mai a pacco fuori sede (a pacco tau ~1161 MPa: si siede).

### Taratura (bilancia da cucina) e lunghezze alternative

1. Misurare L0 vera. Premere la molla di 10 mm sulla bilancia (infilata su un'asta d5): atteso 1403 g, intervallo +-30% 982-1824 g. k = grammi x 0.00981 / 10.
2. Distanziale [mm] = 58 - L0 + 23.5/k - 10.8, per difetto al mezzo mm, con i dischi 0.5/1/2/4/8 (0..15.5 mm).

| k vero | k N/mm | senza taratura | distanziale | con taratura |
|---|---|---|---|---|
| 0.70 x | 0.96 | 16.2 N, 3.27 m, grilletto 17 N | 11.5 mm (0.5+1+2+8) | 23.5 N, 4.29 m, grilletto 25 N |
| 0.85 x | 1.17 | 19.7 N, 3.67 m, grilletto 21 N | 7 mm (1+2+4) | 23.2 N, 4.15 m, grilletto 25 N |
| 1.00 x | 1.38 | 23.2 N, 4.03 m, grilletto 24 N | 4 mm (4) | 23.2 N, 4.03 m, grilletto 24 N |
| 1.15 x | 1.58 | 26.7 N, 4.35 m, grilletto 28 N | 2 mm (2) | 23.5 N, 3.95 m, grilletto 25 N |
| 1.30 x | 1.79 | 30.2 N, 4.66 m, grilletto 32 N | 0.5 mm (0.5) | 23.9 N, 3.87 m, grilletto 25 N |

Lunghezze di taglio alternative (stessa sede, cambia solo il distanziale):

| L0 | spire | k | distanziale | F armato | gittata | grilletto |
|---|---|---|---|---|---|---|
| 45 | 15 | 1.91 | - | non adatta (troppo dura) | - | - |
| 50 | 17 | 1.69 | 11 | 23.4 N | 3.90 m | 24 N |
| 55 | 18 | 1.52 | 7.5 | 23.3 N | 3.97 m | 24 N |
| 60 | 20 | 1.38 | 4 | 23.2 N | 4.03 m | 24 N |
| 65 | 22 | 1.26 | 0.5 | 23.1 N | 4.06 m | 24 N |
| 70 | 23 | 1.16 | - | non adatta (troppo dura) | - | - |

## 2. Pezzi

| pezzo | materiale | note | STL |
|---|---|---|---|
| cane | PLA, sp 7, sdraiato, 100% o 4 perimetri | perno (30.5,-20), coda 20 mm, dente di monta, forcella del percussore | final_cane.stl |
| grilletto | PLA, sp 6, sdraiato | perno (16,-28), naso, lama, braccio nel manico con forcella | final_grilletto.stl |
| rullino | PLA d7 x 2.4 | gira sul perno di filamento | final_rullino.stl |
| perno rullino | filamento PLA d1.75 x 5.8 | | final_perno_rullino_filamento.stl |
| percussore | PLA, in piedi sul collare | collare d5x2, gambo d2.6, L 19.4 | final_percussore.stl |
| coppa | PLA | d8.6 x 3, fra coda del cane e molla | final_coppa.stl |
| pistone + pattino | PLA, sdraiato | quadro 8.8 (non ruota), pattino per il rullino | final_pistone.stl |
| distanziali | PLA | dischi d8.8 x 0.5, 1, 2, 4, 8 | final_distanziale_*mm.stl |
| molla | inox 304 1.0 x 8, L0 60 | | final_molla_acciaio_rif.stl (riferimento) |
| perno cane | spina acciaio d3 x 24.0 (o chiodo/vite M3 tagliata) | | final_perno_cane_acciaio_rif.stl |
| perno grilletto | spina acciaio d2 x 23.4 (o chiodo d2) | | final_perno_grilletto_acciaio_rif.stl |

Assiemi: `concept_stl/final_assieme_armato.stl`, `final_assieme_riposo.stl`; guscio di controllo `final_guscio_sx_schematico.stl`; profili 2D per build.py in `concept_stl/final_profili.json`; disegno `concept_stl/final_profilo.png`.

## 3. Come si arma e come spara

1. **Riposo**: cane abbattuto contro il retro dello scudo (x 40); la punta del percussore sporge 2.5 mm nella camera e **blocca il tamburo**; il naso del grilletto appoggia sul cerchio della camma; molla a 54 mm (8 N).
2. **Armamento (pollice sullo sperone, ~11 N)**: il cane ruota indietro di 30 gradi; la coda spinge la coppa e comprime la molla di 10 mm; la forcella tira indietro il percussore, che rientra 0.3 mm nello scudo. Il naso del grilletto striscia sulla camma.
3. **Monta**: a fine corsa il naso del grilletto, spinto in su dalla molla attraverso rullino e braccio, scatta nella tacca della camma (aggancio 1.2 mm). Cane armato, molla a 43 mm (21 N).
4. **Rotazione del tamburo**: ora (e solo ora) il tamburo gira libero: si porta a mano la camera carica davanti al percussore.
5. **Scatto (~24 N al grilletto)**: il grilletto ruota di 5.9 gradi, il naso esce dalla tacca (+0.3 mm di sicurezza), il braccio comprime di altri 0.5 mm la molla tramite il rullino.
6. **Colpo**: il cane cade, la faccia batte sul collare del percussore (gioco 7.0 mm), il percussore spinge la cartuccia di 2.5 mm oltre la fascia di trattenuta e la lancia; il cane si ferma sullo scudo.
7. **Rilascio**: lasciando il grilletto, la molla (tramite il rullino) lo riporta in avanti finche' il naso torna sulla camma.

Montaggio: guscio sinistro steso; si posano cane (con il percussore nella forcella), grilletto con rullino e perno, coppa, molla, distanziali, pistone (la molla va compressa a mano di 6 mm, ~8 N, per posare il pistone sul rullino); si chiude il guscio destro e si infilano dal fianco la spina d3 del cane e la spina d2 del grilletto.

## 4. Modifiche da applicare a build.py (in quest'ordine)

Tutti i profili stanno in `concept_stl/final_profili.json` (poligoni XZ con fori, gia' nelle coordinate di build.py). Helper da aggiungere in testa a build.py, dopo gli import:

```python
import json
_MEC = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concept_stl', 'final_profili.json')))
def estrudi_mec(voce, larghezza=None):
    """Estrude simmetrico in Y i poligoni XZ di una voce di final_profili.json."""
    s = None
    for pg in voce['poligoni']:
        f = extrude(Plane.XZ * Polygon(*pg['ext'], align=None), amount=(larghezza or voce.get('larghezza') or voce['spessore']) / 2, both=True)
        for h in pg['holes']:
            f -= extrude(Plane.XZ * Polygon(*h, align=None), amount=50, both=True)
        s = f if s is None else s + f
    return s
```

1. **BRIEF / vincolo da sbloccare (prima di tutto)** - Il BRIEF dice che ogni pezzo sottrae `M.vuoto_canale()`. Con questo meccanismo il canale orizzontale del percussore+molla (d8 a z=0 da x -1 a 41) non esiste piu' e, se resta, taglia la cima della sede molla e la feritoia del cane. Serve il vostro OK a togliere quel vincolo. NON cambiare `molla_*`/`precarico` in params.scad: da li' deriva x_cam (posizione del tamburo); restano come 'quote storiche'.
2. **misure d'involucro: `slot_cane`** - da `8 + p.gioco_rot` a `7 + p.gioco_rot` (7.5). Cane spesso 7: con 8 la parete fra feritoia e scanalatura di carica scende a 1.1 mm (con 7: 1.61).
3. **misure d'involucro: `z_fondo_cane`** - togliere (serviva solo a tenere il cane sopra il canale del percussore).
4. **misure d'involucro: nuove costanti** - aggiungere `D_SEDE = 9.2`, `D_PERC_FORO = 2.9` e l'helper `estrudi_mec` qui sopra.
5. **finte viti: lista `viti`** - da `[(10, -10), (16, -28), (30, -6), (q.x_spal + 8, -19.5), (4, -36)]` a `[(6.1, -7.8), (16, -28), (8.7, -0.3), (74.6, -19.5), (14.8, -42.3), (30.5, -20)]` (le vecchie (10,-10), (30,-6), (4,-36) cadono nei vani; (16,-28) e' gia' il perno del grilletto; si aggiunge il perno del cane). Nel ciclo delle teste: per i due perni forare la testa (`- Pos(vx, ys, vz) * Rot(90,0,0) * Cylinder(d/2, 4)`) cosi' la spina passa.
6. **meccanica comune: riga `telaio = telaio - M.vuoto_finestra_tamburo() - M.vuoto_canale() - M.vuoto_canna(x_bocca)`** - togliere `- M.vuoto_canale()` e aggiungere il foro del percussore nello scudo: `telaio -= cil_x(D_PERC_FORO, x_scudo0 - 0.1, t_scudo + 0.2)` (d2.9 a z=0).
7. **meccanica comune: `M.vuoto_asse_tamburo(q.x_cam - 12, x_front + 1)`** - da `q.x_cam - 12` a `q.x_cam - 5.6` (foro da x 38.7, sbuca nella feritoia del cane).
8. **feritoie: `telaio -= Box(34, slot_cane, 40, ...).translate((-18, 0, z_fondo_cane))`** - sostituire con `telaio -= estrudi_mec(_MEC['vano_cane'], slot_cane)`: inviluppo del cane 0-30 gradi (x 6..40, z -29..sopra il dorso).
9. **feritoie: `telaio -= Box(15, slot_gril, 20, ...).translate((28, 0, -42))`** - sostituire con `telaio -= estrudi_mec(_MEC['vano_grilletto'], slot_gril)`: inviluppo di grilletto e rullino (x -29..37, z -81..-25), compreso il braccio nel manico.
10. **feritoie: nuova sede molla** - aggiungere `telaio -= estrudi_mec(_MEC['vano_molla'], D_SEDE)` (canale quadro 9.2 inclinato 32 gradi + vano di pistone e pattino) e `for r in _MEC['raccordi']: telaio -= estrudi_mec(r)` (setti < 1.6 fusi).
11. **feritoie: fori dei perni** - aggiungere `telaio -= Pos(30.5, 0, -20) * Rot(90, 0, 0) * Cylinder(1.5, 60)` e `telaio -= Pos(16, 0, -28) * Rot(90, 0, 0) * Cylinder(1, 60)` (DOPO le teste delle viti).
12. **PERNO DEL TAMBURO: `perno = cil_x(p.tamb_asse_d, q.x_cam - 10, ...)`** - da `q.x_cam - 10` (x 34.3) a `q.x_cam - 4.7` (x 39.6): oggi attraversa la feritoia del cane. Appoggio dietro il tamburo 4.4 mm (nello scudo).
13. **CANE: `cane = profilo([...], 8, ...)` e unghiatura** - sostituire con `cane = estrudi_mec(_MEC['cane']) - estrudi_mec(_MEC['cane']['forcella_gambo']) - Pos(30.5, 0, -20) * Rot(90, 0, 0) * Cylinder(1.65, 10)` (pezzo a riposo). L'unghiatura va riposizionata sulla faccia dietro dello sperone (attorno a (26, 17)).
14. **GRILLETTO: `grilletto = profilo([...], 6, ...)`** - sostituire con `grilletto = estrudi_mec(_MEC['grilletto'])` (a riposo) meno la gola della forcella (cilindro r4 x 2.6 attorno al centro del rullino) e il foro del perno del rullino d1.90.
15. **MONTAGGIO: nuovi `show_object`** - percussore, coppa, molla, distanziali, pistone, rullino, spine: si possono importare gli STL `final_*` o ricostruirli con le stesse primitive di concept_molla_verticale_final.py (sezione SOLIDI).
16. **EXPORT HARNESS: `_pezzi_harness`** - aggiungere i nuovi pezzi.
17. **FACOLTATIVO: dorso (X_DORSO0, Z_DORSO0)** - da (-28,-12) a (-1,-23) come proposto in v3 (-27 mm di gobba): con i vani finali NON e piu valido. E' solo estetica: il meccanismo sta nel profilo di oggi.

Dopo le modifiche: rilanciare build.py e controllare che l'assert della cresta passi ancora (la feritoia e' piu' stretta: il margine aumenta).

## 5. Da verificare con la stampa di prova

1. **Taratura molla**: misura di k (bilancia), scelta del distanziale; poi misurare la gittata vera (attesa 4.0 m) e la forza del grilletto (attesa ~24 N, dinamometro o bottiglia d'acqua appesa).
2. **Trattenuta della cartuccia**: il modello assume 5 N sulla fascia di 1.5 mm (2 N -> piu' gittata, 10 N -> meno). Verificare che la cartuccia non cada dal tamburo e che il percussore la spinga oltre la fascia (2.5 mm di spinta). Non abbattere il cane accompagnandolo su una camera carica: la spinge fuori a meta'.
3. **Indicizzazione del tamburo**: NON c'e' nottolino ne' mano. Il tamburo si gira a mano a cane armato e niente lo allinea: verificare quanto si puo' sbagliare (la punta d2.6 deve cadere sul fondello d10.5) e, se serve, aggiungere un fermo elastico nelle tacche esistenti.
4. **Rullino e ritorno del grilletto**: senza rullino (attrito a secco) il grilletto NON torna (braccio 56 mm). Controllare che il rullino giri libero sul filamento.
5. **Dente di monta in PLA**: 52 N sullo spigolo della tacca (aggancio 1.2 mm): rischio di arrotondamento/usura; stampare cane e grilletto con 4-5 perimetri e strato 0.12-0.16 nella zona del dente.
6. **Fasce di tolleranza della stampa**: giochi 0.25-0.3 per lato fra pezzi mobili e feritoie, fori dei perni nominali (spina a leggera interferenza nel telaio), sede molla quadra (gioco 0.6 sul diametro molla).
7. **Battuta del cane sullo scudo**: urto ripetuto PLA su PLA a ~107 mJ: controllare crepe sul retro dello scudo.
