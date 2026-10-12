"""Continuous perspective ocean micro-motion over an unchanged land plate.
CPU, deterministic, stateless in time. Input/output uint8 BGR; only ocean ROI
is remapped. Does not simulate breaking surf or hydrodynamics.
"""
from functools import lru_cache
import numpy as np
import cv2

@lru_cache(maxsize=6)
def _fields(h,w,shore_y):
    y0=int(np.ceil(h*shore_y)); rh=h-y0
    yy,xx=np.mgrid[:rh,:w].astype(np.float32)
    d=yy/max(rh-1,1)
    # Fade with zero slope at shoreline: no hard seam or wobbly land edge.
    fade=np.minimum(d/.22,1); fade=fade*fade*(3-2*fade)
    depth=.18+.82*d
    perspective=np.log(.15+d)
    phases=[]
    for kx,ky,phi in [(0.052,13,0),(-.081,24,1.7),(.12,37,4.2),
                      (-.16,52,.6),(.025,8,2.8)]:
        phases.append((kx*xx/(.52+.48*d)+ky*perspective+phi).astype(np.float32))
    return y0,xx,yy,fade,depth,phases

def animate_water(image,t,hyperlapse=False,shore_y=.799,*,time_scale=None,shutter_seconds=None):
    """Return BGR frame with continuous ocean motion; all rows above shore fixed.

    Use global seconds or continuous scene seconds. Hyperlapse averages fast
    wind-wave phases over a virtual shutter analytically to avoid strobing.
    Explicit time_scale multiplies output time; shutter_seconds is measured
    in OUTPUT seconds, so speed also scales the physical exposure interval.
    """
    h,w=image.shape[:2]
    if not (0<shore_y<1): raise ValueError('shore_y must be between 0 and 1')
    y0,x,y,fade,depth,phases=_fields(h,w,float(shore_y))
    roi=image[y0:]; dx=np.zeros_like(x); dy=np.zeros_like(x); light=np.zeros_like(x)
    rates=[1.35,2.13,3.05,4.32,.64]
    speed=float(time_scale) if time_scale is not None else (3.4 if hyperlapse else 1.)
    # Hyperlapse integrates 0.20s virtual shutter, ordinary 1/48s.
    shutter=float(shutter_seconds) if shutter_seconds is not None else (.20 if hyperlapse else 1/48)
    for j,(phase,rate) in enumerate(zip(phases,rates)):
        omega=rate*speed
        attenuation=float(np.sinc(omega*shutter/(2*np.pi)))
        arg=phase-omega*float(t)
        s=np.sin(arg)*attenuation; c=np.cos(arg)*attenuation
        dx+=(.62 if j<2 else .25)*s
        dy+=(.72 if j<2 else .26)*c
        light+=(1.05 if j<2 else .5)*s
    # Foreground excursions remain under 3 native 1080p pixels.
    scale=h/1080
    dx*=fade*depth*scale; dy*=fade*depth*scale
    mapx=x+dx; mapy=y+dy
    warped=cv2.remap(roi,mapx,mapy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
    # Gentle moving glints; multiplicative so dark water stays dark.
    shimmer=(light*fade*depth*.038)[:,:,None]
    result=image.copy()
    result[y0:]=np.clip(warped.astype(np.float32)*(1+shimmer),0,255).astype(np.uint8)
    # First ocean row is exactly unchanged, maintaining coastline continuity.
    result[y0]=image[y0]
    return result

if __name__=='__main__':
    import argparse,json,time
    from pathlib import Path
    p=argparse.ArgumentParser(); p.add_argument('--asset',default='tambora/assets/calm.png')
    p.add_argument('--output',default='tambora/outputs/water_test.mp4'); a=p.parse_args()
    im=cv2.resize(cv2.imread(a.asset),(1920,1080),interpolation=cv2.INTER_CUBIC)
    writer=cv2.VideoWriter(a.output,cv2.VideoWriter_fourcc(*'mp4v'),24,(1920,1080))
    y0=int(np.ceil(1080*.799)); diffs=[]; maximum_land=0; previous=None; samples=[]
    begin=time.time()
    for i in range(288):
        frame=animate_water(im,i/24)
        maximum_land=max(maximum_land,int(np.abs(frame[:y0].astype(np.int16)-im[:y0]).max()))
        if previous is not None: diffs.append(float(np.abs(frame[y0:].astype(np.int16)-previous[y0:].astype(np.int16)).mean()))
        previous=frame; writer.write(frame)
        if i in [0,72,144,216]: samples.append(cv2.resize(frame,(640,360)))
    writer.release()
    contact=np.vstack([np.hstack(samples[:2]),np.hstack(samples[2:])])
    cv2.imwrite(str(Path(a.output).with_suffix('.jpg')),contact)
    metrics={'seconds':12,'fps':24,'land_max_pixel_change':maximum_land,
             'ocean_consecutive_mean_abs_change':float(np.mean(diffs)),
             'ocean_largest_consecutive_change':float(np.max(diffs)),
             'render_seconds':time.time()-begin}
    Path(a.output).with_suffix('.json').write_text(json.dumps(metrics,indent=2)); print(metrics)
