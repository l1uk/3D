C10 ; file di configurazione (Professional Firmware: niente dialoghi)
; =====================================================================
; E-STEPS: estrude 100 mm lentamente attraverso l'ugello caldo
;
; PRIMA di avviare: con l'ugello gia' a 210 C, fai un segno sul filo
; a 120 mm dall'ingresso dell'estrusore (misura col calibro).
; DOPO: misura la distanza rimasta tra ingresso e segno.
;   estruso   = 120 - distanza_rimasta
;   nuovi_E   = E_attuali * 100 / estruso
; (E attuali: li vedi in Control > Motion > Steps/mm, oppure M503 -> M92)
; Salva:  M92 E<nuovi_E>  poi  M500   (o dal menu + Store Settings)
; Esempio: rimasti 23.0 -> estruso 97.0 -> 93 * 100 / 97 = 95.88
; Ripeti finche' l'errore e' sotto 0.5 mm.
; =====================================================================
M117 E-steps: riscaldo...
M104 S210
M109 S210
G4 S10                 ; 10 s per stabilizzare
M83                    ; estrusione relativa
M117 Estrudo 100 mm...
G1 E100 F100           ; 100 mm a 100 mm/min (lento: niente slittamenti)
M400
M82
M117 Misura il segno!
M503                   ; stampa gli steps attuali (M92) sul terminale
