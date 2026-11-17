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

# fin-a : l'épilogue animé de la DA (32 s, quatre plans coupés à 8, 16 et 24 s, PR #223). Rien ne sonne :
#   0-8 s    la corde se balance sous la bouche de la cloche (période 3,2 s) : le chanvre grince à chaque bout ;
#   8-16 s   les pelletées de terre par-dessus le parapet, deux casques décalés ;
#   16-24 s  un soldat siffle le Cantique ; la larme paraît à 19,5 s, le sifflet se casse quand elle coule (21,5 s) ;
#   24-32 s  la Mère-Cloche murmure des noms (24,6-30 s), la lampe se rallume (26,5 s), ses doigts s'arrêtent
#            sur un nom (28,5 s) : le chœur se résout tout bas, et tient sur le fondu au papier.
PERIODE_CORDE=3.2
PELLETEES=((8.4,9.9,11.4,12.9,14.4),(9.1,10.6,12.1,13.6,15.1))   # deux casques
LARME,LARME_COULE=19.5,21.5
MURMURE=(24.6,30.0); LAMPE=26.5; NOM=28.5
def corde_grince(force=1.0):   # le chanvre qui tourne sur son anneau, au bout du balancement
    n=mk(0.5); tt=np.arange(n)/SR; f=np.linspace(380,300,n)*(1+0.03*np.sin(2*np.pi*23*tt))
    y=fftfilt(np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*burst(n,lo=300,hi=3000)*0.3+burst(n,lo=800,hi=2500)*0.2,lo=250,hi=2200)
    return y*np.sin(np.pi*tt/tt[-1])**2*force
def pelletee():   # la terre lancée qui retombe sur la toile et les planches
    n=mk(0.9); tt=np.arange(n)/SR; y=np.zeros(n)
    k=mk(0.08); place(y,burst(k,hi=500)*np.exp(-np.arange(k)/SR*30),0)                      # le choc mat
    pluie=burst(n,lo=1500,hi=6000)*np.exp(-tt*6)*(rng.random(n)<0.04)*1.0
    return y+fftfilt(pluie,lo=1200,hi=6000)*0.6+burst(n,hi=300)*np.exp(-tt*9)*0.4
def sifflet(f,dur,casse=0.0):   # un sifflet humain : sinus, souffle, vibrato qui s'installe
    n=mk(dur); tt=np.arange(n)/SR
    fv=f*(1+0.006*np.sin(2*np.pi*5.2*tt)*np.clip(tt/0.3,0,1))*(1-casse*np.clip((tt-dur*0.4)/(dur*0.6),0,1)*0.04)
    y=np.sin(2*np.pi*np.cumsum(fv)/SR)+burst(n,lo=f*0.9,hi=f*1.2)*0.15
    return y*env_ar(n,0.06,0.12)*(1-casse*np.clip((tt-dur*0.5)/(dur*0.5),0,1))
def fin_a():   # son propre hasard (graine 1920), puis les tirages de l'ancienne fin-a : tout ce qui suit reste identique
    global rng
    principal=rng; rng=np.random.default_rng(1920)
    try: y=_fin_a()
    finally: rng=principal
    _tirages_fin_a_v1()
    return y
def _tirages_fin_a_v1():   # l'ancienne fin-a (62 s, avant la ciné), rejouée pour ses seuls tirages ; le résultat est jeté
    jouer(MEL,ACC[:7]+[MAJEUR],L_EPI,[(0,1,'u'),(-12,0.6,'m')],harmo=0.5); battant_dans_le_vide()
