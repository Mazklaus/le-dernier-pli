# Étapes 5 (la Forêt de Croix) et 6 (la Cathédrale enterrée) : ambiances procédurales, boucles sans couture.
# Étape 5 : une boucle. Un même oiseau et un même craquement marquent le retour devant la croix
#           (sfx_boucle_raccord, joué par le Passage « Continuer »), pour qu'on comprenne qu'on est
#           revenu sans croire à un bug.
# Étape 6 : un noir très long dans la nef, puis les voix chaudes de la tablée, écho inversé de la noce.
# Usage : python3 generer_ambiance_foret_cathedrale.py <sortie> <repo>/assets/audio [mus_village-cloches-muettes_noce.ogg]
import numpy as np, scipy.signal as ss, scipy.io.wavfile as wf, sys, os, subprocess, tempfile
SR=44100; BPM=48; BEAT=60/BPM; D4=293.66; D3=D4/2; D2=D3/2
rng=np.random.default_rng(1923); OUT=sys.argv[1]; OUT_SFX=sys.argv[2] if len(sys.argv)>2 else OUT
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
def gusts(L,p=7.0):
    g=np.zeros(L)
    for q,a in ((p,1),(p*2.7,0.6),(p*0.43,0.3)): g+=a*lfo(L,q,rng.uniform(0,6))
    return (g/g.max())**1.6
def place(buf,ev,pos): np.add.at(buf,(np.arange(len(ev))+pos)%len(buf),ev)
def burst(n,lo=None,hi=None):  # bruit court filtré
    return fftfilt(rng.standard_normal(n+mk(0.05)),lo=lo,hi=hi)[:n]
def reverb(x,sec,wet,seed=0,hi=4000):
    L=len(x); r=np.random.default_rng(seed); n=mk(sec); ir=r.standard_normal(n)*np.exp(-6.9*np.arange(n)/n)
    ir=fftfilt(np.pad(ir,(0,L-n)),hi=hi); y=np.fft.irfft(np.fft.rfft(x)*np.fft.rfft(ir),L); y*=np.std(x)/(np.std(y)+1e-9)
    return (1-wet)*x+wet*y
def q(f,L): return round(f*L/SR)*SR/L          # fréquence arrondie à un nombre entier de cycles : la boucle ne claque pas
def lfilter_circ(b,a,x): return ss.lfilter(b,a,np.concatenate([x,x]))[len(x):]   # filtre en régime établi, bouclable
def nrm(x,p=1.0): return x/(np.abs(x).max()+1e-9)*p
def stereo(m,delay=0.017): return np.stack([m,np.roll(m,mk(delay))],1)
def save(name,x,peak=0.85): x=nrm(x,peak); wf.write(os.path.join(OUT,name+".wav"),SR,(x*32767).astype(np.int16)); print(name)
def env_ar(n,a,r):
    e=np.ones(n); a=max(1,mk(a)); r=max(1,mk(r)); e[:a]=np.linspace(0,1,a); e[-r:]*=np.linspace(1,0,r); return e
def gazouillis():
    n=mk(rng.uniform(0.05,0.14)); tt=np.arange(n)/SR; f0=rng.uniform(2800,5200)
    f=f0*(1+rng.uniform(-0.3,0.3)*tt/tt[-1]+0.08*np.sin(2*np.pi*rng.uniform(30,70)*tt))
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.hanning(n)
def merle(fausse=0.0):  # ré-fa-sol, sifflé deux octaves au-dessus ; la troisième note presque juste
    out=[]
    for st,d in ((0,0.22),(3,0.22),(5+fausse,0.45)):
        n=mk(d); tt=np.arange(n)/SR; f=D4*4*2**(st/12)*(1+0.012*np.sin(2*np.pi*7*tt))
        out.append(np.sin(2*np.pi*np.cumsum(f)/SR)*env_ar(n,0.02,0.08)*(1+0.3*np.sin(4*np.pi*np.cumsum(f)/SR)))
    return np.concatenate(out)
