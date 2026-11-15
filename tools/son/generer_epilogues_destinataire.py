# Étape 7 : la salle des cloches tues et les cinq épilogues du Cantique du Pli.
# Toute la déconstruction du thème se paie ici : il se résout, se brise ou reste suspendu.
# Noms de fichiers neutres (règle du Game Director) : la correspondance lettre → fin est dans
# tools/son/README.md, jamais dans un nom de fichier.
#   fin-a : se résout tout bas, puis le battant touche la cloche sans qu'elle sonne
#   fin-b : résolution pleine sur ré majeur, tout ce que le thème a perdu revient
#   fin-c : la même résolution, puis les cloches sonnent pour de bon (la seule fois du jeu)
#   fin-d : l'harmonium seul manque d'air et se brise à la septième mesure
#   fin-e : le thème reste suspendu sur la, sans se poser
# Les épilogues ne bouclent pas (AudioDirector.jouer_epilogue) ; la salle et l'autre bouclent.
# Usage : python3 generer_epilogues_destinataire.py <sortie>
import numpy as np, scipy.io.wavfile as wf, sys, os
SR=44100; D3=146.83; D2=D3/2
rng=np.random.default_rng(1921); OUT=sys.argv[1]
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
def place(buf,ev,pos):
    pos=int(pos); n=min(len(ev),len(buf)-pos)
    if n>0: buf[pos:pos+n]+=ev[:n]
def place_circ(buf,ev,pos): np.add.at(buf,(np.arange(len(ev))+pos)%len(buf),ev)
def burst(n,lo=None,hi=None): return fftfilt(rng.standard_normal(n+mk(0.05)),lo=lo,hi=hi)[:n]
def reverb(x,sec,wet,seed=0,hi=4000,circ=True):
    L=len(x); r=np.random.default_rng(seed); n=mk(sec); ir=r.standard_normal(n)*np.exp(-6.9*np.arange(n)/n)
    if not circ: x=np.pad(x,(0,n)); L=len(x)
    ir=fftfilt(np.pad(ir,(0,L-n)),hi=hi); y=np.fft.irfft(np.fft.rfft(x)*np.fft.rfft(ir),L); y*=np.std(x)/(np.std(y)+1e-9)
    return (1-wet)*x+wet*y
def q(f,L): return round(f*L/SR)*SR/L
def nrm(x,p=1.0): return x/(np.abs(x).max()+1e-9)*p
def stereo(m,delay=0.017): return np.stack([m,np.roll(m,mk(delay))],1)
def env_ar(n,a,r):
    e=np.ones(n); a=max(1,min(n,mk(a))); r=max(1,min(n,mk(r))); e[:a]=np.linspace(0,1,a); e[-r:]*=np.linspace(1,0,r); return e
def save(name,x,peak=0.85): x=nrm(x,peak); wf.write(os.path.join(OUT,name+".wav"),SR,(x*32767).astype(np.int16)); print(name)

MEL=[0,3,5,7, 7,5,3,2, 0,2,3,5, 7,None,None,None, 10,9,7,5, 3,5,7,3, 2,0,2,-2, 0,None,None,None]
ACC=[[0,3,7],[7,10,14],[0,3,7],[7,10,14],[-2,2,5],[3,7,10],[-2,2,5],[0,3,7]]
MAJEUR=[0,4,7]            # la tierce picarde : le ré mineur se pose en ré majeur
SUSPENDU=[7,11,14]        # la majeur, la dominante : appelle ré et ne l'obtient pas
BPM=42; B=60/BPM          # plus lent que partout ailleurs

# --- Instruments repris des étapes précédentes ---
def voix(f,dur,vowel,vid,fatigue=0.0):   # chœur d'hommes (étape 1)
    n=mk(dur); tt=np.arange(n)/SR
    vib=1+0.005*np.sin(2*np.pi*rng.uniform(4.2,5.6)*tt+vid)*np.clip(tt/0.6,0,1)
    sag=1-fatigue*np.clip((tt-dur*0.6)/(dur*0.4+1e-9),0,1)
    fv=f*2**(rng.uniform(-6,6)/1200)*vib*sag; ph=np.cumsum(fv)/SR
    F={'o':(450,800,2500),'u':(330,750,2400),'a':(700,1150,2500),'m':(260,900,2200)}[vowel]; y=np.zeros(n)
    for k in range(1,36):
        fk=f*k
        if fk>7000: break
        w=np.exp(-((fk-F[0])/170)**2)+0.55*np.exp(-((fk-F[1])/230)**2)+0.12*np.exp(-((fk-F[2])/350)**2)+0.02/k
        y+=w*np.sin(2*np.pi*k*ph+rng.uniform(0,6.28))
    return y*env_ar(n,0.25,0.45)