def _fin_a():
    L=mk(35); t=np.arange(L)/SR
    # 0-16 s : le chœur tout bas, bouche presque fermée, sur les deux premières mesures ; il se tait sous le sifflet
    lit=jouer(MEL[:12]+[None]*20,ACC[:3],L,[(0,1,'u'),(-12,0.6,'m')],harmo=0.4)
    lit*=np.clip((16.5-t)/2.5,0,1)
    # 0-8 s : la corde, sous la bouche muette ; un souffle grave de bronze qui ne vient pas
    plan1=np.zeros(L)
    for k in range(int(8/(PERIODE_CORDE/2))+1):
        place(plan1,corde_grince(0.8 if k%2 else 1.0),mk(0.2+k*PERIODE_CORDE/2))
    tt=np.arange(mk(8.4))/SR
    plan1[:len(tt)]+=sum(a*np.sin(2*np.pi*D2*r*tt) for r,a in ((1,1),(2,0.4),(2.4,0.2)))*0.08*np.clip(tt/2,0,1)*np.clip((8.2-tt)/0.3,0,1)
    # 8-16 s : la terre
    plan2=np.zeros(L)
    for c,serie in enumerate(PELLETEES):
        for tp in serie: place(plan2,pelletee()*(1.0 if c==0 else 0.75),mk(tp))
    # 16-24 s : le Cantique sifflé, trois octaves au-dessus (registre d'un sifflet) ; il se casse quand la larme coule
    plan3=np.zeros(L); bt=0.5; t0=16.4
    for i,st in enumerate(MEL[:16]):
        if st is None: continue
        d=1
        while i+d<16 and MEL[i+d] is None: d+=1
        debut=t0+i*bt
        if debut>=LARME_COULE+0.3: break
        casse=1.0 if debut<=LARME_COULE<debut+d*bt else 0.0
        trem=0.35 if debut>=LARME else 0.0               # la larme paraît : le souffle tremble
        y=sifflet(D3*8*2**(st/12)*(1-0.01*trem),d*bt*1.02,casse)
        if trem: y=y*(1+trem*0.5*np.sin(2*np.pi*7.5*np.arange(len(y))/SR))
        place(plan3,y,mk(debut))
    k=mk(0.6); place(plan3,burst(k,lo=300,hi=1500)*np.linspace(1,0,k)**2*0.25,mk(LARME_COULE+0.25))   # le souffle qui lâche
    plan3=reverb(fftfilt(plan3,lo=400,hi=6000),2.0,0.5,seed=91,circ=False)[:L]
    vent=fftfilt(colored(L,1.4),lo=80,hi=1200)*np.clip((t-16.0)/0.2,0,1)*np.clip((24.0-t)/0.2,0,1)   # dehors, l'air de la tranchée
    plan3=nrm(plan3)+nrm(vent)*0.06
    # 24-32 s : les noms murmurés, la lampe, le doigt qui s'arrête ; le chœur se pose tout bas
    plan4=np.zeros(L); tm=MURMURE[0]
    while tm<min(MURMURE[1],NOM+0.2):
        n=mk(rng.uniform(0.35,0.7)); tt=np.arange(n)/SR
        place(plan4,burst(n,lo=1200,hi=5000)*(0.5+0.5*np.sin(2*np.pi*rng.uniform(4,7)*tt))**2*np.hanning(n)*0.5,mk(tm))
        tm+=n/SR+rng.uniform(0.08,0.25)
    n=mk(0.5); tt=np.arange(n)/SR
    place(plan4,(burst(n,lo=600,hi=4000)*np.exp(-tt*5)+burst(n,hi=250)*np.clip(tt/0.2,0,1))*0.35,mk(LAMPE))   # la mèche reprend
    fin=jouer(MEL[28:29]+[None]*3,[MAJEUR],mk(10),[(0,1,'u'),(-12,0.6,'m')],harmo=0.5)
    place(plan4,fin*np.clip((np.arange(len(fin))/SR)/1.5,0,1),mk(NOM))
    m=nrm(lit)*0.35+nrm(plan1)*0.35+nrm(plan2)*0.7+nrm(plan3)*0.55+nrm(plan4)*0.6
    m*=np.clip((34.5-t)/3.0,0,1)**2                          # le fondu au papier, puis plus rien
    return stereo(reverb(m,3.5,0.4,seed=71,circ=False)[:L],0.011)
def fin_b():   # tout revient : le chœur entier, l'harmonium, les fils, la vielle ; ré majeur
    m=jouer(MEL,ACC[:7]+[MAJEUR],L_EPI,PUPITRES+[(12,0.35,'a')])
    fils=np.zeros(L_EPI)
    for i,st in enumerate(MEL[:16]):
        if st is None: continue
        place(fils,fil(D3*4*2**(st/12),B*1.1),mk((16+i)*B))   # les fils reprennent la seconde moitié, justes cette fois
    v=np.zeros(L_EPI); place(v,vielle(32*B-12*B+10),mk(12*B))
    m=m+nrm(fils)*0.12+nrm(v)*0.18
    return stereo(reverb(m,3.5,0.45,seed=72),0.011)