def oiseaux(L,densite,merles):
    b=np.zeros(L)
    for _ in range(int(densite*L/SR)):
        pos=rng.integers(0,L)
        for k in range(rng.integers(1,5)): place(b,gazouillis()*rng.uniform(0.2,0.7),pos+mk(k*rng.uniform(0.08,0.16)))
    for tm,fa in merles: place(b,merle(fa)*0.8,mk(tm))
    return b
def syllabe(f0,dur,F):
    n=mk(dur); tt=np.arange(n)/SR; f=f0*(1+rng.uniform(-0.15,0.15)*tt/dur); ph=np.cumsum(f)/SR; y=np.zeros(n)
    for k in range(1,30):
        fk=f0*k
        if fk>6000: break
        w=sum(a*np.exp(-((fk-Fi)/bw)**2) for Fi,a,bw in zip(F,(1,0.6,0.15),(150,220,350)))+0.01/k
        y+=w*np.sin(2*np.pi*k*ph)
    return y*np.hanning(n)
VOY=[(700,1200,2600),(400,2000,2700),(450,800,2500),(300,2300,3000),(550,1700,2500)]
def babil(L,n,f0lo,f0hi,dlo=0.08,dhi=0.22):
    b=np.zeros(L)
    for _ in range(n):
        pos=rng.integers(0,L); f0=rng.uniform(f0lo,f0hi); t=0
        for _ in range(rng.integers(2,8)):
            d=rng.uniform(dlo,dhi); place(b,syllabe(f0*rng.uniform(0.9,1.15),d,VOY[rng.integers(0,5)])*rng.uniform(0.4,1),pos+mk(t)); t+=d+rng.uniform(0.0,0.08)
    return b
MEL=[0,3,5,7, 7,5,3,2, 0,2,3,5, 7,None,None,None, 10,9,7,5, 3,5,7,3, 2,0,2,-2, 0,None,None,None]
L80=mk(64*BEAT); L20=mk(20)
def goutte():
    n=mk(0.12); tt=np.arange(n)/SR; f=rng.uniform(700,1600)
    return np.sin(2*np.pi*f*(1+2*np.exp(-tt*60))*tt)*np.exp(-tt*45)
def craquement(d=0.5,f0=140):   # du bois qui travaille
    n=mk(d); tt=np.arange(n)/SR; f=f0*(1+0.3*tt/d)
    y=np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*(np.sin(2*np.pi*30*tt)>0.2)
    return fftfilt(np.pad(y,(0,mk(0.05))),lo=150,hi=2000)[:n]*np.hanning(n)
# Le raccord de la boucle : toujours le même oiseau (trois notes, la dernière trop basse) et le même
# craquement de croix, à l'identique, pour que l'oreille reconnaisse l'endroit.
R=np.random.default_rng(55)
def raccord():
    n=mk(2.4); y=np.zeros(n)
    for k,(st,d) in enumerate(((7,0.18),(5,0.18),(-0.6,0.42))):
        m=mk(d); tt=np.arange(m)/SR; f=D4*4*2**(st/12)*(1+0.01*np.sin(2*np.pi*8*tt))
        e=np.sin(2*np.pi*np.cumsum(f)/SR)*np.hanning(m); p=mk(0.1+k*0.24); y[p:p+m]+=e*0.6
    c=craquement(0.7,120); p=mk(1.3); y[p:p+len(c)]+=c*0.5
    return y

