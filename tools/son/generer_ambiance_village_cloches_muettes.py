# Étape 3, le Village aux cloches muettes : ambiances et musiques procédurales, boucles sans couture.
# « Accueillant et libre, puis se refermer comme un piège » : un jour chaud où tout sonne presque juste,
# une nuit trop silencieuse. Aucune cloche ne sonne (bible narrative) : seulement la cloche muette.
# Usage : python3 generer_ambiance_village_cloches_muettes.py <sortie>
import numpy as np, scipy.signal as ss, scipy.io.wavfile as wf, sys, os
SR=44100; BPM=48; BEAT=60/BPM; D4=293.66; D3=D4/2
rng=np.random.default_rng(1919); OUT=sys.argv[1]
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
MEL=[0,3,5,7, 7,5,3,2, 0,2,3,5, 7,None,None,None, 10,9,7,5, 3,5,7,3, 2,0,2,-2, 0,None,None,None]
L80=mk(64*BEAT); L20=mk(20)

# --- Oiseaux : des pépiements libres, et de temps en temps un merle qui siffle le début du Cantique ---
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
# --- Voix sans mots (enfants, convives) : syllabes formantiques, comme les timbres ---
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
# --- La cloche muette (seul son de cloche permis hors du Dernier Pli) : la résonance arrive à
#     l'envers, le battant frappe dans le vide, plus rien. ---
def cloche_muette(L,f=D3):
    k=mk(4); tt=np.arange(k)/SR
    ring=sum(a*np.sin(2*np.pi*f*r*tt)*np.exp(-tt*(0.6+r*0.4)) for r,a in ((0.5,1),(1,0.8),(1.183,0.5),(1.506,0.4),(2,0.35)))
    kk=mk(0.18); tk=np.arange(kk)/SR
    thud=burst(kk,hi=220)*np.exp(-tk*30)*3+np.sin(2*np.pi*48*tk)*np.exp(-tk*25)*2
    return np.concatenate([ring[::-1]*np.linspace(0,1,k)**2*0.6,thud])

# ===== Couches globales (80 s, stéréo) =====
def jour():   # vent tiède, oiseaux, le village qui travaille au loin
    m=np.stack([fftfilt(colored(L80,1.3),lo=60,hi=1400)*(0.3+0.7*gusts(L80,10+s))+fftfilt(colored(L80,0.4),lo=2500,hi=8000)*0.08*gusts(L80,4+s) for s in (0,1)],1)
    o=oiseaux(L80,2.2,[(9.0,0.0),(31.5,0.0),(52.0,0.35),(71.0,0.0)])   # le troisième merle chante faux
    work=np.zeros(L80)
    for i in range(int(80/2.6)):    # un marteau sur du bois, très loin, régulier comme une horloge
        if i%7==5: continue
        kk=mk(0.09); place(work,burst(kk,lo=200,hi=1800)*np.exp(-np.arange(kk)/SR*40),mk(i*2.6+0.3))
    work=reverb(fftfilt(work,hi=1500),2.5,0.6,seed=31)
    enf=reverb(fftfilt(babil(L80,10,330,480),lo=300,hi=3000),1.2,0.5,seed=32)   # des enfants, loin
    return nrm(m)*0.55+np.stack([nrm(o),np.roll(nrm(o),mk(0.009))],1)*0.3+stereo(nrm(work))*0.12+stereo(nrm(enf),0.023)*0.1
