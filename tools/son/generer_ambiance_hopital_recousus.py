# Étape 4, l'Hôpital des Recousus : ambiances et bruitages procéduraux, boucles sans couture.
# Une descente fermée : on est conduit, les portes se referment derrière Tobie. Les Recousus ont la
# bouche cousue : le Cantique n'est plus qu'un fredonnement nasal, et il ne vient que de l'autre.
# Usage : python3 generer_ambiance_hopital_recousus.py <sortie ambiances> [<sortie bruitages>]
import numpy as np, scipy.signal as ss, scipy.io.wavfile as wf, sys, os
SR=44100; BPM=48; BEAT=60/BPM; D4=293.66; D3=D4/2
rng=np.random.default_rng(1920); OUT=sys.argv[1]; OUT_SFX=sys.argv[2] if len(sys.argv)>2 else OUT
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
def souffle(dur,lo=200,hi=1100):   # une respiration (inspir + expir)
    n=mk(dur); tt=np.arange(n)/SR; e=np.sin(np.pi*tt/tt[-1])**2
    return burst(n,lo=lo,hi=hi)*e
def goutte():
    n=mk(0.12); tt=np.arange(n)/SR; f=rng.uniform(700,1600)
    return np.sin(2*np.pi*f*(1+2*np.exp(-tt*60))*tt)*np.exp(-tt*45)
def grincement(dur,f0,f1):
    n=mk(dur); tt=np.arange(n)/SR; f=np.linspace(f0,f1,n)*(1+0.03*np.sin(2*np.pi*23*tt))
    y=np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*(np.sin(2*np.pi*rng.uniform(25,45)*tt)>0.2)
    return fftfilt(np.pad(y,(0,mk(0.05))),lo=200,hi=3000)[:n]*np.hanning(n)
def fredon(f,dur,vid):   # bouche fermée, « mmm » nasal
    n=mk(dur); tt=np.arange(n)/SR; fv=f*2**(rng.uniform(-12,12)/1200)*(1+0.004*np.sin(2*np.pi*rng.uniform(4,5)*tt+vid))
    ph=np.cumsum(fv)/SR; y=np.zeros(n)
    for k in range(1,25):
        fk=f*k
        if fk>4000: break
        w=np.exp(-((fk-250)/120)**2)+0.3*np.exp(-((fk-2200)/300)**2)+0.02/k
        y+=w*np.sin(2*np.pi*k*ph+rng.uniform(0,6.28))
    return y*env_ar(n,0.3,0.5)

# ===== Couches globales (80 s, stéréo) =====
def hopital():   # la pierre, l'eau quelque part, des lits loin, des pas feutrés de sœurs
    piece=np.stack([fftfilt(colored(L80,2.0),lo=30,hi=260)*(0.7+0.3*lfo(L80,16,s)) for s in (0,1)],1)
    eau=np.zeros(L80)
    for i in range(int(80/1.9)): place(eau,goutte()*0.6,mk(i*1.9+rng.uniform(-0.05,0.05)))
    eau=reverb(eau,2.5,0.6,seed=61)
    lits=np.zeros(L80)
    for _ in range(6): place(lits,grincement(rng.uniform(0.3,0.7),rng.uniform(250,400),rng.uniform(200,350)),rng.integers(0,L80))
    lits=reverb(fftfilt(lits,hi=1500),2.0,0.7,seed=62)
    pas=np.zeros(L80)
    for tm in (20.0,61.0):
        for k in range(10):
            kk=mk(0.08); place(pas,burst(kk,lo=150,hi=900)*np.exp(-np.arange(kk)/SR*40)*0.6,mk(tm+k*0.62))
    pas=reverb(pas,2.0,0.7,seed=63)
    return nrm(piece)*0.45+stereo(nrm(eau))*0.12+stereo(nrm(lits),0.02)*0.12+stereo(nrm(pas),0.011)*0.1
