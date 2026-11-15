# Ambiance procédurale de la Tranchée-Mère — boucles sans couture (tout est circulaire)
import numpy as np, scipy.signal as ss, scipy.io.wavfile as wf, sys, os
SR=44100; BPM=48; BEATS=64; L=int(SR*BEATS*60/BPM)  # 80 s
rng=np.random.default_rng(1947)
t=np.arange(L)/SR
def fftfilt(x, lo=None, hi=None, order=2):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); g=np.ones_like(f)
    if hi: g/= np.sqrt(1+(f/hi)**(2*order))
    if lo: g/= np.sqrt(1+(lo/np.maximum(f,1e-3))**(2*order))
    return np.fft.irfft(X*g,len(x))
def colored(alpha):  # 1/f^alpha noise, circular
    X=np.fft.rfft(rng.standard_normal(L)); f=np.fft.rfftfreq(L,1/SR); f[0]=1
    y=np.fft.irfft(X/f**(alpha/2),L); return y/np.abs(y).max()
def lfo(period, phase=0):  # périodique sur la boucle
    n=max(1,round(L/SR/period)); return 0.5+0.5*np.sin(2*np.pi*n*t/(L/SR)+phase)
def reverb(x, sec=3.0, wet=0.4, seed=0):
    r=np.random.default_rng(seed); n=int(sec*SR)
    ir=r.standard_normal(n)*np.exp(-6.9*np.arange(n)/n); ir=fftfilt(np.pad(ir,(0,L-n)),hi=4000)
    y=np.fft.irfft(np.fft.rfft(x)*np.fft.rfft(ir),L); y*= np.std(x)/(np.std(y)+1e-9)
    return (1-wet)*x+wet*y
def place(buf, ev, pos):  # ajout circulaire
    idx=(np.arange(len(ev))+pos)%L; np.add.at(buf, idx, ev)
def pan(m, p):  # p in [-1,1]
    a=(p+1)*np.pi/4; return np.stack([m*np.cos(a), m*np.sin(a)],1)
def norm(x, peak): return x/np.abs(x).max()*peak

# ---------- COUCHE RÉELLE ----------
def wind():
    out=[]
    for s in (0,1):
        n=colored(1.6); n=fftfilt(n,lo=60,hi=700)
        env=0.35+0.65*lfo(26, s*1.3)*(0.7+0.3*lfo(9, s))
        out.append(n*env)
    return norm(np.stack(out,1),1)
def rain():
    out=[]
    for s in (0,1):
        n=fftfilt(rng.standard_normal(L),lo=2500,hi=9000)*(0.6+0.4*lfo(40,s*2))
        out.append(n)
    return norm(np.stack(out,1),1)
def drip(f0):
    n=int(0.12*SR); tt=np.arange(n)/SR
    return np.sin(2*np.pi*(f0*(1+2*np.exp(-tt*60)))*tt)*np.exp(-tt*45)
def drips(count, quant=None, base=None):
    out=np.zeros((L,2))
    for i in range(count):
        if quant: pos=int(rng.integers(0,BEATS*2))*int(SR*30/BPM)
        else: pos=int(rng.integers(0,L))
        f=base if base else rng.uniform(500,1400)
        ev=drip(f)*rng.uniform(0.3,1); m=np.zeros(L); place(m,ev,pos)
        out+=pan(m, rng.uniform(-0.8,0.8))
    return out
def thump():
    n=int(4*SR); tt=np.arange(n)/SR
    body=np.sin(2*np.pi*np.cumsum(30+45*np.exp(-tt*4))/SR)*np.exp(-tt*1.8)
    nz=fftfilt(np.pad(rng.standard_normal(n),(0,L-n)),hi=180)[:n]*np.exp(-tt*1.2)
    return body*0.8+nz*1.5
def artillery(times):
    m=np.zeros(L)
    for k,tm in enumerate(times):
        place(m, thump()*rng.uniform(0.4,1), int(tm*SR))
    m=reverb(fftfilt(m,hi=250),sec=5,wet=0.6,seed=3)
    return np.stack([m*0.9, m*0.75],1)
def creak():
    n=int(rng.uniform(0.6,1.4)*SR); tt=np.arange(n)/SR
    f=rng.uniform(140,260)*(1+0.3*np.sin(2*np.pi*rng.uniform(0.5,1.5)*tt))
    pulses=(np.sin(2*np.pi*np.cumsum(f)/SR)>0.92).astype(float)
    y=fftfilt(np.pad(pulses,(0,L-n)),lo=300,hi=3000)[:n]
    return y*np.hanning(n)
