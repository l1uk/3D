# Note del designer

## Giro 5 (livello 2) — impugnatura inclinata con pancia
- L'impugnatura del telaio non è più una lista di punti fissi: è generata da `profilo_imp()` lungo un asse inclinato all'indietro di `ANG_IMP = 20°`, con il dorso a pancia convessa (`PANCIA = 6 mm`, profilo a seno) e il fondo appena bombato (`H_TALL`).
- Guancette, campo zigrinato, medaglione, vite della guancetta e anello del cordino usano lo stesso sistema di coordinate (`imp_xz`), quindi seguono l'inclinazione e restano allineati al telaio.
- Meccanica, telaio superiore e ponticello sono invariati. La build gira e `check_stampa` dà manifold sì e 14 corpi come prima.

## Giro 6 (livello 2) — tallone arrotondato
- `profilo_imp()` non chiude più il fondo con una linea bombata fra due spigoli: frontale e dorso scendono fino alla quota `L_IMP + H_TALL` e si raccordano con due archi tangenti, la punta (`R_PUNTA = 6`) e il tallone (`R_TALL = 14`). Gli archi sono generati da `arco_imp()`.
- Il tallone parte da dove arriva la pancia del dorso (`dorso(s_t)`), così la curva dorsale prosegue nel fondo senza scalini. Guancette e campo zigrinato usano gli stessi raggi ridotti del rientro (con un minimo di `R_MIN`).
- La build gira e `check_stampa` dà manifold sì e 14 corpi. Il raccordo 2D del telaio e quello delle guancette si applicano ancora, e l'anello del cordino resta attaccato al fondo.

## Giro 7 (livello 2) — dorso convesso e raccordo ampio col telaio
- `PANCIA` passa da 6 a 12 mm e il massimo si sposta verso l'alto (`PICCO_PANCIA = 0.7`, seno sull'ascissa elevata), così la pancia sta sotto il cane invece che a meta' impugnatura.
- Il vecchio punto `(-10, -20)` che chiudeva il dorso del telaio (un rientro a gradino) è sostituito da `(-17, -24), (-13, -10)`: il dorso sale dal calcio al cane in un'unica curva sporgente, che il raccordo 2D del telaio arrotonda.
- Build ok, check_stampa: manifold sì, 14 corpi.

## Giro 8 (livello 2) — profilo dorsale del telaio
- I punti a scalino dietro il cane `(-9,-2),(-6,6),(0,10),(16,10.5)` sono sostituiti da un quarto di ellisse convesso (`X_DORSO0/1`, `Z_DORSO0/1`) che parte dal dorso dell'impugnatura in verticale e si appiattisce sulla cinghia a x=22: lo spigolo posteriore alto e' ora un'unica curva ampia (raggio >> 8 mm) invece di una scatola.
- Rimosso il punto `(-13,-10)`; il dorso sale da `(-17,-24)` direttamente alla curva. Build ok, manifold sì, 14 corpi.

## Giro 10 (livello 2) — fianchi bombati sopra il tamburo
- Il tentativo del giro 9 (ponti stretti + disco anteriore) e' stato scartato: il disco copriva il tamburo. Qui non si tocca la zona del tamburo: il tetto del telaio (cinghia sopra tamburo e canna, dal cane al frontale) diventa una volta tonda in sezione (`R_VOLTA = 13`), con i fianchi che scendono di ~5 mm verso il tamburo, che cosi' emerge di piu' dai fianchi.
- Meccanica invariata. Build ok, manifold, 14 corpi, parete minima 0.37 mm (come prima).

## Giro 11 (livello 2) — manicotto snubnose unico
- Tolti i due cilindri a gradini, l'alloggio-slitta sotto la canna (con astina a barra) e il mirino squadrato. Ora `manicotto` e' un solo cilindro tozzo (`SP_MAN = 5` mm di spessore sopra la canna) dal frontale del telaio fin quasi alla volata, con testate raccordate (`R_MAN = 4`).
- `astina` resta come pezzo, ridotta a un pomello tondo sul fianco del manicotto. Meccanica invariata. Build ok, manifold, 14 corpi.

## Giro 12 (livello 2) — raccordi del blocco telaio sopra la canna
- Lo spigolo alto-anteriore del telaio (prima rettangolare, tetto piatto a 12.5 e salto a 10) diventa un quarto d'ellisse lungo `A_FRONTE = 24` mm: la cinghia scende da 12.5 a `Z_FRONTE = 9.5` al frontale. L'angolo basso-anteriore e' un arco di raggio `R_FONDO_F = 9`.
- Cosi' la vista laterale del blocco non e' piu' un rettangolo. Meccanica invariata; build ok.

