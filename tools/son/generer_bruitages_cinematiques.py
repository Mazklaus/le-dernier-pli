# Bruitages des gestes et des cinématiques courtes (directive du Game Director, 15/11) :
# https://claude.ai/artifact/EVvDNH3RZJJj7sEukPdD5a
# Mono 44,1 kHz, trois variantes par geste, crête 0,75 comme les bruitages de l'étape 1.
# Règles : pas de jump scare, que des fausses notes ; aucune cloche ne sonne (cloche_souffle n'est
# que la respiration de la grande cloche, sans attaque) ; ce qui est dur reste hors champ.
# Usage : python3 generer_bruitages_cinematiques.py <repo>/assets/audio
import numpy as np, scipy.io.wavfile as wf, sys, os
SR=44100; D2=73.42; OUT=sys.argv[1]
rng=np.random.default_rng(1922)
def mk(s): return int(s*SR)
def fftfilt(x,lo=None,hi=None,order=2):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); g=np.ones_like(f)
    if hi: g/=np.sqrt(1+(f/hi)**(2*order))
    if lo: g/=np.sqrt(1+(lo/np.maximum(f,1e-3))**(2*order))
    return np.fft.irfft(X*g,len(x))
def burst(n,lo=None,hi=None): return fftfilt(rng.standard_normal(n+mk(0.05)),lo=lo,hi=hi)[:n]
def dec(n,k): return np.exp(-np.arange(n)/SR*k)
def at(buf,ev,t):
    p=mk(t); n=min(len(ev),len(buf)-p)
    if n>0: buf[p:p+n]+=ev[:n]
def reverb(x,sec,wet,seed):
    r=np.random.default_rng(seed); n=mk(sec); x=np.pad(x,(0,n)); L=len(x)
    ir=fftfilt(np.pad(r.standard_normal(n)*np.exp(-6.9*np.arange(n)/n),(0,L-n)),hi=4000)
    y=np.fft.irfft(np.fft.rfft(x)*np.fft.rfft(ir),L); y*=np.std(x)/(np.std(y)+1e-9)
    return (1-wet)*x+wet*y
def fin(x,peak=0.75):
    x=x/(np.abs(x).max()+1e-9)*peak; f=mk(0.02); x[-f:]*=np.linspace(1,0,f)
    nz=np.nonzero(np.abs(x)>1e-4)[0]; return x[:nz[-1]+1] if len(nz) else x
def save(base,fn,peak=0.75):
    for i in range(3):
        x=fin(fn(i),peak); wf.write(os.path.join(OUT,f"{base}_{i+1:02d}.wav"),SR,(x*32767).astype(np.int16))
    print(base)
def froisse(d,lo=1200,hi=7000,grains=40):   # papier, toile : grains serrés
    n=mk(d); y=np.zeros(n)
    for _ in range(int(grains*d)):
        k=mk(rng.uniform(0.004,0.02)); at(y,burst(k,lo=lo,hi=hi)*np.hanning(k)*rng.uniform(0.2,1),rng.uniform(0,d-0.03))
    return y
def grince(d,f0,f1):
    n=mk(d); tt=np.arange(n)/SR; f=np.linspace(f0,f1,n)
    y=np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*(np.sin(2*np.pi*rng.uniform(20,40)*tt)>0.3)
    return fftfilt(y,lo=150,hi=2500)*np.hanning(n)

# --- Étape 1 ---
def pli_tendre(i):      # le pli passe de la main de Lamarre à la poitrine de Tobie : cuir, papier, drap
    y=np.zeros(mk(1.4)); at(y,froisse(0.35,800,5000,60)*0.6,0.05)
    at(y,froisse(0.5,300,2500,50)*0.8,0.55+0.05*i)               # glissé sous la vareuse
    k=mk(0.08); at(y,burst(k,hi=600)*dec(k,40)*0.5,1.05)            # la main qui le plaque contre la poitrine
    return y
def couverture_tomber(i):  # la couverture anti-gaz retombe derrière Tobie : un rideau lourd, mouillé
    n=mk(1.1); y=burst(n,lo=80,hi=1200)*np.concatenate([np.linspace(0,1,mk(0.25))**2,np.exp(-np.arange(n-mk(0.25))/SR*4)])
    k=mk(0.15); at(y,burst(k,hi=400)*dec(k,25)*1.5,0.3+0.04*i); return y
def parapet_franchir(i):   # les sacs de sable sous les mains, la terre qui coule, puis plus rien
    y=np.zeros(mk(1.6))
    for t in (0.0,0.35+0.03*i): k=mk(0.18); at(y,burst(k,lo=150,hi=1500)*dec(k,18),t)
    at(y,burst(mk(0.9),lo=600,hi=5000)*(rng.random(mk(0.9))>0.85)*np.linspace(1,0,mk(0.9))*0.5,0.5)
    return y