# fin-c : la ciné « cloches » de la DA (36 s, planche du 17/11), la seule sonnerie du jeu. Grille de coups
# partagée avec la DA (temps depuis le début de l'épilogue ; le noir de e7_corde_tiree reste muet) :
#   0-8 s    la grande cloche oscille : un coup à chaque extrémité, toutes les 1,8 s ; les bouchons de cire
#            claquent (2,6 / 4,4 / 6,0 s), tombent 0,4 s plus tard, et chaque petite cloche entre aussitôt ;
#   8-18 s   travelling vers le haut : la volée continue, entendue à travers galeries, forêt, champs d'Ilde, tranchée ;
#   18-26 s  la main de Tobie : la volée revient tout près, puis les coups s'espacent, la corde va seule ;
#   26-36 s  Lamarre lève la tête : seule la résonance lointaine arrive là-haut, et dure sur le noir final (GD).
GRANDE_PERIODE=1.8
CIRE=(2.6,4.4,6.0)
TRAVELLING=((8.0,"galeries"),(10.5,"foret"),(13.0,"champs"),(15.5,"tranchee"),(18.0,"main"))   # paliers DA : 10-11, 12,5-13,5, 15-16 s
DERNIERS_COUPS=((18.0,1.0),(19.9,0.75),(22.0,0.5),(24.4,0.3))   # la corde va et vient seule
def pan(x,p): a=(p+1)*np.pi/4; return np.stack([x*np.cos(a),x*np.sin(a)],1)
def cire_claque():   # le bouchon de cire noire se fend : un craquement sec ; il tombe sur la pierre 0,4 s plus tard
    k=mk(0.6); y=np.zeros(k); c=mk(0.05)
    for j in range(3): place(y,burst(c,lo=2500,hi=8000)*np.exp(-np.arange(c)/SR*90)*(1-0.3*j),mk(j*0.018))
    t=mk(0.12); tt=np.arange(t)/SR; place(y,(burst(t,hi=600)*0.6+np.sin(2*np.pi*180*tt))*np.exp(-tt*45)*0.5,mk(0.4))
    return y
def fin_c():   # son propre hasard (graine 1922), puis les tirages de l'ancienne fin-c : fin-d et fin-e restent identiques
    global rng
    principal=rng; rng=np.random.default_rng(1922)
    try: y=_fin_c()
    finally: rng=principal
    _tirages_fin_c_v1()
    return y
def _tirages_fin_c_v1():   # l'ancienne fin-c (73 s, avant la ciné), rejouée pour ses seuls tirages ; le résultat est jeté
    L=L_EPI+mk(12); fin_b(); t0=mk(32*B+1.5); cl=np.zeros(L)
    for k in range(18):
        f=(D3,D3*0.75,D2*1.5,D2)[k%4]; place(cl,cloche(f,1.0),t0+mk(k*0.62+rng.normal(0,0.02)))