## Giro 13
Frontale dell'impugnatura (sotto il ponticello): da linea dritta a profilo a S, con gola concava di CONC_DITA=8 mm per le dita (picco spostato verso il telaio, PICCO_CONC=0.75) che poi torna in avanti verso il tallone. N_IMP portato a 16 per curva liscia.

## Giro 15
Canna a vista dimezzata (40 → 20 mm oltre il frontale del telaio): `CANNA_VISTA` in build.py, x_bocca e lunghezza canna (M.canna(L_CANNA)) derivati; manicotto e volata seguono. Sede canna e meccanica invariate. Scopo: baricentro sul tamburo/impugnatura, snubnose come la reference.

## Giro 16
Riempito il vuoto dietro il tamburo/cane: dorso del telaio spostato indietro (X_DORSO0/Z_DORSO0 da -14,-8 a -28,-12), volta estesa (X_VOLTA0=-30) e nuovo contorno posteriore (-21,-31),(-27,-22) al posto del punto (-17,-24). Massa verso il calcio, silhouette meno a punta in avanti. Meccanica invariata; build ok, manifold, 14 corpi.

## Giro 1 (livello 1)
Blocco del telaio davanti al tamburo, sopra la canna: il raccordo superiore anteriore passa da A_FRONTE=24 a 44 mm (la cinghia scende in curva continua dal tamburo alla volata, non piu' un mattone piatto) e l'angolo basso-anteriore da R_FONDO_F=9 a 11 mm. Scopo: ingombro anteriore rastremato come nelle reference. Meccanica invariata.

## Giro 3 (livello 1) — ponticello pieno
Ponticello: anello da parete 3.5 a 5.5 mm (R_PONT=17.5, r_PONT=12) e larghezza Y da 7 a 10 (W_PONT), infilato nel telaio fino a Z_PONT_TOP=-30.3 (prima tagliato a -37.5, quasi appeso). Due gattoni poligonali (davanti e dietro) lo raccordano al frontale e all'impugnatura. Niente fillet sull'anello, per evitare il non-manifold del giro 2. Build ok, manifold, 14 corpi.

## Giro 5 (livello 1) — telaio aperto sopra e sotto il tamburo
Nella zona della finestra del tamburo (x_cam..x_cam+finestra_L) i fianchi del telaio sopra Z_APRI_SUP e sotto Z_APRI_INF sono asportati, lasciando solo un ponte superiore sottile (PONTE_SUP_W=6) e un'anima inferiore (ANIMA_INF_W=6). Cosi' il cilindro non e' piu' un rettangolo incassato: si vede la curvatura in vista laterale e 3/4. Meccanica invariata; il taglio avviene prima del ponticello.

## Giro 6 (livello 1) — gobba e dorso in un'unica curva
Tolto il gradino dorsale: il dorso dell'impugnatura si ferma a S_FUSIONE=8 e una curva di Hermite (tangente al dorso, verticale all'attacco della gobba a (-28,-12)) sostituisce i punti fissi (-21,-31),(-27,-22). Profilo continuo dal cane al tallone. `profilo_imp` ha il nuovo parametro `s_dorso` (solo per il telaio; guancette e cappetta invariate). Build ok, manifold, 14 corpi.

