#!/usr/bin/env python3
"""Export reviewed first five seconds only; preserve full v2 unchanged."""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[1];o=root/'outputs'
def run(args):subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',*map(str,args)],check=True)
run(['-i',o/'tambora_opening_v3_8s.mp4','-i',o/'Tambora_1815_Revised_1080p_24fps.mp4','-map','0:v','-map','1:a','-c:v','libx264','-preset','fast','-crf','14','-threads','3','-c:a','copy','-t','5','-movflags','+faststart',o/'Tambora_First_5_Seconds_1080p_24fps.mp4'])
