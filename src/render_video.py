#!/usr/bin/env python3
"""Deterministic 2.5D documentary renderer; animated reconstruction, not CFD.
Photo-texture advection is limited to ash masks. Terrain remains rigid.
"""
from pathlib import Path
import argparse, subprocess, json, time, shutil
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
W,H,FPS=1920,1080,24
cv2.setNumThreads(3)
FILES={'calm':'e41bdaeb-9be6-4115-abcc-00f5748e3e03','eruption':'f1102ec7-b5d0-4a48-96a7-db729b814a4c','pdc':'82c341ca-b34f-4e75-84ca-6b711a7a450d','aftermath':'8d58a719-9f1e-4593-88a5-04cb6bca5fd4','column':'cb8b7b9a-5208-42c1-91b9-40eb95237618'}
for name,uid in FILES.items():
 p=ROOT/'assets'/f'{name}.png'
 if not p.exists(): shutil.copy(ROOT.parent/'generated_images'/f'exec-{uid}.png',p)
A={k:cv2.resize(cv2.imread(str(ROOT/'assets'/f'{k}.png')),(W,H),interpolation=cv2.INTER_CUBIC) for k in FILES}
y,x=np.mgrid[:H,:W].astype(np.float32); X=x/W;Y=y/H
rng=np.random.default_rng(1815)
def noise(h,w):return cv2.resize(rng.normal(size=(h,w)).astype(np.float32),(W,H),interpolation=cv2.INTER_CUBIC)
N=noise(18,32);N2=noise(9,16)
def smooth(a):
 a=np.clip(a,0,1);return a*a*(3-2*a)
def blend(a,b,m):
 if np.isscalar(m): return cv2.addWeighted(a,1-float(m),b,float(m),0)
 return np.clip(a.astype(np.float32)*(1-m[:,:,None])+b.astype(np.float32)*m[:,:,None],0,255).astype(np.uint8)