def harmonium_acc(acc,dur,base=D3,souffle=1.0):
    n=mk(dur); tt=np.arange(n)/SR; y=np.zeros(n)
    for st in acc+[acc[0]-12]:
        f=base*2**(st/12)*(1+0.0015*rng.standard_normal()); ph=2*np.pi*f*tt
        y+=sum(np.sin(k*ph)*(1/k**1.1)*(1.4 if k in (2,4) else 1) for k in range(1,14))
    return fftfilt(np.pad(y*env_ar(n,0.4,0.6)*souffle,(0,mk(0.05))),hi=2200)[:n]
def fil(f,dur):            # les fils du No Man's Land (étape 2)
    n=mk(dur); tt=np.arange(n)/SR
    y=sum(a*np.sin(2*np.pi*f*r*tt+rng.uniform(0,6)) for r,a in ((1,1),(2.013,0.45),(3.04,0.25)))
    return y*(0.7+0.3*np.sin(2*np.pi*2.2*tt))*env_ar(n,0.35,0.4)
def vielle(dur,base=D2):  # le bourdon de la noce (étape 3)
    n=mk(dur); tt=np.arange(n)/SR
    y=sum(np.sin(2*np.pi*k*base*tt)/k for k in range(1,20))+0.6*sum(np.sin(2*np.pi*k*base*1.5*tt)/k for k in range(1,20))
    return fftfilt(np.pad(y*env_ar(n,1.5,2.5),(0,mk(0.05))),hi=2000)[:n]
def cloche(f,force=1.0,dur=9.0):   # une vraie cloche, avec son attaque : la seule du jeu
    n=mk(dur); tt=np.arange(n)/SR
    y=sum(a*np.sin(2*np.pi*f*r*tt+rng.uniform(0,6))*np.exp(-tt*(0.35+r*0.5)) for r,a in
          ((0.5,0.9),(1,1),(1.2,0.7),(1.5,0.5),(2,0.6),(2.5,0.3),(2.67,0.25),(3,0.2),(4.2,0.12)))
    k=mk(0.03); y[:k]+=burst(k,lo=1500,hi=9000)*np.exp(-np.arange(k)/SR*120)*1.5
    return y*force
def battant_dans_le_vide(f=D2):   # la cloche muette : résonance à l'envers, battant qui frappe, plus rien
    k=mk(4); tt=np.arange(k)/SR
    ring=sum(a*np.sin(2*np.pi*f*r*tt)*np.exp(-tt*(0.6+r*0.4)) for r,a in ((0.5,1),(1,0.8),(1.2,0.5),(1.5,0.4),(2,0.35)))
    kk=mk(0.25); tk=np.arange(kk)/SR
    thud=burst(kk,hi=220)*np.exp(-tk*28)*3+np.sin(2*np.pi*44*tk)*np.exp(-tk*22)*2
    return np.concatenate([ring[::-1]*np.linspace(0,1,k)**2*0.5,thud])

def jouer(mel,accords,L,pupitres,harmo=1.0,arret=None,souffle_harmo=None):
    """Chœur (pupitres : liste de (octave, amp, voyelle)) et harmonium sur la grille de 32 temps."""
    ch=np.zeros(L); hm=np.zeros(L)
    for i,st in enumerate(mel):
        if st is None or (arret is not None and i>=arret): continue
        d=1
        while i+d<len(mel) and mel[i+d] is None: d+=1
        tenue=d*B*(2.2 if i==len(mel)-4 else 1.04)      # la dernière note tient
        for v,(octv,amp,voy) in enumerate(pupitres):
            place(ch,voix(D3*2**((st+octv)/12),tenue,voy,v)*amp,mk(i*B+rng.normal(0,0.03)+0.05))
    for b,acc in enumerate(accords):
        if arret is not None and b*4>=arret: break
        dur=4*B*(2.2 if b==7 else 1.0)+0.4
        s=souffle_harmo(b) if souffle_harmo else 1.0
        place(hm,harmonium_acc(acc,dur,souffle=s),mk(b*4*B))
    return nrm(ch)*0.75+nrm(hm)*0.32*harmo

