#!/usr/bin/env python3
"""Revised continuous 2.5D reconstruction. No cyclic flow-map resets.
All photographic camera cuts are clean; the coastal base plate is persistent.
"""
import render_video as v
from render_video import ROOT,W,H,FPS,A,x,y,X,Y,N,N2,smooth,blend,camera,LABEL,END,lightning,ejecta
from pathlib import Path
import cv2,numpy as np,subprocess,time,json,argparse
from water_motion import animate_water
cv2.setNumThreads(3)
# Native-alpha plume asset, transformed in premultiplied form to avoid fringes.
plume=cv2.resize(cv2.imread(str(ROOT/'assets/plume_alpha.png'),cv2.IMREAD_UNCHANGED),(W,H),interpolation=cv2.INTER_AREA)
MATTE=plume[:,:,3].astype(np.float32)/255
rgb=plume[:,:,:3].astype(np.float32)
# Remove colored matte spill from the generated fine transparent edge.
gray=cv2.cvtColor(plume[:,:,:3],cv2.COLOR_BGR2GRAY).astype(np.float32)
rgb=rgb*.35+gray[:,:,None]*.65
PREMULT=rgb*MATTE[:,:,None]
PLUMEFLOW=smooth((.975-Y)/.20)
# Coastal plate: stable mountain and coastline from the calm photograph.
# Dynamic sky masks touch only the sky; they cannot translate terrain.
SKY=v.SKY
COAST=A['calm']
PDC=v.PDC
COL=v.COL
collapse_path=ROOT/'assets/collapse.png'
COLLAPSE=cv2.resize(cv2.imread(str(collapse_path)),(W,H))
# PDC difference matte gives only gray current lobes, not a new terrain image.
# Feathering is spatially fixed, so composition cannot crawl at the boundary.
PDC=cv2.GaussianBlur(PDC,(0,0),3)

def advect(src,t,kind='sky',strength=1):
 """Single continuous trajectory for every pixel; never wraps or resets."""
 if kind=='sky':
  m=SKY*smooth((v.skyline[None,:]-y-90)/110);vx=(1.4+.33*N+.2*N2)*m;vy=(-2.7-.38*N2)*m
 elif kind=='column':
  m=COL;vx=(.60+.2*N)*m;vy=(-2.3-.3*N2)*m
 elif kind=='pdc':
  m=PDC;vx=((X-.5)*12+.3*N)*m;vy=(3.6+.3*N2)*m
 else:
  m=np.exp(-((X-.5)/.22)**2-((Y-.38)/.17)**2);vx=m*.4;vy=m*-1
 # A continuously translating fine curl adds evolution without sinusoidal jelly.
 tt=float(t)*strength
 return cv2.remap(src,(x-vx*tt).astype(np.float32),(y-vy*tt).astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)

def grade(im,amount):
 # Global exposure/white balance changes keep terrain and sky synchronized.
 return np.clip(im.astype(np.float32)*np.array([1-.50*amount,1-.57*amount,1-.60*amount],np.float32),0,255).astype(np.uint8)

def coastbase(t,night=0):
 im=animate_water(COAST,t,hyperlapse=t<25,shore_y=.799)
 return grade(im,night)

def coastal_eruption(t,night=.45):
 im=advect(A['eruption'],t,'sky')
 im=animate_water(im,t,shore_y=.799)
 return grade(im,night)

