#!/usr/bin/env python3
"""Harness di design iterativo: DESIGNER -> CANCELLI -> RENDER -> CRITICO A/B.

Uso (dalla root del workspace, con il venv CAD):
  .venv/bin/python tools/harness/harness.py BOMBONIERA/v8            # avvia o riprende
  .venv/bin/python tools/harness/harness.py BOMBONIERA/v8 --giri 3   # limita i giri di questa sessione
  .venv/bin/python tools/harness/harness.py BOMBONIERA/v8 --stato    # riepilogo senza lanciare nulla
  touch ../3D-harness-v8/.harness/v8/STOP                            # ferma alla fine del giro corrente

La cartella del progetto contiene harness.json, BRIEF.md, RUBRICA.md, BACKLOG.md e
opzionalmente riferimenti/ (immagini). Tutto il lavoro avviene in un git worktree
separato (../<repo>-harness-<nome>, branch harness/<nome>): main non viene toccato.
Ogni versione accettata e' un commit con tag harness/<nome>/best-N.

Il ciclo:
  1. il designer (kiro-cli, contesto pulito) applica UNA modifica dal backlog
  2. cancelli deterministici: build, file protetti, check_stampa, interferenze,
     slicing (supporti, tempo, grammi), check-spec agentcad. Se falliscono si scarta.
  3. render a camere fisse (Blender), stesse inquadrature del primo giro
  4. il critico (altro agente, vede solo immagini, brief e rubrica) confronta la
     versione migliore con la candidata in ordine casuale (X/Y): si tiene solo se migliora
  5. dopo `plateau` rifiuti di fila si passa al livello di dettaglio successivo;
     dopo l'ultimo livello, o al checkpoint, ci si ferma e si aspetta l'utente.
Vedi tools/harness/README.md.
"""
import argparse
import json
import os
import random
import re
import shlex
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

QUI = Path(__file__).resolve().parent
PROTETTI_DEFAULT = ["harness.json", "BRIEF.md", "RUBRICA.md", "riferimenti/"]


# ---------------------------------------------------------------- utilita'
def sh(cmd, cwd, timeout=None, env=None, log=None):
    """Esegue un comando (lista o stringa shell); ritorna (codice, output)."""
    try:
        p = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), capture_output=True,
                           text=True, timeout=timeout, env=env)
        out, rc = p.stdout + p.stderr, p.returncode
    except subprocess.TimeoutExpired as e:
        out, rc = f"{e.stdout or ''}{e.stderr or ''}\nTIMEOUT dopo {timeout} s", 124
    if log:
        Path(log).write_text(out)
    return rc, out


def git(args, cwd, check=True):
    rc, out = sh(["git", *args], cwd)
    if check and rc != 0:
        raise RuntimeError(f"git {' '.join(args)}: {out.strip()}")
    return out.strip()


def ora():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