def creaks(count):
    out=np.zeros((L,2))
    for i in range(count):
        m=np.zeros(L); place(m,creak()*rng.uniform(0.4,1),int(rng.integers(0,L)))
        out+=pan(m,rng.uniform(-0.6,0.6))
    return out
def distant_men():  # voix lointaines sans mots : murmures filtrés
    m=np.zeros(L)
    for i in range(14):
        n=int(rng.uniform(0.8,2.2)*SR); tt=np.arange(n)/SR
        f0=rng.uniform(95,140)*(1+0.08*np.sin(2*np.pi*3*tt))
        ph=np.cumsum(f0)/SR; v=sum(np.sin(2*np.pi*k*ph)/k for k in range(1,12))
        syl=0.5+0.5*np.sin(2*np.pi*rng.uniform(3,5)*tt)
        place(m, v*syl*np.hanning(n)*rng.uniform(0.3,1), int(rng.integers(0,L)))
    m=fftfilt(m,lo=200,hi=900); m=reverb(m,sec=2.5,wet=0.7,seed=5)
    return np.stack([m*0.7,m],1)

# ---------- COUCHE « AUTRE » ----------
D4=293.66
MEL=[0,3,5,7, 7,5,3,2, 0,2,3,5, 7,None,None,None, 10,9,7,5, 3,5,7,3, 2,0,2,-2, 0,None,None,None]  # demi-tons depuis ré, dorien
FAUX={6:0.42, 13:0.0, 21:-0.38, 27:0.45}  # fausses notes (demi-tons de décalage)
def choir_note(f, dur):
    n=int(dur*SR); tt=np.arange(n)/SR; out=np.zeros(n)
    for v in range(4):
        fv=f*2**(rng.uniform(-12,12)/1200)*(1+0.006*np.sin(2*np.pi*rng.uniform(4.5,5.5)*tt+v))
        ph=np.cumsum(fv)/SR
        for k in range(1,30):
            fk=f*k; w=np.exp(-((fk-450)/180)**2)+0.6*np.exp(-((fk-800)/250)**2)+0.15*np.exp(-((fk-2600)/400)**2)
            if fk<9000 and w>1e-3: out+=w*np.sin(2*np.pi*k*ph+v)
    a=int(0.25*SR); env=np.ones(n); env[:a]=np.linspace(0,1,a); env[-a:]=np.linspace(1,0,a)
    return out*env
def ghost_cantique():
    m=np.zeros(L); beat=60/BPM
    for rep in range(2):
        for i,st in enumerate(MEL):
            if st is None: continue
            d=1
            while i+d<len(MEL) and MEL[i+d] is None: d+=1
            st2=st+FAUX.get(i,0)*(1 if rep==1 else 0.5)
            f=D4/2*2**(st2/12)
            place(m, choir_note(f, d*beat*1.05), int((rep*32+i)*beat*SR))
    drone=sum(np.sin(2*np.pi*(D4/4)*k*t)*np.exp(-((D4/4*k-450)/200)**2) for k in range(1,16))
    m=m/np.abs(m).max()+0.25*drone/np.abs(drone).max()
    m=reverb(fftfilt(m,hi=2500),sec=4.5,wet=0.65,seed=9)
    d=int(0.013*SR)
    return np.stack([m, np.roll(m,d)],1)
def tuned_wind():  # le vent tient une note (filtre en peigne sur ré et la)
    n=colored(1.0); y=np.zeros(L)
    for f in (D4/2, D4*0.75, D4):
        b,a=ss.iirpeak(f,60,fs=SR); y+=ss.lfilter(b,a,n)
    y*=0.4+0.6*lfo(20)
    return norm(np.stack([y,np.roll(y,int(0.02*SR))],1),1)
def heartbeat():
    m=np.zeros(L); beat=60/54
    k=0
    for i in range(int(L/SR/beat)):
        for off,amp in ((0,1),(0.28,0.6)):
            n=int(0.25*SR); tt=np.arange(n)/SR
            ev=np.sin(2*np.pi*45*tt)*np.exp(-tt*22)*amp
            place(m,ev,int((i*beat+off)*SR))
    return np.stack([m,m],1)