# --- Étape 2 ---
def mort_bras(i):       # le bras raide du Mort se lève d'un coup : cuir gelé, os, un fil de fer qui vibre
    y=np.zeros(mk(1.5)); at(y,grince(0.25,220+30*i,160)*0.9,0.0)
    k=mk(0.05); at(y,burst(k,lo=500,hi=4000)*dec(k,60),0.24)
    k=mk(1.2); tt=np.arange(k)/SR; f=rng.uniform(700,900)
    at(y,(np.sin(2*np.pi*f*tt)+0.4*np.sin(2*np.pi*f*2.03*tt))*dec(k,4)*0.35,0.25)   # le fil, un peu faux
    return y
def terre_ebouler(i):   # la terre s'éboule derrière Tobie : petites mottes puis une coulée, assez court
    y=np.zeros(mk(2.2))
    for _ in range(14): k=mk(0.06); at(y,burst(k,lo=100,hi=900)*dec(k,35)*rng.uniform(0.3,1),rng.uniform(0,0.6))
    k=mk(1.5); at(y,burst(k,lo=60,hi=700)*np.sin(np.pi*np.arange(k)/k)**1.5*1.4,0.3+0.05*i)
    return y
# --- Étape 3 ---
def corde_tirer(i):     # le sonneur tire la corde coupée : le chanvre glisse, la poutre grince, aucune cloche
    y=np.zeros(mk(1.8)); at(y,froisse(0.5,400,3000,70)*0.7,0.0)
    at(y,grince(0.6,110+10*i,95)*0.6,0.35)
    k=mk(0.2); at(y,burst(k,hi=250)*dec(k,20)*0.4,1.1)               # le bout de corde retombe contre le bois
    return reverb(y,1.5,0.35,seed=30+i)
# --- Étape 4 ---
def aiguille_coudre(i): # la greffe, hors champ : le fil qui passe, un petit choc de métal, un souffle retenu
    y=np.zeros(mk(2.4))
    for p in range(3):
        n=mk(0.35); tt=np.arange(n)/SR; f=np.linspace(1800,2600,n)
        fil=np.sin(2*np.pi*np.cumsum(f)/SR)*(0.5+0.5*np.sign(np.sin(2*np.pi*90*tt)))*np.hanning(n)
        at(y,fftfilt(fil,lo=1000,hi=5000)*0.25,0.2+p*0.7+0.03*i)
    k=mk(0.4); tk=np.arange(k)/SR; f=rng.uniform(3500,4200)
    at(y,(np.sin(2*np.pi*f*tk)+0.5*np.sin(2*np.pi*f*2.7*tk))*dec(k,14)*0.3,1.9)
    k=mk(1.0); at(y,burst(k,lo=200,hi=1000)*np.sin(np.pi*np.arange(k)/k)**2*0.25,0.0)   # le souffle retenu
    return y
# --- Étape 5 ---
def lame_entailler(i):  # la lame mord dans le bois de la croix
    y=np.zeros(mk(0.7)); k=mk(0.03); at(y,burst(k,lo=1500,hi=8000)*dec(k,80),0.0)
    k=mk(0.35); tt=np.arange(k)/SR; at(y,burst(k,lo=600,hi=4000)*np.sign(np.sin(2*np.pi*(40+8*i)*tt)).clip(0)*dec(k,6)*0.6,0.03)
    k=mk(0.12); at(y,burst(k,hi=500)*dec(k,30)*0.4,0.0); return y
def lame_graver(i):     # une lettre gravée : trois ou quatre traits courts
    y=np.zeros(mk(1.2))
    for s in range(3+i%2):
        k=mk(rng.uniform(0.12,0.22)); tt=np.arange(k)/SR
        at(y,burst(k,lo=1200,hi=6000)*(0.5+0.5*np.sign(np.sin(2*np.pi*rng.uniform(50,80)*tt)))*np.hanning(k),0.05+s*0.27)
    return y
# --- Étape 6 ---
def sol_ceder(i):       # le sol cède : un craquement sourd, puis la glissade dans le noir
    y=np.zeros(mk(2.6)); k=mk(0.4); tk=np.arange(k)/SR
    at(y,burst(k,hi=300)*dec(k,10)*1.5+np.sin(2*np.pi*45*tk)*dec(k,8),0.0)
    k=mk(1.8); at(y,burst(k,lo=100,hi=1500)*np.linspace(1,0.2,k)*0.8,0.3+0.05*i)
    r=mk(0.15); y[:r]*=np.linspace(0,1,r)
    return reverb(y,1.8,0.4,seed=60+i)
