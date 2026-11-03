C10 ; file di configurazione (Professional Firmware: niente dialoghi)
; =====================================================================
; PID autotune del piatto a 60 C (PLA su vetro carborundum)
; Dura 10-15 minuti. Lascia il piatto libero.
; =====================================================================
M117 PID piatto 60C...
M303 E-1 S60 C8 U1     ; 8 cicli, applica i valori (U1)
M500
M117 PID piatto salvato