def autre():   # le Cantique fredonné bouche cousue, des fils qu'on tire, un cœur de pierre
    m=np.zeros(L80); B=BEAT
    for i,st in enumerate(MEL):
        if st is None or i%8==7: continue          # une note manque à chaque phrase : le fil a tiré
        d=1
        while i+d<len(MEL) and MEL[i+d] is None: d+=1
        for v,(base,amp) in enumerate(((D3,1),(D3*2,0.6),(D3/2,0.5))):
            place(m,fredon(base*2**((st+(0.4 if (i%8==3 and v==1) else 0))/12),d*B*1.05,v)*amp,mk(i*B+rng.normal(0,0.04)))
    m=reverb(fftfilt(m,hi=1800),3.0,0.55,seed=64)
    fils=np.zeros(L80)
    for _ in range(12):
        n=mk(rng.uniform(0.4,1.0)); tt=np.arange(n)/SR; f=np.linspace(rng.uniform(900,1300),rng.uniform(1400,2000),n)
        y=np.sin(2*np.pi*np.cumsum(f)/SR)*(0.5+0.5*np.sign(np.sin(2*np.pi*60*tt)))*np.hanning(n)
        place(fils,fftfilt(np.pad(y,(0,mk(0.05))),lo=600,hi=4000)[:n],rng.integers(0,L80))
    coeur=np.zeros(L80)
    for i in range(int(80/(60/40))):
        for off,a in ((0,1),(0.3,0.6)):
            kk=mk(0.3); tk=np.arange(kk)/SR; place(coeur,np.sin(2*np.pi*38*tk)*np.exp(-tk*14)*a,mk(i*1.5+off))
    return stereo(nrm(m)*0.5+nrm(fils)*0.12+nrm(coeur)*0.3,0.014)

# ===== Lieux (20 s, mono) =====
def porche():    # dehors : la pluie fine sur la pierre, le tronc des offrandes qui grince
    pluie=fftfilt(colored(L20,0.3),lo=1500,hi=9000)*0.5+fftfilt(colored(L20,1.0),lo=200,hi=1500)*0.4
    gout=np.zeros(L20)
    for _ in range(60): place(gout,goutte()*rng.uniform(0.1,0.5),rng.integers(0,L20))
    tronc=np.zeros(L20); place(tronc,grincement(0.8,180,140),mk(7)); place(tronc,grincement(0.5,160,150),mk(15.5))
    return nrm(pluie)*0.4+nrm(gout)*0.2+nrm(tronc)*0.25
def salle():     # les respirations alignées : trente lits, un seul souffle ; une poitrine en retard
    m=np.zeros(L20)
    for i in range(5):
        for lit in range(14):
            place(m,souffle(3.2,180,1000)*rng.uniform(0.3,0.7),mk(i*4+rng.normal(0,0.03)))
        place(m,souffle(3.0,200,1100)*0.8,mk(i*4+1.1))    # celui qui n'y arrive pas
    lits=np.zeros(L20)
    for _ in range(3): place(lits,grincement(0.5,300,260),rng.integers(0,L20))
    return reverb(nrm(m)*0.6+nrm(lits)*0.12+nrm(fftfilt(colored(L20,2),lo=30,hi=200))*0.2,1.6,0.4,seed=71)
def lingerie():  # les draps mouillés qui gouttent, un drap qu'on tord
    gout=np.zeros(L20)
    for _ in range(45): place(gout,goutte()*rng.uniform(0.2,0.8),rng.integers(0,L20))
    tord=np.zeros(L20)
    for tm in (5.0,13.0):
        n=mk(1.6); tt=np.arange(n)/SR; place(tord,burst(n,lo=300,hi=3000)*np.hanning(n)*(0.5+0.5*np.sin(2*np.pi*9*tt)),mk(tm))
        place(tord,fftfilt(np.pad(rng.standard_normal(mk(1.2)),(0,mk(0.05))),lo=800,hi=5000)[:mk(1.2)]*(rng.random(mk(1.2))>0.9)*0.6,mk(tm+1.5))  # l'eau qui coule
    return reverb(nrm(gout)*0.35+nrm(tord)*0.4+nrm(fftfilt(colored(L20,1.8),lo=40,hi=300))*0.2,0.7,0.3,seed=72)
def atelier():   # le silence clinique : une mouche, un instrument posé, le verre d'un bocal
    mouche=np.zeros(L20)
    for tm,d in ((2.0,2.5),(11.0,3.5)):
        n=mk(d); tt=np.arange(n)/SR; f=q(180,n)*(1+0.08*np.sin(2*np.pi*3*tt))
        place(mouche,np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*np.hanning(n)*(0.6+0.4*np.sin(2*np.pi*0.7*tt)),mk(tm))
    mouche=fftfilt(mouche,lo=150,hi=2500)
    inst=np.zeros(L20)
    for tm in (7.3,16.1):
        kk=mk(0.6); tk=np.arange(kk)/SR; f=rng.uniform(2500,3800)
        place(inst,sum(a*np.sin(2*np.pi*f*r*tk)*np.exp(-tk*(8+r*5)) for r,a in ((1,1),(2.76,0.5),(5.4,0.25))),mk(tm))
    verre=np.zeros(L20)
    kk=mk(1.2); tk=np.arange(kk)/SR; place(verre,np.sin(2*np.pi*1850*tk)*np.exp(-tk*4)*0.4,mk(13.0))
    ciseaux=np.zeros(L20); kk=mk(0.05); place(ciseaux,burst(kk,lo=3000,hi=9000)*np.exp(-np.arange(kk)/SR*60),mk(18.2))
    return nrm(mouche)*0.12+nrm(inst)*0.3+nrm(verre)*0.15+nrm(ciseaux)*0.2+nrm(fftfilt(colored(L20,2),lo=30,hi=150))*0.05
