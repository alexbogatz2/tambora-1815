# Tambora — April 1815

A 120-second cinematic animated reconstruction made with locally rendered effects, generated photographic plates, and synthesized sound. No paid external generation API is used by the rendering scripts.

## Reproduce

Requires Python 3.12+, FFmpeg with libx264 and Flite, and the packages in requirements.txt.

```sh
python -m pip install -r requirements.txt
python src/render_video.py
python src/render_audio.py
python src/assemble.py
```

The video renderer creates a 1920×1080, 24 fps picture master. Assembly writes an H.264/AAC 1080p MP4 and a Lanczos-upscaled 3840×2160 MP4. Source plates are 1672×941; the 4K file is not native 4K footage. See `docs/scientific_review.md` for source evidence and reconstruction limitations.

## Chapters

| Seconds | Scene |
|---|---|
| 0–25 | Accelerated escalation from the coast |
| 25–40 | Distant eruption column |
| 40–55 | Ash-darkened lightning |
| 55–75 | Pyroclastic density currents |
| 75–88 | Incandescent ejecta |
| 88–105 | Ash-obscured accelerated collapse |
| 105–120 | Caldera aftermath |

Only time-acceleration labels and closing titles appear onscreen. Scientific notes remain outside the film.

## Production team

- Coordinator: project structure, scene plates, integration, final export and delivery.
- Animation agent: deterministic masked texture advection, progression, procedural lightning and ballistic particles.
- Audio agent: stereo ambience, delayed reports and thunder, sparse locally synthesized narration.
- Independent reviewer: research evidence, source plate review, montage and renderer review.

This is an image-based animated reconstruction, not a validated multiphase fluid simulation. Exact terrain before eruption, lightning details, cloud shape, and the visible collapse sequence are interpretive. The generated images are assets for this project, not historical photographs.