def lanterne_rouler(i): # la lanterne roule sur la pierre, s'arrête, sa vitre tinte une fois
    y=np.zeros(mk(2.0))
    for c in range(9):
        k=mk(0.05); at(y,burst(k,lo=800,hi=5000)*dec(k,50)*(1-c/10),c*0.13*(1+0.1*c))
    k=mk(0.6); tk=np.arange(k)/SR; f=2900+150*i; at(y,np.sin(2*np.pi*f*tk)*dec(k,9)*0.3,1.45)
    return y
def lampe_approcher(i): # la lampe d'Éloi : le chuintement de la flamme qui grandit en approchant
    n=mk(2.5); y=fftfilt(rng.standard_normal(n),lo=300,hi=2000)*np.linspace(0.05,1,n)**2
    y*=1+0.3*np.sin(2*np.pi*rng.uniform(5,8)*np.arange(n)/SR); return y
def voute_effondrer(i): # la voûte tombe derrière Tobie : grondement, pierres, poussière, puis le silence
    y=np.zeros(mk(4.5)); k=mk(2.5); tk=np.arange(k)/SR
    at(y,burst(k,hi=200)*np.exp(-tk*1.5)*2+np.sin(2*np.pi*35*tk)*np.exp(-tk*2),0.0)
    for _ in range(30): kk=mk(0.08); at(y,burst(kk,lo=200,hi=2500)*dec(kk,30)*rng.uniform(0.2,0.8),rng.uniform(0.1,1.8))
    at(y,burst(mk(2),lo=2000,hi=8000)*np.linspace(0.3,0,mk(2))*0.2,1.5)   # la poussière qui retombe
    r=mk(0.5); y[:r]*=np.linspace(0,1,r)**2        # le grondement monte d'abord : pas de choc soudain
    return reverb(y,2.5,0.45,seed=70+i)
# --- Étape 7 ---
def cloche_souffle(i):  # la grande cloche respire : un bourdon qui enfle sans attaque et retombe. Elle ne sonne pas.
    n=mk(6.0); tt=np.arange(n)/SR; f=D2*(1+0.004*i)
    y=sum(a*np.sin(2*np.pi*f*r*tt+rng.uniform(0,6)) for r,a in ((0.5,1),(1,0.8),(1.2,0.4),(1.5,0.3),(2,0.25)))
    return y*np.sin(np.pi*tt/tt[-1])**3
def greffe_fausse_note(i):   # e4_greffe, à la coupe au noir : un ré fredonné bouche cousue, un quart de ton trop bas,
    n=mk(0.9); tt=np.arange(n)/SR    # qui enfle vite ; le fil qui tire le coupe à 0,6 s, au retour de l'image
    f=146.83*2**((-0.5+0.03*i)/12)*(1+0.004*np.sin(2*np.pi*4.6*tt))
    ph=np.cumsum(f)/SR; y=np.zeros(n)
    for k in range(1,24):
        if 146.83*k>4000: break
        w=np.exp(-((146.83*k-250)/120)**2)+0.3*np.exp(-((146.83*k-2200)/300)**2)+0.02/k
        y+=w*np.sin(2*np.pi*k*ph+rng.uniform(0,6))
    y*=np.clip(tt/0.2,0,1)**1.5*np.clip((0.6-tt)/0.06,0,1)
    k=mk(0.3); t2=np.arange(k)/SR; fl=np.linspace(1800,2600,k)
    at(y,fftfilt(np.sin(2*np.pi*np.cumsum(fl)/SR)*(0.5+0.5*np.sign(np.sin(2*np.pi*90*t2)))*np.hanning(k),lo=1000,hi=5000)*0.25,0.42)
    return y