class Harness:
    def __init__(self, progetto, args):
        self.args = args
        progetto = Path(progetto).resolve()
        self.repo = Path(git(["rev-parse", "--show-toplevel"], progetto))
        self.rel = progetto.relative_to(self.repo)
        self.conf = json.loads((progetto / "harness.json").read_text())
        self.nome = re.sub(r"[^a-z0-9_-]+", "-", self.conf.get("nome", progetto.name).lower())
        self.wt = self.repo.parent / f"{self.repo.name}-harness-{self.nome}"
        self.P = self.wt / self.rel                 # progetto dentro il worktree
        self.S = self.wt / ".harness" / self.nome   # stato (non versionato)
        self.py = self.wt / ".venv/bin/python"
        # chi giudica: "ai" (agente critico-3d) o "umano" (tu, dal terminale)
        self.modo_critico = getattr(args, "critico", None) or self.conf.get("critico", "ai")

    # ------------------------------------------------------------ setup
    def prepara(self):
        if not self.wt.exists():
            if not git(["ls-files", str(self.rel / "harness.json")], self.repo):
                sys.exit(f"{self.rel}/harness.json non e' nel repository: fai commit del progetto "
                         "prima di avviare l'harness (il worktree contiene solo file versionati).")
            ramo = f"harness/{self.nome}"
            esiste = git(["branch", "--list", ramo], self.repo)
            git(["worktree", "add", *([] if esiste else ["-b", ramo]), str(self.wt),
                 *([ramo] if esiste else ["HEAD"])], self.repo)
        venv = self.wt / ".venv"
        if not venv.exists():
            venv.symlink_to(self.repo / ".venv")
        for d in ("giri", "best"):
            (self.S / d).mkdir(parents=True, exist_ok=True)
        # una sola istanza per progetto: due cicli sullo stesso worktree si pestano i piedi
        import fcntl
        self._lock = open(self.S / "lock", "w")
        try:
            fcntl.flock(self._lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            if not self.args.stato:
                sys.exit(f"Un'altra istanza dell'harness '{self.nome}' e' gia' in esecuzione.")
        self.stato_file = self.S / "stato.json"
        self.stato = json.loads(self.stato_file.read_text()) if self.stato_file.exists() else {
            "giro": 0, "livello": 1, "plateau": 0, "accettati": 0, "best_commit": None,
            "best_metriche": None, "inizio": ora(), "fine_motivo": None, "fallimenti_di_fila": 0}

    def salva(self):
        self.stato_file.write_text(json.dumps(self.stato, indent=1))

    def diario(self, testo):
        with open(self.S / "DIARIO.md", "a") as f:
            f.write(f"\n## Giro {self.stato['giro']} ({ora()}, livello {self.stato['livello']})\n{testo}\n")

    # ------------------------------------------------------------ backlog
    def livelli(self):
        return self.conf.get("livelli", ["funzione e ingombri", "forme principali",
                                         "raccordi e proporzioni", "ornamenti", "micro-dettagli"])

    def prossima_voce(self):
        """Prima voce '- [ ]' sotto '## Livello N' in BACKLOG.md (o None)."""
        testo = (self.P / "BACKLOG.md").read_text()
        sez = re.split(r"^## ", testo, flags=re.M)
        for s in sez:
            if re.match(rf"Livello {self.stato['livello']}\b", s):
                m = re.search(r"^- \[ \] (.+)$", s, flags=re.M)
                return m.group(1).strip() if m else None
        return None

    def spunta_voce(self, voce):
        f = self.P / "BACKLOG.md"
        f.write_text(f.read_text().replace(f"- [ ] {voce}", f"- [x] {voce}", 1))

    def aggiungi_voci(self, voci, origine="critico"):
        """Suggerimenti del critico in coda al livello corrente (senza duplicati)."""
        f = self.P / "BACKLOG.md"
        testo = f.read_text()
        nuove = []
        for v in voci:
            v = " ".join((v or "").split())
            if v and v not in testo and v not in nuove:
                nuove.append(v)
        if not nuove:
            return
        tit = f"## Livello {self.stato['livello']}"
        if tit not in testo:
            testo += f"\n{tit}\n"
        i = testo.index(tit)
        j = testo.find("\n## ", i + 1)
        j = len(testo) if j < 0 else j
        blocco = "".join(f"- [ ] {v} ({origine}, giro {self.stato["giro"]})\n" for v in nuove[:3])
        testo = testo[:j].rstrip("\n") + "\n" + blocco + testo[j:]
        f.write_text(testo)

    # ------------------------------------------------------------ cancelli
    def cancelli(self, cartella):
        """Controlli deterministici. Ritorna (ok, motivi, metriche)."""
        motivi, met = [], {"pezzi": {}}
        build = self.conf["build"]
        rc, out = sh(build, self.P, timeout=self.conf.get("build_timeout_s", 900), log=cartella / "build.log")
        if rc != 0:
            righe = [l for l in out.strip().splitlines() if l.strip()]
            return False, [f"build fallita (codice {rc}): {righe[-1] if righe else '?'} "
                           f"(log: {(cartella / 'build.log').relative_to(self.wt)})"], met
        chk = str(self.wt / "tools/check_stampa.py")
        sli = str(self.wt / "tools/slice_stima.py")
        for p in self.conf.get("pezzi", []):
            stl = self.P / p["stl"]
            if not stl.exists():
                motivi.append(f"{p['nome']}: STL mancante ({p['stl']})")
                continue
            rc, out = sh([str(self.py), chk, "--json", str(stl)], self.P)
            try:
                r = json.loads(out[out.index("{"):])["pezzi"][0]
            except Exception:
                motivi.append(f"{p['nome']}: check_stampa non leggibile: {out[-300:]}")
                continue
            m = {"ingombro_mm": r["ingombro_mm"], "volume_cm3": r["volume_cm3"],
                 "sbalzi_mm2": r["sbalzi"]["area_mm2"], "corpi": r["corpi"]}
            if r.get("pareti", {}).get("campioni"):
                m["parete_min_mm"] = r["pareti"]["spessore_min_mm"]
                m["pareti_sottili_pct"] = r["pareti"]["percentuale_sotto_minimo"]
            if not r["manifold"]:
                motivi.append(f"{p['nome']}: non manifold")
            if not r["nel_piatto"]:
                motivi.append(f"{p['nome']}: fuori piatto {r['fuori_piatto_assi']}")
            if r["corpi"] > p.get("corpi_max", 1):
                motivi.append(f"{p['nome']}: {r['corpi']} corpi separati (max {p.get('corpi_max', 1)})")
            if "max_pareti_sottili_pct" in p and m.get("pareti_sottili_pct", 0) > p["max_pareti_sottili_pct"]:
                motivi.append(f"{p['nome']}: {m['pareti_sottili_pct']}% di pareti sotto il minimo "
                              f"(max {p['max_pareti_sottili_pct']}%)")
            if not self.args.no_slice:
                extra = [a for s in p.get("slice", []) for a in ("-s", s)]
                rc, out = sh([str(self.py), sli, "--json", "--supporti", *extra, str(stl)], self.P, timeout=900)
                try:
                    s = json.loads(out[out.index("["):])[0]
                    m.update(minuti=round(s["tempo_s"] / 60, 1), grammi=s["filamento_g"],
                             supporti=s["supporti_generati"])
                    if p.get("senza_supporti", True) and s["supporti_generati"]:
                        motivi.append(f"{p['nome']}: lo slicer genera supporti (il pezzo deve stamparsi senza)")
                    if "max_minuti" in p and m["minuti"] > p["max_minuti"]:
                        motivi.append(f"{p['nome']}: {m['minuti']} min di stampa (max {p['max_minuti']})")
                    if "max_grammi" in p and m["grammi"] > p["max_grammi"]:
                        motivi.append(f"{p['nome']}: {m['grammi']} g (max {p['max_grammi']})")
                except Exception:
                    motivi.append(f"{p['nome']}: slicing fallito: {out.strip()[-300:]}")
            met["pezzi"][p["nome"]] = m
        for gruppo in self.conf.get("interferenze", []):
            files = [str(self.P / g) for g in gruppo]
            rc, out = sh([str(self.py), chk, "--json", "--interf", "--no-pareti", *files], self.P)
            try:
                for i in json.loads(out[out.index("{"):])["interferenze"]:
                    if not i.get("ok"):
                        motivi.append(f"interferenza {Path(i['a']).name} / {Path(i['b']).name}: "
                                      f"{i.get('volume_mm3', i.get('errore'))} mm3")
            except Exception:
                motivi.append(f"controllo interferenze non leggibile: {out[-300:]}")
        for sp in self.conf.get("spec", []):
            rc, out = sh([str(self.wt / ".venv/bin/agentcad"), "check-spec", sp["step"], sp["spec"]], self.P)
            try:
                r = json.loads(out.strip().splitlines()[-1])
                if not r.get("passed"):
                    motivi.append(f"check-spec {sp['spec']}: mancano {r.get('missing_features')}")
            except Exception:
                motivi.append(f"check-spec {sp['spec']} non leggibile: {out[-300:]}")
        (cartella / "cancelli.json").write_text(json.dumps({"motivi": motivi, "metriche": met}, indent=1))
        return not motivi, motivi, met

    def file_toccati(self):
        """File modificati/aggiunti nel worktree rispetto a HEAD."""
        # niente strip() sull'output: la prima colonna di --porcelain puo' essere uno spazio
        _, out = sh(["git", "status", "--porcelain", "--untracked-files=all"], self.wt)
        return [l[3:].strip('"') for l in out.splitlines() if len(l) > 3]

    def violazioni(self, toccati):
        prot = [str(self.rel / p) for p in self.conf.get("protetti", PROTETTI_DEFAULT)]
        prot += [str(self.rel / s["spec"]) for s in self.conf.get("spec", [])]
        v = []
        for f in toccati:
            if f.startswith(".harness/") or f == ".venv":
                continue
            if not f.startswith(str(self.rel) + "/"):
                v.append(f"{f} (fuori dal progetto)")
            elif any(f == p or f.startswith(p.rstrip("/") + "/") for p in prot):
                v.append(f"{f} (protetto)")
        return v

    def scarta(self):
        """Riporta il progetto all'ultima versione accettata (solo nel worktree dell'harness)."""
        git(["checkout", "--", "."], self.wt)
        git(["clean", "-fdq", "--", str(self.rel)], self.wt)

    # ------------------------------------------------------------ render e foglio
    def render(self, cartella):
        rc_conf = self.conf.get("render", {})
        inq = self.S / "inquadratura.json"
        cfg = {
            "pezzi": [dict(p, stl=str(self.P / p["stl"])) for p in rc_conf.get("pezzi", [])],
            "viste": rc_conf.get("viste", {"3q": [35, 25], "fronte": [0, 5], "lato": [90, 5], "alto": [0, 89]}),
            "dettagli": rc_conf.get("dettagli", []),
            "risoluzione": rc_conf.get("risoluzione", [900, 700]),
            "campioni": rc_conf.get("campioni", 48),
            "out": str(cartella / "render"),
        }
        if inq.exists():
            cfg["inquadratura"] = json.loads(inq.read_text())
        else:
            cfg["inquadratura_out"] = str(inq)
        (cartella / "render").mkdir(exist_ok=True)
        (cartella / "render.json").write_text(json.dumps(cfg, indent=1))
        rc, out = sh(["blender", "-b", "--factory-startup", "-P", str(QUI / "render_fissi.py"), "--",
                      str(cartella / "render.json")], self.P, timeout=1800, log=cartella / "render.log")
        if "RENDER_OK" not in out:
            raise RuntimeError(f"render fallito, vedi {cartella / 'render.log'}")
        return self.foglio(cartella / "render", cartella / "foglio.png")

    @staticmethod
    def foglio(cartella, out, etichetta=""):
        """Unisce le viste in un'unica immagine a griglia (una per versione)."""
        from PIL import Image, ImageDraw
        img = sorted(cartella.glob("*.png"))
        if not img:
            raise RuntimeError(f"nessuna immagine in {cartella}")
        tiles = [Image.open(i).convert("RGB") for i in img]
        w, h = tiles[0].size
        col = 3 if len(tiles) > 4 else 2
        rig = -(-len(tiles) // col)
        fg = Image.new("RGB", (w * col, h * rig + 40), "white")
        d = ImageDraw.Draw(fg)
        d.text((10, 10), etichetta, fill="black")
        for k, (t, nome) in enumerate(zip(tiles, img)):
            x, y = (k % col) * w, (k // col) * h + 40
            fg.paste(t, (x, y))
            d.text((x + 8, y + 8), nome.stem, fill="black")
        fg.save(out)
        return out

    # ------------------------------------------------------------ agenti (motore configurabile)
    def carica_motore(self):
        """Ricetta del motore-agente scelto (--motore, poi harness.json, default 'kiro')."""
        reg = json.loads((QUI / "motori.json").read_text())
        nome = self.args.motore or self.conf.get("motore", "kiro")
        if nome not in reg:
            sys.exit(f"motore '{nome}' sconosciuto. Disponibili: "
                     + ", ".join(k for k in reg if not k.startswith('_')))
        m = reg[nome]
        for c in m.get("richiede", []):
            if not shutil.which(c):
                sys.exit(f"il motore '{nome}' richiede '{c}', che non e' nel PATH.")
        self.motore_nome, self.motore = nome, m

    def prompt_sistema(self, agente):
        """Prompt di sistema per i motori senza file-agente (codex/aider/...).
        Da tools/harness/prompt_sistema_<agente>.md se esiste, altrimenti da .kiro/agents/<agente>.json."""
        f = QUI / f"prompt_sistema_{agente}.md"
        if f.exists():
            return f.read_text()
        aj = self.repo / ".kiro" / "agents" / f"{agente}.json"
        if aj.exists():
            return json.loads(aj.read_text()).get("prompt", "")
        return ""

    def agente_cli(self, agente, prompt, log, timeout_min):
        """Invoca il motore scelto in modalita' non interattiva. Ritorna (codice, output)."""
        m = self.motore
        if m.get("system_prompt"):
            sp = self.prompt_sistema(agente)
            if sp:
                prompt = sp.rstrip() + "\n\n---\n\n" + prompt
        argv = list(self.conf["motore_cmd"]) if m.get("override_cmd_da_conf") else list(m["cmd"])
        sub = {
            "{agente}": agente,
            "{modello}": self.conf.get("modello", ""),
            "{trust}": (m.get("trust", {}) or {}).get(agente, ""),
        }
        # Costruisci l'argv in coppie: un flag "--x {segnaposto}" il cui valore si risolve
        # a vuoto fa saltare anche il flag. Cosi' --model sparisce quando non c'e' un modello.
        prompt_su_stdin = False
        VUOTI = {"--model", "--agent"}            # flag che hanno sempre un valore
        argv_out, i = [], 0
        while i < len(argv):
            a = argv[i]
            if a == "{prompt}":
                argv_out.append(prompt)
            elif a == "{prompt_stdin}":
                prompt_su_stdin = True
            elif a in VUOTI and i + 1 < len(argv):
                val = argv[i + 1]
                for k, v in sub.items():
                    val = val.replace(k, v)
                if val != "":
                    argv_out += [a, val]
                i += 1                            # consuma anche il valore
            else:
                for k, v in sub.items():
                    a = a.replace(k, v)
                argv_out.append(a)
            i += 1
        argv = argv_out
        stdin = prompt if prompt_su_stdin else None
        try:
            p = subprocess.run(argv, cwd=self.wt, capture_output=True, text=True,
                               timeout=timeout_min * 60, input=stdin)
            out, rc = p.stdout + p.stderr, p.returncode
        except subprocess.TimeoutExpired as e:
            out, rc = f"{e.stdout or ''}{e.stderr or ''}\nTIMEOUT dopo {timeout_min} min", 124
        Path(log).write_text(f"$ {' '.join(argv)}\n"
                             + (f"[prompt su stdin, {len(prompt)} char]\n" if prompt_su_stdin else "")
                             + "\n" + out)
        return rc, out

    # alias storico
    def kiro(self, agente, prompt, log, timeout_min):
        return self.agente_cli(agente, prompt, log, timeout_min)

    def designer(self, cartella, voce, ultimo_errore, variante=""):
        prompt = (QUI / "prompt_designer.md").read_text().format(
            progetto=self.rel, livello=self.stato["livello"],
            nome_livello=self.livelli()[self.stato["livello"] - 1],
            voce=voce or "(backlog vuoto per questo livello: scegli tu UNA modifica del livello corrente, "
                         "coerente con BRIEF.md e RUBRICA.md, e aggiungila al BACKLOG come [x])",
            build=self.conf["build"], ultimo_errore=ultimo_errore or "nessuno",
            diario=self.coda_diario(), cartella=cartella)
        if variante:
            prompt += "\n" + variante + "\n"
        (cartella / "prompt_designer.md").write_text(prompt)
        if self.args.simula_designer:
            return sh(self.args.simula_designer, self.P, log=cartella / "designer.log")
        return self.kiro("designer-3d", prompt, cartella / "designer.log", self.conf.get("designer_timeout_min", 30))

    @staticmethod
    def affianca(fogli, etichette, out):
        """Mette i fogli uno accanto all'altro con un'etichetta grande sopra ciascuno."""
        from PIL import Image, ImageDraw, ImageFont
        imm = [Image.open(f).convert("RGB") for f in fogli]
        scala = 900 / imm[0].width
        imm = [i.resize((int(i.width * scala), int(i.height * scala))) for i in imm]
        w, h = imm[0].size
        tela = Image.new("RGB", (w * len(imm) + 20 * (len(imm) - 1), h + 60), "white")
        d = ImageDraw.Draw(tela)
        try:
            font = ImageFont.load_default(size=32)
        except TypeError:
            font = ImageFont.load_default()
        for k, (i, e) in enumerate(zip(imm, etichette)):
            tela.paste(i, (k * (w + 20), 60))
            d.text((k * (w + 20) + 10, 12), e, fill="black", font=font)
        tela.save(out)
        return out

    def note_designer(self):
        f = self.P / "NOTE_DESIGNER.md"
        return f.read_text().strip() if f.exists() else "(nessuna nota)"

    def critico_umano(self, cartella, foglio_best, foglio_cand):
        """Tu sei il critico: vedi le due versioni affiancate e scegli dal terminale."""
        conf = self.affianca([foglio_best, foglio_cand], ["A  attuale (la migliore finora)", "B  nuova"],
                             cartella / "confronto.png")
        if not os.environ.get("HARNESS_NO_OPEN"):
            subprocess.Popen(["xdg-open", str(conf)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"\n=== Giro {self.stato['giro']}, livello {self.stato['livello']} "
              f"({self.livelli()[self.stato['livello'] - 1]})")
        print(f"Confronto: {conf}\nViste singole: {cartella / 'render'}")
        print(f"Note del designer:\n{self.note_designer()}\n")
        while (r := input("Quale tieni? [a] attuale / [b] nuova / [p] pari / [s] stop: ").strip().lower()[:1]) \
                not in ("a", "b", "p", "s"):
            pass
        if r == "s":
            (self.S / "STOP").touch()
            r = "p"
        motivo = input("Perché, o cosa non va (lo legge il designer al prossimo giro): ").strip()
        sugg = input("Prossime modifiche da mettere nel backlog, separate da ';' (invio = nessuna): ")
        v = {"vincitore": {"a": "attuale", "b": "nuova", "p": "pari"}[r], "motivo": motivo or "(nessun motivo)",
             "suggerimenti": [s for s in sugg.split(";") if s.strip()], "critico": "umano"}
        (cartella / "verdetto.json").write_text(json.dumps(v, indent=1, ensure_ascii=False))
        return r == "b", v

    def critico(self, cartella, foglio_best, foglio_cand):
        if self.modo_critico == "umano":
            return self.critico_umano(cartella, foglio_best, foglio_cand)
        # ordine casuale: il critico non sa quale sia la versione nuova
        nuova_e_x = random.random() < 0.5
        x, y = (foglio_cand, foglio_best) if nuova_e_x else (foglio_best, foglio_cand)
        shutil.copy(x, cartella / "X.png")
        shutil.copy(y, cartella / "Y.png")
        verd = cartella / "verdetto.json"
        prompt = (QUI / "prompt_critico.md").read_text().format(
            progetto=self.rel, livello=self.stato["livello"],
            nome_livello=self.livelli()[self.stato["livello"] - 1],
            x=(cartella / "X.png").relative_to(self.wt), y=(cartella / "Y.png").relative_to(self.wt),
            verdetto=verd.relative_to(self.wt))
        (cartella / "prompt_critico.md").write_text(prompt)
        if self.args.simula_critico:
            scelta = self.args.simula_critico
            if scelta == "caso":
                scelta = random.choice(["nuova", "vecchia"])
            vince = ("X" if nuova_e_x else "Y") if scelta == "nuova" else ("Y" if nuova_e_x else "X")
            verd.write_text(json.dumps({"vincitore": vince, "motivo": "simulato", "suggerimenti": []}))
        else:
            self.kiro("critico-3d", prompt, cartella / "critico.log", self.conf.get("critico_timeout_min", 10))
        try:
            v = json.loads(verd.read_text())
        except Exception:
            return False, {"vincitore": "?", "motivo": "verdetto mancante o non valido", "suggerimenti": []}
        v["candidata_era"] = "X" if nuova_e_x else "Y"
        verd.write_text(json.dumps(v, indent=1, ensure_ascii=False))
        return v.get("vincitore") == v["candidata_era"], v

    def coda_diario(self, n=6):
        f = self.S / "DIARIO.md"
        if not f.exists():
            return "(vuoto)"
        voci = f.read_text().split("\n## ")
        return "\n## ".join(voci[-n:]).strip()

    # ------------------------------------------------------------ ciclo
    def baseline(self):
        c = self.S / "giri" / "000"
        c.mkdir(parents=True, exist_ok=True)
        ok, motivi, met = self.cancelli(c)
        if not ok:
            sys.exit("Il design di partenza non passa i cancelli, correggilo prima di avviare:\n- "
                     + "\n- ".join(motivi))
        f = self.render(c)
        shutil.copy(f, self.S / "best" / "foglio.png")
        self.stato.update(best_commit=git(["rev-parse", "HEAD"], self.wt), best_metriche=met)
        self.diario(f"Baseline: cancelli ok, render in giri/000. Metriche: {json.dumps(met['pezzi'])}")
        self.salva()

    def giro(self):
        st = self.stato
        st["giro"] += 1
        c = self.S / "giri" / f"{st['giro']:03d}"
        c.mkdir(parents=True, exist_ok=True)
        voce = self.prossima_voce()
        t0 = time.time()
        rc, _ = self.designer(c, voce, st.get("ultimo_errore"))
        toccati = [f for f in self.file_toccati() if not f.startswith(".harness/") and f != ".venv"]
        esito = {"giro": st["giro"], "livello": st["livello"], "voce": voce, "designer_rc": rc,
                 "designer_min": round((time.time() - t0) / 60, 1)}

        def rifiuta(perche, plateau=True):
            perche = perche if len(perche) < 1200 else perche[:300] + " [...] " + perche[-800:]
            self.scarta()
            st["ultimo_errore"] = perche
            if plateau:
                st["plateau"] += 1
            self.diario(f"Voce: {voce}\nRIFIUTATO: {perche}")
            esito["esito"] = f"rifiutato: {perche}"

        v = self.violazioni(toccati)
        if not toccati:
            rifiuta("il designer non ha modificato nulla")
        elif v:
            rifiuta("modificati file non consentiti: " + ", ".join(v))
        else:
            ok, motivi, met = self.cancelli(c)
            if not ok:
                st["fallimenti_di_fila"] += 1
                rifiuta("cancelli: " + "; ".join(motivi))
            else:
                st["fallimenti_di_fila"] = 0
                foglio = self.render(c)
                migliore, verd = self.critico(c, self.S / "best" / "foglio.png", foglio)
                esito["verdetto"] = verd
                self.aggiungi_voci(verd.get("suggerimenti", []), "tu" if verd.get("critico") == "umano" else "critico")
                if migliore:
                    if voce:
                        self.spunta_voce(voce)
                    st["accettati"] += 1
                    git(["add", "-A", "--", str(self.rel)], self.wt)
                    git(["commit", "-q", "-m", f"harness {self.nome} giro {st['giro']}: {voce or 'modifica libera'}",
                         "-m", f"Critico: {verd.get('motivo', '')}"], self.wt)
                    git(["tag", "-f", f"harness/{self.nome}/best-{st['accettati']:03d}"], self.wt)
                    shutil.copy(foglio, self.S / "best" / "foglio.png")
                    shutil.copy(foglio, self.S / "best" / f"best-{st['accettati']:03d}.png")
                    st.update(best_commit=git(["rev-parse", "HEAD"], self.wt), best_metriche=met,
                              plateau=0, ultimo_errore=None)
                    self.diario(f"Voce: {voce}\nACCETTATO (best-{st['accettati']:03d}). Critico: "
                                f"{verd.get('motivo', '')}\nMetriche: {json.dumps(met['pezzi'])}")
                    esito["esito"] = "accettato"
                else:
                    # i suggerimenti aggiunti al backlog restano: si salvano prima di scartare
                    backlog = (self.P / "BACKLOG.md").read_text()
                    self.scarta()
                    (self.P / "BACKLOG.md").write_text(backlog)
                    git(["commit", "-q", "-am", f"harness {self.nome}: backlog aggiornato dal critico"],
                        self.wt, check=False)
                    st["plateau"] += 1
                    st["ultimo_errore"] = f"il critico ha preferito la versione precedente: {verd.get('motivo', '')}"
                    self.diario(f"Voce: {voce}\nRIFIUTATO dal critico: {verd.get('motivo', '')}")
                    esito["esito"] = "rifiutato dal critico"
        with open(self.S / "giri.jsonl", "a") as f:
            f.write(json.dumps(esito, ensure_ascii=False) + "\n")
        if st["plateau"] >= self.conf.get("plateau", 4):
            st["plateau"] = 0
            st["livello"] += 1
            self.diario(f"Plateau: passo al livello {st['livello']}")
        self.salva()
        self.riepilogo()
        return esito

    def motivo_stop(self, t_inizio, giri_sessione):
        st, b = self.stato, self.conf.get("budget", {})
        if (self.S / "STOP").exists():
            return "file STOP"
        if st["livello"] > len(self.livelli()):
            return "tutti i livelli completati (plateau sull'ultimo)"
        if st["giro"] >= b.get("giri_totali", 60):
            return f"raggiunti {b.get('giri_totali', 60)} giri totali"
        if self.args.giri and giri_sessione >= self.args.giri:
            return f"fatti i {self.args.giri} giri richiesti"
        if (time.time() - t_inizio) / 60 >= b.get("minuti_sessione", 600):
            return "tempo della sessione esaurito"
        if st["fallimenti_di_fila"] >= b.get("max_fallimenti_di_fila", 5):
            return f"{st['fallimenti_di_fila']} giri di fila bocciati dai cancelli: serve un intervento"
        ogni = b.get("checkpoint_ogni_accettati", 8)
        if st["accettati"] and st["accettati"] % ogni == 0 and st.get("ultimo_checkpoint") != st["accettati"]:
            st["ultimo_checkpoint"] = st["accettati"]
            return f"checkpoint: {st['accettati']} versioni accettate, rivedi best/ e la rubrica"
        return None

    def riepilogo(self):
        st = self.stato
        righe = [json.loads(l) for l in (self.S / "giri.jsonl").read_text().splitlines()] \
            if (self.S / "giri.jsonl").exists() else []
        txt = [f"# Harness {self.nome}", "",
               f"Worktree `{self.wt}`, branch `harness/{self.nome}`. Aggiornato {ora()}.", "",
               f"- giri: {st['giro']}, accettati: {st['accettati']}, livello {st['livello']}/{len(self.livelli())}"
               + (f" ({self.livelli()[st['livello'] - 1]})" if st["livello"] <= len(self.livelli()) else ""),
               f"- migliore: commit `{(st['best_commit'] or '')[:8]}`, foglio `best/foglio.png`",
               f"- fermo: {st.get('fine_motivo') or 'in corso'}", "", "| giro | liv | voce | esito |",
               "|---|---|---|---|"]
        def cella(s, n):
            return " ".join(str(s).split()).replace("|", "/")[:n]
        txt += [f"| {r['giro']} | {r['livello']} | {cella(r.get('voce') or '-', 60)} | {cella(r['esito'], 90)} |"
                for r in righe]
        if st.get("best_metriche"):
            txt += ["", "Metriche della versione migliore:", "```",
                    json.dumps(st["best_metriche"]["pezzi"], indent=1), "```"]
        (self.S / "RIEPILOGO.md").write_text("\n".join(txt) + "\n")

    # ------------------------------------------------------------ proposte (critico umano asincrono)
    def ramo_proposta(self, k):
        # non sotto harness/<nome>/: un ramo non puo' essere anche "cartella" di altri rami
        return f"harness-proposte/{self.nome}/g{self.stato['giro']:03d}-p{k}"

    def genera_proposte(self, K):
        """K alternative per la stessa voce, tutte dalla versione migliore. Poi si aspetta la tua scelta."""
        st = self.stato
        st["giro"] += 1
        c = self.S / "giri" / f"{st['giro']:03d}"
        c.mkdir(parents=True, exist_ok=True)
        voce = self.prossima_voce()
        base = f"harness/{self.nome}"
        proposte, scartate, note_prec = [], [], []
        for k in range(1, K + 1):
            ck = c / f"p{k}"
            ck.mkdir(exist_ok=True)
            variante = (f"Questa è la proposta {k} di {K} per la stessa voce: l'utente sceglierà la migliore. "
                        "Proponi un'interpretazione chiaramente diversa dalle precedenti, sempre dentro il BRIEF.")
            if note_prec:
                variante += "\nNote delle proposte già fatte (non ripeterle):\n" + "\n---\n".join(note_prec)
            print(f"proposta {k}/{K}: designer...", flush=True)
            self.designer(ck, voce, st.get("ultimo_errore"), variante)
            toccati = [f for f in self.file_toccati() if not f.startswith(".harness/") and f != ".venv"]
            v = self.violazioni(toccati)
            motivi = (["nessuna modifica"] if not toccati else
                      ["file non consentiti: " + ", ".join(v)] if v else None)
            if motivi is None:
                ok, motivi, met = self.cancelli(ck)
                motivi = None if ok else motivi
            if motivi:
                scartate.append({"k": k, "motivi": motivi})
                self.scarta()
                print(f"  scartata: {'; '.join(motivi)[:200]}")
                continue
            foglio = self.render(ck)
            note = self.note_designer()
            ramo = self.ramo_proposta(k)
            git(["checkout", "-q", "-b", ramo], self.wt)
            git(["add", "-A", "--", str(self.rel)], self.wt)
            git(["commit", "-q", "-m", f"proposta {k} giro {st['giro']}: {voce or 'modifica libera'}"], self.wt)
            git(["checkout", "-q", base], self.wt)
            proposte.append({"k": k, "ramo": ramo, "foglio": str(foglio), "note": note, "metriche": met})
            note_prec.append(f"Proposta {k}: {note}")
            print("  pronta")
        st["in_attesa"] = {"giro": st["giro"], "voce": voce, "proposte": proposte, "scartate": scartate}
        if not proposte:
            st["in_attesa"] = None
            st["fallimenti_di_fila"] += 1
            self.diario(f"Voce: {voce}\nNessuna delle {K} proposte ha passato i cancelli: {scartate}")
        else:
            st["fallimenti_di_fila"] = 0
            self.pagina_proposte()
        self.salva()
        self.riepilogo()

    def pagina_proposte(self):
        att = self.stato["in_attesa"]
        fogli = [self.S / "best" / "foglio.png"] + [Path(p["foglio"]) for p in att["proposte"]]
        etich = ["0  attuale"] + [f"{p['k']}  proposta" for p in att["proposte"]]
        conf = self.affianca(fogli, etich, self.S / "PROPOSTE.png")
        righe = [f"# Proposte del giro {att['giro']}", "", f"Voce: {att['voce'] or 'modifica libera'}", "",
                 f"Confronto: `{conf}`", ""]
        for p in att["proposte"]:
            righe += [f"## Proposta {p['k']}", f"Foglio: `{p['foglio']}`", "", p["note"], "",
                      "```", json.dumps(p["metriche"]["pezzi"], ensure_ascii=False), "```", ""]
        for s in att["scartate"]:
            righe += [f"- proposta {s['k']} scartata dai cancelli: {'; '.join(s['motivi'])[:300]}"]
        nums = "|".join(str(p["k"]) for p in att["proposte"])
        righe += ["", "Per scegliere:", "```",
                  f".venv/bin/python tools/harness/harness.py {self.rel} --scegli {nums}|nessuna "
                  "--motivo \"perche'\" --suggerimenti \"modifica 1; modifica 2\"", "```"]
        (self.S / "PROPOSTE.md").write_text("\n".join(righe) + "\n")
        if not os.environ.get("HARNESS_NO_OPEN"):
            subprocess.Popen(["xdg-open", str(conf)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def scegli(self, scelta, motivo, suggerimenti):
        st, att = self.stato, self.stato.get("in_attesa")
        if not att:
            sys.exit("Nessuna proposta in attesa.")
        st["giro"] = att["giro"]
        sugg = [s for s in (suggerimenti or "").split(";") if s.strip()]
        voce = att["voce"]
        esito = {"giro": att["giro"], "livello": st["livello"], "voce": voce, "critico": "umano",
                 "verdetto": {"scelta": scelta, "motivo": motivo, "suggerimenti": sugg}}
        if scelta == "nessuna":
            st["plateau"] += 1
            st["ultimo_errore"] = f"l'utente ha scartato tutte le proposte: {motivo}"
            self.diario(f"Voce: {voce}\nTUTTE LE PROPOSTE RIFIUTATE dall'utente: {motivo}")
            esito["esito"] = "proposte rifiutate dall'utente"
        else:
            p = next((p for p in att["proposte"] if str(p["k"]) == str(scelta)), None)
            if not p:
                sys.exit(f"Proposta {scelta} inesistente: scegli tra {[p['k'] for p in att['proposte']]}")
            git(["merge", "-q", "--ff-only", p["ramo"]], self.wt)
            st["accettati"] += 1
            if voce:
                self.spunta_voce(voce)
            git(["tag", "-f", f"harness/{self.nome}/best-{st['accettati']:03d}"], self.wt)
            shutil.copy(p["foglio"], self.S / "best" / "foglio.png")
            shutil.copy(p["foglio"], self.S / "best" / f"best-{st['accettati']:03d}.png")
            st.update(best_metriche=p["metriche"], plateau=0, ultimo_errore=None)
            self.diario(f"Voce: {voce}\nACCETTATA dall'utente la proposta {scelta} (best-{st['accettati']:03d}): "
                        f"{motivo}\nNote del designer: {p['note']}")
            esito["esito"] = f"accettata proposta {scelta}"
        self.aggiungi_voci(sugg, "tu")
        git(["commit", "-q", "-am", f"harness {self.nome}: scelta dell'utente al giro {att['giro']}"],
            self.wt, check=False)
        st["best_commit"] = git(["rev-parse", "HEAD"], self.wt)
        for q in att["proposte"]:
            git(["branch", "-q", "-D", q["ramo"]], self.wt, check=False)
        st["in_attesa"] = None
        if st["plateau"] >= self.conf.get("plateau", 4):
            st["plateau"] = 0
            st["livello"] += 1
            self.diario(f"Plateau: passo al livello {st['livello']}")
        with open(self.S / "giri.jsonl", "a") as f:
            f.write(json.dumps(esito, ensure_ascii=False) + "\n")
        self.salva()
        self.riepilogo()
        print(esito["esito"])

    def esegui(self):
        self.prepara()
        if self.args.stato:
            self.riepilogo()
            print((self.S / "RIEPILOGO.md").read_text())
            return
        if self.args.scegli:
            return self.scegli(self.args.scegli, self.args.motivo or "", self.args.suggerimenti)
        if self.stato.get("in_attesa"):
            sys.exit(f"Ci sono proposte in attesa della tua scelta: vedi {self.S / 'PROPOSTE.md'}")
        if not self.args.simula_designer:
            self.carica_motore()
            if self.motore_nome == "kiro" and not os.environ.get("KIRO_API_KEY"):
                print("Nota: motore 'kiro' senza KIRO_API_KEY; serve il login di kiro-cli.", file=sys.stderr)
        (self.S / "STOP").unlink(missing_ok=True)
        if not self.stato["best_commit"]:
            print("Giro 0: baseline")
            self.baseline()
        if self.args.proposte:
            self.genera_proposte(self.args.proposte)
            if self.stato.get("in_attesa"):
                print(f"Proposte pronte: {self.S / 'PROPOSTE.md'} (confronto in PROPOSTE.png)")
            return
        t0, n = time.time(), 0
        self.stato["fine_motivo"] = None
        while not (motivo := self.motivo_stop(t0, n)):
            e = self.giro()
            n += 1
            print(f"giro {e['giro']} (liv {e['livello']}): {e['esito']}", flush=True)
        self.stato["fine_motivo"] = motivo
        self.salva()
        self.riepilogo()
        print(f"Fermo: {motivo}\nRiepilogo: {self.S / 'RIEPILOGO.md'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("progetto", help="cartella del progetto con harness.json")
    ap.add_argument("--giri", type=int, help="massimo giri in questa sessione")
    ap.add_argument("--stato", action="store_true", help="mostra il riepilogo ed esce")
    ap.add_argument("--no-slice", action="store_true", help="salta lo slicing nei cancelli (piu' veloce)")
    ap.add_argument("--motore", help="motore-agente: kiro, codex, aider, claude, comando "
                    "(vedi tools/harness/motori.json). Default: da harness.json o 'kiro'.")
    ap.add_argument("--critico", choices=["ai", "umano"],
                    help="chi giudica ogni giro: l'agente (default) o tu dal terminale")
    ap.add_argument("--proposte", type=int, metavar="K",
                    help="genera K alternative per la prossima voce e aspetta la tua scelta")
    ap.add_argument("--scegli", metavar="N|nessuna", help="scegli una proposta in attesa (o nessuna)")
    ap.add_argument("--motivo", help="con --scegli: perche' (lo legge il designer)")
    ap.add_argument("--suggerimenti", help="con --scegli: prossime modifiche per il backlog, separate da ';'")
    ap.add_argument("--simula-designer", help="comando shell al posto del designer (test)")
    ap.add_argument("--simula-critico", choices=["nuova", "vecchia", "caso"], help="critico finto (test)")
    a = ap.parse_args()
    Harness(a.progetto, a).esegui()


if __name__ == "__main__":
    main()
