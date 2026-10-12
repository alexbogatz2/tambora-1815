#!/usr/bin/env python3
"""Deterministic, local-only Tambora soundtrack: CPU synthesis + optional Flite.
No music, borrowed recordings, or external service calls. Sound design is an
interpretation of distant volcanic acoustics, not a historical recording.
"""
from pathlib import Path
import json, subprocess
import numpy as np
from scipy import signal
from scipy.io import wavfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs'; OUT.mkdir(parents=True,exist_ok=True)
SR=48000; DUR=120; N=SR*DUR
rng=np.random.default_rng(18150410)
t=np.arange(N,dtype=np.float32)/SR

def band_noise(n, lo, hi):
    z=rng.standard_normal(n).astype(np.float32)
    sos=signal.butter(3,[lo,hi],btype='bandpass',fs=SR,output='sos')
    z=signal.sosfilt(sos,z).astype(np.float32)
    return z/(np.sqrt(np.mean(z*z))+1e-8)

# Independent stereo turbulence, shared low-frequency body; deliberately no
# discrete reports synchronized to distant visible eruptive pulses.
strength=np.interp(t,[0,6,15,25,40,55,75,88,103,110,120],
                   [.08,.14,.3,.65,.9,1,.85,.95,.85,.40,.12]).astype(np.float32)
mod=(.83+.10*np.sin(t*1.1)+.07*np.sin(t*.37)).astype(np.float32)
common=band_noise(N,29,145)
a=np.empty((N,2),np.float32)
for ch in range(2):
    low=band_noise(N,34,200)
    wind=band_noise(N,160,1050)
    a[:,ch]=strength*mod*(.047*common+.020*low+.008*wind)
# Quiet coastal air and low irregular wash establish a believable distant mic.
for ch in range(2):
    surf=band_noise(N,180,2100)
    sw=(.5+.5*np.sin(t*.47+ch*.2))**3
    a[:,ch]+=.0045*surf*sw*(1-.65*strength)

def report(start,length,amp,pan,thunder=False):
    n=int(length*SR); tt=np.arange(n)/SR
    # Slow attack prevents the sharp, close-range artillery trope.
    env=(1-np.exp(-tt/(.19 if thunder else .45)))*np.exp(-tt/(2 if thunder else 3.1))
    env*=np.minimum((length-tt)/.9,1).clip(0,1)
    body=band_noise(n,32,330 if thunder else 160)
    if thunder:
        # Rolling late arrivals at irregular intervals.
        for delay,weight in [(1.05,.4),(2.8,.26),(4.15,.13)]:
            env+=weight*np.exp(-((tt-delay)/.7)**2)*np.minimum((length-tt),1).clip(0,1)
    z=(body*env*amp).astype(np.float32)
    at=int(start*SR); end=min(at+n,N); z=z[:end-at]
    gains=[np.sqrt((1-pan)/2),np.sqrt((1+pan)/2)]
    for ch in range(2):
        offset=int((.014 if ch else 0)*SR)
        count=min(len(z),N-at-offset)
        a[at+offset:at+offset+count,ch]+=z[:count]*gains[ch]

# Earlier unseen activity is audible during the opening and column views.
for ev in [(13,9,.08,-.2),(23,11,.12,.1),(35,12,.14,-.1),
           (65,12,.13,.22),(90,10,.12,-.2),(96.5,12,.15,.05),(102,11,.10,.2)]:
    report(*ev)
# Flashes at 42.2, 47.6, 52.1: delays 9.4, 10.1, and 11.2 seconds.
for ev in [(51.6,8,.10,-.45),(57.7,9,.12,.4),(63.3,8,.105,-.1)]:
    report(*ev,thunder=True)
# Fade both ends smoothly.
a*=np.minimum(t/3,1)[:,None]*np.minimum((DUR-t)/4,1)[:,None]
# Sparse narration, saved separately so the editor may select natural ambience.
phrases=[(4.0,'Mount Tambora. Sumbawa. April eighteen fifteen.'),
         (28.0,'An eruption column rose tens of kilometers into the atmosphere.'),
         (68.0,'Currents of hot ash swept down the mountain and reached the sea.'),
         (109.0,'Sulfur from the eruption helped bring the year without a summer, in eighteen sixteen.')]
v=np.zeros((N,2),np.float32); passages=[]
for idx,(start,words) in enumerate(phrases):
    txt=OUT/f'narration_{idx+1}.txt'; txt.write_text(words)
    tmp=OUT/f'narration_{idx+1}.wav'
    subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i',
        f'flite=textfile={txt}:voice=rms','-af','highpass=f=90,lowpass=f=6500,atempo=0.96',
        '-ar',str(SR),'-y',str(tmp)],check=True)
    rate,data=wavfile.read(tmp); z=data.astype(np.float32)/32768
    z*=.20/(np.sqrt(np.mean(z*z))+1e-8)
    z=np.tanh(z*.9)
    at=int(start*SR); count=min(len(z),N-at)
    v[at:at+count,:]+=z[:count,None]*.8
    passages.append({'start':start,'end':start+count/SR,'text':words})
# Duck the environment with gentle ramps, retaining scale under spoken words.
duck=np.ones(N,np.float32)
for p in passages:
    s,e=p['start'],p['end']
    duck=np.minimum(duck,np.interp(t,[0,max(0,s-.65),s,e,e+.9,DUR],[1,1,.32,.32,1,1]))
final=a*duck[:,None]+v
# One global gain preserves dynamics and provides 1.5 dB true-sample headroom.
gain=min(1.,.84/(np.max(np.abs(final))+1e-9)); final*=gain
for name,data in [('tambora_audio.wav',final),('tambora_ambience.wav',a),('tambora_narration.wav',v)]:
    peak=float(np.max(np.abs(data)))
    if peak>.94: data=data*(.94/peak)
    wavfile.write(OUT/name,SR,np.round(data*32767).astype(np.int16))
meta={'duration_seconds':DUR,'sample_rate':SR,'channels':2,'seed':18150410,
      'peak':float(np.max(np.abs(final))),'rms':float(np.sqrt(np.mean(final*final))),
      'clipped_samples':int(np.count_nonzero(np.abs(final)>=1)),
      'narration':passages,'lightning_sound_times':[51.6,57.7,63.3],
      'notes':'Synthetic distant ambience. Flite RMS narration is optional; separate stems supplied.'}
(OUT/'audio_report.json').write_text(json.dumps(meta,indent=2))
print(json.dumps(meta,indent=2))