def nuit():   # aucun grillon, aucune chouette : un silence de village qui retient son souffle
    m=np.stack([fftfilt(colored(L80,1.8),lo=40,hi=500)*(0.2+0.8*gusts(L80,14+s)) for s in (0,1)],1)
    t=np.arange(L80)/SR
    drone=sum(a*np.sin(2*np.pi*q(f,L80)*t+rng.uniform(0,6)) for f,a in ((D3/2,1),(D3/2*1.5*1.003,0.4)))*(0.5+0.5*lfo(L80,20))
    creak=np.zeros(L80)
    for tm in (17.0,58.5):          # un volet qui grince d'un cran, puis se retient
        kk=mk(0.6); tk=np.arange(kk)/SR; f=320*(1+0.4*tk)
        place(creak,np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*(np.sin(2*np.pi*35*tk)>0.6)*np.hanning(kk),mk(tm))
    chien=np.zeros(L80)              # un chien aboie deux fois, la troisième s'étrangle
    for k,(dt,a) in enumerate(((0,1),(0.45,0.9),(0.95,0.5))):
        kk=mk(0.18 if k<2 else 0.07); place(chien,syllabe(520,kk/SR,(800,1300,2600))*a,mk(39+dt))
    chien=reverb(fftfilt(chien,lo=300,hi=2500),2.0,0.7,seed=33)
    return nrm(m)*0.5+stereo(nrm(drone))*0.08+stereo(nrm(fftfilt(creak,hi=2500)),0.005)*0.06+stereo(nrm(chien),0.03)*0.12
def autre():  # les cloches qu'on n'entend pas : partout, des résonances qui arrivent à l'envers
    n=colored(L80,1.0); y=np.zeros(L80)
    for f in (D4,D4*1.5):            # le vent revient sur ré et la : on se rapproche du Cantique
        b,a=ss.iirpeak(f,80,fs=SR); y+=lfilter_circ(b,a,n)
    y*=0.3+0.7*lfo(L80,20)
    cl=np.zeros(L80)
    for tm,f,a in ((6,D3,0.9),(23,D3*0.75,0.6),(38,D3,1.0),(44.5,D3*1.5,0.5),(66,D3*0.5,0.8)):
        place(cl,cloche_muette(L80,f)*a,mk(tm))
    cl=reverb(cl,3.0,0.5,seed=34)
    pri=babil(L80,14,110,170,0.2,0.45)[::-1]   # une prière murmurée, à l'envers
    pri=reverb(fftfilt(pri,lo=150,hi=1500),2.5,0.6,seed=35)
    return stereo(nrm(y)*0.35+nrm(cl)*0.5+nrm(pri)*0.2,0.013)

# ===== Lieux (20 s, mono, émetteurs positionnels) =====
def verger():   # les feuilles, et les enfants qui jouent à la guerre : bâtons qui claquent, « pan »
    leaves=fftfilt(colored(L20,0.6),lo=1500,hi=7000)*(0.2+0.8*gusts(L20,4))
    clac=np.zeros(L20)
    for _ in range(14):
        kk=mk(0.04); tk=np.arange(kk)/SR; f=rng.uniform(900,1600)
        place(clac,(np.sin(2*np.pi*f*tk)+burst(kk,lo=800,hi=5000))*np.exp(-tk*90),rng.integers(0,L20))
    pan=np.zeros(L20)
    for tm in (3.1,3.5,11.0,11.3,11.6,16.4):
        place(pan,syllabe(rng.uniform(380,470),0.16,(700,1200,2600))*0.8,mk(tm))
    cris=babil(L20,5,340,500)
    return nrm(leaves)*0.35+nrm(oiseaux(L20,1.0,[]))*0.15+nrm(clac)*0.3+nrm(pan)*0.35+nrm(cris)*0.3
def place_noce():   # la foule de la noce : rires, conversations, gobelets, bancs
    foule=babil(L20,60,100,260)
    rires=np.zeros(L20)
    for _ in range(6):
        pos=rng.integers(0,L20); f0=rng.uniform(180,320)
        for k in range(rng.integers(3,6)): place(rires,syllabe(f0*(1-0.04*k),0.09,(750,1200,2600)),pos+mk(k*0.14))
    gob=np.zeros(L20)
    for _ in range(18):
        kk=mk(0.25); tk=np.arange(kk)/SR; f=rng.uniform(1800,3200)
        place(gob,sum(a*np.sin(2*np.pi*f*r*tk)*np.exp(-tk*(18+6*r)) for r,a in ((1,1),(2.4,0.4),(3.9,0.2))),rng.integers(0,L20))
    banc=np.zeros(L20)
    for _ in range(5):
        kk=mk(0.3); place(banc,burst(kk,lo=100,hi=700)*np.hanning(kk),rng.integers(0,L20))
    return reverb(nrm(foule)*0.5+nrm(rires)*0.35+nrm(gob)*0.18+nrm(banc)*0.2,0.6,0.2,seed=41)
