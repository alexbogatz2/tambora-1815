#!/usr/bin/env python3
"""Mux local picture/audio and export an explicitly upscaled 4K copy."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs'
for fourk in (False, True):
    name='Tambora_1815_4K.mp4' if fourk else 'Tambora_1815_1080p.mp4'
    cmd=['ffmpeg','-hide_banner','-y','-i',str(OUT/'tambora_picture_1080p.mp4'),'-i',str(OUT/'tambora_audio.wav'),'-map','0:v','-map','1:a']
    cmd+=['-vf','scale=3840:2160:flags=lanczos','-c:v','libx264','-preset','fast','-crf','20','-threads','6','-pix_fmt','yuv420p'] if fourk else ['-c:v','copy']
    cmd+=['-c:a','aac','-b:a','192k','-movflags','+faststart','-t','120',str(OUT/name)]
    subprocess.run(cmd,check=True)
