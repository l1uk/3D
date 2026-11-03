# BRIEF — corpo del revolver giocattolo GUN (protetto, non modificare)

Revolver giocattolo da stampare in PLA, stile **far west / revolver d'epoca snubnose**,
come le due pistole in `riferimenti/`. Deve restare chiaramente un giocattolo (volata arancione).

## Il problema da risolvere
La versione attuale (`GUN/corpo/v10_A2_frontiera/`) è andata nella direzione sbagliata: è
**squadrata e spigolosa**, impugnatura quasi verticale e a spigoli vivi, telaio a scatola,
tamburo nascosto in un blocco rettangolare. Sembra una pistola a stampo, non un revolver western.
Obiettivo dell'harness: avvicinare la **silhouette e le proporzioni** alla reference, non
aggiungere altri dettagli.

## Cosa deve assomigliare alla reference
- **Impugnatura**: inclinata all'indietro ~18–25° rispetto alla verticale, pancia convessa sul
  dorso, tallone (fondo) arrotondato, non un parallelepipedo. Transizione morbida dal telaio.
- **Telaio**: linee curve e piene, spigoli raccordati; lo "scheletro" dal cane al calcio è una
  curva continua. Niente facce piatte a scatola.
- **Tamburo**: cilindro tondo ben visibile ai lati, non inglobato in un blocco squadrato.
- **Canna**: corta e tozza (snubnose), con manicotto/volata tondeggiante.
- **Ponticello del grilletto**: anello tondo pieno.
- Insieme compatto e "paffuto", non allungato e spigoloso.

## Vincoli che NON cambiano mai
- La **meccanica** è definita in `../meccanica.py` e `../parametri.py` (fonte: `GUN/params.scad`
  e `GUN/provino_balistico.scad`). Le quote funzionali — asse canna, posizione e diametro del
  tamburo (`q.R_tamb`, `q.x_cam`, `q.L_tamb`, `q.z_asse_tamb`), finestra, canale del percussore,
  sede e lunghezza della canna, corsa — si usano SOLO leggendole da lì. Non ricopiare numeri,
  non cambiare `meccanica.py` né `parametri.py`.
- Ogni pezzo deve continuare a sottrarre i volumi meccanici (`vuoto_finestra_tamburo`,
  `vuoto_canale`, `vuoto_canna`, `vuoto_asse_tamburo`) così la pistola resta "funzionante".
- Stampa in PLA su Ender 3 (piatto 220×220), ugello 0.4, pareti ≥ 1.6 mm. Telaio in due gusci
  uniti da perni in filamento 1.75 (fori già previsti). I pezzi mobili (tamburo, cane, grilletto)
  restano separati con i loro giochi.
- Resta un giocattolo: **volata arancione**, nessuna replica fedele di un'arma reale esistente.

## Cosa può cambiare liberamente
Profili e curve dell'involucro (telaio, impugnatura, ponticello, manicotto), raccordi, smussi,
proporzioni estetiche, decori (zigrinatura, medaglione, viti finte), palette dei colori.

## Deliverable
Un `build.py` nella cartella del progetto che genera l'assieme (gli stessi pezzi della v10:
telaio, tamburo, perno, sportello, canna, manicotto, astina, guance, cane, grilletto, cordino,
volata) e li espone con `show_object`. Parti nei loro colori da giocattolo.