L_EPI=mk(32*B+16)    # le thème, sa note finale tenue, puis la queue de réverbération
PUPITRES=[(0,1,'o'),(0,0.9,'o'),(0,0.8,'u'),(-12,0.7,'o'),(-12,0.6,'u')]

def fin_a():   # tout bas : un chœur réduit, bouche presque fermée, puis le battant dans le vide
    m=jouer(MEL,ACC[:7]+[MAJEUR],L_EPI,[(0,1,'u'),(-12,0.6,'m')],harmo=0.5)*0.6
    fin=np.zeros(L_EPI); place(fin,battant_dans_le_vide(),mk(32*B+5))
    m=m+nrm(fin)*0.5
    return stereo(reverb(m,3.5,0.5,seed=71),0.011)
def fin_b():   # tout revient : le chœur entier, l'harmonium, les fils, la vielle ; ré majeur
    m=jouer(MEL,ACC[:7]+[MAJEUR],L_EPI,PUPITRES+[(12,0.35,'a')])
    fils=np.zeros(L_EPI)
    for i,st in enumerate(MEL[:16]):
        if st is None: continue
        place(fils,fil(D3*4*2**(st/12),B*1.1),mk((16+i)*B))   # les fils reprennent la seconde moitié, justes cette fois
    v=np.zeros(L_EPI); place(v,vielle(32*B-12*B+10),mk(12*B))
    m=m+nrm(fils)*0.12+nrm(v)*0.18
    return stereo(reverb(m,3.5,0.45,seed=72),0.011)
def fin_c():   # la résolution, puis les cloches sonnent pour de bon, couvrent tout, et tout s'arrête
    L=L_EPI+mk(12)
    m=np.zeros(L); m[:L_EPI]=fin_b()[:,0]*0.6      # le chœur plus bas : les cloches doivent tout couvrir
    t0=mk(32*B+1.5)                                  # pendant que l'accord final tient encore
    cl=np.zeros(L)
    for k in range(18):                               # une volée qui enfle : quatre cloches en ronde
        f=(D3,D3*0.75,D2*1.5,D2)[k%4]; force=min(1.0,0.25+k*0.06)
        place(cl,cloche(f,force),t0+mk(k*0.62+rng.normal(0,0.02)))
    cl=reverb(cl,4.5,0.4,seed=73,hi=6000,circ=False)[:L]
    m=m+np.tanh(3*nrm(cl))*1.0                      # saturées : une volée pleine, sans pic isolé
    coupe=t0+mk(18*0.62+2.5); m[coupe:]=0.0       # Tobie meurt sous le son : coupure nette, silence
    m[coupe-mk(0.01):coupe]*=np.linspace(1,0,mk(0.01))
    return stereo(m,0.009)
