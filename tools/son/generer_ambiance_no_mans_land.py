# Étape 2, le No Man's Land — ambiances procédurales, boucles sans couture (tout est circulaire).
# Usage : python3 generer_ambiance_no_mans_land.py <sortie> [chemin de mus_tranchee-mere_theme.wav ou .ogg]
import numpy as np, scipy.signal as ss, scipy.io.wavfile as wf, sys, os, subprocess, tempfile
SR=44100; BPM=48; BEAT=60/BPM; D4=293.66
rng=np.random.default_rng(1917); OUT=sys.argv[1]
def mk(sec): return int(sec*SR)
def fftfilt(x,lo=None,hi=None,order=2):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); g=np.ones_like(f)
    if hi: g/=np.sqrt(1+(f/hi)**(2*order))
    if lo: g/=np.sqrt(1+(lo/np.maximum(f,1e-3))**(2*order))
    return np.fft.irfft(X*g,len(x))
def colored(L,alpha):
    X=np.fft.rfft(rng.standard_normal(L)); f=np.fft.rfftfreq(L,1/SR); f[0]=1
    y=np.fft.irfft(X/f**(alpha/2),L); return y/np.abs(y).max()
def lfo(L,period,phase=0):
    dur=L/SR; n=max(1,round(dur/period)); t=np.arange(L)/SR; return 0.5+0.5*np.sin(2*np.pi*n*t/dur+phase)
def gusts(L,seed_period=7.0):  # rafales irrégulières mais périodiques sur la boucle
    g=np.zeros(L)
    for p,a in ((seed_period,1),(seed_period*2.7,0.6),(seed_period*0.43,0.3)): g+=a*lfo(L,p,rng.uniform(0,6))
    return (g/g.max())**1.6
def place(buf,ev,pos): np.add.at(buf,(np.arange(len(ev))+pos)%len(buf),ev)
def reverb(x,sec,wet,seed=0,hi=4000):
    L=len(x); r=np.random.default_rng(seed); n=mk(sec); ir=r.standard_normal(n)*np.exp(-6.9*np.arange(n)/n)
    ir=fftfilt(np.pad(ir,(0,L-n)),hi=hi); y=np.fft.irfft(np.fft.rfft(x)*np.fft.rfft(ir),L); y*=np.std(x)/(np.std(y)+1e-9)
    return (1-wet)*x+wet*y
def nrm(x,p=1.0): return x/(np.abs(x).max()+1e-9)*p
def stereo(m,delay=0.017): return np.stack([m,np.roll(m,mk(delay))],1)
def save(name,x,peak=0.85): x=nrm(x,peak); wf.write(os.path.join(OUT,name+".wav"),SR,(x*32767).astype(np.int16)); print(name)
def thump(L):
    n=mk(4); tt=np.arange(n)/SR
    body=np.sin(2*np.pi*np.cumsum(28+40*np.exp(-tt*4))/SR)*np.exp(-tt*1.6)
    nz=fftfilt(np.pad(rng.standard_normal(n),(0,L-n)),hi=150)[:n]*np.exp(-tt*1.1)
    return body*0.8+nz*1.5
def drip():
    n=mk(0.12); tt=np.arange(n)/SR; f=rng.uniform(600,1500)
    return np.sin(2*np.pi*f*(1+2*np.exp(-tt*60))*tt)*np.exp(-tt*45)
MEL=[0,3,5,7, 7,5,3,2, 0,2,3,5, 7,None,None,None, 10,9,7,5, 3,5,7,3, 2,0,2,-2, 0,None,None,None]
# une fausse note par phrase (4 phrases de 8 temps) : indices et décalage en demi-tons
FAUSSES={2:0.45, 13:-0.4, 18:0.5, 27:-0.45}

L80=mk(64*BEAT)  # 80 s, même grille que l'étape 1

