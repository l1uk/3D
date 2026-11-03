C10 ; file di configurazione (Professional Firmware: niente dialoghi)
; =====================================================================
; Autotune MPC dell'hotend (build standard del Professional Firmware)
; Le release standard usano MPC al posto del PID per l'ugello.
; Se la tua build usa il PID, usa 01b_pid_hotend.gcode invece di questo.
; Dura circa 5-10 minuti. Ugello pulito, filamento caricato, calza in silicone montata.
; =====================================================================
M117 Autotune MPC...
G28
G0 X110 Y110 Z5 F3000 ; testina al centro, vicino al piatto come in stampa
M306 T                 ; autotune MPC
M500                   ; salva in EEPROM
M117 MPC salvato
M306                   ; stampa i valori ottenuti sul terminale