def _fin_c():
    L=mk(41); t=np.arange(L)/SR
    proche=np.zeros((L,2))
    # la grande cloche : le battant frappe à chaque extrémité, gauche puis droite
    n=0; tc=0.0
    while tc<18.0-1e-6:
        c=pan(cloche(D3,1.0,12.0),-0.3 if n%2==0 else 0.3)
        place(proche[:,0],c[:,0],mk(tc)); place(proche[:,1],c[:,1],mk(tc))
        n+=1; tc=n*GRANDE_PERIODE
    for tc,force in DERNIERS_COUPS:
        c=pan(cloche(D3,force,12.0),0.3 if round(tc/GRANDE_PERIODE)%2 else -0.3)
        place(proche[:,0],c[:,0],mk(tc)); place(proche[:,1],c[:,1],mk(tc))
    # les petites cloches : cire qui claque, qui tombe, puis des coups courts sans balancement
    for j,(tcire,f,p) in enumerate(zip(CIRE,(D3*2,D3*2*2**(4/12),D3*3),(-0.6,0.6,0.1))):
        cc=pan(cire_claque()*0.5,p); place(proche[:,0],cc[:,0],mk(tcire)); place(proche[:,1],cc[:,1],mk(tcire))
        tc=tcire+0.7; k=0
        while tc<20.0:
            c=pan(cloche(f,0.45*(1.0 if tc<18.5 else 0.6),5.0),p)
            place(proche[:,0],c[:,0],mk(tc)); place(proche[:,1],c[:,1],mk(tc))
            k+=1; tc=tcire+0.7+k*0.9+rng.normal(0,0.03)
    # le Cantique se pose encore dessous : l'accord final de la résolution, avalé par la volée
    choeur=fin_b()[mk(28*B):,0]; choeur=choeur[:mk(12)]*np.linspace(1,0,mk(12))**1.5
    proche[:len(choeur)]+=stereo(nrm(choeur)*0.25,0.011)
    proche=np.stack([reverb(proche[:,c],4.5,0.4,seed=73+c,hi=6000,circ=False)[:L] for c in (0,1)],1)
    proche=np.tanh(2.5*nrm(proche))                  # une volée pleine, saturée, sans pic isolé
    # ce que le travelling entend : la même volée, à travers chaque décor
    def couleur(x,lieu):
        if lieu=="galeries": y=[fftfilt(reverb(x.mean(1),2.5,0.6,seed=81,hi=900),hi=400)]*2; g=0.8   # à travers la terre : plus de côtés
        elif lieu=="foret":  y=[reverb(fftfilt(x[:,c],hi=2500),3.0,0.6,seed=83+c) for c in (0,1)]; g=0.6
        elif lieu=="champs": y=[fftfilt(x[:,c],lo=80,hi=5000) for c in (0,1)]; g=0.45
        elif lieu=="tranchee": y=[reverb(fftfilt(x[:,c],lo=120,hi=1500),2.0,0.7,seed=85+c) for c in (0,1)]; g=0.2
        else: return x
        return nrm(np.stack(y,1))*g
    def fenetre(a,b,xa=0.4,xb=None):   # 1 entre a et b, fondus centrés de xa (entrée) et xb (sortie) secondes
        xb=xa if xb is None else xb
        return np.clip((t-a+xa/2)/xa,0,1)*np.clip((b-t+xb/2)/xb,0,1)
    m=proche*fenetre(-1,8.0,0.4,0.1)[:,None]
    bornes=[a for a,_ in TRAVELLING]
    for (a,lieu),b in zip(TRAVELLING[:-1],bornes[1:]):   # coupes sèches à 8 et 18 s, fondus d'1 s pendant chaque palier
        m+=couleur(proche,lieu)*fenetre(a,b,0.1 if a==8.0 else 1.0,0.1 if b==18.0 else 1.0)[:,None]
    m+=proche*(fenetre(18.0,27.0,0.1,1.0)*np.clip((27.0-t)/3.0,0,1)**0.5)[:,None]    # la main : tout près, puis ça s'éteint
    # Lamarre : la résonance arrive là-haut, très loin, avec le vent ; elle tient sur le noir final
    n=L-mk(25.5); tt=np.arange(n)/SR
    res=sum(a*np.sin(2*np.pi*D3*r*tt+rng.uniform(0,6)) for r,a in ((0.5,1),(1,0.6),(1.2,0.3),(2,0.15)))
    res=fftfilt(res*np.clip(tt/1.5,0,1)*np.exp(-tt/8.0),hi=700)
    vent=fftfilt(colored(n,1.4),lo=60,hi=900)*np.clip(tt/2,0,1)
    loin=np.stack([reverb(nrm(res)*0.32+nrm(vent)*0.05,3.0,0.6,seed=87+c) for c in (0,1)],1)
    loin*=np.clip((L-mk(1.0)-mk(25.5)-np.arange(n))/mk(3.0),0,1)[:,None]**2   # éteint vers 40 s, puis le silence
    m[mk(25.5):]+=loin
    return m
# fin-d : l'épilogue animé de la DA (32 s, coupes à 8, 14 et 24 s, PR #225). L'harmonium seul, qui manque d'air :
#   0-8 s    la main pose le pli sur les autres (2,0 / 3,4 / 4,6 s) ;
#   8-14 s   personne ne grave rien : l'harmonium seul, le soufflet faiblit ;
#   14-24 s  le garçon reçoit la sacoche (16 s), la cloche sans battant (17,5 s, aucun son de cloche), l'ordre (19 s) ;
#   24-32 s  l'harmonium se brise à la coupe ; il ne reste que le pas, le même que celui de Tobie (24,5-30,5 s,
#            un pas toutes les 0,4 s), qui s'éloigne sur le fondu au papier.
PLIS=(2.0,3.4,4.6); SACOCHE,CLOCHE_MUETTE,ORDRE=16.0,17.5,19.0
PAS=(24.5,30.5,0.4); BRISE=24.0; BT_D=1.07          # le thème un peu plus vif : la rupture tombe sur la coupe de 24 s
def pli_pose():     # un pli de papier épais posé sur la pile
    n=mk(0.35); tt=np.arange(n)/SR; y=np.zeros(n)
    for _ in range(14):
        k=mk(rng.uniform(0.004,0.015)); place(y,burst(k,lo=1500,hi=7000)*np.hanning(k)*rng.uniform(0.2,0.8),mk(rng.uniform(0,0.12)))
    k=mk(0.05); place(y,burst(k,hi=900)*np.exp(-np.arange(k)/SR*70)*1.2,mk(0.1))   # la tape sur la pile
    return y
