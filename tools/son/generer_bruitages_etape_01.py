# Bruitages et sons d'interface de l'étape 1 — procéduraux, graine fixe, WAV mono 16 bits.
import numpy as np, scipy.signal as ss, scipy.io.wavfile as wf, sys, os
SR=44100; rng=np.random.default_rng(1915); OUT=sys.argv[1]
def T(d): return np.arange(int(d*SR))/SR
def bp(x,lo,hi,o=2): return ss.sosfilt(ss.butter(o,[lo,hi],'band',fs=SR,output='sos'),x)
def lp(x,f,o=2): return ss.sosfilt(ss.butter(o,f,fs=SR,output='sos'),x)
def hp(x,f,o=2): return ss.sosfilt(ss.butter(o,f,'high',fs=SR,output='sos'),x)
def nz(d): return rng.standard_normal(int(d*SR))
def env(n,a,r):  # attaque/relâchement en secondes
    e=np.ones(n); a=max(1,int(a*SR)); r=max(1,int(r*SR)); e[:a]=np.linspace(0,1,a); e[-r:]*=np.linspace(1,0,r)**2; return e
def dec(d,k): return np.exp(-T(d)*k)
def pad(x,d): return np.concatenate([x,np.zeros(int(d*SR))])
def mix(*parts):  # (signal, décalage s)
    L=max(int(o*SR)+len(s) for s,o in parts); y=np.zeros(L)
    for s,o in parts: i=int(o*SR); y[i:i+len(s)]+=s
    return y
def room(x,sec=0.25,wet=0.15):
    n=int(sec*SR); ir=rng.standard_normal(n)*np.exp(-6.9*np.arange(n)/n); y=np.pad(ss.fftconvolve(x,ir),(0,1))[:len(x)+n]
    x=np.pad(x,(0,n)); y*=np.std(x)/(np.std(y)+1e-9); return (1-wet)*x+wet*y
def save(name,x,peak=0.8):
    x=x-np.mean(x); f=int(0.004*SR); x[-f:]*=np.linspace(1,0,f)
    x=x/(np.abs(x).max()+1e-9)*peak; wf.write(os.path.join(OUT,name+".wav"),SR,(x*32767).astype(np.int16))
# --- Pas ---
def pas_boue():
    d=0.45; heel=lp(nz(0.06),500)*dec(0.06,60)*1.5
    suck=bp(nz(0.3),300,1600)*np.sin(np.pi*T(0.3)/0.3)**3*0.6      # la boue aspire la semelle
    bub=np.zeros(int(0.3*SR))
    for _ in range(rng.integers(2,5)):
        k=int(0.05*SR); tt=T(0.05); b=np.sin(2*np.pi*rng.uniform(250,600)*(1+tt*10)*tt)*np.exp(-tt*70); i=rng.integers(0,len(bub)-k); bub[i:i+k]+=b*0.4
    return mix((heel,0),(suck+bub,0.08))
def pas_planche():
    thud=lp(nz(0.08),900)*dec(0.08,45); tt=T(0.25)
    plank=sum(np.sin(2*np.pi*f*tt)*np.exp(-tt*k) for f,k in ((rng.uniform(120,180),25),(rng.uniform(330,420),40)))*0.6
    squish=bp(nz(0.15),500,2500)*dec(0.15,25)*0.25
    return mix((thud,0),(plank,0.002),(squish,0.03))
def pas_terre():
    return mix((lp(nz(0.07),400)*dec(0.07,55),0),(bp(nz(0.18),800,4000)*dec(0.18,30)*0.3,0.02))  # sol tassé, grains qui roulent
def echelle():
    tt=T(0.5); metal=sum(a*np.sin(2*np.pi*f*tt)*np.exp(-tt*k) for f,a,k in ((rng.uniform(600,800),1,12),(rng.uniform(1700,2100),0.5,18),(rng.uniform(3100,3500),0.25,25)))
    grip=bp(nz(0.12),1000,5000)*dec(0.12,30)*0.5; wood=lp(nz(0.05),700)*dec(0.05,60)
    return mix((wood,0),(metal*0.35,0.003),(grip,0.15))