def maison_ilde():  # le feu, la marmite qui frémit, l'horloge qui bat un peu trop lentement
    feu=fftfilt(colored(L20,1.2),lo=80,hi=900)*(0.6+0.4*lfo(L20,2.5))
    crep=np.zeros(L20)
    for _ in range(90):
        kk=mk(rng.uniform(0.003,0.012)); place(crep,burst(kk,lo=1500,hi=8000)*rng.uniform(0.1,1),rng.integers(0,L20))
    bulles=np.zeros(L20)
    for _ in range(70):
        kk=mk(0.05); tk=np.arange(kk)/SR; f=rng.uniform(250,600)
        place(bulles,np.sin(2*np.pi*f*(1+tk*8)*tk)*np.exp(-tk*60),rng.integers(0,L20))
    hor=np.zeros(L20)
    for i in range(18):   # 18 battements en 20 s : 0,9 battement par seconde, un rien de trop lent
        kk=mk(0.03); place(hor,burst(kk,lo=2000,hi=6000)*np.exp(-np.arange(kk)/SR*150)*(1 if i%2 else 0.7),mk(i*20/18))
    return reverb(nrm(feu)*0.4+nrm(crep)*0.25+nrm(bulles)*0.15+nrm(hor)*0.2,0.5,0.25,seed=42)
def clocher():  # la charpente vide : le vent dans les abat-sons, le bois qui travaille, des pigeons
    vent=fftfilt(colored(L20,1.4),lo=100,hi=1600)*(0.2+0.8*gusts(L20,5))
    t=np.arange(L20)/SR
    sif=sum(a*np.sin(2*np.pi*q(f,L20)*t*(1+0.004*np.sin(2*np.pi*0.25*t))) for f,a in ((D4*2,1),(D4*3,0.4)))*gusts(L20,5)**2   # les abat-sons sifflent ré
    bois=np.zeros(L20)
    for _ in range(5):
        kk=mk(rng.uniform(0.4,0.9)); tk=np.arange(kk)/SR; f=rng.uniform(90,160)*(1+0.3*tk)
        place(bois,np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*np.hanning(kk)*0.5,rng.integers(0,L20))
    ailes=np.zeros(L20)
    for tm in (6.0,14.5):
        for k in range(rng.integers(6,10)):
            kk=mk(0.06); place(ailes,burst(kk,lo=400,hi=3000)*np.hanning(kk),mk(tm+k*0.09))
    cordes=np.zeros(L20)     # les bouts de corde coupés qui se cognent à la poutre
    for tm in (2.0,2.7,9.3,17.8):
        kk=mk(0.08); place(cordes,burst(kk,hi=500)*np.exp(-np.arange(kk)/SR*40),mk(tm))
    return reverb(nrm(vent)*0.4+nrm(sif)*0.05+nrm(fftfilt(bois,hi=1200))*0.2+nrm(ailes)*0.2+nrm(cordes)*0.3,2.2,0.45,seed=43)
def chambre():  # la nuit dans la chambre : le bois de la maison, le volet, le souffle de Tobie
    piece=fftfilt(colored(L20,2.0),lo=30,hi=250)
    volet=np.zeros(L20)
    for tm in (4.0,13.2):
        kk=mk(0.12); place(volet,burst(kk,lo=200,hi=1500)*np.exp(-np.arange(kk)/SR*30),mk(tm))
    souffle=np.zeros(L20)
    for i in range(5):
        kk=mk(1.8); tk=np.arange(kk)/SR; place(souffle,burst(kk,lo=200,hi=1100)*np.sin(np.pi*tk/tk[-1])**2,mk(i*4))
    return nrm(piece)*0.4+nrm(volet)*0.3+nrm(souffle)*0.15
