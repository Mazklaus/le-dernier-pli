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