# --- Passages ---
def escalier(): return mix(*[(pas_terre()*(0.8-0.1*i),i*0.32) for i in range(4)])
def toile():  # rideau de toile de tente / bâche qu'on écarte
    d=0.7; x=bp(nz(d),400,5000)*(np.abs(lp(nz(d),12))*8).clip(0,1)*env(int(d*SR),0.08,0.3)
    return room(x,0.2,0.1)
# --- Lanterne ---
def allumer():
    strike=hp(nz(0.18),1500)*dec(0.18,14)*np.clip(T(0.18)*30,0,1)
    whoosh=bp(nz(0.6),150,1500)*env(int(0.6*SR),0.05,0.4)*0.7
    glass=sum(np.sin(2*np.pi*f*T(0.4))*np.exp(-T(0.4)*20) for f in (2900,4300))*0.08
    return mix((strike,0),(whoosh,0.12),(glass,0.55))
def eteindre():
    puff=bp(nz(0.35),200,2500)*env(int(0.35*SR),0.01,0.3); hiss=hp(nz(0.5),3000)*dec(0.5,8)*0.15
    tink=np.sin(2*np.pi*3600*T(0.3))*np.exp(-T(0.3)*25)*0.1
    return mix((puff,0),(hiss,0.1),(tink,0.35))
def remplir():  # huile versée
    d=1.0; x=np.zeros(int(d*SR))
    for _ in range(60):
        k=int(0.03*SR); tt=T(0.03); f=rng.uniform(500,1100)+400*(_/60)   # le son monte quand le réservoir se remplit
        i=rng.integers(0,len(x)-k); x[i:i+k]+=np.sin(2*np.pi*f*(1+tt*6)*tt)*np.exp(-tt*90)
    return lp(x,4000)*env(len(x),0.05,0.15)+bp(nz(d),300,1200)*0.08
# --- Sceau et pli ---
def sceau_abimer():  # ongle dans la cire : craquement sec, éclats
    crack=hp(nz(0.04),800)*dec(0.04,90)*1.4; x=[(crack,0)]
    for i in range(5): x.append((bp(nz(0.02),2000,8000)*dec(0.02,150)*rng.uniform(0.2,0.6),rng.uniform(0.03,0.25)))
    return room(mix(*x),0.1,0.1)
def sceau_rechauffer():  # cire qui ramollit contre la flamme : grésillement doux, bulles lentes
    d=1.6; sizzle=hp(nz(d),2500)*(rng.random(int(d*SR))>0.985)*0.6+hp(nz(d),4000)*0.04
    flame=bp(nz(d),100,700)*0.25; return (sizzle+flame)*env(int(d*SR),0.3,0.5)
def sceau_ouvrir():  # cire qui cède, ruban, papier — irréversible : un silence avant le papier
    crack=lp(hp(nz(0.09),300),3000)*dec(0.09,40)*1.5
    ribbon=bp(nz(0.4),600,3000)*np.sin(np.pi*T(0.4)/0.4)*0.3
    return mix((crack,0),(ribbon,0.15),(pli_lire()*0.8,0.9))
def pli_lire():
    d=0.8; x=bp(nz(d),700,7000)*(np.abs(lp(nz(d),20))*10).clip(0,1)**2*env(int(d*SR),0.05,0.25)
    crisp=np.zeros(int(d*SR))
    for _ in range(8): i=rng.integers(0,len(crisp)-200); crisp[i:i+200]+=hp(nz(200/SR),3000)*np.hanning(200)
    return x+crisp*0.3
def carnet():  # le carnet frémit : à peine un froissement, jamais une fanfare
    d=0.35; return bp(nz(d),1500,6000)*np.sin(np.pi*T(d)/d)**2*(0.5+0.5*np.sin(2*np.pi*28*T(d)))*0.6
