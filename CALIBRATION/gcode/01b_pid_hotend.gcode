C10 ; file di configurazione (Professional Firmware: niente dialoghi)
; =====================================================================
; PID autotune dell'hotend a 210 C (temperatura tipica PLA)
; Usa questo SOLO se la tua build usa PID per l'ugello (se usa MPC
; il firmware risponde con un errore: usa 01a_mpc_hotend.gcode).
; Ventola del pezzo accesa come durante la stampa.
; =====================================================================
M117 PID ugello 210C...
G28
G0 X110 Y110 Z5 F3000
M106 S255              ; ventola pezzo al 100%
M303 E0 S210 C8 U1     ; 8 cicli, applica i valori (U1)
M107
M500
M117 PID ugello salvato