def priere_murmurer(i):  # e3_priere_champs (12 s, la nuit, PR #233 de la DA) : le village à genoux en cercle, front contre terre.
    # P1 0-4 s de profil : des dos qui respirent (un souffle par seconde, chacun le sien), les cierges qui vacillent ;
    # P2 4-8 s en plongée : plus loin ; P3 8-12 s poussée vers la place vide, le vent couche les flammes à 9,5 s.
    # Dessous, le Cantique fredonné vers le sol, bouche fermée, « comme pour quelqu'un qui dort ». Aucune cloche.
    L=mk(12.0); t=np.arange(L)/SR; D3=146.83
    plan=np.where(t<4.0,1.0,np.where(t<8.0,0.55,0.35))                       # coupes sèches à 4 et 8 s
    souffles=np.zeros(L)
    for _ in range(14):                                                        # quatorze dos, chacun son rythme
        p=rng.uniform(0.85,1.2); t0=rng.uniform(0,p)
        while t0<12.0:
            n=mk(rng.uniform(0.5,0.75)); tt=np.arange(n)/SR
            at(souffles,burst(n,lo=350,hi=2200)*np.sin(np.pi*tt/tt[-1])**2*rng.uniform(0.4,1),t0); t0+=p*rng.uniform(0.9,1.1)
    fredon=np.zeros(L); air=[0,3,5,7,5,3,2,0]                                # la première phrase, lente, qui ne monte pas
    for v in range(6):
        f0=D3*(0.5 if v%2 else 1.0)*2**(rng.uniform(-8,8)/1200)
        for k,st in enumerate(air):
            d=1.5; n=mk(d*1.1); tt=np.arange(n)/SR; f=f0*2**(st/12)*(1+0.004*np.sin(2*np.pi*rng.uniform(4,5.5)*tt))
            ph=2*np.pi*np.cumsum(f)/SR
            y=sum(np.exp(-((f0*2**(st/12)*h-250)/150)**2)*np.sin(h*ph)/h for h in range(1,12))
            at(fredon,y*np.sin(np.pi*tt/tt[-1])**1.5,k*d+0.1*v+rng.normal(0,0.05))
    fredon=fftfilt(fredon,hi=900)
    flammes=fftfilt(burst(L,hi=300),hi=300)*(0.6+0.4*np.sin(2*np.pi*0.7*t+i))
    for _ in range(25): k=mk(0.006); at(flammes,burst(k,lo=2000,hi=8000)*np.hanning(k)*rng.uniform(1,3),rng.uniform(0,12))   # mèches qui crépitent
    vent=np.clip((t-9.3)/0.4,0,1)*np.clip((11.2-t)/1.2,0,1)
    rafale=fftfilt(burst(L,lo=150,hi=1600),lo=150,hi=1600)*vent**1.5
    claque=np.zeros(L)
    for k in range(8): n=mk(0.08); at(claque,burst(n,hi=600)*np.hanning(n)*(1-k/10),9.55+k*0.09)                 # les flammes couchées qui battent
    m=fftfilt(souffles,hi=2500)*plan*0.5+fredon*0.6*(0.8+0.2*(t>4.0))+flammes*0.15*plan+rafale*0.9+claque*0.45
    m=reverb(m,1.6,0.3,seed=301+i)[:L]
    return m*np.clip((12.0-t)/0.5,0,1)
def archet_noce(f,dur,faux=0.0):   # le violon de la noce (generer_ambiance_village_cloches_muettes.archet)
    n=mk(dur); tt=np.arange(n)/SR; fv=f*2**(faux/12)*(1+0.006*np.sin(2*np.pi*5.5*tt)*np.clip(tt/0.15,0,1))
    ph=np.cumsum(fv)/SR; y=sum(np.sin(2*np.pi*k*ph)/k*(1.3 if k in (3,4) else 1) for k in range(1,18))
    a=max(1,mk(0.02)); r=max(1,mk(0.05)); e=np.ones(n); e[:a]=np.linspace(0,1,a); e[-r:]*=np.linspace(1,0,r)
    return fftfilt(np.pad(y,(0,mk(0.05))),lo=250,hi=4500)[:n]*e
def danse_tourner(i):   # e3_danse_rose (10 s, le jour sur la place, PR #235 de la DA) : la noce, en ré majeur,
    # la tierce du violon un quart de ton trop haute comme partout dans la noce. Pas de voix (aucun doublage) :
    # le rire de Rose, c'est le violon qui le fait.
    #   P1 0-3 s : le violon reprend, un coup d'archet toutes les 0,3 s ; Rose se tourne (1,8 s) : la jupe.
    #   P2 3-7 s : un seul tour à deux, la vielle et le tambourin, les rubans de papier ; il trébuche (5,2 s).
    #   P3 7-10 s : elle rit (7,0 s), la tête en arrière (7,7 et 8,9 s) : le violon éclate en traits et en trilles.
    L=mk(10.0); t=np.arange(L)/SR; D4=293.66
    maj=[0,2,4,7,7,4,2,0,0,2,4,5,7,7,9,7, 11,9,7,5,4,5,7,4, 2,0,2,-1,0,0]     # le Cantique mis en fête
    vio=np.zeros(L); k=0; tn=0.0
    while tn<7.0-1e-6:
        st=maj[k%len(maj)]; dur=0.3
        faux=0.5 if st==4 else 0.0
        if 5.2<=tn<5.5: faux+=-0.8                                    # il trébuche : l'archet dérape
        at(vio,archet_noce(D4*2**(st/12),dur*0.98,faux)*(0.8 if k%3 else 1.0),tn); k+=1; tn=k*0.3
    for t0,traits in ((7.0,[0,2,4,7,9,11,12,14]),(7.7,[12,14,12,14,12]),(8.9,[12,14,12,14,12,11,12])):   # le rire
        for j,st in enumerate(traits):
            faux=0.5 if st%12==4 else 0.0; at(vio,archet_noce(D4*2**(st/12),0.11,faux)*0.9,t0+j*0.075)
    at(vio,archet_noce(D4*2,1.2)*np.linspace(1,0,mk(1.2)),9.45)                      # le ré d'en haut, qui s'en va
    vielle=sum(np.sin(2*np.pi*k2*73.42*t)/k2 for k2 in range(1,25))+0.6*sum(np.sin(2*np.pi*k2*110.13*t)/k2 for k2 in range(1,25))
    vielle=fftfilt(vielle,hi=2500)*np.clip((t-0.9)/1.2,0,1)*(1+0.15*np.sign(np.sin(2*np.pi*t/0.9)))
    tamb=np.zeros(L)
    for b in range(int(3.0/0.9),int(9.9/0.9)+1):
        kk=mk(0.15); tk=np.arange(kk)/SR; at(tamb,np.sin(2*np.pi*90*tk)*np.exp(-tk*25)+burst(kk,lo=3000,hi=9000)*np.exp(-tk*30)*0.4,b*0.9)
    gestes=np.zeros(L)
    n=mk(0.6); tt=np.arange(n)/SR; at(gestes,fftfilt(burst(n,lo=400,hi=3000),lo=400,hi=3000)*np.sin(np.pi*tt/tt[-1])**2*0.5,1.65)   # la jupe qui tourne
    rubans=froisse(4.0,1500,7000,60)*np.sin(np.pi*np.arange(mk(4.0))/mk(4.0))**0.5
    at(gestes,rubans*0.5,3.0)
    kk=mk(0.12); at(gestes,burst(kk,hi=500)*dec(kk,35)*1.2,5.2); at(gestes,froisse(0.35,800,4000,50)*0.8,5.22)  # le pied dans la traîne
    m=fftfilt(vio,hi=6000)*0.55+vielle/np.abs(vielle).max()*0.25+tamb*0.25+gestes*0.6
    m=reverb(m,1.0,0.2,seed=311+i)[:L]
    return m*np.clip((10.0-t)/0.4,0,1)
