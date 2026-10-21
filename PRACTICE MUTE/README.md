# Practice Mute per tromba in Sib

Sordina da studio parametrica per tromba in Sib, progettata per stampa 3D FDM
(Creality Ender-3 V2, PLA/PETG/ABS, ugello 0.4-0.6 mm, 0 supporti).

## File principali

| File | Cosa è |
|---|---|
| `sordina_tromba.scad` | **Design corrente.** Corpo + fondello con varianti d'uscita (A/B/C) e tasca a vasca per l'imbottitura. È il file da usare. |
| `supporto_tromba_con_sordina.scad` | *(vedi cartella `TRUMPET STAND/` del workspace)* supporto universale per la tromba con o senza sordina. |
| `analizza_sordina.py` | Script di misura: riduce le registrazioni microfoniche a una tabella di attenuazione (dB), deviazione di intonazione (cent) e stabilità. Nessun audio lascia il PC. |

### Come usare `sordina_tromba.scad`
Seleziona `mode` in testa al file:
- `assembly` / `cross_section` — visualizzazione e ispezione.
- `body_only` — esporta STL del corpo superiore.
- `cap_only` — esporta STL del fondello (con stelo + tasca imbottitura).
- `test_ring` — provino rapido della gola del sughero (~20 min).
- `lip_test` — anello di prova del collare per tarare l'innesto (~20 min).

Variante d'uscita del suono: `cap_variant = "A" | "B" | "C"` (cambia solo lo stelo).
Tasca imbottitura: `pad_cage = true`, parametri `pad_*`.
Il report acustico e dimensionale viene stampato in console (echo).

## Cartelle

- `stl/` — STL stampabili esportati (corpo, fondello, provini).
- `slicer/` — progetti dello slicer (`.3mf`).
- `archivio/` — iterazioni storiche del design (v2 → v5, varianti pre-vasca, primi prototipi). Riferimento storico, non usare per stampare.
- `doc/` — `transcript.md`: la cronologia completa del progetto e del ragionamento acustico.

## Stato del progetto (sintesi)

- Il **corpo V2** è stampato e validato (ABS), buona aderenza alla campana e ottima attenuazione soggettiva.
- L'innesto corpo-fondello V2 è a frizione: chiude bene ma è difficile da aprire → il
  fondello corrente ha flangia più larga, collare più stretto e nervature a interferenza
  controllata per facilitare lo smontaggio.
- L'imbottitura (ovatta di **poliestere**, non cotone) va nella **tasca ricavata nel corpo**:
  a fondello smontato il corpo e' una ciotola aperta dal basso, ci si appoggia l'ovatta a
  manciate e si richiude col fondello. Una **griglia di ritenzione** stampata in alto nel
  corpo (`pocket_grid`) impedisce all'imbottitura di risalire verso il collo. Serve a
  dissipare le risonanze e ridurre il wah / la deriva di intonazione. Dosi indicative: 3-8 g.
  NB: la tasca e' nel CORPO, quindi per averla va ristampato il corpo (`mode = "body_only"`).
- Prossimo passo: misure con microfono (vedi `analizza_sordina.py`) per confrontare
  varianti e dosi di imbottitura.