# --- Surface : le vent seul, ouvert, sec ; l'artillerie n'est plus qu'un souvenir ---
def surface():
    out=[]
    for s in (0,1):
        w=fftfilt(colored(L80,1.4),lo=50,hi=1100)*(0.25+0.75*gusts(L80,9+s))
        hiss=fftfilt(colored(L80,0.5),lo=2000,hi=7000)*0.12*gusts(L80,5+s)   # le vent dans les herbes mortes
        out.append(w+hiss)
    m=np.stack(out,1)
    art=np.zeros(L80)
    for tm in (12.0,51.0): place(art,thump(L80)*0.5,mk(tm))
    art=reverb(fftfilt(art,hi=160),6,0.7,seed=3)
    flap=np.zeros(L80)  # un lambeau de toile accroché quelque part
    for _ in range(9):
        n=mk(rng.uniform(0.4,1.0)); tt=np.arange(n)/SR
        y=fftfilt(np.pad(rng.standard_normal(n),(0,L80-n)),lo=300,hi=2500)[:n]*(np.sin(2*np.pi*rng.uniform(6,11)*tt)>0.3)*np.hanning(n)
        place(flap,y*rng.uniform(0.3,0.8),rng.integers(0,L80))
    return nrm(m)*0.8+stereo(nrm(art))*0.35+stereo(nrm(flap),0.004)*0.12
# --- Les fils qui fredonnent l'air de Jacquot (positionnel, mono) ---
def fil_note(f,dur):
    n=mk(dur); tt=np.arange(n)/SR; y=np.zeros(n)
    for r,a in ((1,1),(2.013,0.45),(3.04,0.25),(4.11,0.12),(5.3,0.06)):   # partiels légèrement inharmoniques : du métal, pas une voix
        y+=a*np.sin(2*np.pi*f*r*tt*(1+0.002*np.sin(2*np.pi*0.7*tt))+rng.uniform(0,6))
    beat=0.6+0.4*np.sin(2*np.pi*rng.uniform(1.5,3.5)*tt)                     # battement des fils voisins
    a=mk(0.35); env=np.ones(n); env[:a]=np.linspace(0,1,a); env[-mk(0.4):]*=np.linspace(1,0,mk(0.4))
    return y*beat*env
def fils():
    m=np.zeros(L80)
    for rep in range(2):
        for i,st in enumerate(MEL):
            if st is None: continue
            d=1
            while i+d<len(MEL) and MEL[i+d] is None: d+=1
            f=D4*2*2**((st+FAUSSES.get(i,0))/12)   # une octave au-dessus : comme sifflé
            place(m,fil_note(f,d*BEAT*1.1),mk((rep*32+i)*BEAT))
    m*= 0.35+0.65*gusts(L80,6)                  # le vent joue les fils : sans vent, ils se taisent presque
    twang=np.zeros(L80)
    for _ in range(14):
        n=mk(0.5); tt=np.arange(n)/SR; f=rng.uniform(900,1600)
        place(twang,np.sin(2*np.pi*f*tt)*np.exp(-tt*9)*(1+np.sin(2*np.pi*f*1.5*tt))*0.5,rng.integers(0,L80))
    return reverb(nrm(m)+0.15*nrm(twang),1.5,0.25,seed=5)
# --- Le brouillard : tout se rapproche et s'étouffe ---
def brouillard():
    w=fftfilt(colored(L80,2.0),lo=40,hi=350)*(0.5+0.5*gusts(L80,13))
    dr=np.zeros(L80)
    for _ in range(40): place(dr,drip()*rng.uniform(0.2,0.8),rng.integers(0,L80))   # gouttes sur les fils
    breath=np.zeros(L80)
    for i in range(int(80/4.2)):                                                    # sa propre respiration, proche
        n=mk(1.6); tt=np.arange(n)/SR
        y=fftfilt(np.pad(rng.standard_normal(n),(0,L80-n)),lo=200,hi=1200)[:n]*np.sin(np.pi*tt/tt[-1])**2
        place(breath,y,mk(i*4.2))
    m=nrm(w)*0.7+nrm(fftfilt(dr,hi=3000))*0.25+nrm(breath)*0.12
    return stereo(reverb(m,0.8,0.3,seed=8))