def barbeles_foncer(i):   # e2_barbeles_foncer (7 s, le noir et le brouillard, PR #237 de la DA) : Tobie fonce dans les fils.
    #   0-2,5 s : la course dans la boue, un pas toutes les 0,2 s ; il touche les fils à 2,5 s.
    #   2,5-5 s : gros plan, tendu, presque muet : les fils vibrent encore, la pointe dans l'étoffe ; la goutte perle (3,3 s),
    #             grossit (4,1 s) sans un bruit ; il tire d'un coup (4,5-4,9 s), l'étoffe se déchire à 4,9 s.
    #   5-7 s : il repart, s'éloigne et pâlit dans le brouillard (6-7 s) ; le lambeau bat au vent toutes les 0,3 s.
    # En fond, les fils fredonnent l'air de Jacquot (étape 2), avec ses fausses notes.
    L=mk(7.0); t=np.arange(L)/SR; D4=293.66
    def pas_boue():
        n=mk(0.3); tt=np.arange(n)/SR
        y=fftfilt(rng.standard_normal(n),hi=500)*np.exp(-tt*60)*1.5
        y+=fftfilt(rng.standard_normal(n),lo=300,hi=1600)*np.sin(np.pi*tt/tt[-1])**3*0.5          # la boue qui aspire
        return y
    course=np.zeros(L)
    for k in range(13): at(course,pas_boue()*(0.85 if k%2 else 1.0),0.05+k*0.2)                        # 0 à 2,5 s
    for k in range(10): at(course,pas_boue()*(0.85 if k%2 else 1.0)*max(0.05,1-max(0,5.1+k*0.2-6.0)),5.1+k*0.2)   # il s'éloigne
    souffle=np.zeros(L)
    for k in range(6): n=mk(0.3); tt=np.arange(n)/SR; at(souffle,burst(n,lo=500,hi=2500)*np.sin(np.pi*tt/tt[-1])**2*0.3,0.1+k*0.4)
    # le choc dans les fils : le fer qui claque, les fils voisins qui répondent, le tissu qui accroche
    choc=np.zeros(L); n=mk(1.6); tt=np.arange(n)/SR
    for f,a in ((1180,1),(1630,0.6),(2410,0.4),(890,0.5)):
        choc[mk(2.5):mk(2.5)+n]+=a*np.sin(2*np.pi*f*tt+0.4*np.sin(2*np.pi*7*tt))*np.exp(-tt*2.2)
    k=mk(0.08); at(choc,burst(k,lo=1500,hi=8000)*dec(k,50)*1.5,2.5); at(choc,froisse(0.2,800,5000,60),2.52)
    # 4,5-4,9 s : il tire ; le fil se tend et grince, puis l'étoffe se déchire
    tire=np.zeros(L); n=mk(0.4); tt=np.arange(n)/SR; f=np.linspace(700,1100,n)
    at(tire,fftfilt(np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*(rng.random(n)<0.3),lo=600,hi=4000)*np.linspace(0.2,1,n)*0.3,4.5)
    n=mk(0.25); tt=np.arange(n)/SR
    dechire=fftfilt(rng.standard_normal(n)*(rng.random(n)<0.5),lo=1200,hi=7000)*np.exp(-tt*10)*1.2
    at(tire,dechire,4.9)
    k=mk(1.2); kt=np.arange(k)/SR; at(tire,np.sin(2*np.pi*1180*kt)*np.exp(-kt*3)*0.5,4.9)                # le fil relâché qui chante
    lambeau=np.zeros(L)
    for k in range(7):
        n=mk(0.12); tt=np.arange(n)/SR; at(lambeau,fftfilt(rng.standard_normal(n),lo=300,hi=2500)*np.hanning(n)*0.5,5.0+k*0.3)
    # les fils qui fredonnent l'air de Jacquot, loin, sous tout le reste
    fils=np.zeros(L); air=[0,3,5,7,7,5,3,2,0,2,3,5]; fausses={2:0.45}
    for k,st in enumerate(air):
        n=mk(0.65); tt=np.arange(n)/SR; f0=D4*2*2**((st+fausses.get(k,0))/12)
        y=sum(a*np.sin(2*np.pi*f0*r*tt) for r,a in ((1,1),(2.013,0.45),(3.04,0.25)))*np.sin(np.pi*tt/tt[-1])
        at(fils,y,k*0.58)
    brouillard=fftfilt(burst(L,lo=40,hi=350),lo=40,hi=350)
    pale=np.clip((7.0-t)/1.0,0.15,1)                                                                       # il pâlit dans le brouillard
    calme=np.where((t>2.7)&(t<4.5),0.35,1.0)                                                              # le gros plan retient tout
    m=course*0.5+souffle*calme+choc*0.35+tire*0.6+lambeau*0.35+fils*0.06*calme+brouillard*0.15
    m=reverb(m*pale,1.2,0.3,seed=321+i)[:L]
    return m*np.clip((7.0-t)/0.3,0,1)
