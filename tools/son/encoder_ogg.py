# Encodage OGG Vorbis des boucles (budget du build web : 60 Mo, demande du Lead Prog du 15/11).
#   amb_* : quality 2 (~80-96 kbit/s), en mono quand la stéréo n'est qu'une copie retardée
#           (corrélation décalée > 0,95, cas de stereo() dans les générateurs) ou déjà mono ;
#   mus_* : quality 3 (~112 kbit/s), stéréo gardée.
# Les sfx_ et vox_ restent en WAV. Usage : python3 encoder_ogg.py <dossier des .wav> <repo>/assets/audio
import sys, os, glob, subprocess, numpy as np, scipy.io.wavfile as wf
QUALITE = {"amb": 2, "mus": 3}
SEUIL_FAUSSE_STEREO = 0.95

def fausse_stereo(x):
    a, b = x[:, 0].astype(float), x[:, 1].astype(float)
    cc = np.fft.irfft(np.fft.rfft(a) * np.conj(np.fft.rfft(b)), len(a))
    return cc.max() / np.sqrt((a**2).sum() * (b**2).sum() + 1e-9) > SEUIL_FAUSSE_STEREO

def encoder(wav, sortie):
    nom = os.path.basename(wav)[:-4]; famille = nom.split("_")[0]
    if famille not in QUALITE:
        return
    _, x = wf.read(wav)
    mono = x.ndim == 1 or (famille == "amb" and fausse_stereo(x))
    cmd = ["ffmpeg", "-loglevel", "error", "-y", "-i", wav, "-c:a", "libvorbis", "-q:a", str(QUALITE[famille])]
    if mono:
        cmd += ["-ac", "1"]
    subprocess.run(cmd + [os.path.join(sortie, nom + ".ogg")], check=True)
    print(f"{nom} : q{QUALITE[famille]} {'mono' if mono else 'stéréo'}")

if __name__ == "__main__":
    for w in sorted(glob.glob(os.path.join(sys.argv[1], "*.wav"))):
        encoder(w, sys.argv[2])
