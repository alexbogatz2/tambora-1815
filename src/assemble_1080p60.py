#!/usr/bin/env python3
"""Insert approved 5-second opening; export full 120 seconds at 1080p60.
Frame-rate conversion preserves source frames (no synthetic motion interpolation).
"""
from pathlib import Path
import subprocess
r=Path(__file__).resolve().parents[1];o=r/'outputs'
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','warning','-i',str(o/'tambora_opening_v4_picture.mp4'),'-i',str(o/'Tambora_1815_Revised_1080p_24fps.mp4'),'-filter_complex','[0:v]trim=duration=5,setpts=PTS-STARTPTS[a];[1:v]trim=start=5:end=120,setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0,fps=60[v]','-map','[v]','-map','1:a','-c:v','libx264','-preset','fast','-crf','17','-threads','6','-pix_fmt','yuv420p','-c:a','copy','-t','120','-movflags','+faststart','-progress',str(o/'export_1080p60_progress.txt'),str(o/'Tambora_1815_1080p_60fps.mp4')],check=True)
