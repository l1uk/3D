#!/usr/bin/env python3
"""
analizza_sordina.py  -  confronta registrazioni di tromba con e senza sordina.

Legge i WAV, trova da solo le note tenute, e stampa una tabella di numeri
(livello, armoniche, intonazione). Nessun audio da condividere: incolla la tabella.

Uso:
    python analizza_sordina.py --ref 01_senza.wav 02_A_vuota.wav 03_A_imbottita.wav
    python analizza_sordina.py --ref 01_senza.wav --rumore 00_rumore.wav 02_A_vuota.wav

Requisiti:  pip install numpy soundfile      (in alternativa basta numpy + scipy)

Convenzioni:
  - le note sono indicate come SCRITTE per tromba in Sib (suono reale = 2 semitoni sotto)
  - "att." = attenuazione = livello(senza sordina) - livello(con sordina), in dB: positivo = piu' silenzio
"""
import argparse
import math
import sys

import numpy as np

NOMI = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


# ---------------------------------------------------------------- lettura file
def carica(path):
    try:
        import soundfile as sf
        x, sr = sf.read(path, always_2d=True)
        x = x.astype(np.float64)
    except ImportError:
        from scipy.io import wavfile
        sr, x = wavfile.read(path)
        k = x.dtype.kind
        if k == "i":
            x = x.astype(np.float64) / float(np.iinfo(x.dtype).max + 1)
        elif k == "u":
            x = (x.astype(np.float64) - 128.0) / 128.0
        else:
            x = x.astype(np.float64)
        if x.ndim == 1:
            x = x[:, None]
    clip = bool(np.max(np.abs(x)) >= 0.999)
    return x.mean(axis=1), sr, clip


# ------------------------------------------------------- livelli e segmentazione
def livelli_frame(x, sr, win=0.05):
    n = int(sr * win)
    m = len(x) // n
    fr = x[: m * n].reshape(m, n)
    return 20 * np.log10(np.sqrt((fr ** 2).mean(axis=1)) + 1e-12), n


def trova_note(x, sr, margine_db=10.0, min_len=1.2, buco_max=0.3):
    lev, n = livelli_frame(x, sr)
    pavimento = np.percentile(lev, 10)
    on = lev > pavimento + margine_db
    # chiude i buchi brevi (respiri, vibrato)
    fmax = int(buco_max / 0.05)
    i = 0
    while i < len(on):
        if not on[i]:
            j = i
            while j < len(on) and not on[j]:
                j += 1
            if 0 < i and j < len(on) and (j - i) <= fmax:
                on[i:j] = True
            i = j
        else:
            i += 1
    seg, i = [], 0
    while i < len(on):
        if on[i]:
            j = i
            while j < len(on) and on[j]:
                j += 1
            if (j - i) * 0.05 >= min_len:
                L = j - i
                a = i + int(0.25 * L)
                b = j - int(0.25 * L)
                seg.append((a * n, b * n, i * n, j * n))
            i = j
        else:
            i += 1
    return seg, pavimento


# ------------------------------------------------------------- analisi di una nota
def f0_autocorr(y, sr, fmin=140.0, fmax=1250.0):
    y = y[: min(len(y), sr)] - np.mean(y[: min(len(y), sr)])
    N = 1 << (2 * len(y) - 1).bit_length()
    F = np.fft.rfft(y, N)
    acf = np.fft.irfft(F * np.conj(F))[: len(y)]
    acf /= acf[0] + 1e-18
    lo, hi = int(sr / fmax), int(sr / fmin)
    seg = acf[lo:hi]
    m = seg.max()
    cand = [k for k in range(1, len(seg) - 1)
            if seg[k] >= 0.9 * m and seg[k] >= seg[k - 1] and seg[k] >= seg[k + 1]]
    k = cand[0] if cand else int(np.argmax(seg))
    if 0 < k < len(seg) - 1:  # interpolazione parabolica
        a, b, c = seg[k - 1], seg[k], seg[k + 1]
        d = 0.5 * (a - c) / (a - 2 * b + c + 1e-18)
    else:
        d = 0.0
    return sr / (lo + k + d)


