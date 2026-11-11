# Banco di prova del meccanismo

Proof of concept senza estetica: due gusci ridotti alla zona del meccanismo, con sede molla,
feritoie e fori delle spine identici al telaio vero (li calcola `meccanismo.py`), più un blocco con
una sola camera al posto del tamburo. Si genera con `python banco.py` e non dipende dal design
(`profili.py`, `build.py`): se la cinematica cambia, basta rilanciarlo.

- `stl/banco/stampa/` — pezzi già orientati per la stampa (piano a z = 0)
- `stl/banco/assieme/` — gli stessi pezzi montati (controlli e render)
- `stl/banco/banco.png`, `stl/banco/render/banco.png` — disegno e render

## Cosa stampare

| pezzo | orientamento | note | stima (0.2 mm, 3 pareti, 15%) |
|---|---|---|---|
| `guscio_sx`, `guscio_dx` | faccia esterna sul piano, vani aperti in alto | niente supporti | 3 h 20 min e 27 g ciascuno |
| `cane` | sdraiato | 4-5 perimetri o 100%: sul dente di monta arrivano ~52 N | 30 min, 4 g |
| `grilletto` | sdraiato | 4-5 perimetri | 27 min, 3 g |
| `blocco_camera_v1/v2/v3` | camera verticale, lato scudo in basso | tre varianti della fascia che trattiene la cartuccia (interferenza 0.05 / 0.10 / 0.15 mm, 1 / 2 / 3 tacche in cima), come il blocco `camera_c` del provino: si tiene quella che trattiene senza frenare | 45 min, 7 g ciascuno |
| `percussore` | in piedi sul collare | strato 0.12-0.16 | pochi minuti |
| `rullino`, `coppa`, `pistone` | come esportati | | pochi minuti |
| `distanziale_0.5/1/2/4/8mm` | dischi | il nominale è 4 mm | pochi minuti |
| `canna` | in piedi | è la canna del provino (anima 10.8): se l'avete già, non serve | |

Cartuccia: quella del provino (`GUN/stl/provino/cartuccia_aperta.stl`).

## Lista della spesa

| cosa | misura | quanti | dove |
|---|---|---|---|
| molla a compressione inox | filo 1.0 mm, diametro esterno 8 mm, passo ~3 mm, lunga almeno 60 mm | 1 | online ("molla compressione inox filo 1 mm diametro esterno 8", oppure "molla a metro" da tagliare), mollificio, forniture industriali. Le scatole assortite dei brico di solito sono troppo corte |
| perno del cane | acciaio d3 x 22 mm | 1 | un chiodo da 3 tagliato e sbavato, il gambo di una punta da trapano da 3, una vite M3 lunga senza testa, oppure una "spina cilindrica 3x22" (DIN 7 / ISO 2338; va bene anche 3x24) |
| perno del grilletto | acciaio d2 x 22 mm | 1 | chiodo da 2, punta da trapano da 2, raggio di bicicletta, oppure spina cilindrica 2x22 (o 2x24) |
| viti M3 x 20 a testa cilindrica con esagono incassato | testa d5.5 | 6 | qualsiasi ferramenta o brico; di recupero da computer e stampanti |
| dadi M3 esagonali | chiave 5.5 | 6 | idem |
| perno del rullino | filamento 1.75 mm, 6 mm | 1 | dalla bobina |

Una **spina** e' un cilindretto d'acciaio pieno e liscio, senza testa ne' filetto: si infila in un
foro e fa da asse. Qui entra forzata nei gusci (fori a misura nominale: se non entra, ripassarli con
una punta da 3 e da 2) e il cane e il grilletto ci ruotano sopra.

Solo la molla deve essere davvero di metallo e di quelle misure: deve dare ~23 N in un canale da
9 mm e restare precaricata senza cedere, cosa che una molla stampata non fa. Con filo 1.0 e diametro
8 ma passo o lunghezza diversi va bene lo stesso (minimo 60 mm): cambia la rigidezza, che si misura
con la bilancia e si compensa con i distanziali (tabella in `MECCANISMO.md`). Con filo 1.2 e' troppo dura.

Attrezzi: tronchesi e lima (per tagliare molla e perni), pinza (per chiudere l'ultima spira della
molla a ogni capo), chiave a brugola da 2.5, punte da 2 e da 3, bilancia da cucina.

## Prima di stampare

- Gli STL non sono nel repository (`stl/` e' ignorata da git): si rigenerano con
  `../../.venv/bin/python banco.py` (circa 45 secondi).
- Le stime di tempo vengono dal profilo PLA dell'Ender 3 (`tools/slice_stima.py`): con un'altra
  stampante vanno risliciati.
- Stampare 2 percussori (e' il pezzo piu' fragile) e qualche cartuccia.

## Montaggio

1. Guscio sinistro steso, vani verso l'alto.
2. Rullino nella forcella del grilletto con il suo perno di filamento; grilletto sul suo perno.
3. Percussore nella forcella del cane, punta nel foro dello scudo; cane sul suo perno.
4. Coppa (cono verso la coda del cane), molla, distanziale da 4, pistone con il pattino sul rullino:
   la molla va compressa a mano di ~6 mm (~8 N) per posare il pistone.
5. Guscio destro, 6 viti, poi le due spine dai fianchi.

## Prove, in quest'ordine

1. **A vuoto, senza molla**: cane e grilletto ruotano liberi nelle feritoie? Il percussore scorre?
2. **Monta e sgancio**: armando il cane (30 gradi) il naso del grilletto scatta nella tacca; premendo
   il grilletto il cane cade. Attesi ~10 N al pollice e ~24 N al grilletto (bottiglia d'acqua appesa:
   1 litro = 10 N).
3. **Ritorno del grilletto**: lasciandolo torna avanti da solo? Se no, controllare che il rullino giri.
4. **Taratura molla**: bilancia da cucina, tabella in `MECCANISMO.md`; scegliere il distanziale.
5. **Tiro**: armare, calare il blocco camera con la cartuccia (a cane abbattuto non entra: la punta
   del percussore sporge nella camera, come nel revolver), sparare in orizzontale da 1.2 m.
   Gittata attesa ~3.9 m.
6. **Usura**: dopo 30-50 colpi guardare il dente di monta e la battuta del cane sullo scudo.

## Cosa NON prova

Indicizzazione del tamburo, sportello di carica, resistenza dei gusci veri (qui le pareti attorno
ai vani sono più generose: 4 mm contro i 2.4 del telaio).