# ===== Étape 5 : la Forêt de Croix =====
def foret():   # le vent dans les branches nues, les croix de bois qui grincent et se cognent, un corbeau loin
    m=np.stack([fftfilt(colored(L80,1.3),lo=80,hi=1500)*(0.3+0.7*gusts(L80,9+s))+fftfilt(colored(L80,0.5),lo=2000,hi=6000)*0.06*gusts(L80,4+s) for s in (0,1)],1)
    cr=np.zeros(L80)
    for _ in range(12): place(cr,craquement(rng.uniform(0.3,0.8),rng.uniform(100,200))*rng.uniform(0.3,1),rng.integers(0,L80))
    toc=np.zeros(L80)
    for _ in range(9):
        k=mk(0.08); place(toc,burst(k,lo=200,hi=1500)*np.exp(-np.arange(k)/SR*40),rng.integers(0,L80))
    corb=np.zeros(L80)
    for tm in (21.0,63.0):
        for j in range(2): place(corb,syllabe(330,0.25,(900,1400,2600))*0.8,mk(tm+j*0.4))
    corb=reverb(fftfilt(corb,lo=300,hi=3000),2.5,0.6,seed=81)
    return nrm(m)*0.6+stereo(nrm(reverb(cr,1.5,0.4,seed=82)))*0.15+stereo(nrm(toc),0.007)*0.1+stereo(nrm(corb),0.02)*0.12
def autre5():  # des noms soufflés (on peut les lire, on ne les compte pas), le Cantique sifflé par quelqu'un qui vous suit
    noms=np.zeros(L80)
    for i in range(int(80/4.3)):
        n=mk(rng.uniform(0.5,1.0)); tt=np.arange(n)/SR
        place(noms,burst(n,lo=1500,hi=6000)*(0.5+0.5*np.sin(2*np.pi*rng.uniform(4,7)*tt))**2*np.hanning(n),mk(i*4.3+rng.uniform(0,1.5)))
    sif=np.zeros(L80)
    for rep in range(2):
        for i,st in enumerate(MEL[:16] if rep==0 else MEL[16:]):
            if st is None: continue
            n=mk(BEAT*0.9); tt=np.arange(n)/SR; f=D4*4*2**((st+(0.45 if i==6 else 0))/12)*(1+0.006*np.sin(2*np.pi*5*tt))
            place(sif,np.sin(2*np.pi*np.cumsum(f)/SR)*env_ar(n,0.05,0.15),mk((20+rep*36+i)*BEAT/1.0)%L80)
    sif=reverb(sif,3.0,0.7,seed=83)
    t=np.arange(L80)/SR; y=lfilter_circ(*ss.iirpeak(D4,80,fs=SR),colored(L80,1.0))*(0.3+0.7*lfo(L80,20))
    return stereo(nrm(noms)*0.25+nrm(sif)*0.3+nrm(y)*0.3,0.015)
def oree():      # l'orée : encore un peu de champ, des oiseaux, le vent qui entre sous les arbres
    return nrm(fftfilt(colored(L20,1.3),lo=80,hi=1500)*(0.3+0.7*gusts(L20,6)))*0.5+nrm(oiseaux(L20,1.2,[]))*0.2
def boucle():    # le sentier : les croix tout près, serrées ; le vent ne passe plus ; rien d'autre
    cr=np.zeros(L20)
    for _ in range(6): place(cr,craquement(rng.uniform(0.3,0.7),rng.uniform(90,150)),rng.integers(0,L20))
    return reverb(nrm(fftfilt(colored(L20,1.8),lo=50,hi=500))*0.4+nrm(cr)*0.3,1.2,0.35,seed=84)
def campement(): # un feu de camp abandonné qui fume encore, une toile qui bat
    feu=fftfilt(colored(L20,1.2),lo=80,hi=700)*(0.5+0.5*lfo(L20,3))
    crep=np.zeros(L20)
    for _ in range(40): k=mk(rng.uniform(0.003,0.01)); place(crep,burst(k,lo=1500,hi=7000)*rng.uniform(0.1,1),rng.integers(0,L20))
    toile=np.zeros(L20)
    for _ in range(6):
        n=mk(rng.uniform(0.4,0.9)); tt=np.arange(n)/SR
        place(toile,burst(n,lo=300,hi=2500)*(np.sin(2*np.pi*rng.uniform(6,10)*tt)>0.3)*np.hanning(n),rng.integers(0,L20))
    return nrm(feu)*0.3+nrm(crep)*0.2+nrm(toile)*0.2+nrm(fftfilt(colored(L20,1.4),lo=60,hi=900)*gusts(L20,5))*0.3