def pain():
    tear=bp(nz(0.25),600,4000)*(np.abs(lp(nz(0.25),30))*8).clip(0,1)*env(int(0.25*SR),0.01,0.08)
    return mix((tear,0),*[(lp(nz(0.09),1200)*dec(0.09,30)*0.6,0.35+i*0.28) for i in range(3)])
def cendre():  # le pouce de l'aumônier sur le front : poudre sèche
    powder=bp(nz(0.4),1200,6000)*np.sin(np.pi*T(0.4)/0.4)**2*0.4
    return mix((lp(nz(0.05),600)*dec(0.05,50)*0.5,0),(powder,0.02))
def periscope_regarder():  # cuir contre l'œil, tube métallique ; la motte, elle, ne fait aucun bruit
    leather=bp(nz(0.3),200,1500)*env(int(0.3*SR),0.05,0.2)*0.6
    tube=sum(np.sin(2*np.pi*f*T(0.8))*np.exp(-T(0.8)*k) for f,k in ((210,6),(530,9),(1170,14)))*0.12
    return mix((leather,0),(tube,0.1))
# --- Interface ---
def ui_survol(): return bp(nz(0.05),2500,7000)*dec(0.05,70)*0.5     # pointe de plume qui effleure
def ui_valider(): return mix((lp(nz(0.04),1500)*dec(0.04,80),0),(bp(nz(0.12),1500,6000)*dec(0.12,30)*0.4,0.01))  # plume posée
def ui_maintien():  # appui maintenu 1,2 s des gestes irréversibles : la tension monte, puis cède
    d=1.2; tt=T(d); f=180*2**(tt/d*1.0)
    tone=np.sin(2*np.pi*np.cumsum(f)/SR)*(tt/d)**1.5*0.25
    creak=bp(nz(d),300,2000)*(np.sin(2*np.pi*np.cumsum(9+20*tt/d)/SR)>0.6)*(tt/d)*0.4
    return lp(tone+creak,3000)
def ui_annuler(): return bp(nz(0.18),300,1500)*env(int(0.18*SR),0.01,0.15)*0.5
PACK={
 'sfx_pas_boue':(pas_boue,6),'sfx_pas_planche':(pas_planche,4),'sfx_pas_terre':(pas_terre,4),
 'sfx_echelle_monter':(echelle,3),'sfx_passage_escalier':(escalier,1),'sfx_passage_toile':(toile,2),
 'sfx_lanterne_allumer':(allumer,1),'sfx_lanterne_eteindre':(eteindre,1),'sfx_lanterne_remplir':(remplir,1),
 'sfx_sceau_abimer':(sceau_abimer,1),'sfx_sceau_rechauffer':(sceau_rechauffer,1),'sfx_sceau_ouvrir':(sceau_ouvrir,1),
 'sfx_pli_lire':(pli_lire,2),'sfx_carnet_fremir':(carnet,2),'sfx_pain_manger':(pain,1),
 'sfx_cendre_front':(cendre,1),'sfx_periscope_regarder':(periscope_regarder,1),
 'sfx_ui_survol':(ui_survol,3),'sfx_ui_valider':(ui_valider,2),'sfx_ui_maintien':(ui_maintien,1),'sfx_ui_annuler':(ui_annuler,1),
}
PEAK={'sfx_ui_maintien':0.45,'sfx_cendre_front':0.5,'sfx_ui_annuler':0.45,'sfx_ui_survol':0.35,'sfx_ui_valider':0.5,'sfx_carnet_fremir':0.35,'sfx_pas_boue':0.6,'sfx_pas_planche':0.6,'sfx_pas_terre':0.5}
for base,(fn,n) in PACK.items():
    for i in range(1,n+1): save(f"{base}_{i:02d}", fn(), PEAK.get(base,0.75))
print(sum(n for _,n in PACK.values()),"fichiers")