def crypte_descendre(i):   # e4_descente_crypte (10 s, PR #241 de la DA) : l'escalier en vis qui descend vers la crypte.
    #   0-4 s : la vis tourne et s'enfonce ; un pas sur la pierre toutes les 0,25 s, la cage résonne de plus en plus.
    #   4-8 s : de côté, neuf marches de 4,2 à 7,6 s ; la lumière d'en haut rétrécit (5,2 / 6,3 / 7,3 s) : l'air de
    #           l'hôpital s'étouffe par paliers, et disparaît quand elle s'éteint (7,8 s).
    #   8-10 s : le noir ; presque rien : la cire froide qui craque une fois, la buée des saints qu'on ne voit pas encore.
    L=mk(10.0); t=np.arange(L)/SR
    def pas_pierre(force=1.0):
        n=mk(0.25); tt=np.arange(n)/SR
        y=fftfilt(rng.standard_normal(n),hi=700)*np.exp(-tt*50)*1.2                        # le talon sur la marche
        y+=fftfilt(rng.standard_normal(n),lo=1500,hi=6000)*np.exp(-tt*35)*0.25*(rng.random(n)<0.4)   # le grain de la pierre
        return y*force
    pas=np.zeros(L)
    for k in range(16): at(pas,pas_pierre(0.8 if k%2 else 0.9),0.05+k*0.25)
    for k in range(9): at(pas,pas_pierre(1.0 if k%2 else 0.9),4.2+k*0.425)
    pas=fftfilt(pas,hi=4000)
    profond=np.clip(t/8.0,0,1)                                                               # la cage de plus en plus profonde
    sec=pas*(1-0.5*profond); humide=reverb(pas,2.8,1.0,seed=331+i)[:L]*(0.25+0.6*profond)
    en_haut=np.ones(L)                                                                        # l'air de l'hôpital, par la porte
    for tc,g in ((5.2,0.6),(6.3,0.35),(7.3,0.15),(7.8,0.0)): en_haut[t>=tc]=g
    en_haut=np.convolve(en_haut,np.ones(mk(0.15))/mk(0.15),mode="same")
    air=fftfilt(burst(L,lo=200,hi=2500),lo=200,hi=2500)*0.12
    for _ in range(8):                                                                        # des voix lointaines, sans mots
        n=mk(rng.uniform(0.3,0.6)); tt=np.arange(n)/SR; f=rng.uniform(110,180)
        at(air,sum(np.sin(2*np.pi*f*h*tt)*np.exp(-((f*h-500)/250)**2) for h in range(1,10))*np.hanning(n)*0.03,rng.uniform(0,7.5))
    air=fftfilt(air,hi=1200)*en_haut*(1-0.6*np.clip(t/4.0,0,1))
    noir=np.zeros(L)
    n=mk(1.4); tt=np.arange(n)/SR; at(noir,fftfilt(burst(n,lo=250,hi=1200),lo=250,hi=1200)*np.sin(np.pi*tt/tt[-1])**2*0.06,8.3)   # la buée des saints
    noir=reverb(noir,3.0,0.35,seed=341+i)[:L]
    k=mk(0.05); at(noir,burst(k,lo=2500,hi=7000)*np.exp(-np.arange(k)/SR*80)*0.05,8.6)       # la cire froide, sèche
    m=sec*0.6+humide*0.5+air+noir
    return m*np.clip((10.0-t)/0.3,0,1)
