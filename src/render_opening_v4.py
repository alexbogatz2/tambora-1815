#!/usr/bin/env python3
"""Five-second sample with a shared plume/water clock and shutter."""
import json, subprocess, time
import numpy as np
import render_opening_v3 as r
from water_motion import animate_water

SOURCE_ACCELERATION=7.0  # Visible x7 label on the USGS source film.
TIME_SCALE=5.74          # Real elapsed seconds per output second, both layers.
SHUTTER=1/(2*r.FPS)     # Output seconds; physical exposure is TIME_SCALE*SHUTTER.

def frame(t):
    # Average the video layer over the same exposure used analytically by water.
    layers=[]
    for offset in [-SHUTTER/3,0,SHUTTER/3]:
        physical_time=(t+offset)*TIME_SCALE
        source_time=7.50+physical_time/SOURCE_ACCELERATION
        pos=source_time*r.SFPS; i=int(pos); f=pos-i
        layers.append(r.matte_frame(i)*(1-f)+r.matte_frame(i+1)*f)
    layer=sum(layers)/3
    dark=.60*r.v.smooth(t/25)
    water=animate_water(r.v.COAST,t,shore_y=.799,
                        time_scale=TIME_SCALE,shutter_seconds=SHUTTER)
    base=r.v.grade(water,dark).astype(np.float32)
    visibility=.48+.52*r.v.smooth(t/3)
    alpha=np.clip(layer[:,:,3]*r.OCC*visibility,0,1)
    tint=np.array([1-.50*dark,1-.57*dark,1-.60*dark],np.float32)
    color=layer[:,:,:3]*r.OCC[:,:,None]*visibility*tint
    im=np.clip(base*(1-alpha[:,:,None])+color,0,255).astype(np.uint8)
    im=r.v.blend(im,r.v.LABEL[0],r.v.LABEL[1]*.8)
    if t<1: im=(im.astype(np.float32)*r.v.smooth(t)).astype(np.uint8)
    return np.ascontiguousarray(im)

if __name__=='__main__':
    out=r.ROOT/'outputs'; target=out/'tambora_opening_v4_picture.mp4'
    cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{r.W}x{r.H}','-r',str(r.FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','14','-threads','3','-pix_fmt','yuv420p','-movflags','+faststart',str(target)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE); start=time.time()
    for i in range(120):
        p.stdin.write(frame(i/r.FPS).tobytes())
        if i%24==0:
            progress={'frames':i,'total':120,'percent':round(i/120*100),'elapsed':round(time.time()-start,1)}
            (out/'opening_v4_progress.json').write_text(json.dumps(progress))
    p.stdin.close()
    if p.wait(): raise RuntimeError('Video encoding failed')
    (out/'opening_v4_progress.json').write_text(json.dumps({'frames':120,'total':120,'percent':100}))
    print(target)