def chemin_nuit():   # les haies, la boue, les pas d'une foule qui avance devant, les cierges
    vent=fftfilt(colored(L20,1.5),lo=60,hi=800)*(0.3+0.7*gusts(L20,6))
    pas=np.zeros(L20)
    for i in range(70):
        kk=mk(0.12); place(pas,burst(kk,lo=80,hi=900)*np.exp(-np.arange(kk)/SR*25)*rng.uniform(0.3,1),mk(i*20/70+rng.uniform(0,0.15)))
    cier=fftfilt(colored(L20,0.8),lo=300,hi=2500)*0.3*(rng.random(L20)>0.995)
    return reverb(nrm(vent)*0.45+nrm(fftfilt(pas,hi=700))*0.35+nrm(cier)*0.1,1.0,0.35,seed=44)
def chemin_aube():   # l'aube : quelques oiseaux, la rosée qui goutte, plus personne
    vent=fftfilt(colored(L20,1.4),lo=80,hi=1200)*(0.2+0.8*gusts(L20,8))
    rosee=np.zeros(L20)
    for _ in range(14):
        kk=mk(0.1); tk=np.arange(kk)/SR; f=rng.uniform(900,1800)
        place(rosee,np.sin(2*np.pi*f*(1+2*np.exp(-tk*60))*tk)*np.exp(-tk*45),rng.integers(0,L20))
    return nrm(vent)*0.4+nrm(oiseaux(L20,0.6,[(12.0,0.0)]))*0.3+nrm(rosee)*0.15

# ===== Musiques =====
# La noce : danse à trois temps (vielle à roue et violon), en ré majeur, le Cantique mis en fête.
# Diégétique (émetteur sur la place). La tierce du violon est trop haute d'un quart de ton.
def archet(f,dur,faux=0.0):
    n=mk(dur); tt=np.arange(n)/SR; fv=f*2**(faux/12)*(1+0.006*np.sin(2*np.pi*5.5*tt)*np.clip(tt/0.15,0,1))
    ph=np.cumsum(fv)/SR; y=sum(np.sin(2*np.pi*k*ph)/k*(1.3 if k in (3,4) else 1) for k in range(1,18))
    return fftfilt(np.pad(y,(0,mk(0.05))),lo=250,hi=4500)[:n]*env_ar(n,0.03,0.06)
def noce():
    tempo=90; temps=60/tempo; L=mk(48*temps)    # 16 mesures de 3/4 : 32 s
    # le Cantique en majeur et en croches : ré mi fa# la | la fa# mi ré ...
    maj={0:0,2:2,3:4,5:5,7:7,9:9,10:11,-2:-1}
    vio=np.zeros(L)
    notes=[s for s in MEL if s is not None]
    for i in range(48):
        st=maj.get(notes[i%len(notes)],0); faux=0.5 if st==4 else 0.0
        place(vio,archet(D4*2**(st/12),temps*0.95,faux),mk(i*temps))
    t=np.arange(L)/SR; ph=lambda f: 2*np.pi*q(f,L)*t
    bourdon=sum(np.sin(k*ph(D3/2))/k for k in range(1,25))+0.6*sum(np.sin(k*ph(D3/2*1.5))/k for k in range(1,25))
    bourdon=fftfilt(bourdon*(1+0.15*np.sign(np.sin(ph(tempo/60/3)))),hi=2500)   # la roue s'appuie sur le premier temps
    for mes in (11,):    # une mesure où la vielle cale, puis repart
        a,b=mk(mes*3*temps),mk((mes+1)*3*temps); bourdon[a:b]*=np.linspace(1,0.15,b-a)
    tamb=np.zeros(L)
    for i in range(48):
        kk=mk(0.15); tk=np.arange(kk)/SR
        y=np.sin(2*np.pi*90*tk)*np.exp(-tk*25)*(1 if i%3==0 else 0)+burst(kk,lo=3000,hi=9000)*np.exp(-tk*30)*0.4
        place(tamb,y*(1 if i%3==0 else 0.5),mk(i*temps))
    m=nrm(vio)*0.55+nrm(bourdon)*0.35+nrm(tamb)*0.3
    return stereo(reverb(m,1.2,0.25,seed=51),0.008)