# --- Couche « autre » de l'étape 2 ---
def autre():
    L=L80; n=colored(L,1.0); y=np.zeros(L)
    for f in (D4*0.75,D4*1.125):                                    # le vent accordé sur la et mi (on s'éloigne du ré)
        b,a=ss.iirpeak(f,70,fs=SR); y+=ss.lfilter(b,a,n)
    y*=0.3+0.7*lfo(L,16)
    rev=fils()[::-1]*0.5                                           # le cantique des fils, à l'envers
    hb=np.zeros(L)
    for i in range(int(80/(60/58))):
        for off,amp in ((0,1),(0.27,0.6)):
            k=mk(0.25); tt=np.arange(k)/SR; place(hb,np.sin(2*np.pi*42*tt)*np.exp(-tt*22)*amp,mk(i*60/58+off))
    wh=np.zeros(L)
    for _ in range(20):
        k=mk(rng.uniform(0.4,1.2)); tt=np.arange(k)/SR
        v=np.zeros(L); v[:k]=rng.standard_normal(k)*(0.5+0.5*np.sin(2*np.pi*rng.uniform(4,7)*tt))**2*np.hanning(k)
        wh+=np.roll(fftfilt(v,lo=1200,hi=5000),rng.integers(0,L))
    # la cloche muette du village qu'on approche : résonance inversée, battant dans le vide
    k=mk(4); tt=np.arange(k)/SR; f=D4/2
    ring=sum(a*np.sin(2*np.pi*f*r*tt)*np.exp(-tt*(0.6+r*0.4)) for r,a in ((0.5,1),(1,0.8),(1.183,0.5),(1.506,0.4),(2,0.35)))
    kk=mk(0.18); tk=np.arange(kk)/SR
    thud=fftfilt(np.pad(rng.standard_normal(kk),(0,L-kk)),hi=220)[:kk]*np.exp(-tk*30)*3+np.sin(2*np.pi*48*tk)*np.exp(-tk*25)*2
    bell=np.zeros(L); place(bell,np.concatenate([ring[::-1]*np.linspace(0,1,k)**2*0.6,thud]),mk(61))
    m=nrm(y)*0.45+nrm(rev)*0.35+nrm(hb)*0.3+nrm(wh)*0.15+nrm(reverb(bell,1.5,0.3,seed=4))*0.35
    return stereo(m,0.013)
# --- Lieux (boucles mono de 20 s) ---
L20=mk(20)
def trou_obus():   # au fond du trou : le vent passe au-dessus, la boue suinte
    w=fftfilt(colored(L20,1.6),lo=60,hi=300)*(0.4+0.6*gusts(L20,5))
    ooze=np.zeros(L20)
    for _ in range(25):
        k=mk(0.08); tt=np.arange(k)/SR; f=rng.uniform(150,400)
        place(ooze,np.sin(2*np.pi*f*(1+tt*6)*tt)*np.exp(-tt*40),rng.integers(0,L20))
    dr=np.zeros(L20)
    for _ in range(8): place(dr,drip()*rng.uniform(0.3,0.8),rng.integers(0,L20))
    return reverb(nrm(w)*0.6+nrm(ooze)*0.35+nrm(dr)*0.3,0.5,0.25,seed=11)
