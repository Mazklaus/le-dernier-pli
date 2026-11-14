# Timbres de dialogue sans mots — étape 1. Synthèse par formants, graine fixe.
import numpy as np, scipy.signal as ss, scipy.io.wavfile as wf, sys, os
SR=44100; rng=np.random.default_rng(1919)
VOW={'a':(750,1200,2600),'o':(450,800,2600),'u':(320,800,2400),'e':(500,1700,2500),'i':(300,2200,2900),'eu':(450,1400,2400)}
def resonate(x,f,bw):
    b,a=ss.iirpeak(min(f,SR/2-100),f/bw,fs=SR); return ss.lfilter(b,a,x)
def voice(syls, f0, rate, breath=0.15, jitter=0.0, vib=(5,0.0), tilt=1.2, contour=0.0, gap=0.06, formant_shift=1.0):
    out=[]
    for i,(v,dur) in enumerate(syls):
        n=int(dur/rate*SR); tt=np.arange(n)/SR
        prog=(i+tt/ (n/SR))/len(syls)
        f=f0*(1+contour*(prog-0.5))*(1+vib[1]*np.sin(2*np.pi*vib[0]*tt))*(1+jitter*np.convolve(rng.standard_normal(n),np.ones(200)/200,'same'))
        ph=np.cumsum(f)/SR; src=sum(np.sin(2*np.pi*k*ph)/k**tilt for k in range(1,40) if k*f0<8000)
        src=src+breath*rng.standard_normal(n)*np.abs(src).max()
        F=VOW[v]; y=sum(resonate(src,F[j]*formant_shift,[8,10,12][j])*[1,0.6,0.25][j] for j in range(3))
        a=int(min(0.03,dur/rate/4)*SR); env=np.ones(n); env[:a]=np.linspace(0,1,a); env[-a:]=np.linspace(1,0,a)
        out+= [y*env*(1 if i else 1.0), np.zeros(int(gap*SR))]
    return np.concatenate(out)
def whistle(notes, rate):
    out=[]
    for st,dur in notes:
        n=int(dur/rate*SR); tt=np.arange(n)/SR; f=1175*2**(st/12)*(1+0.004*np.sin(2*np.pi*5.5*tt))
        y=np.sin(2*np.pi*np.cumsum(f)/SR)+0.08*ss.lfilter(*ss.iirpeak(f[0],6,fs=SR),rng.standard_normal(n))
        a=int(0.02*SR); env=np.ones(n); env[:a]=np.linspace(0,1,a); env[-a:]=np.linspace(1,0,a); out.append(y*env)
    return np.concatenate(out)
def reverb(x,sec,wet,seed=0):
    r=np.random.default_rng(seed); n=int(sec*SR); ir=r.standard_normal(n)*np.exp(-6.9*np.arange(n)/n)
    y=np.pad(ss.fftconvolve(x,ir),(0,1))[:len(x)+n]; x=np.pad(x,(0,n)); y*=np.std(x)/(np.std(y)+1e-9); return (1-wet)*x+wet*y
def rs(k,choices): return [choices[i] for i in rng.integers(0,len(choices),k)]
V=list(VOW)
def gen(name,i):
    if name=='tobie':   # timide : doux, soufflé, hésitant, montant
        k=int(rng.integers(2,4)); y=voice([(v,0.16) for v in rs(k,['eu','e','i','u'])],165,1.0,breath=0.35,tilt=1.8,contour=0.15,gap=0.12)
    elif name=='lamarre':  # usé : grave, rauque, lent, descendant
        k=int(rng.integers(2,4)); y=voice([(v,0.26) for v in rs(k,['a','o','eu'])],98,1.0,breath=0.2,jitter=0.05,tilt=1.0,contour=-0.25,gap=0.05)
    elif name=='cassien':  # tremblant : vibrato large et rapide
        k=int(rng.integers(3,5)); y=voice([(v,0.18) for v in rs(k,['o','u','e'])],135,1.0,breath=0.25,vib=(7.5,0.05),tilt=1.4,contour=0.05,gap=0.07)
    elif name=='jacquot':  # lumineux : siffle un fragment du Cantique (ré dorien)
        frags=[[(0,0.22),(3,0.22),(5,0.22),(7,0.45)],[(7,0.22),(5,0.22),(3,0.22),(2,0.45)],[(10,0.22),(9,0.22),(7,0.45)]]
        y=whistle(frags[i%3],1.0)*0.5
    elif name=='ravaude':  # gouailleuse : vive, aiguë, intonation qui saute
        k=int(rng.integers(4,7)); syl=[(v,rng.uniform(0.08,0.14)) for v in rs(k,['a','e','o','a'])]
        y=voice(syl,215,1.0,breath=0.1,tilt=1.0,contour=float(rng.choice([-0.4,0.4])),gap=0.025,vib=(3,0.06))
    elif name=='guetteur':  # immobile : un seul souffle grave, presque rien
        y=voice([('u',0.9)],82,1.0,breath=0.5,tilt=2.2,contour=-0.05)*0.6
    elif name=='voix-sous-terre':  # très lente, liturgique : psalmodie sur ré, formants abaissés
        notes=[[0,0,3,0],[0,-2,0],[3,5,3,0]][i%3]
        parts=[voice([(v,0.6)],65*2**(st/12),1.0,breath=0.15,tilt=1.1,formant_shift=0.8,gap=0.15,vib=(4,0.01)) for st,v in zip(notes,rs(len(notes),['o','u','a']))]
        y=reverb(np.concatenate(parts),3.5,0.6,seed=i)
    if name!='voix-sous-terre': y=reverb(y,0.4 if name!='guetteur' else 0.8,0.15,seed=i)
    fade=int(0.01*SR); y[-fade:]*=np.linspace(1,0,fade)
    return y/np.abs(y).max()*0.7
out=sys.argv[1]
for name in ['tobie','lamarre','cassien','jacquot','ravaude','guetteur','voix-sous-terre']:
    for i in range(3):
        y=gen(name,i); wf.write(os.path.join(out,f"vox_{name}_{i+1:02d}.wav"),SR,(y*32767).astype(np.int16))
