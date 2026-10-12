#!/usr/bin/env python3
"""Opening-only motion study using USGS public-domain volcanic motion reference.
A fixed-vent compositing approximation; this is not a Tambora flow simulation.
"""
from pathlib import Path
import cv2,numpy as np,subprocess,argparse,json,time
import render_video_v2 as v
W,H,FPS=v.W,v.H,v.FPS
ROOT=v.ROOT
cv2.setNumThreads(3)
CAP=cv2.VideoCapture(str(ROOT/'references/usgs_2008.mp4'))
SFPS=CAP.get(cv2.CAP_PROP_FPS);SOURCE=[]
while True:
 ok,im=CAP.read()
 if not ok:break
 SOURCE.append(im)
CAP.release()
sh,sw=SOURCE[0].shape[:2]
y,x=np.mgrid[:sh,:sw].astype(np.float32)
# Source credit remains in repository and accompanying scientific notes.
# Its terrain, horizon, timestamps and logo never enter the composite.
REGION=v.smooth((x-110)/45)*v.smooth((450+15*np.sin(y*.035)-x)/65)*v.smooth((y-42-12*np.sin(x*.04))/65)*v.smooth((348-y)/28)
M=np.float32([[.68,0,.497*W-234*.68],[0,.68,.520*H-331*.68]])
OCC=v.smooth((v.v.skyline[None,:]-v.y)/4)
CACHE={}
def matte_frame(idx):
 if idx in CACHE:return CACHE[idx]
 src=SOURCE[min(max(idx,0),len(SOURCE)-1)].astype(np.float32)
 lum=cv2.cvtColor(src,cv2.COLOR_BGR2GRAY)
 # Row-adaptive background key rejects actual source canyon/terrain layers.
 bg=np.percentile(lum[:,15:100],80,axis=1)[:,None]
 alpha=v.smooth((lum-bg-18)/58)*REGION
 support=(alpha>.035).astype(np.uint8)
 support=cv2.morphologyEx(support,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
 count,labels,stats,_=cv2.connectedComponentsWithStats(support)
 if count>1:
  largest=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]);support=(labels==largest).astype(np.uint8)
 support=cv2.erode(support,np.ones((3,3),np.uint8))
 support=cv2.GaussianBlur(support.astype(np.float32),(0,0),.7)
 alpha=cv2.GaussianBlur(alpha*support,(0,0),.65)
 bgc=np.percentile(src[:,15:100,:],80,axis=1)[:,None,:]
 # Solve foregroundcolor from observed edge mixture, removing dark canyon spill.
 fg=np.clip((src-bgc*(1-alpha[:,:,None]))/np.maximum(alpha[:,:,None],.15),0,255)
 # Neutral ash plus blue-gray aerial perspective appropriate to distant coast.
 neutral=cv2.cvtColor(fg.astype(np.float32),cv2.COLOR_BGR2GRAY)[:,:,None]
 color=(fg*.35+neutral*.65)*.66+np.array([53,46,39],np.float32)
 rgba=np.dstack((color*alpha[:,:,None],alpha))
 # Premultiplication prevents source-sky fringes at resampled thin edges.
 result=cv2.warpAffine(rgba,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
 if len(CACHE)>3:CACHE.pop(next(iter(CACHE)))
 CACHE[idx]=result
 return result

def physical_motion(t):
 # Source film already7x time accelerated;0.82x yields about5.7x real time.
 st=7.50+.82*t
 pos=st*SFPS;i=int(pos);frac=pos-i
 a=matte_frame(i);b=matte_frame(i+1)
 layer=a*(1-frac)+b*frac
 dark=.60*v.smooth(t/25)
 base=v.coastbase(t,dark).astype(np.float32)
 visibility=.48+.52*v.smooth(t/3)
 alpha=np.clip(layer[:,:,3]*OCC*visibility,0,1)
 tint=np.array([1-.50*dark,1-.57*dark,1-.60*dark],np.float32)
 color=layer[:,:,:3]*OCC[:,:,None]*visibility*tint
 return np.clip(base*(1-alpha[:,:,None])+color,0,255).astype(np.uint8)

def frame(t):
 # First5seconds use fixed-size real evolving motion. Between5and8 the
 # overlapping vent plume dissolves into the unchanged approved opening.
 im=physical_motion(min(t,5)) if t<=5 else physical_motion(t)
 if t>5:
  im=v.blend(im,v.plume_grow(t),v.smooth((t-5)/3))
 im=v.blend(im,v.LABEL[0],v.LABEL[1]*.8)
 if t<1:im=(im.astype(np.float32)*v.smooth(t)).astype(np.uint8)
 return np.ascontiguousarray(im)

def main():
 p=argparse.ArgumentParser();p.add_argument('--duration',type=float,default=5);p.add_argument('--stills',action='store_true');a=p.parse_args()
 out=ROOT/'outputs';out.mkdir(exist_ok=True)
 if a.stills:
  ims=[]
  for t in [1,2,3,4,5,7.9]:
   im=frame(t);cv2.imwrite(str(out/f'opening_v3_{t}.jpg'),im);ims.append(cv2.resize(im,(640,360)))
  cv2.imwrite(str(out/'opening_v3_contact.jpg'),np.vstack([np.hstack(ims[:3]),np.hstack(ims[3:])]))
  return
 target=out/f'tambora_opening_v3_{a.duration:g}s.mp4'
 cmd=['ffmpeg','-y','-hide_banner','-loglevel','warning','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','14','-x264-params','keyint=48:min-keyint=48:scenecut=0:aq-mode=3','-threads','3','-pix_fmt','yuv420p','-movflags','+faststart',str(target)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE);start=time.time()
 for i in range(round(a.duration*FPS)):
  proc.stdin.write(frame(i/FPS).tobytes())
  if i%24==0:print(i,round(time.time()-start,1),flush=True)
 proc.stdin.close();rc=proc.wait()
 if rc:raise RuntimeError(rc)
 print('DONE',target,flush=True)
if __name__=='__main__':main()