# Conservative skyline, matching all coastal reference images.
skyline=np.interp(np.arange(W),np.array([0,.15,.3,.4,.47,.51,.58,.7,.85,1])*W,np.array([.665,.60,.555,.52,.495,.505,.55,.59,.62,.67])*H)
SKY=smooth((skyline[None,:]-y)/20).astype(np.float32)
COL=smooth((.837-Y)/.025)*smooth((X-.27)/.07)*smooth((.91-X)/.06)
PDC=smooth((Y-.49)/.035)*smooth((.799-Y)/.018)
diff=np.mean(np.abs(A['pdc'].astype(float)-A['eruption']),axis=2)
PDC*=smooth((cv2.GaussianBlur(diff.astype(np.float32),(0,0),10)-8)/25)
FLOW={}
FLOW['sky']=(SKY*(2+N*1.8+N2),SKY*(-7-3*N2))
FLOW['column']=(COL*(1+N*1.5+N2),COL*(-5-2*N2))
FLOW['pdc']=(PDC*((X-.50)*29+N*1.7),PDC*(7+np.abs(X-.5)*7+N2))
FLOW['steam']=(np.exp(-((X-.5)/.25)**2-((Y-.36)/.16)**2)*(1+N),np.exp(-((X-.5)/.25)**2-((Y-.36)/.16)**2)*(-2+N))
def advect(src,t,kind='sky',strength=1):
 # Dual staggered, cross-faded flow maps avoid discontinuities at texture resets.
 vx,vy=FLOW[kind]; period=5.7
 p=(t%period)/period;q=(p+.5)%1
 weight=abs(2*p-1)
 a=cv2.remap(src,x-vx*(p-.5)*period*strength,y-vy*(p-.5)*period*strength,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
 b=cv2.remap(src,x-vx*(q-.5)*period*strength,y-vy*(q-.5)*period*strength,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
 return cv2.addWeighted(a,1-weight,b,weight,0)
def camera(im,z=1,px=0,py=0):
 if z==1 and px==0 and py==0:return im
 M=np.float32([[z,0,W*(1-z)/2+px],[0,z,H*(1-z)/2+py]])
 return cv2.warpAffine(im,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
def text_layer(lines):
 im=Image.new('RGBA',(W,H));d=ImageDraw.Draw(im)
 for txt,size,ypos in lines:
  f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',size)
  d.text((W/2,ypos),txt,font=f,fill=(238,237,231,255),anchor='mt',stroke_width=1,stroke_fill=(10,10,10,150))
 ar=np.array(im);return ar[:,:,:3][:,:,::-1].copy(),ar[:,:,3].astype(np.float32)/255
LABEL=text_layer([('TIME ACCELERATED',20,1024)])
END=text_layer([('MOUNT TAMBORA — APRIL 1815',43,823),('VEI 7 — One of the largest explosive eruptions in recorded history.',25,888),('Its atmospheric effects contributed to the Year Without a Summer in 1816.',24,929)])
# Deterministic jagged lightning geometry, cloud-local with short branches.
BOLTS=[]
for seed,start in [(21,(.53,.15)),(32,(.65,.3)),(53,(.44,.12))]:
 r=np.random.default_rng(seed);pts=[(int(start[0]*W),int(start[1]*H))]
 for i in range(13):pts.append((pts[-1][0]+int(r.normal(0,19)),pts[-1][1]+int(r.uniform(6,17))))
 BOLTS.append(np.array(pts,np.int32))
def lightning(im,t):
 flash=0.;layer=np.zeros_like(im)
 for event,pts in zip([42.2,47.6,52.1],BOLTS):
  dt=t-event
  a=max(0,1-dt/.12) if 0<=dt<.12 else (max(0,1-(dt-.19)/.07)*.45 if .19<dt<.26 else 0)
  if a:
   flash=max(flash,a);cv2.polylines(layer,[pts],False,(250,222,210),2,cv2.LINE_AA)
   branch=np.array([pts[6],pts[6]+[45,12],pts[6]+[68,36],pts[6]+[99,41]])
   cv2.polylines(layer,[branch],False,(200,174,160),1,cv2.LINE_AA)
 if flash:
  glow=cv2.GaussianBlur(layer,(0,0),12)
  im=cv2.addWeighted(im,1+.65*flash,glow,3*flash,4*flash)
  im=cv2.addWeighted(im,1,layer,flash,0)
 return im
particles=[]
for event in [76,80.3,85]:
 for i in range(62):particles.append((event+rng.uniform(0,.5),rng.normal(0,16),rng.uniform(-48,-15),rng.uniform(.65,1.7),rng.uniform(.5,1.5)))
def ejecta(im,t):
 layer=np.zeros_like(im)
 for birth,vx,vy,life,size in particles:
  dt=t-birth
  if 0<dt<life:
   xx=int(.496*W+vx*(1-np.exp(-.35*dt))/.35);yy=int(.496*H+vy*dt+19*dt*dt)
   if yy<.505*H:
    fade=(1-dt/life)**.6
    cv2.circle(layer,(xx,yy),max(1,int(size)),(int(50*fade),int(170*fade),int(255*fade)),-1,cv2.LINE_AA)
 return cv2.add(im,cv2.addWeighted(layer,1,cv2.GaussianBlur(layer,(0,0),3),1.3,0))
collapse_path=ROOT/'assets/collapse.png'
def frame(t):
 if t<25:
  u=t/25; im=A['calm'].copy();ash=advect(A['eruption'],t*3)
  # Expanding eruption: starts at vent, rises and broadens over time.
  h=.035+.61*smooth((u-.09)/.70); width=.022+.88*smooth((u-.12)/.84)
  radius=np.sqrt(((X-.498)/max(width,.025))**2+((Y-.50)/max(h,.04))**2)
  front=smooth((1-radius+.065*N+.06*N2)/.35)*SKY
  im=blend(im,ash,front*smooth(u/.7))
  im=blend(im,A['eruption'],smooth((u-.80)/.20)*.4)
  im=blend(im,LABEL[0],LABEL[1]*.7)
 elif t<40:
  im=advect(A['column'],t-25,'column');im=camera(im,1+.025*(t-25)/15)
 elif t<55:
  im=advect(A['eruption'],t-40);im=(im.astype(np.float32)*np.array([.42,.37,.33])).astype(np.uint8);im=lightning(im,t);im=camera(im,1.08)
 elif t<75:
  u=(t-55)/20;im=advect(A['eruption'],t-55);p=advect(A['pdc'],t-55,'pdc',1.6)
  reach=.49+.32*smooth(u/.85)
  mask=PDC*smooth((reach-Y+.015*N)/.04)
  im=blend(im,p,mask)
 elif t<88:
  im=advect(A['eruption'],t-75);im=(im.astype(np.float32)*np.array([.40,.35,.31])).astype(np.uint8);im=ejecta(im,t);im=camera(im,1.22)
 elif t<105:
  u=(t-88)/17;im=advect(A['pdc'],t-88,'pdc',.8)
  if collapse_path.exists():
   if 'collapse' not in A:A['collapse']=cv2.resize(cv2.imread(str(collapse_path)),(W,H))
   other=advect(A['collapse'],t-88,'sky',.5)
  else:other=A['aftermath']
  # Ash cover obscures unknown structural chronology, then reveals lowered summit.
  im=blend(im,other,smooth((u-.20)/.62))
  veil=np.exp(-((Y-.49)/.23)**2)*np.exp(-((X-.5)/.49)**2)*(.5+.1*N)
  opacity=float(np.sin(np.pi*u)**2)*.45
  im=blend(im,np.full_like(im,(85,88,91)),np.clip(veil*opacity,0,.6))
  im=blend(im,LABEL[0],LABEL[1]*.7)
 else:
  u=(t-105)/15;im=advect(A['aftermath'],t-105,'steam',.4)
  haze=np.exp(-((X-.51)/.13)**2-((Y-.45)/.10)**2)*.53
  im=blend(im,np.full_like(im,(152,151,149)),haze);im=camera(im,1.055-.055*u)
  if t>111:
   a=smooth((t-111)/2);grad=smooth((Y-.69)/.25)*.58*a;im=blend(im,np.zeros_like(im),grad)
   im=blend(im,END[0],END[1]*a)
 if t<1:im=(im.astype(np.float32)*smooth(t)).astype(np.uint8)
 if t>119:im=(im.astype(np.float32)*smooth(120-t)).astype(np.uint8)
 return np.ascontiguousarray(im)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--preview',action='store_true');ap.add_argument('--start',type=float,default=0);ap.add_argument('--duration',type=float,default=120);args=ap.parse_args()
 out=ROOT/'outputs';out.mkdir(exist_ok=True)
 if args.preview:
  shots=[frame(t) for t in [0.8,12,24,33,42.25,66,80.7,99,113]]
  thumbs=[cv2.resize(s,(640,360)) for s in shots];montage=np.vstack([np.hstack(thumbs[i:i+3]) for i in range(0,9,3)])
  cv2.imwrite(str(out/'preview_montage.jpg'),montage);return
 target=out/'tambora_picture_1080p.mp4'
 cmd=['ffmpeg','-y','-hide_banner','-loglevel','warning','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-threads','3','-pix_fmt','yuv420p','-movflags','+faststart',str(target)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE);beg=time.time();total=round(args.duration*FPS)
 for i in range(total):
  p.stdin.write(frame(args.start+i/FPS).tobytes())
  if i%120==0:
   status={'frames':i,'total':total,'percent':round(i/total*100,1),'elapsed_seconds':round(time.time()-beg,1)}
   (out/'render_progress.json').write_text(json.dumps(status));print(status,flush=True)
 p.stdin.close();rc=p.wait()
 if rc:raise RuntimeError(f'ffmpeg exit {rc}')
 (out/'render_progress.json').write_text(json.dumps({'frames':total,'total':total,'percent':100,'elapsed_seconds':round(time.time()-beg,1)}))
 print('DONE',target,flush=True)
if __name__=='__main__':main()
