# Harness di design iterativo

Lascia lavorare due agenti in ciclo su un progetto e tiene solo le versioni che migliorano.

```
giro:  DESIGNER (kiro-cli, contesto pulito, UNA modifica dal BACKLOG)
         -> CANCELLI deterministici   build, file protetti, check_stampa, interferenze,
                                       slicing (supporti, minuti, grammi), check-spec agentcad
         -> RENDER a camere fisse     Blender, stesse inquadrature dal primo giro
         -> CRITICO A/B               altro agente: vede solo immagini, BRIEF e RUBRICA;
                                       ordine X/Y casuale, "pari" = si tiene la vecchia
       accettata -> commit + tag harness/<nome>/best-N      rifiutata -> scartata, annotata nel diario
       `plateau` rifiuti di fila -> livello di dettaglio successivo
```

I livelli (funzione → forme → raccordi → ornamenti → micro-dettagli) impediscono di rifinire
dettagli su una forma ancora sbagliata. Il critico confronta, non dà voti: il design non può
peggiorare. I suggerimenti del critico finiscono in coda al BACKLOG del livello corrente.

## Preparare un progetto

1. Copia `tools/harness/modello/` nella cartella del progetto (es. `BOMBONIERA/v8/`).
2. Scrivi tu `BRIEF.md` (vincoli e quote che non cambiano) e `RUBRICA.md` (cosa rende un design
   migliore). Metti immagini di riferimento in `riferimenti/`. Sono **protetti**: se il designer
   li tocca il giro è scartato.
3. In `harness.json`: comando di `build` (che rigenera gli STL, percorso del venv relativo alla
   cartella del progetto, es. `../../.venv/bin/python build.py`), i `pezzi` nel loro orientamento
   di stampa con i limiti (`senza_supporti`, `max_minuti`, `max_grammi`, `corpi_max`,
   `max_pareti_sottili_pct`, `slice` = impostazioni Cura extra), gli STL assemblati per
   `interferenze` e `render`, eventuali `spec` agentcad (`{"step": ..., "spec": ...}`).
4. Riempi `BACKLOG.md` con poche voci per livello.
5. Il design di partenza deve passare i cancelli. Fai commit del progetto su main: l'harness
   lavora in un worktree e vede solo file versionati.

## Avviare

```bash
export KIRO_API_KEY=...          # chiave per kiro-cli headless (kiro.dev, impostazioni account)
.venv/bin/python tools/harness/harness.py BOMBONIERA/v8 --giri 3     # primo test, guardando
.venv/bin/python tools/harness/harness.py BOMBONIERA/v8              # notte: fino a budget/plateau/checkpoint
.venv/bin/python tools/harness/harness.py BOMBONIERA/v8 --stato      # riepilogo
touch ../3D-harness-v8/.harness/v8/STOP                              # ferma a fine giro
```

Lavoro e stato:
- worktree `../3D-harness-<nome>`, branch `harness/<nome>`: main non viene mai toccato.
  Per portare il risultato su main: `git merge harness/<nome>` (o cherry-pick di un `best-N`).
- `.harness/<nome>/` nel worktree: `RIEPILOGO.md`, `DIARIO.md`, `giri.jsonl`, `best/` (fogli
  di render delle versioni accettate), `giri/NNN/` (prompt, log, cancelli, render, verdetto).

Si ferma da solo per: file STOP, `giri_totali`, `minuti_sessione`, `max_fallimenti_di_fila`
bocciature consecutive, checkpoint ogni `checkpoint_ogni_accettati` versioni accettate (rivedi
`best/`, aggiorna la RUBRICA, riordina il BACKLOG, poi rilancia), plateau sull'ultimo livello.

## Test senza agenti

```bash
.venv/bin/python tools/harness/harness.py <progetto> --giri 2 --no-slice \
  --simula-designer "bash mio_script.sh" --simula-critico nuova|vecchia|caso
```

## Sicurezza e limiti

- Agenti in `.kiro/agents/designer-3d.json` e `critico-3d.json`. In headless sono fidati solo
  `read, glob, grep, write` (designer) e `read, write` (critico); la shell del designer accetta
  solo i comandi in `allowedCommands` (venv python/agentcad, blender, openscad, script in tools/),
  gli altri vengono negati. Niente git, rete, pip, OctoPrint.
- Il designer può comunque eseguire Python arbitrario tramite il venv: non è una sandbox. La
  protezione vera è il worktree separato più il controllo `git status` dopo ogni giro (file fuori
  dal progetto o protetti = giro scartato). Per un isolamento completo serve un container.
- Il gusto del critico non sostituisce il tuo: usa i checkpoint.
- Costo: due chiamate all'agente per giro più render e slicing (~1-3 min di calcolo locale).