def village_tablee(i):   # e6_village_sous_terre (12 s, PR #243 de la DA) : le village sous l'argile, la tablée.
    #   0-4 s : les toits dans l'argile, les fumées qui montent : la caverne, les feux, une goutte.
    #   4-8 s : la longue table ; chaque convive frappe son écuelle toutes les 0,6 s, trois rangs décalés de 0,2 s :
    #           un coup toutes les 0,2 s, et les écuelles jouent le Cantique à l'envers, comme la noce de la tablée.
    #   8-12 s : la chaise vide, l'écuelle qui fume : les cuillères se taisent net ; il reste la vapeur et la caverne.
    L=mk(12.0); t=np.arange(L)/SR; D4=293.66
    caverne=fftfilt(burst(L,lo=30,hi=180),lo=30,hi=180)*0.5+fftfilt(burst(L,lo=200,hi=900),lo=200,hi=900)*0.06
    feux=np.zeros(L)
    for _ in range(40): k=mk(0.01); at(feux,burst(k,lo=1500,hi=6000)*np.hanning(k)*rng.uniform(0.3,1),rng.uniform(0,8))   # les braises
    feux+=fftfilt(burst(L,lo=300,hi=1500),lo=300,hi=1500)*0.15*np.clip((8.0-t)/0.5,0.2,1)
    k=mk(0.4); kt=np.arange(k)/SR
    for tg in (1.3,3.4): at(feux,np.sin(2*np.pi*(900+2500*np.exp(-kt*40))*kt)*np.exp(-kt*25)*0.3,tg)        # une goutte d'argile
    air=[0,-2,2,0,2,3,7,5,3,7,5,3,5,7,9,10]                                                         # le Cantique à l'envers
    cuilleres=np.zeros(L); k=0; tc=4.0
    while tc<8.0-1e-6:
        st=air[k%len(air)]; f=D4*2*2**(st/12)*2**(rng.uniform(-15,15)/1200)
        n=mk(0.18); tt=np.arange(n)/SR
        y=sum(a*np.sin(2*np.pi*f*r*tt)*np.exp(-tt*(25+r*15)) for r,a in ((1,1),(2.7,0.35),(5.1,0.12)))    # l'écuelle de terre
        y+=burst(n,lo=2000,hi=7000)*np.exp(-tt*120)*0.4                                             # le bois de la cuillère
        at(cuilleres,y*(1.0 if k%3==0 else 0.8),tc+rng.normal(0,0.008)); k+=1; tc=4.0+k*0.2
    vapeur=fftfilt(burst(L,lo=1500,hi=6000),lo=1500,hi=6000)*np.clip((t-8.0)/0.6,0,1)*(0.6+0.4*np.sin(2*np.pi*0.35*t))*0.2
    m=caverne*0.7+feux*0.7+cuilleres*0.55+vapeur
    m=reverb(m,2.2,0.35,seed=351+i)[:L]
    return m*np.clip(t/0.3,0,1)*np.clip((12.0-t)/0.5,0,1)