## Giro 7 (livello 1)
Manicotto di volata rifatto come un unico cilindro tozzo e tondeggiante (D_MAN = 22 mm, vicino all'altezza del telaio, raccordo 4 mm), eliminato l'anello/flangia sottile.
Prima sembrava un tubicino con un disco; ora la parte anteriore e' paffuta e snubnose. Build OK, STL manifold.

## Giro 8 (livello 1)
Dorso del telaio sopra il tamburo: la sezione della guaina davanti passa a semicerchio pieno (R_CRESTA_DAV=11, ALZO_CRESTA_DAV=0, interpolati con lo stesso smoothstep del resto), cosi' la cima non e' piu' un piano tagliato dal profilo con spigoli vivi ma una volta con raccordi ampi sui fianchi. Dietro (cane) invariato. Build ok.

## Ridisegno v15 — sagoma da revolver, telaio a fianchi piani
- Abbandonata la guaina in loft (gonfia, lenta, fragile). La silhouette ora si disegna in 2D in `profili.py` (shapely, gira in un attimo: `python profili.py` -> `stl/profili.png`) e `forme.py` ne fa solidi a fianchi piani con gli spigoli tondi (loft rigato fra sezioni rientrate, poche facce: build completa ~2.5 min invece di 6; `GUN_VELOCE=1` salta zigrinatura ed elica della molla).
- Forma: cinghia superiore dritta, sella dietro lo scudo con il cane a vista, gobba e dorso che seguono la molla (32 gradi) con `MARGINE` 2.4 mm sui vani (`profili.verifica()`), calcio a testa d'uccello, ponticello ovale sottile, tamburo libero nella finestra con scanalature aperte davanti, camicia della canna (canna tonda + bindella + alloggio del perno) fusa nel telaio, testa del perno del tamburo sotto la volata come astina, mirino a rampa, filetto della cartella, leva finta in ottone, guancette bombate.
- Tolti: manicotto e astina (sostituiti dalla camicia), cappetta e anello del cordino. Canna a vista 20 -> 28 mm.
- Toccato in `meccanismo.py` solo l'aspetto del cane: sperone allungato all'indietro, unghiatura sul dorso, foro di alleggerimento spostato sotto la sella (z 15 -> 7.6). Perni, angoli, camma, forcella invariati; `verifica_pose()` senza interferenze.
- Cancelli: tutti i pezzi validi e watertight, assieme manifold, 16 corpi (15 + leva).

## v16 — retro compattato, design derivato dall'interfaccia del meccanismo
- **Studio della cinematica** (`studio_cinematica.py`, usa `meccanismo.variante()` e `dinamica.py`): aumentare l'angolo di armamento (35-40 gradi, coda piu' corta a pari corsa) accorcia il retro di soli 2-3 mm sulla gobba, alleggerisce grilletto e dente (24 -> 18 N, 52 -> 39 N) ma dimezza o peggio la coppia di ritorno del grilletto (57 -> 34 -> 17 Nmm), allunga il percussore e lascia pareti sottili nella forcella del cane. Gittata invariata (~4.0 m). Il perno del cane non puo' avanzare: la testa della spina finirebbe nella scanalatura di carica. Conclusione: cinematica ufficiale invariata; lo spazio era nella sagoma, non nel meccanismo.
- **Sagoma**: la gobba stava 7-9 mm dietro a dove serve. Ora scudo -> gobba 37 mm (prima 44), manico spesso 33 mm (prima 38), lunghezza 156, altezza 105.
- **Indipendenza**: `meccanismo.py` espone una sezione "INTERFACCIA COL DESIGN" (INGOMBRO_CHIUSO, INGOMBRO_PERCUSSORE, vano_cane, VANO_LAMA, vano_molla, asse della molla, perni, scudo). `profili.py` legge solo quella: ogni punto della sagoma nella zona del meccanismo e' "ingombro + costante di stile" (blocco STILE in testa al file) e l'ingombro viene comunque unito alla sagoma, quindi la parete MARGINE e' garantita per costruzione. Cambiando la cinematica la sagoma la segue; cambiando lo stile il meccanismo non si tocca.
- `dinamica.py`: forze, urto e gittata come modulo a se' (riproduce MECCANISMO.md: 166 mJ, 8.6 m/s, 4.0 m, grilletto 24 N).
- Cane: tolto il foro di alleggerimento (vale +-5 cm di gittata). Feritoia del cane aperta verso l'alto (`camino_cane2d`): prima restava un velo di 0.04 mm sopra la feritoia.
- `rendi.py [nome]`: render a colori a quattro viste in `stl/render/<nome>/`.
- Cancelli: 16 pezzi validi e watertight, assieme manifold, telaio con parete minima 1.5 mm.

## v17 — piu' vicino alla reference
- Canna: camicia a blocco a fianchi piani (W 20, spigoli tondi) al posto di quella tonda, con fazzoletto diagonale sotto verso il telaio, bindella sopra (0.4 sotto la cinghia: a filo l'unione dei solidi fallisce) e un solco sui fianchi. Canna a vista 28 -> 32.
- Cane: sperone ad arco "a virgola" (solo forma; perni, camma e forcella invariati). Piu' massa in alto: gittata simulata 3.99 -> 3.85 m.
- Impugnatura: pancia sul dorso verso il tallone, calcio piu' largo e tondo, frontale piu' incavato.
- Guancetta con bordo alto ad arco; bottone tondo dietro lo scudo al posto della leva oblunga.
- Cancelli: 16 pezzi validi e watertight, assieme manifold.
