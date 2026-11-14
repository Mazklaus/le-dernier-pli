# « Le Cantique du Pli », version étape 1 : chanté par les soldats, juste mais fatigué.
# Chœur d'hommes sans paroles + harmonium. Boucle de 80 s sans couture (tout est circulaire).
import numpy as np, scipy.io.wavfile as wf, sys, os
SR=44100; BPM=48; BEAT=60/BPM; BEATS=64; L=int(SR*BEATS*BEAT)
rng=np.random.default_rng(1918); t=np.arange(L)/SR; D3=146.83
MEL=[0,3,5,7, 7,5,3,2, 0,2,3,5, 7,None,None,None, 10,9,7,5, 3,5,7,3, 2,0,2,-2, 0,None,None,None]
# accords par mesure (demi-tons depuis ré) : Rém, Lam, Rém, Lam, Do, Fa, Do, Rém
ACC=[[0,3,7],[7,10,14],[0,3,7],[7,10,14],[-2,2,5],[3,7,10],[-2,2,5],[0,3,7]]
def place(buf,ev,pos): np.add.at(buf,(np.arange(len(ev))+pos)%L,ev)
def fftfilt(x,hi=None,lo=None):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); g=np.ones_like(f)
    if hi: g/=np.sqrt(1+(f/hi)**4)
    if lo: g/=np.sqrt(1+(lo/np.maximum(f,1e-3))**4)
    return np.fft.irfft(X*g,len(x))
def reverb(x,sec,wet,seed):
    r=np.random.default_rng(seed); n=int(sec*SR); ir=r.standard_normal(n)*np.exp(-6.9*np.arange(n)/n)
    ir=fftfilt(np.pad(ir,(0,L-n)),hi=5000); y=np.fft.irfft(np.fft.rfft(x)*np.fft.rfft(ir),L); y*=np.std(x)/(np.std(y)+1e-9)
    return (1-wet)*x+wet*y
def voix(f, dur, vowel, voix_id):
    n=int(dur*SR); tt=np.arange(n)/SR
    sag=1-0.009*np.clip((tt-dur*0.6)/(dur*0.4+1e-9),0,1)        # la note s'affaisse en fin de tenue
    vib=1+0.005*np.sin(2*np.pi*rng.uniform(4.2,5.6)*tt+voix_id)*np.clip(tt/0.6,0,1)
    fv=f*2**(rng.uniform(-8,8)/1200)*sag*vib; ph=np.cumsum(fv)/SR
    F={'o':(450,800,2500),'u':(330,750,2400),'a':(700,1150,2500)}[vowel]
    out=np.zeros(n)
    for k in range(1,36):
        fk=f*k
        if fk>7000: break
        w=np.exp(-((fk-F[0])/170)**2)+0.55*np.exp(-((fk-F[1])/230)**2)+0.12*np.exp(-((fk-F[2])/350)**2)+0.02/k
        out+=w*np.sin(2*np.pi*k*ph+rng.uniform(0,6.28))
    out+=0.04*fftfilt(np.pad(rng.standard_normal(n),(0,L-n)),hi=3000,lo=300)[:n]*np.abs(out).max()  # souffle
    a=int(0.18*SR); r=int(0.3*SR); env=np.ones(n); env[:a]=np.linspace(0,1,a)**1.5; env[-r:]*=np.linspace(1,0,r)
    return out*env
def choeur():
    m=np.zeros(L)
    for rep in range(2):
        voyelle='o' if rep==0 else 'u'                 # second passage fredonné, bouche presque fermée
        for i,st in enumerate(MEL):
            if st is None: continue
            d=1
            while i+d<len(MEL) and MEL[i+d] is None: d+=1
            for v,(octv,amp) in enumerate([(0,1),(0,0.9),(0,0.8),(-12,0.7),(-12,0.6)]):
                if rep==1 and octv==0 and v==2: continue   # une voix s'est tue au second passage
                jit=rng.normal(0,0.035)                         # ils ne partent pas tous ensemble
                f=D3*2**((st+octv)/12)
                place(m, voix(f,d*BEAT*1.04,voyelle,v)*amp*(0.85 if rep else 1), int(((rep*32+i)*BEAT+jit+0.02)*SR))
    return m
def harmonium():
    m=np.zeros(L)
    for rep in range(2):
        for b,acc in enumerate(ACC):
            n=int(4*BEAT*SR)+int(0.4*SR); tt=np.arange(n)/SR; y=np.zeros(n)
            for st in acc+[acc[0]-12]:
                f=D3*2**(st/12)*(1+0.0015*rng.standard_normal())
                ph=2*np.pi*f*tt; y+=sum(np.sin(k*ph)*(1/k**1.1)*(1.4 if k in (2,4) else 1) for k in range(1,14))
            a=int(0.35*SR); env=np.ones(n); env[:a]=np.linspace(0,1,a); env[-int(0.4*SR):]*=np.linspace(1,0,int(0.4*SR))
            env*=1-0.12*np.sin(2*np.pi*tt/(4*BEAT))**2       # le soufflet respire
            place(m,y*env,int((rep*32+b*4)*BEAT*SR))
    return fftfilt(m,hi=2200)
c=choeur(); h=harmonium()
c/=np.abs(c).max(); h/=np.abs(h).max()
mix=0.75*c+0.32*h
mix=reverb(mix,3.0,0.45,seed=7)
st=np.stack([mix, np.roll(mix,int(0.011*SR))],1)
st=st/np.abs(st).max()*0.85
wf.write(os.path.join(sys.argv[1],"mus_tranchee-mere_theme.wav"),SR,(st*32767).astype(np.int16))