def cimetiere(): # le cimetière des coureurs : silence, une plaque de métal qui tinte au vent, la terre fraîche
    t=np.arange(L20)/SR
    plaque=np.zeros(L20)
    for tm in (3.0,11.5,17.0):
        k=mk(1.5); tk=np.arange(k)/SR; f=rng.uniform(1100,1300)
        place(plaque,(np.sin(2*np.pi*f*tk)+0.4*np.sin(2*np.pi*f*2.6*tk))*np.exp(-tk*3),mk(tm))
    return nrm(fftfilt(colored(L20,1.6),lo=50,hi=600)*(0.3+0.7*gusts(L20,7)))*0.4+nrm(plaque)*0.12
def clairiere(): # la clairière : le ciel rouvert, le vent large ; au fond, la fissure qui souffle (l'étape 6)
    vent=fftfilt(colored(L20,1.3),lo=60,hi=1800)*(0.3+0.7*gusts(L20,8))
    t=np.arange(L20)/SR; souffle=np.sin(2*np.pi*q(D2,L20)*t)*(0.5+0.5*lfo(L20,10))**2
    return nrm(vent)*0.5+nrm(oiseaux(L20,0.5,[]))*0.15+nrm(souffle)*0.08

# ===== Étape 6 : la Cathédrale enterrée =====
def profondeur(): # la terre au-dessus, la pierre qui garde le froid, l'eau qui suinte loin, un bourdon sans attaque
    piece=np.stack([fftfilt(colored(L80,2.0),lo=25,hi=220)*(0.7+0.3*lfo(L80,16,s)) for s in (0,1)],1)
    eau=np.zeros(L80)
    for _ in range(30): place(eau,goutte()*rng.uniform(0.2,0.7),rng.integers(0,L80))
    eau=reverb(eau,4.0,0.7,seed=91)
    t=np.arange(L80)/SR
    bourdon=sum(a*np.sin(2*np.pi*q(D2*r,L80)*t+rng.uniform(0,6)) for r,a in ((0.5,1),(1,0.6),(1.5,0.25)))*(0.5+0.5*lfo(L80,26))
    return nrm(piece)*0.45+stereo(nrm(eau))*0.12+stereo(nrm(bourdon),0.02)*0.12
def autre6():   # la langue des Enfouis : des mots de la liturgie, chantés à l'envers sous la pierre
    pri=babil(L80,22,100,150,0.25,0.5)
    pri=reverb(fftfilt(pri,lo=120,hi=1400),4.5,0.7,seed=92)[::-1]
    t=np.arange(L80)/SR; y=lfilter_circ(*ss.iirpeak(D3,60,fs=SR),colored(L80,1.0))*(0.3+0.7*lfo(L80,20))
    return stereo(nrm(pri)*0.4+nrm(y)*0.35,0.013)
def fissure():  # la fissure : l'air qui monte du dessous, chaud, et un écho trop long
    souffle=fftfilt(colored(L20,1.6),lo=40,hi=700)*(0.4+0.6*lfo(L20,5))
    cail=np.zeros(L20)
    for tm in (4.0,12.5):
        for j in range(4): k=mk(0.05); place(cail,burst(k,lo=500,hi=4000)*np.exp(-np.arange(k)/SR*50)*(1-j*0.2),mk(tm+j*0.3+j*j*0.05))
    return reverb(nrm(souffle)*0.5+nrm(cail)*0.3,3.5,0.5,seed=93)
def nef():      # la nef engloutie, dans le noir : presque rien, une goutte qui met longtemps à se perdre
    gout=np.zeros(L20)
    for tm in (2.0,13.0): place(gout,goutte()*0.8,mk(tm))
    return reverb(nrm(fftfilt(colored(L20,2.2),lo=20,hi=120))*0.4+nrm(gout)*0.25,6.0,0.7,seed=94)