def analizza_nota(y, sr):
    rms = 20 * math.log10(math.sqrt(float(np.mean(y ** 2))) + 1e-12)
    f0 = f0_autocorr(y, sr)
    w = np.hanning(len(y))
    N = 1 << (len(y) - 1).bit_length()
    X = np.abs(np.fft.rfft(y * w, N)) * 2.0 / np.sum(w)
    fr = np.fft.rfftfreq(N, 1.0 / sr)

    def picco(k):
        m = (fr > k * f0 * 0.975) & (fr < k * f0 * 1.025)
        return 20 * math.log10(float(X[m].max()) + 1e-12) if m.any() and k * f0 < sr / 2 else float("nan")

    arm = [picco(k) for k in range(1, 6)]
    band = (fr > 100) & (fr < 8000)
    p = X[band] ** 2
    centroide = float(np.sum(fr[band] * p) / (np.sum(p) + 1e-18))
    midi_scritta = 69 + 12 * math.log2(f0 / 440.0) + 2  # tromba in Sib: scritta = reale + 2 semitoni
    r = round(midi_scritta)
    nome = NOMI[r % 12] + str(r // 12 - 1)
    cent = (midi_scritta - r) * 100
    return dict(nota=nome, f0=f0, cent=cent, rms=rms, arm=arm, centroide=centroide)


# ----------------------------------------------- stabilita' della nota (effetto "wah")
def _env_hilbert(y):
    n = len(y)
    h = np.zeros(n)
    if n % 2 == 0:
        h[0] = h[n // 2] = 1
        h[1:n // 2] = 2
    else:
        h[0] = 1
        h[1:(n + 1) // 2] = 2
    return np.abs(np.fft.ifft(np.fft.fft(y) * h))


def _picco_modulazione(sig, fs, fmin=0.7, fmax=12.0):
    t = np.arange(len(sig))
    sig = sig - np.polyval(np.polyfit(t, sig, 2), t)          # toglie l'andamento lento
    N = 1 << (len(sig) * 8 - 1).bit_length()
    X = np.abs(np.fft.rfft(sig * np.hanning(len(sig)), N))
    fr = np.fft.rfftfreq(N, 1.0 / fs)
    m = (fr >= fmin) & (fr <= fmax)
    return float(fr[m][np.argmax(X[m])]) if m.any() else float("nan")


def stabilita(y, sr):
    """modulazione di ampiezza (dB rms) e di intonazione (cent rms) con la frequenza dominante (0.7-12 Hz)"""
    env = _env_hilbert(y)
    m = max(1, int(0.02 * sr))
    env = np.convolve(env, np.ones(m) / m, "same")
    fs = 200.0
    db = 20 * np.log10(env[:: int(sr / fs)] + 1e-12)[10:-10]
    t = np.arange(len(db))
    am_db = float(np.std(db - np.polyval(np.polyfit(t, db, 2), t)))
    am_hz = _picco_modulazione(db, fs)
    win, hop = int(0.1 * sr), int(0.025 * sr)
    f0s = []
    for s0 in range(0, len(y) - win, hop):
        try:
            f0s.append(f0_autocorr(y[s0:s0 + win], sr))
        except Exception:
            f0s.append(np.nan)
    f0s = np.array(f0s)
    cent = 1200 * np.log2(f0s / np.nanmedian(f0s))
    cent[np.abs(cent) > 150] = np.nan
    ok = ~np.isnan(cent)
    if ok.sum() < 8:
        return dict(am_db=am_db, am_hz=am_hz, fm_cent=float("nan"), fm_hz=float("nan"))
    cent = np.interp(np.arange(len(cent)), np.where(ok)[0], cent[ok])
    return dict(am_db=am_db, am_hz=am_hz, fm_cent=float(np.std(cent)),
                fm_hz=_picco_modulazione(cent, sr / hop))


def analizza_file(path):
    x, sr, clip = carica(path)
    seg, pav = trova_note(x, sr)
    note = []
    for a, b, A, B in seg:
        if b - a < int(0.4 * sr):
            continue
        info = analizza_nota(x[a:b], sr)
        y_full = x[A + int(0.3 * sr): B - int(0.3 * sr)]
        if len(y_full) >= int(0.8 * sr):
            info.update(stabilita(y_full, sr))
        else:
            info.update(am_db=float("nan"), am_hz=float("nan"), fm_cent=float("nan"), fm_hz=float("nan"))
        note.append(info)
    return dict(path=path, sr=sr, clip=clip, pavimento=pav, note=note)


def per_nota(res):
    d = {}
    for n in res["note"]:
        d.setdefault(n["nota"], []).append(n)
    out = {}
    for k, v in d.items():
        out[k] = dict(
            nota=k, n=len(v),
            f0=np.mean([a["f0"] for a in v]), cent=np.mean([a["cent"] for a in v]),
            rms=np.mean([a["rms"] for a in v]),
            arm=[np.nanmean([a["arm"][i] for a in v]) for i in range(5)],
            centroide=np.mean([a["centroide"] for a in v]),
            am_db=np.nanmean([a["am_db"] for a in v]), am_hz=np.nanmean([a["am_hz"] for a in v]),
            fm_cent=np.nanmean([a["fm_cent"] for a in v]), fm_hz=np.nanmean([a["fm_hz"] for a in v]),
        )
    return out


# --------------------------------------------------------------------- stampa
def ordina(note_dict):
    def chiave(k):
        n = note_dict[k]
        return n["f0"]
    return sorted(note_dict, key=chiave)


def stampa_assoluto(res, floor_db, righe):
    righe.append(f"\n### {res['path']}  (fs={res['sr']} Hz, note trovate: {len(res['note'])})")
    if res["clip"]:
        righe.append("ATTENZIONE: clipping rilevato nel file -> ripeti con meno guadagno")
    righe.append("| nota scritta | f0 reale (Hz) | cent | RMS (dB) | h1 | h2 | h3 | h4 | centroide (Hz) | SNR (dB) |")
    righe.append("|---|---|---|---|---|---|---|---|---|---|")
    nd = per_nota(res)
    for k in ordina(nd):
        n = nd[k]
        snr = n["rms"] - floor_db
        flag = " !" if snr < 10 else ""
        righe.append(f"| {k} | {n['f0']:.1f} | {n['cent']:+.0f} | {n['rms']:.1f} | "
                     + " | ".join(f"{a:.1f}" for a in n["arm"][:4])
                     + f" | {n['centroide']:.0f} | {snr:.0f}{flag} |")


def stampa_stabilita(res, righe):
    righe.append(f"\n#### Stabilita' delle note: {res['path']}  (effetto wah = modulazione 1-8 Hz)")
    righe.append("| nota scritta | modul. ampiezza (dB rms) | freq. (Hz) | wobble intonazione (cent rms) | freq. (Hz) |")
    righe.append("|---|---|---|---|---|")
    nd = per_nota(res)
    for k in ordina(nd):
        n = nd[k]
        righe.append(f"| {k} | {n['am_db']:.2f} | {n['am_hz']:.1f} | {n['fm_cent']:.1f} | {n['fm_hz']:.1f} |")


def stampa_confronto(ref, res, floor_ref, floor_db, righe):
    nr, nf = per_nota(ref), per_nota(res)
    righe.append(f"\n### ATTENUAZIONE: {ref['path']}  ->  {res['path']}")
    righe.append("| nota scritta | att. RMS (dB) | att. h1 | att. h2 | att. h3 | att. h4 | delta cent | delta centroide (Hz) | SNR (dB) |")
    righe.append("|---|---|---|---|---|---|---|---|---|")
    for k in ordina(nr):
        if k not in nf:
            righe.append(f"| {k} | (nota non trovata nel file) | | | | | | | |")
            continue
        a, b = nr[k], nf[k]
        snr = b["rms"] - floor_db
        flag = " ! (vicino al rumore: attenuazione sottostimata)" if snr < 10 else ""
        righe.append(f"| {k} | {a['rms'] - b['rms']:.1f} | "
                     + " | ".join(f"{a['arm'][i] - b['arm'][i]:.1f}" for i in range(4))
                     + f" | {b['cent'] - a['cent']:+.0f} | {b['centroide'] - a['centroide']:+.0f} | {snr:.0f}{flag} |")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", help="registrazioni WAV (con sordina, e il riferimento)")
    ap.add_argument("--ref", required=True, help="registrazione senza sordina (riferimento)")
    ap.add_argument("--rumore", help="registrazione del solo rumore di fondo (opzionale)")
    ap.add_argument("--out", default="risultati.txt", help="file di testo con la tabella")
    args = ap.parse_args()

    righe = []
    rif = analizza_file(args.ref)
    floor_global = None
    if args.rumore:
        x, sr, _ = carica(args.rumore)
        floor_global = 20 * math.log10(math.sqrt(float(np.mean(x ** 2))) + 1e-12)
        righe.append(f"Rumore di fondo ({args.rumore}): {floor_global:.1f} dB RMS")

    def floor_di(res):
        return floor_global if floor_global is not None else res["pavimento"]

    stampa_assoluto(rif, floor_di(rif), righe)
    stampa_stabilita(rif, righe)
    for f in args.files:
        if f == args.ref:
            continue
        r = analizza_file(f)
        stampa_assoluto(r, floor_di(r), righe)
        stampa_confronto(rif, r, floor_di(rif), floor_di(r), righe)
        stampa_stabilita(r, righe)

    testo = "\n".join(righe)
    print(testo)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(testo + "\n")
    print(f"\n[salvato in {args.out}: incolla questo testo nella chat]")


if __name__ == "__main__":
    sys.exit(main())
