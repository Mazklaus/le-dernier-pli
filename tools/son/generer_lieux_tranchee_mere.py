# Émetteurs localisés des lieux de la Tranchée-Mère — boucles mono de 20 s sans couture (circulaires)
import numpy as np, scipy.signal as ss, scipy.io.wavfile as wf, sys, os
SR=44100; L=20*SR; t=np.arange(L)/SR; D4=293.66
rng=np.random.default_rng(1916)
def fftfilt(x, lo=None, hi=None, order=2):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); g=np.ones_like(f)
    if hi: g/=np.sqrt(1+(f/hi)**(2*order))
    if lo: g/=np.sqrt(1+(lo/np.maximum(f,1e-3))**(2*order))
    return np.fft.irfft(X*g,len(x))
def noise(alpha=0):
    X=np.fft.rfft(rng.standard_normal(L)); f=np.fft.rfftfreq(L,1/SR); f[0]=1
    y=np.fft.irfft(X/f**(alpha/2),L); return y/np.abs(y).max()
def lfo(period,phase=0):
    n=max(1,round(20/period)); return 0.5+0.5*np.sin(2*np.pi*n*t/20+phase)
def place(buf,ev,pos): np.add.at(buf,(np.arange(len(ev))+pos)%L,ev)
def creverb(x,sec,wet,seed=0):
    r=np.random.default_rng(seed); n=int(sec*SR); ir=r.standard_normal(n)*np.exp(-6.9*np.arange(n)/n)
    y=np.fft.irfft(np.fft.rfft(x)*np.fft.rfft(np.pad(ir,(0,L-n))),L); y*=np.std(x)/(np.std(y)+1e-9); return (1-wet)*x+wet*y
def scatter(make,count,amp=(0.3,1)):
    m=np.zeros(L)
    for _ in range(count): place(m,make()*rng.uniform(*amp),int(rng.integers(0,L)))
    return m
def nrm(x): return x/(np.abs(x).max()+1e-9)
def drip():
    n=int(0.12*SR); tt=np.arange(n)/SR; f=rng.uniform(500,1300)
    return np.sin(2*np.pi*f*(1+2*np.exp(-tt*60))*tt)*np.exp(-tt*45)
def creak():
    n=int(rng.uniform(0.5,1.2)*SR); tt=np.arange(n)/SR; f=rng.uniform(140,260)*(1+0.3*np.sin(2*np.pi*rng.uniform(0.5,1.5)*tt))
    p=(np.sin(2*np.pi*np.cumsum(f)/SR)>0.92).astype(float); y=ss.lfilter(*ss.butter(2,[300,3000],'band',fs=SR),p); return y*np.hanning(n)
def murmur(f0lo=95,f0hi=140,dur=(0.8,2.0)):
    n=int(rng.uniform(*dur)*SR); tt=np.arange(n)/SR; f0=rng.uniform(f0lo,f0hi)*(1+0.08*np.sin(2*np.pi*3*tt))
    ph=np.cumsum(f0)/SR; v=sum(np.sin(2*np.pi*k*ph)/k for k in range(1,14)); syl=0.5+0.5*np.sin(2*np.pi*rng.uniform(3,5)*tt)
    return ss.lfilter(*ss.butter(2,[200,1400],'band',fs=SR),v*syl*np.hanning(n))
def breath_cycle(period,f0hi=900):  # respiration / ronflement périodique
    n=int(period*SR)
    reps=int(round(20/period)); per=L//reps; m=np.zeros(L)
    for i in range(reps):
        k=int(per*0.45); tt=np.arange(k)/SR
        nz=ss.lfilter(*ss.butter(2,[120,f0hi],'band',fs=SR),rng.standard_normal(k))
        snore=np.sin(2*np.pi*np.cumsum(np.full(k,rng.uniform(55,75)))/SR)*(np.sin(2*np.pi*28*tt)>0)*0.5
        place(m,(nz+snore)*np.hanning(k),i*per)
    return m
def tick():
    n=int(0.02*SR); return ss.lfilter(*ss.butter(2,3000,'high',fs=SR),rng.standard_normal(n))*np.exp(-np.arange(n)/SR*400)
def periodic(ev,interval,jit=0.0,amp=1.0):
    m=np.zeros(L); k=int(round(20/interval))
    for i in range(k): place(m,ev()*amp,int((i*20/k+rng.uniform(-jit,jit))*SR)%L)
    return m
def flame():  # bougie / lampe : souffle et petits crépitements
    return fftfilt(noise(1),lo=80,hi=600)*(0.6+0.4*np.abs(fftfilt(rng.standard_normal(L),hi=4)*30).clip(0,1))+0.3*scatter(lambda: tick()*0.4,25)
def paper():
    n=int(rng.uniform(0.3,0.8)*SR); return ss.lfilter(*ss.butter(2,[1500,7000],'band',fs=SR),rng.standard_normal(n))*np.hanning(n)*(rng.random(n)>0.6)