def fin_d():   # l'harmonium seul, qui manque d'air ; il se brise à la septième mesure
    def souffle(b): return 1.0 if b<4 else max(0.2,1.0-(b-3)*0.25)
    m=jouer(MEL,ACC,L_EPI,[(0,0.0,'o')],harmo=1.0,arret=26,souffle_harmo=souffle)
    mel=np.zeros(L_EPI)
    for i,st in enumerate(MEL[:26]):        # la mélodie à l'harmonium, une voix
        if st is None: continue
        d=1
        while i+d<len(MEL) and MEL[i+d] is None: d+=1
        n=mk(d*B); tt=np.arange(n)/SR; f=D3*2*2**(st/12)
        if i==25: f=f*(1-0.03*np.clip(tt/(d*B),0,1))           # la dernière note s'affaisse : le soufflet est vide
        ph=2*np.pi*np.cumsum(np.full(n,f) if np.isscalar(f) else f)/SR
        y=sum(np.sin(k*ph)/k**1.2 for k in range(1,10))*env_ar(n,0.1,0.15 if i<25 else 0.02)*souffle(i//4)
        place(mel,y,mk(i*B))
    a=mk(26*B); m[a:]=0                                          # rien ne vient après
    souffle_fin=np.zeros(L_EPI); n=mk(1.2); place(souffle_fin,burst(n,lo=200,hi=900)*np.linspace(1,0,n)**2*0.3,a)
    m=m+nrm(fftfilt(mel,hi=2500))*0.6+souffle_fin
    m=reverb(m,2.5,0.4,seed=74,circ=False)[:a+mk(8)]          # huit secondes de silence, pas plus
    m*=np.concatenate([np.ones(len(m)-mk(1)),np.linspace(1,0,mk(1))])
    return stereo(m,0.011)
def fin_e():   # suspendu : la dernière note devient la, sur l'accord de la, et le chœur se retire sans se poser
    mel=list(MEL); mel[28]=7
    m=jouer(mel,ACC[:7]+[SUSPENDU],L_EPI,[(0,1,'o'),(0,0.8,'u'),(-12,0.6,'o')])
    vent=fftfilt(colored(L_EPI,1.4),lo=60,hi=900)*np.clip((np.arange(L_EPI)/SR-20)/20,0,1)
    m=reverb(m+nrm(vent)*0.15,3.5,0.5,seed=75)
    m*=np.concatenate([np.ones(L_EPI-mk(8)),np.linspace(1,0,mk(8))**2])   # le vent emporte tout, sans conclure
    return stereo(m,0.011)

# --- La salle des cloches tues (couches globales, boucles de 80 s) ---
L80=mk(80)
def salle():   # le bourdon sans attaque des cloches tues, la pierre immense, un murmure liturgique au loin
    t=np.arange(L80)/SR
    bourdon=sum(a*np.sin(2*np.pi*q(D2*r,L80)*t+rng.uniform(0,6)) for r,a in ((0.5,1),(1,0.8),(1.2,0.35),(1.5,0.3),(2,0.25)))
    bourdon*=0.6+0.4*lfo(L80,20)
    piece=np.stack([fftfilt(colored(L80,2.0),lo=25,hi=200) for _ in (0,1)],1)
    mur=np.zeros(L80)
    for _ in range(18):
        pos=rng.integers(0,L80); f0=rng.uniform(95,140)
        for k in range(rng.integers(3,7)):
            n=mk(rng.uniform(0.25,0.5)); place_circ(mur,voix(f0,n/SR,'o' if k%2 else 'a',k)*0.5,pos+mk(k*0.45))
    mur=reverb(fftfilt(mur,lo=120,hi=1200),5.0,0.75,seed=76)
    return stereo(nrm(bourdon)*0.5,0.02)+nrm(piece)*0.3+stereo(nrm(mur),0.031)*0.12
def autre():   # le chœur de toutes les étapes, à l'envers, et des souffles de noms qu'on ne comprend pas
    m=jouer(MEL,ACC,L80,[(0,1,'u'),(-12,0.7,'m')],harmo=0.6)[::-1]
    m=reverb(fftfilt(m,hi=1800),4.0,0.6,seed=77)
    noms=np.zeros(L80)
    for i in range(int(80/5.5)):
        n=mk(rng.uniform(0.6,1.1)); tt=np.arange(n)/SR
        place_circ(noms,burst(n,lo=1500,hi=6000)*(0.5+0.5*np.sin(2*np.pi*rng.uniform(4,7)*tt))**2*np.hanning(n),mk(i*5.5+rng.uniform(0,1)))
    return stereo(nrm(m)*0.45+nrm(reverb(noms,2.0,0.6,seed=78))*0.15,0.013)

save("amb_destinataire_salle",salle())
save("amb_destinataire_autre",autre())
save("mus_destinataire_fin-a",fin_a())
save("mus_destinataire_fin-b",fin_b())
save("mus_destinataire_fin-c",fin_c(),0.95)
save("mus_destinataire_fin-d",fin_d())
save("mus_destinataire_fin-e",fin_e())