def plume_grow(t):
 u=t/25
 dark=.60*smooth(u)
 base=coastbase(t,dark)
 scale=.016+2.20*smooth((u-.055)/.93)
 anchor=(.527*W,.987*H);vent=(.497*W,.529*H)
 M=np.float32([[scale,0,vent[0]-anchor[0]*scale],[0,scale,vent[1]-anchor[1]*scale]])
 # Continuous ash transport, including matte, anchored at the emitting vent.
 mx=(x-PLUMEFLOW*(.8+.2*N)*t).astype(np.float32)
 my=(y+PLUMEFLOW*(1.7+.2*N2)*t).astype(np.float32)
 rgba=np.dstack((PREMULT,MATTE))
 moving=cv2.remap(rgba,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
 transformed=cv2.warpAffine(moving,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
 occlusion=smooth((v.skyline[None,:]-y)/4)*smooth(t/3)
 alpha=np.clip(transformed[:,:,3]*occlusion,0,1)
 tint=np.array([1-.50*dark,1-.57*dark,1-.60*dark],np.float32)
 color=transformed[:,:,:3]*occlusion[:,:,None]*tint
 return np.clip(base.astype(np.float32)*(1-alpha[:,:,None])+color,0,255).astype(np.uint8)

def scene(t):
 if t<25:
  im=plume_grow(t);im=blend(im,LABEL[0],LABEL[1]*.8)
 elif t<40:
  im=advect(A['column'],t-25,'column');im=grade(im,.60*(t-25)/15)
  im=animate_water(im,t,shore_y=.928);im=camera(im,1+.018*(t-25)/15)
 elif t<55:
  im=coastal_eruption(t-40,.90);im=lightning(im,t);im=camera(im,1.08)
 elif t<75:
  u=(t-55)/20;im=coastal_eruption(t-55,.88)
  currents=grade(advect(A['pdc'],t-55,'pdc'),.88)
  # Currents accelerate through valleys; each front has a soft irregular edge.
  reach=.53+.30*smooth(u/.85)
  mask=PDC*smooth((reach-Y+.024*N)/.085)
  im=blend(im,currents,mask)
 elif t<88:
  im=coastal_eruption(t-75,.94);im=ejecta(im,t);im=camera(im,1.22)
 elif t<105:
  u=(t-88)/17
  # Opaque local ash obscures the structural transition: no double mountain.
  source=A['pdc'] if u<.52 else COLLAPSE
  im=grade(advect(source,t-88,'sky',.8),.82)
  # Keep same animated foreground sea throughout this shot.
  water=coastbase(t,.82);mask=smooth((Y-.798)/.002)
  im=blend(im,water,mask)
  veil=smooth((u-.10)/.30)*(1-smooth((u-.62)/.30))
  ashtexture=grade(advect(A['eruption'],t-88,'sky',1.4),.80)
  # Cover full mountain and sky at transition, leaving sea intact.
  cover=smooth((.802-Y)/.014)*veil
  # Stretch actual ash texture over mountain so the veil is not a gray rectangle.
  fog=cv2.resize(ashtexture[:int(H*.45)],(W,int(H*.81)),interpolation=cv2.INTER_LINEAR)
  fogfull=im.copy();fogfull[:fog.shape[0]]=fog
  im=blend(im,fogfull,cover)
  im=blend(im,LABEL[0],LABEL[1]*.8)
 else:
  u=(t-105)/15;im=advect(A['aftermath'],t-105,'steam',.4)
  haze=np.exp(-((X-.51)/.13)**2-((Y-.45)/.10)**2)*.53
  im=blend(im,np.full_like(im,(152,151,149)),haze);im=camera(im,1.055-.055*u)
  if t>111:
   a=smooth((t-111)/2);im=blend(im,np.zeros_like(im),smooth((Y-.69)/.25)*.58*a)
   im=blend(im,END[0],END[1]*a)
 if t<1:im=(im.astype(np.float32)*smooth(t)).astype(np.uint8)
 if t>119:im=(im.astype(np.float32)*smooth(120-t)).astype(np.uint8)
 return np.ascontiguousarray(im)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--test',action='store_true');ap.add_argument('--stills',action='store_true');ap.add_argument('--start',type=float,default=0);ap.add_argument('--duration',type=float,default=120);ap.add_argument('--output');args=ap.parse_args()
 out=ROOT/'outputs';out.mkdir(exist_ok=True)
 if args.stills:
  for t in [5,12,20,63,96,101]:cv2.imwrite(str(out/f'v2_check_{t}.jpg'),scene(t))
  return
 # Review actual timeline excerpts, not speed-compressed substitutes.
 timeline=np.concatenate([np.arange(12*FPS)/FPS+5,np.arange(6*FPS)/FPS+60]) if args.test else args.start+np.arange(round(args.duration*FPS))/FPS
 target=out/(args.output or ('tambora_motion_test_v2.mp4' if args.test else 'tambora_picture_v2_1080p.mp4'))
 cmd=['ffmpeg','-y','-hide_banner','-loglevel','warning','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','14','-x264-params','keyint=48:min-keyint=48:scenecut=0:aq-mode=3','-threads','3','-pix_fmt','yuv420p','-movflags','+faststart',str(target)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE);beg=time.time()
 progress=out/('motion_test_v2_progress.json' if args.test else (Path(args.output).stem+'_progress.json' if args.output else 'render_v2_progress.json'))
 for i,t in enumerate(timeline):
  p.stdin.write(scene(float(t)).tobytes())
  if i%120==0:
   st={'frames':i,'total':len(timeline),'percent':round(i/len(timeline)*100,1),'elapsed_seconds':round(time.time()-beg,1)};progress.write_text(json.dumps(st));print(st,flush=True)
 p.stdin.close();rc=p.wait()
 if rc:raise RuntimeError(f'ffmpeg exit{rc}')
 progress.write_text(json.dumps({'frames':len(timeline),'total':len(timeline),'percent':100,'elapsed_seconds':round(time.time()-beg,1)}));print('DONE',target,flush=True)
if __name__=='__main__':main()