def bubble():
    n=int(0.08*SR); tt=np.arange(n)/SR; f=rng.uniform(200,500)*(1+tt*8); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*50)
def clink():
    n=int(0.6*SR); tt=np.arange(n)/SR; f=rng.uniform(1800,3200)
    return sum(a*np.sin(2*np.pi*f*r*tt)*np.exp(-tt*(8+r*6)) for r,a in ((1,1),(2.76,0.5),(5.4,0.25)))
def harmonium(level=1.0):  # bourdon ré-la, le dernier lieu « chaud »
    y=np.zeros(L)
    for f,a in ((D4/2,1),(D4*0.75,0.6),(D4,0.4)):
        ph=2*np.pi*f*t; y+=a*sum(np.sin(k*ph)/k**1.3 for k in range(1,12))
    return fftfilt(y,hi=1800)*(0.75+0.25*lfo(5))*level
def wind(lo=60,hi=700,alpha=1.6): return fftfilt(noise(alpha),lo=lo,hi=hi)*(0.4+0.6*lfo(10)*(0.7+0.3*lfo(4,1)))
def slit_whistle():  # vent dans la fente du périscope : sifflement fin et instable
    n=noise(0); y=np.zeros(L)
    for f in (1240,1870):
        b,a=ss.iirpeak(f,90,fs=SR); y+=ss.lfilter(b,a,n)
    return y*(0.2+0.8*lfo(6.67)**3)
def earth_groan():
    n=int(rng.uniform(2,4)*SR); tt=np.arange(n)/SR
    y=fftfilt(np.pad(rng.standard_normal(n),(0,L-n)),hi=120)[:n]*np.sin(np.pi*tt/tt[-1])**2
    return y*6
def thud():
    n=int(1.5*SR); tt=np.arange(n)/SR; return np.sin(2*np.pi*(32+20*np.exp(-tt*5))*tt)*np.exp(-tt*3)
def wire_hum():  # barbelé qui vibre au vent : presque ré, un peu trop haut (annonce l'étape 2)
    f=D4*2*2**(0.35/12); y=sum(np.sin(2*np.pi*f*k*t)*np.exp(-k*0.6) for k in range(1,6))
    return y*(0.05+0.95*(lfo(6.67,2)**4))
def room(): return fftfilt(noise(2),lo=30,hi=250)
Z={}
Z['couchette']   = 0.6*nrm(breath_cycle(4.0)) + 0.35*nrm(breath_cycle(5.0,600)) + 0.5*nrm(scatter(drip,12)) + 0.25*nrm(scatter(creak,3)) + 0.18*nrm(room())
Z['boyau-arriere']= 0.6*nrm(scatter(lambda: murmur(),10)) + 0.4*nrm(wind(80,500)) + 0.3*nrm(scatter(creak,4))
Z['abri-sergent'] = 0.5*nrm(flame()) + 0.45*nrm(periodic(tick,0.5)) + 0.4*nrm(scatter(paper,4)) + 0.15*nrm(room())
Z['carrefour']    = 0.7*nrm(wind(60,900)) + 0.3*nrm(scatter(lambda: murmur(),4)) + 0.2*nrm(scatter(creak,3))
Z['cantine']      = 0.5*nrm(scatter(bubble,180,(0.2,1))) + 0.35*nrm(scatter(clink,10)) + 0.6*nrm(scatter(lambda: murmur(100,200,(0.5,1.4)),22)) + 0.2*nrm(flame())
Z['chapelle']     = 0.55*nrm(harmonium()) + 0.35*nrm(scatter(lambda: murmur(90,120,(1.5,3)),6)) + 0.4*nrm(flame())
Z['periscope']    = 0.5*nrm(slit_whistle()) + 0.6*nrm(wind(100,1200,1.2)) + 0.3*nrm(scatter(creak,2))
Z['vieille-sape'] = 0.7*nrm(scatter(earth_groan,3)) + 0.45*nrm(scatter(drip,6)) + 0.4*nrm(scatter(thud,2)) + 0.12*nrm(wind(40,200,2)) + 0.2*nrm(room())
Z['sape-sortie']  = 0.5*nrm(scatter(drip,10)) + 0.4*nrm(scatter(creak,5)) + 0.55*nrm(wind(100,900))
Z['pied-echelle'] = 0.75*nrm(wind(60,1500,1.3)) + 0.25*nrm(wire_hum()) + 0.5*nrm(scatter(thud,2))
REV={'couchette':(0.6,0.25),'abri-sergent':(0.4,0.2),'cantine':(0.7,0.25),'chapelle':(1.6,0.4),'vieille-sape':(2.5,0.5),'sape-sortie':(0.9,0.3)}
out=sys.argv[1]
for k,y in Z.items():
    if k in REV: y=creverb(y,*REV[k],seed=len(k))
    y=nrm(y)*0.8
    wf.write(os.path.join(out,f"amb_tranchee-mere_{k}.wav"),SR,(y*32767).astype(np.int16))
    print(k)