def whispers():
    m=np.zeros((L,2))
    for i in range(18):
        n=int(rng.uniform(0.5,1.5)*SR); tt=np.arange(n)/SR
        nz=rng.standard_normal(n); syl=(0.5+0.5*np.sin(2*np.pi*rng.uniform(4,7)*tt))**2
        v=np.zeros(L); v[:n]=nz*syl*np.hanning(n)
        v=fftfilt(v,lo=1200,hi=5000); v=np.roll(v,int(rng.integers(0,L)))
        m+=pan(v,rng.choice([-0.95,0.95]))
    return m
def muted_bell():  # la cloche muette : une résonance inversée qui monte… et le battant frappe dans le vide
    n=int(5*SR); tt=np.arange(n)/SR; f=D4/2
    partials=[(0.5,1),(1,0.8),(1.183,0.5),(1.506,0.4),(2,0.35),(2.74,0.2)]
    ring=sum(a*np.sin(2*np.pi*f*r*tt)*np.exp(-tt*(0.6+r*0.4)) for r,a in partials)
    swell=ring[::-1]*np.linspace(0,1,n)**2      # aspiration inversée
    k=int(0.18*SR); tk=np.arange(k)/SR
    thud=fftfilt(np.pad(rng.standard_normal(k),(0,L-k)),hi=220)[:k]*np.exp(-tk*30)*3+np.sin(2*np.pi*48*tk)*np.exp(-tk*25)*2
    ev=np.concatenate([swell*0.6, thud])       # puis rien : pas de résonance
    m=np.zeros(L); place(m,ev,int(47*SR)); m=reverb(m,sec=1.2,wet=0.3,seed=11)
    return np.stack([m,m*0.8],1)

print("réel…",file=sys.stderr)
lit = 0.55*wind() + 0.12*rain() + 0.35*norm(drips(70),1) + 0.9*artillery([3.2,17.5,24.1,41.0,58.3,66.0]) + 0.25*norm(creaks(10),1)
# Issue #129 : les voix viennent des groupes de soldats dessinés par la DA près des repères
# et des abris voisins ; plus basses et étouffées (sacs, terre), elles ne flottent plus sans corps.
_dm = distant_men()
voix = 0.12*norm(np.stack([reverb(fftfilt(_dm[:,c],lo=120,hi=900,order=3),2.0,0.5,seed=129+c) for c in (0,1)],1),1)
reel = lit + voix
_k = 0.9/np.abs(reel).max(); lit_s = lit*_k; voix_s = voix*_k
reel = norm(reel,0.9)
print("autre…",file=sys.stderr)
autre = (0.45*tuned_wind() + 0.55*ghost_cantique() + 0.25*norm(drips(40,quant=True,base=D4*2),1)
         + 0.35*norm(heartbeat(),1) + 0.18*norm(whispers(),1) + 0.4*norm(muted_bell(),1))
autre = norm(autre,0.9)
out=sys.argv[1]
def save(name,x): wf.write(os.path.join(out,name+".wav"),SR,(np.clip(x,-1,1)*32767).astype(np.int16))
save("amb_tranchee-mere_reel",reel); save("amb_tranchee-mere_surface-lit",lit_s); save("amb_tranchee-mere_surface-voix",voix_s); save("amb_tranchee-mere_autre",autre)
# démo : Lucidité 100 % -> 0 % sur deux boucles, crossfade à puissance constante + passe-bas progressif
demo_r=np.concatenate([reel,reel]); demo_a=np.concatenate([autre,autre]); N=len(demo_r)
luc=np.clip(1-np.arange(N)/N*1.15,0,1); x=1-luc
gr=np.cos(x*np.pi/2); ga=np.sin(np.clip((x-0.2)/0.8,0,1)*np.pi/2)
# passe-bas sur le réel : on mélange une version filtrée
lp=np.stack([ss.sosfiltfilt(ss.butter(2,600,fs=SR,output='sos'),demo_r[:,c]) for c in (0,1)],1)
r_mix=demo_r*(1-x[:,None])+lp*x[:,None]
demo=r_mix*gr[:,None]+demo_a*ga[:,None]
f=int(3*SR); demo[-f:]*=np.linspace(1,0,f)[:,None]
save("demo_tranchee-mere_lucidite-100-a-0",norm(demo,0.9))