def escalier():  # la pierre, une goutte, une flamme de chandelle
    gout=np.zeros(L20)
    for i in range(7): place(gout,goutte()*0.7,mk(i*20/7+0.4))
    flamme=fftfilt(colored(L20,1),lo=80,hi=500)*(0.6+0.4*lfo(L20,1.7))
    return reverb(nrm(gout)*0.35+nrm(flamme)*0.15+nrm(fftfilt(colored(L20,2),lo=30,hi=200))*0.3,3.0,0.5,seed=73)
def crypte():    # les saints qui respirent (seulement dans le noir) : d'immenses souffles lents, de pierre
    m=np.zeros(L20)
    for i in range(3):
        place(m,souffle(5.5,60,500)*1.0,mk(i*20/3))
        place(m,souffle(5.0,90,700)*0.6,mk(i*20/3+2.2))
    t=np.arange(L20)/SR; voix=np.sin(2*np.pi*q(D3/2,L20)*t)*(0.5+0.5*lfo(L20,20/3))**3
    return reverb(nrm(m)*0.7+nrm(voix)*0.08,4.0,0.6,seed=74)
def escalier_service():  # un courant d'air qui descend de la surface, la porte latérale en haut
    vent=fftfilt(colored(L20,1.4),lo=200,hi=2000)*(0.2+0.8*gusts(L20,4))
    t=np.arange(L20)/SR; sif=np.sin(2*np.pi*q(D4*3,L20)*t)*gusts(L20,4)**3
    return reverb(nrm(vent)*0.5+nrm(sif)*0.04+nrm(fftfilt(colored(L20,2),lo=30,hi=200))*0.2,2.0,0.4,seed=75)
def porte_laterale():  # dehors de nouveau : l'air gris, un oiseau seul, la pluie qui s'arrête
    vent=fftfilt(colored(L20,1.3),lo=80,hi=1500)*(0.3+0.7*gusts(L20,7))
    gout=np.zeros(L20)
    for _ in range(20): place(gout,goutte()*rng.uniform(0.1,0.5),rng.integers(0,L20))
    oiseau=np.zeros(L20)
    for tm in (6.0,6.25,14.0):
        n=mk(0.18); tt=np.arange(n)/SR; place(oiseau,np.sin(2*np.pi*np.cumsum(3200*(1-0.2*tt/tt[-1]))/SR)*np.hanning(n),mk(tm))
    return nrm(vent)*0.45+nrm(gout)*0.15+nrm(oiseau)*0.12

# ===== Bruitage : la porte qui se referme derrière Tobie =====
# Un grand battant de bois, le loquet qui retombe, et le loquet sonne un quart de ton trop bas.
def porte(i):
    n=mk(2.2); y=np.zeros(n); tt=np.arange(n)/SR
    g=grincement(rng.uniform(0.7,1.0),rng.uniform(140,190),rng.uniform(90,120)); y[:len(g)]+=g*0.5
    t0=mk(rng.uniform(0.85,1.05)); k=n-t0; tk=np.arange(k)/SR
    coup=burst(k,hi=400)*np.exp(-tk*18)*2+np.sin(2*np.pi*rng.uniform(55,70)*tk)*np.exp(-tk*12)*1.5
    f=D4*4*2**(-0.5/12)
    loquet=sum(a*np.sin(2*np.pi*f*r*tk)*np.exp(-tk*(14+r*6)) for r,a in ((1,1),(2.4,0.4),(4.1,0.2)))
    lq=np.zeros(k); dl=mk(0.12); lq[dl:]=loquet[:k-dl]*0.35
    y[t0:]+=coup+lq
    y=reverb(np.pad(y,(0,mk(1.5))),1.6,0.35,seed=80+i)
    return nrm(y,0.8)

save("amb_hopital-recousus_hopital",hopital())
save("amb_hopital-recousus_autre",autre())
for nom,fn in (("porche",porche),("salle",salle),("lingerie",lingerie),("atelier",atelier),("escalier",escalier),
               ("crypte",crypte),("escalier-service",escalier_service),("porte-laterale",porte_laterale)):
    save("amb_hopital-recousus_"+nom,fn(),0.8)
for i in range(3):
    x=porte(i); wf.write(os.path.join(OUT_SFX,"sfx_porte_fermer_%02d.wav"%(i+1)),SR,(x*32767).astype(np.int16)); print("sfx_porte_fermer_%02d"%(i+1))
