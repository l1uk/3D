# Calibrazione Ender 3 V2 – PLA Bambu Lab

Stampante: Ender 3 V2, piatto in vetro, estrusore Bowden, Professional Firmware (mriscoc), Cura 5.12.
Segui l'ordine: ogni passo dipende da quelli prima.
Per sapere quali file sono fondamentali e come si usa ciascuno, vedi [GUIDA_FILE.md](GUIDA_FILE.md).

```
CALIBRATION/
├── gcode/   G-code pronti da SD/OctoPrint (MPC/PID, e-steps, Linear Advance)
├── scad/    modelli parametrici OpenSCAD
├── stl/     modelli già esportati
└── tools/   TorreCalibrazione.py (script Cura), genera_linear_advance.py
```

## 0. Meccanica (a mano, a stampante spenta)
- Eccentrici di X, Y e Z: niente gioco del carrello. Girando la ruota col dito senti una leggera resistenza.
- Cinghie X/Y: tese come la corda bassa di una chitarra (tenditori a manopola).
- Gantry: misura l'altezza a sinistra e a destra (V2 = un solo motore Z).
- Estrusore: controlla che il braccio in plastica non sia crepato vicino alla vite.
- Ugello serrato a caldo (240 °C). Tubo PTFE inserito fino in fondo.
- Piatto sgrassato con alcol isopropilico.

## 1. Temperature – `gcode/01a` o `01b`, poi `02`
- Ugello: le build standard del Professional Firmware usano **MPC** → `01a_mpc_hotend.gcode`. Se la tua build usa il PID (M306 dà errore) → `01b_pid_hotend.gcode`.
- Piatto: `02_pid_piatto.gcode`.

## 2. E-steps – `gcode/03_esteps_estrudi_100mm.gcode`
Le istruzioni sono nell'intestazione del file. In alternativa c'è *Move > Extrude 100 mm* dal menu del firmware.
Formula: `nuovi_E = E_attuali × 100 / mm_estrusi`, poi `M92 E…` e `M500`.

## 3. Primo strato – `stl/01_primo_strato.stl`
1. Livellamento a piatto caldo (60 °C) con *Bed Tramming* e uno spessimetro da 0.10 mm. Fai 2 giri sui 4 angoli.
2. Se vuoi, crea una *Manual Mesh* 5×5 e salvala.
3. Stampa i 5 pad e regola lo Z-offset col babystep mentre stampa. Poi salva.

Se usi la mesh, nello **Start G-code di Cura** aggiungi `M420 S1` subito dopo `G28`. Altrimenti la mesh non viene applicata.

## 4. Script Cura "Torre Calibrazione"
Lo script è già installato in `~/.local/share/cura/5.12/scripts/`. Riavvia Cura.
Si aggiunge da *Estensioni > Post-elaborazione > Modifica G-code > Aggiungi script > Torre Calibrazione*.
Ricordati di **rimuoverlo** dopo il test.

| Test | STL | Modalità | Valore iniziale | Passo | Altezza inizio | Altezza blocco |
|---|---|---|---|---|---|---|
| Temperatura | `04_torre_temperatura_230-190` | Temperatura | 230 | -5 | 1 | 8 |
| Retrazione lunghezza | `05_torre_retrazione_lunghezza_2-7mm` | Retrazione lunghezza | 2 | 1 | 1 | 8 |
| Retrazione velocità | `05_torre_retrazione_velocita_30-55` | Retrazione velocità | 30 | 5 | 1 | 8 |

- Layer 0.2 mm (anche il primo). I blocchi sono calcolati su questo valore.
- Per la retrazione: *Combing* Off. Velocità di retrazione fissa a 45 durante il test di lunghezza.
- Lo script rifiuta valori fuori range sicuro (temperatura 170–260, retrazione 0–10 mm). In quel caso Cura non applica lo script.
- Se modifichi le torri in OpenSCAD, i parametri da usare per lo script compaiono nella console (`ECHO`).

## 5. Temperatura – torre 230→190
Scegli il blocco con superficie liscia, ponte teso, sbalzo pulito e pochi fili.
Con Bambu PLA Basic su questa macchina il risultato tipico sta tra 200 e 215 °C.

## 6. Flusso – `stl/06_cubo_flusso.stl`
Impostazioni per questa stampa: 2 pareti, 0% infill, 0 top layers.
Misura le pareti in 8 punti e calcola `Flow = Flow_attuale × (2 × line_width) / misura_media`.

## 7. Linear Advance (facoltativo, richiede una build con LA)
Prima verifica il firmware: manda `M900` dal terminale.
- Se risponde con `Advance K=…`, il Linear Advance c'è.
- Se risponde "Unknown command", serve la build *Special Configurations → LinearAdvance* di mriscoc.

Il file `gcode/linear_advance_test_PLA_210.gcode` è pronto (K da 0 a 1.0, passo 0.05).
Rigeneralo con la tua temperatura e il tuo flusso:
```
python3 tools/genera_linear_advance.py --temp 205 --flusso 0.965 -o gcode/la_205.gcode
```
Le tacche sopra la cornice segnano i cambi di velocità. Scegli la linea più uniforme in quei punti (sul Bowden di serie di solito K è tra 0.4 e 0.8).
Poi:
- metti `M900 K<valore>` nello Start G-code;
- **rifai la torre di retrazione**: con LA basta meno retrazione.

## 8. Retrazione – torri 05
Prima la lunghezza (a 45 mm/s), poi la velocità alla lunghezza scelta.
Prendi il valore più basso senza fili. Sul Bowden di serie è tipicamente 4–6 mm senza LA, 2–4 mm con LA.

## 9. Raffreddamento – `stl/07_sbalzi_ponti.stl` (senza supporti)
Obiettivo: sbalzi puliti fino a 55–60° e ponti fino a 30–40 mm.

## 10. Dimensioni e incastri – `stl/02_tolleranze.stl`, `stl/03_fori_diametri.stl`
- Fori piccoli: *Hole Horizontal Expansion*.
- Esterni grandi: *Horizontal Expansion*.
- Piede d'elefante: *Initial Layer Horizontal Expansion* (ora hai -0.1).
- Non toccare gli steps X/Y: errori percentuali uniformi vengono dal flusso.
- Il calibro di tolleranze dice quale gioco diametrale usare nei tuoi `.scad` per accoppiamenti a pressione, scorrevoli e rotanti.

Alla fine: Benchy e `xyzCalibration_cube.stl` come verifica.

## Profilo Cura PLA di partenza
Il profilo attuale in Cura (245 °C, piatto 100 °C, ventola spenta) non va bene per il PLA. Crea un profilo dedicato:

| Impostazione | Valore iniziale | Da sostituire con |
|---|---|---|
| Temperatura ugello / primo layer | 210 / 215 °C | torre (punto 5) |
| Piatto | 60 °C | |
| Ventola | 0% primo layer, 100% dal layer 3 | test 07 |
| Layer / primo layer | 0.2 / 0.2 mm | |
| Line width | 0.42 mm | |
| Velocità: stampa / parete esterna / primo layer / viaggio | 60 / 40 / 20 / 150 mm/s | |
| Retrazione | 5 mm @ 45 mm/s | torre (punto 8) |
| Flow | 100% | cubo (punto 6) |
| Adesione | Skirt (brim solo per pezzi piccoli o alti) | |
