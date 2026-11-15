# Encodage OGG Vorbis des boucles (budget du build web : 60 Mo, demande du Lead Prog du 15/11).
#   amb_* : quality 2 (~80-96 kbit/s), en mono quand la stéréo n'est qu'une copie retardée
#           (corrélation décalée > 0,95, cas de stereo() dans les générateurs) ou déjà mono ;
#   mus_* : quality 3, en mono depuis le 15/11 (réserve de budget, ~3 Mo) : le mélange L+R est
#           remonté à l'énergie de la stéréo (les canaux décorrélés perdaient 3 à 4,5 dB), crête ≤ -1 dBFS.
# Les sfx_ et vox_ restent en WAV. Usage : python3 encoder_ogg.py <dossier des .wav> <repo>/assets/audio
import sys, os, glob, subprocess, tempfile, numpy as np, scipy.io.wavfile as wf
QUALITE = {"amb": 2, "mus": 3}
SEUIL_FAUSSE_STEREO = 0.95
MONO_FORCE = {"mus"}
CRETE_MAX = 10 ** (-1 / 20)

def fausse_stereo(x):
    a, b = x[:, 0].astype(float), x[:, 1].astype(float)
    cc = np.fft.irfft(np.fft.rfft(a) * np.conj(np.fft.rfft(b)), len(a))
    return cc.max() / np.sqrt((a**2).sum() * (b**2).sum() + 1e-9) > SEUIL_FAUSSE_STEREO

def mixage_mono(sr, x):
    """L+R remonté à l'énergie moyenne des deux canaux, sans dépasser CRETE_MAX ; renvoie un WAV temporaire."""
    plein = float(np.iinfo(x.dtype).max) if x.dtype.kind == "i" else 1.0
    x = x.astype(float) / plein
    m = x.mean(axis=1)
    gain = np.sqrt((x ** 2).mean() / max((m ** 2).mean(), 1e-12))
    gain = min(gain, CRETE_MAX / max(np.abs(m).max(), 1e-9))
    fd, chemin = tempfile.mkstemp(suffix=".wav"); os.close(fd)
    wf.write(chemin, sr, (m * gain * 32767).astype(np.int16))
    return chemin

def encoder(wav, sortie):
    nom = os.path.basename(wav)[:-4]; famille = nom.split("_")[0]
    if famille not in QUALITE:
        return
    sr, x = wf.read(wav)
    mono = x.ndim == 1 or famille in MONO_FORCE or (famille == "amb" and fausse_stereo(x))
    source = wav
    if mono and x.ndim == 2 and famille in MONO_FORCE:
        source = mixage_mono(sr, x)
    cmd = ["ffmpeg", "-loglevel", "error", "-y", "-i", source, "-c:a", "libvorbis", "-q:a", str(QUALITE[famille])]
    if mono:
        cmd += ["-ac", "1"]
    subprocess.run(cmd + [os.path.join(sortie, nom + ".ogg")], check=True)
    if source != wav:
        os.remove(source)
    print(f"{nom} : q{QUALITE[famille]} {'mono' if mono else 'stéréo'}")

if __name__ == "__main__":
    for w in sorted(glob.glob(os.path.join(sys.argv[1], "*.wav"))):
        encoder(w, sys.argv[2])
