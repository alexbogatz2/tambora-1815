# Scientific and visual review — Tambora reconstruction

## Evidence used

| Topic | Evidence status | Production interpretation |
|---|---|---|
| April 10–11, 1815 climax | Supported by deposit reconstructions and historical reports synthesized by Raible et al. (2016) and Self et al. (2004) | Opening escalation compresses hours; individual pulses are invented, not timed historical measurements. |
| VEI 7 | Smithsonian GVP eruptive history | End card may state VEI 7. |
| Pre-eruption summit about 4,300 m / 14,100 ft | Common reconstruction estimate; not a surveyed pre-1815 elevation | Broad steep-sided cone; do not claim surveyed geometry. Smithsonian's separate approximately 4,000 m figure refers to an earlier, >43,000-year-old edifice and must not be confused with this estimate. |
| Approximately 40 km column | Raible et al. summarize estimated maximum/overshoot heights; most gas need not reach the top | Extreme wide view should distinguish a high overshooting top from the lower spreading cloud. |
| PDCs and heavy ashfall | Geological evidence; GVP records currents reaching the sea on all sides of the peninsula | Downhill ground-hugging basal flow with lofted ash; no lava tsunami. |
| Roughly 6–7 km caldera | Geological observation; GVP gives 6 km and Raible gives 7 × 6 km | Summit subsidence, not whole-mountain detonation. Exact collapse order and visibility remain uncertain. |
| Volcanic lightning | Well-established ash-plume phenomenon; no scene-specific Tambora discharge record verified here | Irregular short discharges constitute plausible reconstruction. |
| Year Without a Summer | Strongly supported atmospheric linkage | Long-lived cooling is principally associated with stratospheric sulfate aerosol formed from sulfur gases, not coarse ash lingering for years. |

## Concrete visual direction

- Preserve coastline and lower edifice when animating ash textures. Do not warp the whole photograph.
- Ash motions should expand and rise irregularly. PDC basal motion should spread down/out, with billowing upper regions.
- Keep incandescent fragments restricted near the vent; no broad glowing plume or continuous liquid lava fountain.
- Use short irregular lightning flashes. Avoid synchronizing distant thunder exactly with flashes.
- At 10 km sound takes about 29 seconds at 343 m/s; a brief shot can legitimately show a flash whose thunder is not heard within that shot. Continuous distant rumble need not match a visible pulse.
- Hide uncertain summit failure behind ash rather than showing an implausibly precise or rubber-like collapse.
- The aftermath generated plate includes a central irregular mound. It must not be represented as the documented modern intracaldera cone: GVP records later 19th/20th-century dome and lava activity. Obscuring this region with haze is a conservative approximation.
- Requested TIME ACCELERATED indicators belong only to opening and collapse. No uncertainty warnings are required inside the film. Scientific qualifications stay in these external notes.

## Asset inspection

All five supplied plates were visually inspected. The three close offshore views preserve major shoreline features well. The extreme wide column has a useful mountain-to-column scale difference. Cloud detail is visually plausible as an artistic texture, but repeated rounded lobes and any texture warping must not be described as validated fluid simulation. The aftermath topography and exact coastline are generated approximations, not a georeferenced terrain model.

## Honest delivery scope

This production uses generated photorealistic image plates with procedural animation, compositing, and synthetic sound. It is not a computationally validated multiphase-flow simulation or historical footage. Final resolution alone does not establish native 4K detail. The exact pulse sequence, lightning, illumination, collapse sequence and hypothetical camera locations are reconstructions. These statements belong in delivery notes, not on-screen warnings.

## Sources

1. Smithsonian Global Volcanism Program, Tambora profile and eruptive history: https://volcano.si.edu/volcano.cfm?vn=264040
2. Raible et al. (2016), *Tambora 1815 as a test case for high impact volcanic eruptions: Earth system effects*, WIREs Climate Change 7:569–589, doi:10.1002/wcc.407. https://onlinelibrary.wiley.com/doi/full/10.1002/wcc.407 ; open manuscript https://climate.envsci.rutgers.edu/pdf/RaibleTambora_wcc407.pdf
3. Sigurdsson & Carey (1989), *Plinian and co-ignimbrite tephra fall from the 1815 eruption of Tambora volcano*. Institutional record and abstract: https://digitalcommons.uri.edu/gsofacpubs/1103/
4. Self et al. (2004), *Magma volume, volatile emissions, and stratospheric aerosols from the 1815 eruption of Tambora*. https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2004GL020925
5. Aplin, Houghton & Nicoll (2014), *Electrical charging of ash in Icelandic volcanic plumes*. https://arxiv.org/abs/1404.6905 (mechanism reference; not direct evidence of specific Tambora lightning).

## Final QA

Pending rendered preview. Static assets alone do not verify motion, continuity, timing, or audio propagation.

### Preview and renderer review

Reviewed nine-frame preview montage and `src/render_video.py`. Offshore coastline continuity is preserved; the preview contains restrained local incandescence and no nuclear-style fireball. Accelerated sections have a discreet time label. End-card wording matches the requested qualified historical claim. Central caldera haze reduces the prominence of the generated mound.

Code inspection confirms masked ash-texture advection, downward/outward PDC displacement, intermittent lightning, gravity-like downward acceleration of near-vent particles, and ash cover during the collapse transition. These are visual approximations: no spatial calibration establishes actual flow velocity, and the renderer does not solve mass, energy, or momentum conservation. The result can be described as an animated reconstruction, not a physically validated simulation. Static montage review does not certify the completed encoding or audio track; those require the coordinator's final file checks.