# La procession sous la fenêtre : le Cantique fredonné tout bas par le village, hommes et femmes,
# trop lent, et une voix qui chante une note à côté à chaque phrase.
def voix(f,dur,vowel,vid):
    n=mk(dur); tt=np.arange(n)/SR
    vib=1+0.004*np.sin(2*np.pi*rng.uniform(4,5.5)*tt+vid)*np.clip(tt/0.8,0,1)
    fv=f*2**(rng.uniform(-10,10)/1200)*vib; ph=np.cumsum(fv)/SR
    F={'u':(330,750,2400),'m':(280,900,2200)}[vowel]; y=np.zeros(n)
    for k in range(1,30):
        fk=f*k
        if fk>5000: break
        w=np.exp(-((fk-F[0])/160)**2)+0.4*np.exp(-((fk-F[1])/220)**2)+0.05*np.exp(-((fk-F[2])/350)**2)+0.015/k
        y+=w*np.sin(2*np.pi*k*ph+rng.uniform(0,6.28))
    return y*env_ar(n,0.35,0.5)
def procession():
    B=BEAT*1.25; L=L80                         # plus lent que l'étape 1 : 32 temps de 2,5 s = 80 s
    m=np.zeros(L); faux={6:0.5,13:-0.45,21:0.5,27:-0.5}
    for i,st in enumerate(MEL):
        if st is None: continue
        d=1
        while i+d<len(MEL) and MEL[i+d] is None: d+=1
        for v,(base,amp,voy) in enumerate([(D3,1,'u'),(D3,0.8,'m'),(D3*2,0.7,'u'),(D3*2,0.6,'m'),(D3/2,0.5,'m')]):
            f=base*2**((st+(faux.get(i,0) if v==2 else 0))/12)
            place(m,voix(f,d*B*1.05,voy,v)*amp,mk(i*B+rng.normal(0,0.05)+0.05))
    pas=np.zeros(L)                           # la procession avance au pas, dans la boue
    for i in range(int(80/1.25)):
        kk=mk(0.15); place(pas,burst(kk,lo=60,hi=600)*np.exp(-np.arange(kk)/SR*20),mk(i*1.25+rng.uniform(0,0.1)))
    m=reverb(fftfilt(m,hi=2200),3.5,0.55,seed=52)
    return stereo(nrm(m)*0.8+nrm(pas)*0.15,0.019)

save("amb_village-cloches-muettes_jour",jour())
save("amb_village-cloches-muettes_nuit",nuit(),0.7)
save("amb_village-cloches-muettes_autre",autre())
save("amb_village-cloches-muettes_verger",verger(),0.8)
save("amb_village-cloches-muettes_place",place_noce(),0.8)
save("amb_village-cloches-muettes_maison-ilde",maison_ilde(),0.8)
save("amb_village-cloches-muettes_clocher",clocher(),0.8)
save("amb_village-cloches-muettes_chambre",chambre(),0.7)
save("amb_village-cloches-muettes_chemin-nuit",chemin_nuit(),0.8)
save("amb_village-cloches-muettes_chemin-aube",chemin_aube(),0.8)
save("mus_village-cloches-muettes_noce",noce(),0.8)
save("mus_village-cloches-muettes_procession",procession(),0.75)
