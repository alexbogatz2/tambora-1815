#!/usr/bin/env python3
"""Assemble revised 1080p/24fps review master. No upscale is performed."""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[1]
out=root/'outputs'
subprocess.run(['ffmpeg','-hide_banner','-y','-i',str(out/'tambora_picture_v2_1080p.mp4'),'-i',str(out/'tambora_audio.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart','-t','120',str(out/'Tambora_1815_Revised_1080p_24fps.mp4')],check=True)