def cuir():         # la sacoche : sangle qui frotte, boucle qui tinte à peine
    n=mk(0.6); tt=np.arange(n)/SR
    y=fftfilt(burst(n,lo=300,hi=2500),lo=300,hi=2500)*np.sin(np.pi*tt/tt[-1])**2*0.6
    k=mk(0.08); kt=np.arange(k)/SR; place(y,np.sin(2*np.pi*2400*kt)*np.exp(-kt*80)*0.15,mk(0.4))
    return y
def bronze_mat():   # la cloche sans battant posée dans les mains : un contact sourd, étouffé par la paume, aucune résonance
    n=mk(0.25); tt=np.arange(n)/SR
    return (burst(n,hi=700)*np.exp(-tt*40)+sum(np.sin(2*np.pi*f*tt)*np.exp(-tt*60) for f in (310,770)))*0.6
def pas_tobie():    # le pas de terre tassée de l'étape 1 (generer_bruitages_etape_01.pas_terre)
    a=mk(0.07); b=mk(0.18); y=np.zeros(mk(0.25))
    place(y,fftfilt(rng.standard_normal(a),hi=400)*np.exp(-np.arange(a)/SR*55),0)
    place(y,fftfilt(rng.standard_normal(b),lo=800,hi=4000)*np.exp(-np.arange(b)/SR*30)*0.3,mk(0.02))
    return y
def fin_d():   # son propre hasard (graine 1924), puis les tirages de l'ancienne fin-d : fin-e reste identique
    global rng
    principal=rng; rng=np.random.default_rng(1924)
    try: y=_fin_d()
    finally: rng=principal
    _tirages_fin_d_v1()
    return y
def _fin_d():
    L=mk(34); t=np.arange(L)/SR
    def souffle(b): return 1.0 if b<2 else max(0.25,1.0-(b-1)*0.18)     # par mesure : l'air manque peu à peu
    hm=np.zeros(L); mel=np.zeros(L); arret=int(BRISE/BT_D)
    for b,acc in enumerate(ACC):
        if b*4*BT_D>=BRISE: break
        n=mk(min(4*BT_D+0.4,BRISE-b*4*BT_D)); place(hm,harmonium_acc(acc,n/SR,souffle=souffle(b))[:n],mk(b*4*BT_D))
    for i,st in enumerate(MEL[:arret+1]):
        if st is None: continue
        d=1
        while i+d<len(MEL) and MEL[i+d] is None: d+=1
        dur=min(d*BT_D,BRISE-i*BT_D)
        if dur<=0.05: break
        n=mk(dur); tt=np.arange(n)/SR; f=D3*2*2**(st/12)
        derniere=(i+d)*BT_D>=BRISE
        if derniere: f=f*(1-0.03*np.clip(tt/dur,0,1))             # la dernière note s'affaisse : le soufflet est vide
        ph=2*np.pi*np.cumsum(np.full(n,f) if np.isscalar(f) else f)/SR
        y=sum(np.sin(k*ph)/k**1.2 for k in range(1,10))*env_ar(n,0.08,0.02 if derniere else 0.12)*souffle(i//4)
        place(mel,y,mk(i*BT_D))
    a=mk(BRISE); hm[a:]=0; mel[a:]=0
    musique=nrm(hm)*0.32+nrm(fftfilt(mel,hi=2500))*0.6
    n=mk(1.2); place(musique,burst(n,lo=200,hi=900)*np.linspace(1,0,n)**2*0.3,a)    # le soufflet vide
    musique=reverb(musique,2.5,0.4,seed=74,circ=False)[:L]
    gestes=np.zeros(L)
    for tp in PLIS: place(gestes,pli_pose(),mk(tp))
    place(gestes,cuir(),mk(SACOCHE)); place(gestes,bronze_mat(),mk(CLOCHE_MUETTE)); place(gestes,pli_pose()*0.8,mk(ORDRE))
    pas=np.zeros(L); tp=PAS[0]; k=0
    while tp<=PAS[1]+1e-6:
        place(pas,pas_tobie()*(0.9 if k%2 else 1.0)*np.clip((PAS[1]+1.5-tp)/3.0,0.15,1),mk(tp)); k+=1; tp=PAS[0]+k*PAS[2]   # il s'éloigne
    gestes=reverb(gestes,0.8,0.25,seed=92,circ=False)[:L]; pas=reverb(pas,1.2,0.3,seed=93,circ=False)[:L]
    m=musique+nrm(gestes)*0.35+nrm(pas)*0.8
    m*=np.clip((33.5-t)/3.0,0,1)**2
    return stereo(m,0.011)
def _tirages_fin_d_v1():   # l'ancienne fin-d (45 s, avant la ciné), rejouée pour ses seuls tirages ; le résultat est jeté
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
