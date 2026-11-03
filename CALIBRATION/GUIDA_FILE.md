# Guida ai file – cosa serve e come si usa

Questo file dice **quali file usare e come**. L'ordine dei test e come leggere i risultati sono in [README.md](README.md).

Ci sono tre modi di usare i file:

| Tipo | Come si usa |
|---|---|
| `.gcode` | Copia su microSD (o carica su OctoPrint) e **stampa direttamente**. Non passa da Cura. |
| `.stl` | Apri in **Cura**, fai lo slicing con il profilo PLA, stampa. |
| `.scad` / `.py` | Sorgenti: servono **solo per modificare** i test. Non si stampano. |

---

## Fondamentali (da fare tutti, in questo ordine)

| # | File | Tipo | A cosa serve | Come si usa |
|---|---|---|---|---|
| 1 | `gcode/01a_mpc_hotend.gcode` | G-code | Taratura temperatura ugello (MPC) | Stampa da SD. Salva da solo (M500). Se dà errore, usa `01b_pid_hotend.gcode`. |
| 2 | `gcode/02_pid_piatto.gcode` | G-code | Taratura temperatura piatto a 60 °C | Stampa da SD, piatto libero. Salva da solo. |
| 3 | `gcode/03_esteps_estrudi_100mm.gcode` | G-code | Verifica che l'estrusore spinga davvero 100 mm | Segna il filo a 120 mm, stampa, misura. La formula è nell'intestazione del file. |
| 4 | `stl/01_primo_strato.stl` | STL | Livellamento e Z-offset | In Cura: primo layer 0.2, skirt, **non spostarlo**. Regola il babystep mentre stampa. |
| 5 | `stl/04_torre_temperatura_230-190.stl` | STL + script | Trovare la temperatura giusta del PLA | In Cura aggiungi lo script **Torre Calibrazione** (Temperatura, 230, -5, 1, 8). |
| 6 | `stl/06_cubo_flusso.stl` | STL | Regolare il Flow | In Cura: 2 pareti, 0% infill, 0 top. Misura le pareti col calibro. |
| 7 | `stl/05_torre_retrazione_lunghezza_2-7mm.stl` | STL + script | Lunghezza di retrazione contro i fili | Script **Torre Calibrazione** (Retrazione lunghezza, 2, 1, 1, 8), Combing Off. |
| 8 | `stl/02_tolleranze.stl` | STL | Il gioco giusto per incastri nei tuoi progetti | Stampa con le impostazioni dei pezzi veri. Prova il perno nei 10 fori. |

## Consigliati (qualità extra)

| File | Tipo | A cosa serve | Come si usa |
|---|---|---|---|
| `gcode/linear_advance_test_PLA_210.gcode` | G-code | Angoli netti, meno bave (K del Linear Advance) | **Solo con firmware LA**: prima manda `M900` dal terminale; se risponde `Advance K=`, stampa da SD. |
| `stl/05_torre_retrazione_velocita_30-55.stl` | STL + script | Velocità di retrazione | Dopo la lunghezza. Script: Retrazione velocità, 30, 5, 1, 8. |
| `stl/07_sbalzi_ponti.stl` | STL | Ventola e ponti | In Cura **senza supporti**. |
| `stl/03_fori_diametri.stl` | STL | Fori e esterni precisi | Misura col calibro, correggi Hole/Horizontal Expansion in Cura. |
| `3DBenchy.stl`, `xyzCalibration_cube.stl` | STL | Verifica finale | Stampa alla fine, con il profilo definitivo. |

## Alternative / di riserva

| File | Quando usarlo |
|---|---|
| `gcode/01b_pid_hotend.gcode` | Al posto di `01a` se la tua build usa il PID per l'ugello. |
| `Ender 3_Bed_Level_190x190*.stl` | Test di livellamento più esteso, alternativo a `01_primo_strato`. |

## Strumenti (non si stampano)

### `tools/TorreCalibrazione.py` – script Cura
È **già installato** in `~/.local/share/cura/5.12/scripts/`. Se aggiorni Cura a una nuova versione, ricopialo nella cartella `scripts` della nuova versione.

1. Riavvia Cura.
2. *Estensioni > Post-elaborazione > Modifica G-code > Aggiungi script > Torre Calibrazione*.
3. Inserisci i 5 valori. Per ogni torre li trovi nella tabella del README e nella riga `ECHO` di OpenSCAD.
4. Fai lo slicing e salva.
5. **Rimuovi lo script** prima di stampare altro: resta attivo per tutte le stampe successive.

### `tools/genera_linear_advance.py` – generatore test LA
Rigenera il test con i tuoi valori, dalla cartella `CALIBRATION`:
```
python3 tools/genera_linear_advance.py --temp 205 --flusso 0.965 -o gcode/la_205.gcode
```
Le opzioni utili sono `--temp`, `--letto`, `--flusso`, `--k-fine` e `--k-passo`. `--help` le elenca tutte.

### `scad/*.scad` – sorgenti dei modelli
Apri in OpenSCAD e cambia i parametri nel Customizer. Poi esporta con **F6** e poi **F7** (STL) nella cartella `stl/`.
Ad esempio, nella torre di temperatura puoi cambiare `t_inizio`/`t_fine` per un altro filamento.

---

## Dove finiscono i valori trovati

| Risultato | Dove va |
|---|---|
| MPC/PID, e-steps, Z-offset, mesh | Nel firmware (salvati con M500 / *Store Settings*) |
| Temperatura, Flow, retrazione, ventola, expansion | Nel **profilo PLA di Cura** |
| K del Linear Advance | Nello **Start G-code di Cura** (`M900 K…`) oppure `M900 K…` + `M500` |
| Mesh attiva in stampa | Nello **Start G-code di Cura**: `M420 S1` dopo `G28` |
| Gioco degli incastri | Nei tuoi file `.scad` (es. `d_foro = d_perno + 0.20`) |