def porte_scellee(i):   # e6_porte_scellee (10 s, PR #246 de la DA) : la porte de cire noire, au seuil.
    #   0-3 s : contre-plongée, panoramique lent vers l'arc : l'air du seuil monte, la cire froide craque une fois.
    #   3-7 s : devant la porte ; Tobie respire (une image toutes les 0,5 s : inspire, expire). Éloi se penche (3,6 s),
    #           le bocal touche la pierre (4,4 s : un choc de verre étouffé, l'eau qui bouge), il se redresse (4,7 s).
    #   7-10 s : Éloi recule sans se retourner, six pas de 7,2 à 9,4 s qui s'éloignent dans l'ombre.
    #   Rien derrière la porte : aucun bourdon, aucun souffle de la Mère-Cloche, pas de note tenue.
    L=mk(10.0); t=np.arange(L)/SR
    air=fftfilt(burst(L,lo=60,hi=400),lo=60,hi=400)*0.5+fftfilt(burst(L,lo=500,hi=2000),lo=500,hi=2000)*0.05
    air*=0.5+0.5*np.clip((t-0.2)/2.8,0,1)                                                      # le seuil s'ouvre vers l'arc
    cire=np.zeros(L)
    for tc,g in ((1.7,0.06),(2.75,0.04)):
        k=mk(0.06); at(cire,burst(k,lo=1800,hi=6000)*np.exp(-np.arange(k)/SR*70)*g,tc)       # la cire qui se contracte
    souffle=np.zeros(L)                                                                         # Tobie : inspire puis expire
    for k in range(8):
        n=mk(0.5); tt=np.arange(n)/SR; inspire=k%2==0
        env=np.sin(np.pi*tt/tt[-1])**(1.5 if inspire else 2.5)
        b=burst(n,lo=500 if inspire else 250,hi=3000 if inspire else 1500)
        at(souffle,b*env*(0.12 if inspire else 0.15),3.0+k*0.5)
    geste=np.zeros(L)
    at(geste,froisse(0.35,600,4000,45)*0.35,3.55)                                               # le manteau d'Éloi qui se plie
    at(geste,froisse(0.3,600,4000,40)*0.3,4.65)                                                 # et se déplie
    n=mk(0.5); tt=np.arange(n)/SR
    verre=fftfilt(rng.standard_normal(n),hi=900)*np.exp(-tt*60)*0.5                              # le cul du bocal sur la pierre
    verre+=sum(a*np.sin(2*np.pi*f*tt)*np.exp(-tt*k) for f,a,k in ((1730,0.12,45),(3110,0.06,60),(4470,0.03,80)))   # verre épais, étouffé
    at(geste,verre,4.4)
    n=mk(0.6); tt=np.arange(n)/SR
    eau=fftfilt(rng.standard_normal(n),lo=300,hi=1200)*(0.5+0.5*np.sin(2*np.pi*9*tt))*np.exp(-tt*6)*0.08   # l'eau du bocal qui bouge
    at(geste,eau,4.43)
    pas=np.zeros(L)
    for k in range(6):
        n=mk(0.3); tt=np.arange(n)/SR; g=0.9*(0.72**k)
        y=fftfilt(rng.standard_normal(n),hi=600-60*k)*np.exp(-tt*45)+burst(n,lo=1200,hi=4000)*np.exp(-tt*60)*0.15
        at(pas,y*g,7.2+k*0.44+rng.normal(0,0.02))
    pas=pas*0.5+reverb(pas,2.6,1.0,seed=361+i)[:L]*0.45                                          # il s'efface dans l'ombre
    m=air*0.6+cire+souffle+geste+pas
    m=reverb(m,2.4,0.3,seed=371+i)[:L]
    return m*np.clip(t/0.4,0,1)*np.clip((10.0-t)/0.6,0,1)
def pli_deplier(i):     # le pli se déplie : papier épais, plié depuis longtemps, qui résiste
    y=np.zeros(mk(1.6))
    for p in range(2): at(y,froisse(0.45,500,4000,45)*(0.8 if p else 1.0),0.05+p*0.6+0.04*i)
    k=mk(0.04); at(y,burst(k,lo=2000,hi=7000)*dec(k,70)*0.6,0.55)          # le pli qui cède
    return y

for base,fn in (("sfx_pli_tendre",pli_tendre),("sfx_couverture_tomber",couverture_tomber),("sfx_parapet_franchir",parapet_franchir),
                ("sfx_mort_bras",mort_bras),("sfx_terre_ebouler",terre_ebouler),("sfx_corde_tirer",corde_tirer),
                ("sfx_aiguille_coudre",aiguille_coudre),("sfx_lame_entailler",lame_entailler),("sfx_lame_graver",lame_graver),
                ("sfx_sol_ceder",sol_ceder),("sfx_lanterne_rouler",lanterne_rouler),("sfx_lampe_approcher",lampe_approcher),
                ("sfx_voute_effondrer",voute_effondrer),("sfx_pli_deplier",pli_deplier)):
    save(base,fn)
save("sfx_cloche_souffle",cloche_souffle,0.45)   # un fond, pas un événement
save("sfx_greffe_fausse-note",greffe_fausse_note,0.6)
save("sfx_priere_murmurer",priere_murmurer,0.6)   # un fond de 12 s pour toute la ciné, lancé à 0
save("sfx_danse_tourner",danse_tourner,0.6)    # 10 s pour toute la ciné, lancé à 0
save("sfx_barbeles_foncer",barbeles_foncer,0.6)    # 7 s pour toute la ciné, lancé à 0
save("sfx_crypte_descendre",crypte_descendre,0.6)    # 10 s pour toute la ciné, lancé à 0
save("sfx_village_tablee",village_tablee,0.6)    # 12 s pour toute la ciné, lancé à 0
save("sfx_porte_scellee",porte_scellee,0.6)    # 10 s pour toute la ciné, lancé à 0