def village():  # le village enfoui : une place chaude, des lampes à huile, des pas, un enfant ; la tablée chante à part
    lampes=fftfilt(colored(L20,1.0),lo=200,hi=1200)*(0.6+0.4*lfo(L20,2))
    pas=np.zeros(L20)
    for _ in range(14): k=mk(0.08); place(pas,burst(k,lo=150,hi=1000)*np.exp(-np.arange(k)/SR*35)*rng.uniform(0.3,0.8),rng.integers(0,L20))
    enf=babil(L20,3,330,450)
    return reverb(nrm(lampes)*0.25+nrm(pas)*0.25+nrm(enf)*0.15+nrm(babil(L20,25,100,240))*0.3,2.0,0.45,seed=95)
def niche():    # la niche du veilleur, à la place du clocher : une flamme, un souffle de vieil homme
    flamme=fftfilt(colored(L20,1.0),lo=80,hi=500)*(0.6+0.4*lfo(L20,1.7))
    souf=np.zeros(L20)
    for i in range(4):
        n=mk(3.5); tt=np.arange(n)/SR; place(souf,burst(n,lo=150,hi=900)*np.sin(np.pi*tt/tt[-1])**2,mk(i*5))
    return nrm(flamme)*0.3+nrm(souf)*0.25+nrm(fftfilt(colored(L20,2),lo=30,hi=200))*0.2
def seuil():    # le seuil : la plus grande des cloches tues, toute proche ; son bourdon sans attaque emplit tout
    t=np.arange(L20)/SR
    b=sum(a*np.sin(2*np.pi*q(D2*r,L20)*t+rng.uniform(0,6)) for r,a in ((0.5,1),(1,0.8),(1.2,0.35),(1.5,0.3),(2,0.2)))
    return reverb(nrm(b*(0.6+0.4*lfo(L20,10)))*0.5+nrm(fftfilt(colored(L20,2),lo=25,hi=150))*0.3,4.0,0.5,seed=96)
def tablee(src):   # la noce de l'étape 3, à l'envers, plus lente, plus chaude : le même air vu de dessous
    if src.endswith(".ogg"):
        tmp=tempfile.mktemp(suffix=".wav"); subprocess.run(["ffmpeg","-loglevel","error","-y","-i",src,tmp],check=True); src=tmp
    sr,x=wf.read(src); x=x.astype(float); x=x.mean(1) if x.ndim>1 else x
    x=x[::-1]                                                 # l'écho inversé
    x=ss.resample(x,int(len(x)*1.12))                         # plus lent, un peu plus grave (un ton à peu près)
    x=fftfilt(x,lo=80,hi=2200,order=3)                        # entendu à travers la terre, chaud
    L=len(x); voix=babil(L,int(L/SR*1.5),110,230)             # les convives
    m=reverb(nrm(x)*0.6+nrm(voix)*0.3,2.5,0.45,seed=97)
    return stereo(m,0.011)

save("amb_foret-de-croix_foret",foret())
save("amb_foret-de-croix_autre",autre5())
for nom,fn in (("oree",oree),("boucle",boucle),("campement",campement),("cimetiere",cimetiere),("clairiere",clairiere)):
    save("amb_foret-de-croix_"+nom,fn(),0.8)
save("amb_cathedrale-enterree_profondeur",profondeur())
save("amb_cathedrale-enterree_autre",autre6())
for nom,fn,crete in (("fissure",fissure,0.8),("nef",nef,0.4),("village",village,0.8),("niche-veilleur",niche,0.8),("seuil",seuil,0.8)):
    save("amb_cathedrale-enterree_"+nom,fn(),crete)   # la nef reste un noir presque vide
x=nrm(raccord(),0.75); wf.write(os.path.join(OUT_SFX,"sfx_boucle_raccord_01.wav"),SR,(x*32767).astype(np.int16)); print("sfx_boucle_raccord_01")
if len(sys.argv)>3: save("mus_cathedrale-enterree_tablee",tablee(sys.argv[3]),0.8)
