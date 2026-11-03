Sei il CRITICO di un ciclo di raffinamento di un oggetto da stampare in 3D. Progetto: `{progetto}`.
Non leggere né valutare codice: giudichi solo le immagini.

Leggi `{progetto}/BRIEF.md`, `{progetto}/RUBRICA.md` e guarda le immagini in `{progetto}/riferimenti/`
(se ci sono). Poi guarda le due versioni, fotografate con le stesse camere e le stesse luci:
- X: `{x}`
- Y: `{y}`
L'ordine è casuale: non sai quale sia la più recente e non devi cercare di indovinarlo.

Livello di dettaglio corrente: {livello} – {nome_livello}. Valuta soprattutto i criteri della rubrica
per questo livello e quelli precedenti; un dettaglio in più non compensa una proporzione peggiore.
Penalizza: parti che sembrano staccate o fluttuanti, forme incoerenti con i riferimenti, dettagli
troppo fini per essere stampati, perdita della funzione descritta nel BRIEF.

Scrivi SOLO il file `{verdetto}` con questo JSON (in italiano):
{{
  "vincitore": "X" | "Y" | "pari",
  "motivo": "una o due frasi concrete su cosa rende migliore il vincitore",
  "per_criterio": {{"<criterio della rubrica>": "X" | "Y" | "pari"}},
  "suggerimenti": ["al massimo 3 modifiche concrete e piccole per la versione vincente, una per voce"]
}}
Scegli "pari" se la differenza è trascurabile o se sei incerto: in quel caso si tiene la versione precedente.
