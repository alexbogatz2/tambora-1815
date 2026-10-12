# Opening timing correction

The previous opening had a genuine mismatch: the USGS plume source is labeled ×7 speed and played at 0.82 source seconds per output second, giving 5.74× real time. Ocean animation used its independent 3.4× hyperlapse default.

Revision 4 uses one TIME_SCALE = 5.74 for both. At output time t, plume source time is 7.50 + (5.74 × t)/7; the water phase uses 5.74 × t. Thus the five-second sample represents 28.7 seconds for both layers.

Both use a 180-degree virtual shutter at 24 fps: 1/48 output seconds, equivalent to 0.11958 real seconds. The video plume is averaged at three exposure samples; water sine phases are integrated analytically. Existing source video may already include camera exposure blur.

This fixes the temporal acceleration inconsistency. It does not establish measured ocean wave speeds or calibrate eruption size against the source event: water remains an animated still plate and the source plume is composited at an assumed scale. No other part of the full film changes.