def boyau_detour():  # boyau effondré, sombre : la terre travaille au-dessus du poste
    room=fftfilt(colored(L20,2.0),lo=30,hi=220)
    groan=np.zeros(L20)
    for _ in range(3):
        k=mk(rng.uniform(1.5,3)); tt=np.arange(k)/SR
        place(groan,fftfilt(np.pad(rng.standard_normal(k),(0,L20-k)),hi=110)[:k]*np.sin(np.pi*tt/tt[-1])**2*6,rng.integers(0,L20))
    trickle=np.zeros(L20)
    for _ in range(12):
        k=mk(rng.uniform(0.3,0.9)); tt=np.arange(k)/SR
        place(trickle,fftfilt(np.pad(rng.standard_normal(k),(0,L20-k)),lo=1500,hi=6000)[:k]*(rng.random(k)>0.7)*np.hanning(k),rng.integers(0,L20))
    steps=np.zeros(L20)  # des pas au-dessus : la sentinelle, ou quelqu'un d'autre
    for i in range(6):
        k=mk(0.07); place(steps,fftfilt(np.pad(rng.standard_normal(k),(0,L20-k)),hi=300)[:k]*np.exp(-np.arange(k)/SR*50),mk(4+i*0.75))
    return reverb(nrm(room)*0.35+nrm(groan)*0.6+nrm(trickle)*0.2+nrm(steps)*0.25,1.8,0.45,seed=12)
def poste():   # la bougie dans sa boîte de conserve, les sacs, une sentinelle qui respire et tousse
    flame=fftfilt(colored(L20,1),lo=80,hi=600)*(0.6+0.4*np.abs(fftfilt(rng.standard_normal(L20),hi=4)*30).clip(0,1))
    tin=np.zeros(L20)
    for _ in range(3):
        k=mk(0.5); tt=np.arange(k)/SR; f=rng.uniform(2200,3200)
        place(tin,sum(a*np.sin(2*np.pi*f*r*tt)*np.exp(-tt*(10+r*6)) for r,a in ((1,1),(2.7,0.4))),rng.integers(0,L20))
    cough=np.zeros(L20)
    for tm in (7.5,7.9,15.2):
        k=mk(0.22); tt=np.arange(k)/SR
        place(cough,fftfilt(np.pad(rng.standard_normal(k),(0,L20-k)),lo=150,hi=1500)[:k]*np.exp(-tt*14),mk(tm))
    wind=fftfilt(colored(L20,1.5),lo=60,hi=900)*(0.3+0.7*gusts(L20,6))
    return nrm(flame)*0.35+nrm(tin)*0.15+nrm(cough)*0.3+nrm(wind)*0.4
# --- Le cantique très lointain à la souche : les soldats de la Tranchée-Mère, portés par le vent ---
def cantique_lointain(src):
    if src.endswith(".ogg"):
        tmp=tempfile.mktemp(suffix=".wav"); subprocess.run(["ffmpeg","-loglevel","error","-y","-i",src,tmp],check=True); src=tmp
    sr,x=wf.read(src); x=x.astype(float).mean(1) if x.ndim>1 else x.astype(float)
    assert sr==SR and len(x)>=L80-SR
    x=np.resize(x,L80)
    x=fftfilt(x,lo=180,hi=900,order=3)                       # la distance mange les graves et les aigus
    x=x*(0.15+0.85*gusts(L80,8))                             # le vent l'apporte et le reprend
    x=reverb(x,5,0.75,seed=21,hi=1500)
    w=fftfilt(colored(L80,1.4),lo=50,hi=800)*(0.3+0.7*gusts(L80,8))*0.6   # le vent devant
    return stereo(nrm(x)*0.55+nrm(w)*0.45,0.021)
save("amb_no-mans-land_surface",surface())
save("amb_no-mans-land_autre",autre())
save("amb_no-mans-land_fils",fils(),0.8)
save("amb_no-mans-land_brouillard",brouillard())
save("amb_no-mans-land_trou-obus",trou_obus(),0.8)
save("amb_no-mans-land_boyau-detour",boyau_detour(),0.8)
save("amb_no-mans-land_poste",poste(),0.8)
if len(sys.argv)>2: save("mus_no-mans-land_cantique-lointain",cantique_lointain(sys.argv[2]),0.75)
