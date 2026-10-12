# Motion review v2

## Why v1 review was insufficient

The earlier static montage and code review did not establish convincing temporal motion. User feedback correctly identified frozen water and unconvincing stitching. The v1 image plates are photorealistic, but that alone does not make their animation photorealistic.

## Actual v1 MP4 analysis

Decoded all 2,880 frames from `outputs/Tambora_1815_1080p.mp4`. Computed mean absolute adjacent-frame RGB differences after reduction to 480 × 270. Values below are 8-bit intensity units, not physical speed. Water ROI: rows 225–259, columns 50–429. Terrain ROI: rows177–209, columns180–299. Those named ROIs only correspond to those scene elements in the close offshore shots.

| Scene interval | Median water difference | Median ash difference | Finding |
|---|---:|---:|---|
| 2–24 s | 0.001 | 1.378 | Water effectively frozen while ash changes |
| 40–55 s | 0.006 | 0.334 | Mostly static water, interrupted by flash illumination |
| 55–75 s | 0.001 | 0.753 | PDC scene water effectively frozen |
| 75–88 s | 0.000 | 0.297 | Ejecta scene water frozen |

Sequential visual samples and amplified difference frames saved in `outputs/qa/v1_temporal_samples.jpg`. Raw per-frame measurements saved in `outputs/qa/v1_frame_differences.json`.

The 5.7-second flow-map wrap does **not** show a large discontinuity in the measured samples. The two staggered maps mathematically crossfade at zero weight for the resetting map. Do not diagnose a hard wrap discontinuity without evidence.

There are smaller encoded texture refresh jumps at scene + 10.417 seconds (250 frames). At 35.417s decoded adjacent difference is 0.923, while direct unencoded renderer comparison is 0.250; at65.417s 0.940 versus0.382; at85.417s 0.413 versus0.111. A shorter GOP and lower CRF may reduce codec texture-refresh changes. This is separate from the more consequential image-mask seam.

Sequential samples at11.4 and17.1 seconds expose a soft smeared outer plume boundary. It appears like revealing a photograph through a growing mask, with dark lobes lacking a convincing continuous eruptive connection. Broadening blur alone is not a solution. A continuous vent-connected mask with irregular edge and physically coherent upward growth should improve it.

## Required concrete remedies

1. Animate water locally, with perspective-aware traveling ripples and no displacement at the coastline. Keep the land rigid.
2. Use globally continuous water time across matching offshore plates. Avoid brightness flicker across the whole sea.
3. Improve hyperlapse plume-mask growth and connectivity. Avoid a rectangular or smeared detached patch.
4. Reduce encoded texture popping using an appropriate shorter keyframe interval and modestly higher encoding quality.
5. Inspect integrated sequential frames and adjacent differences from a v2 motion test before a full render. Remain at1080p24 until user approval; upscaling/interpolation does not solve temporal realism.

## v2 status

Water-motion module integrated. The 18-second motion test passed review; full-length revision is rendering.

## Integrated v2 motion-test review

Independently decoded all432 frames of `outputs/tambora_motion_test_v2.mp4` (18s at24fps). First12s map to film5–17s; final6s map to60–66s. Inspected consecutive full-resolution extracted plume crops around film12s and16s, including emitter/terrain contact and alpha edges. Saved `outputs/qa/v2_temporal_plume.jpg` and individual full frames; measurements in `outputs/qa/v2_frame_differences.json`.

The new true-alpha plume removes the broad smeared source-photo matte of v1. It remains visibly attached to the summit in consecutive samples, without the previous ghosted patch boundary. The embedded plume texture still stretches/grows as a 2.5D element: this review does not establish realistic three-dimensional turbulence.

Using identical downsampled ROIs, median water differences are now0.873 during the accelerated opening and0.206 during the PDC sample (v1 approximately0.001). Median terrain differences0.038 and0.015 remain low, consistent with largely rigid terrain and changing illumination/encoding. No abrupt land/water seam was identified in the inspected sequential images.

Short-GOP refresh frames still show modest intensity-difference bumps (for example frame48:1.495 versus neighbors0.967/1.023; frame96:2.530 versus2.101/2.136). They are much smaller than scene cuts or flash effects and do not establish an obvious broken transition. Further codec optimization was not required for this revision.

**Decision:** Proceed to full1080p24 render using the reviewed code. The revision materially corrects frozen water and the broad hyperlapse matte seam. Approval is limited to those corrections and sampled temporal continuity; it does not certify photorealistic fluid dynamics, historical camera geometry, or physically calibrated flow speed. No4K or frame-rate interpolation requested at this stage.

## Final assembled-picture check

Decoded the completed `tambora_picture_v2_1080p.mp4`: metadata1920×1080,24fps,2,880frames. Checked all96frames from53–57s and456frames from87–106s. No exact adjacent duplicates or black frames in those intervals. The55s section join is an intentional viewpoint cut;105s is the intended cut to the aerial aftermath. Sequential samples show no doubled whole-mountain crossfade.

A residual limitation is visible: isolated dark terrain-colored fragments appear above parts of the skyline (left slope near87s and right side near the end of collapse). These may arise from terrain/ash masking or the source image; they should not be described as verified ejecta or as artifact-free. Reported to coordinator rather than silently approving. The major frozen-water and broad source-photo matte defects are corrected, but this remains a2.5D reconstruction with visible limitations.

Evidence: `outputs/qa/final_v2_join_collapse.json`, `outputs/qa/final_collapse_sequence.jpg`, and selected full-resolution frames.

### Skyline defect resolved in corrected encoded master

Animator traced the floating fragments to ash remapping that sampled terrain below an approximate skyline. A conservative zero-velocity buffer above the skyline prevents terrain texels entering the moving ash region. Reviewed corrected direct frames, then independently decoded the patched master and inspected three consecutive frames at86.95s,102s,104.8s. The previously flagged floating fragments are absent. Evidence: `outputs/qa/corrected_skyline_temporal.jpg`.

Repeated the targeted join/collapse decode because those inputs changed:96frames53–57s and456frames87–106s contain no black frames or exact adjacent duplicates. Intended scene cuts remain. Metadata still1920×1080,24fps,2,880frames. **Final decision: approved for mux and delivery within the documented motion/compositing correction scope.** The earlier residual-floating-fragment warning is superseded by this correction; general2.5D physical-realism limitations remain.
