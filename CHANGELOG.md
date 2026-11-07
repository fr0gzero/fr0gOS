# Changelog

All builds are on Betaflight 2026.6.2.

Radio: `radio/` has the EdgeTX tone pack for the Pocket (deadmau5-style synth tones instead of voice).

## v1.3 r08 - 2026-11-08 (MK4-2 test build)
- Layout C (corners) chosen. Left: frog row 0, event log rows 1-5, power 7-9, links 13-16. Right: name 0, time 1, warnings 2, ARMED / mode / AIR 3-5, THR + RPM + G cluster in the bottom corner 12-16.
- Event log is 5 lines. A new message pops in at the top and pushes the older ones down. Each disintegrates into glyphs 4 s after it appears, then disappears.
- Core temp and flight counter removed from the layout.
- Screensaver back on (Matrix rain in the bars after 5 s idle; text shimmer on analog).

## v1.3 r07 - 2026-11-08 (MK4-2 test build)
- No more glyphs across the picture. The arm screen is a centre message only: `ARMED` (plus the crash flip text when flipping) glyphs in for 0.4 s, holds, then glyphs out (1.6 s total). The noise sweep, strays, Matrix rain / shimmer screensaver and HISCORE fireworks are gone. Glyphs stay on side-column changes (feed, mode changes, appear/vanish).
- The frog hops around the black bars. On events (arm, crash flip, mode / air changes, tricks, warnings) it jumps to a random free spot worked out from the live layout. Never sooner than 12 s after the last hop, 50/50 between 12 and 20 s, certain after that, so roughly every 15-20 s of flying. A hop is a glyph puff where it was, a puff where it lands, then the frog.
- Removed from the layout: RSSI dBm, ESC temp, `HDZRO` and the camera lines (and battery % from r05).
- Three layout options (`fonts/hdzero-hacker/frogos_layout_v14_options.png`): A mirrored (default), B eye line, C corners. `quads/mk4-2/layouts/layout_A|B|C.txt` swap between them without reflashing.

## v1.3 r06 - 2026-11-08 (MK4-2 test build)
- `THR` label above throttle and `RPM` label above RPM. Each readout draws its own label on its row and the value on the row below.
- Right column: THR 9, throttle 10, RPM 11, RPM value 12, G 13, ESC temp 14, core temp 15, flights 16.

## v1.3 r05 - 2026-11-08 (MK4-2 test build)
- Activity feed lines glyph away 5 s after they appear, like chat history.
- The frog moves top left (row 0) with the feed under it (rows 1-2). The arm hop goes right to left and lands it there. The craft name is plain `MK4-2`.
- `FLOAT` and `CHOP` removed. `ROLL` / `FLIP` / `SPIN` only fire on a full 360 on that axis (gyro integrated while it keeps turning one way).
- Throttle to a tenth of a percent (`45.3%`), no icon, heat colours (amber 80%+, red 95%+). RPM as the whole number (`38214`), still heat-coloured.
- `ARMED` instead of `[ARM]` (readout and arm screen).
- Battery % retired (the voltage carries the stage colours). The left column moves down: power rows 4-6, links 8-12, video 13-16.

## v1.3 r04 - 2026-11-08 (MK4-2 test build)
- **Activity feed**, top left, two lines (`osd_frog_feed_pos`, replaces `osd_frog_tag_pos`). It shows what the pilot is doing, for the viewer. The newest event types in through glyphs and stays; the previous one drops to line 2.
  - Switches: `ANGLE` `HORZN` `ACRO`, `AIR` `NOAIR`, `ARMED` `SAFE`, `TURTL`, `BEEP`, packet rate and VTX power changes.
  - Flying: `PUNCH` (throttle past 90%), `CHOP` (60%+ to under 8% within 0.3 s), `ROLL` / `FLIP` / `SPIN` (about 85% of max rate), `FLOAT` (under 0.35 G for 0.25 s).
  - Hits: `3.6G!` (3 G+), `CRASH` (4.5 G+), `RECRD` (beats your best G).
  - Warnings: every new warning except battery and temperature.
- Battery noise in the black bars removed completely (`osd_frog_noise_pos = 0`).
- Six battery stages, per cell, from the live sag voltage (about 5 Hz), so a hard punch drops it into the low stages and it comes back when you ease off (0.02 V hysteresis):
  - FULL 4.00 / GOOD 3.80 / MID 3.65: green; bar glyph 4 / 3 / 2.
  - LOW 3.50: amber breathing; bar 1.
  - LAND 3.35: red/amber pulse; bar blinking.
  - DEAD under 3.35: red flicker, % scrambles, bar strobes.
  - The bottom three animate all the time. Voltage, % and bar follow the stage on HD. Analog: the % blinks (LAND) and scrambles (DEAD); the voltage stays plain.
- The frog sweats from LOW down. Betaflight warnings line up with the stages: `vbat_warning_cell_voltage = 350`, `vbat_min_cell_voltage = 335`.
- RPM is livelier: always one decimal (`38.2K`), and on HD it heats up against this quad's own best RPM: amber from 60%, red from 85%, red/amber flicker at 97%+.

## v1.3 r03 - 2026-11-08 (MK4-2 test build)
- Battery noise, Matrix rain and HISCORE fireworks use 5 columns each side on HD (was 6), so they stay in the black bars instead of creeping over the picture.
- The frog is the dash in the craft name: `MK4`, frog, `2`. The arm hop lands it there.
- `FR0G` + cursor tag top left removed for now (`osd_frog_tag_pos = 0`).

## MK4-2 CLI update - 2026-11-08
- Battery warnings were set far too low in MK4-2's battery profile (LOW 3.20 V, LAND 3.10 V), so the warning came when the pack was already dead. Now LOW 3.50 V and LAND 3.30 V (Betaflight defaults). `quads/mk4-2/battery_warning_fix_2026-11-08.txt` applies it without reflashing.
- `tools/make_hd_cli.py`: per-quad extras that set something already in the diff now replace it in place.

## v1.3 r02 - 2026-11-07 (MK4-2 test build)
- Crash flip gets the glitch treatment. Arming into crash flip plays a red sweep that travels up the screen. `[ARM]` decodes in, then the crash flip text decodes in from red noise and keeps glitching red/amber.
- The `TURTL` warning no longer blinks. On HD it chases red/amber with scrambles; on analog, one character of its own text scrambles now and then.
- Core temp warning at 75 C (`osd_core_temp_alarm = 75`, was 70).
- Test flight note: if the upside-down frog shows as an `E`, the goggles still have the v1.1 font. Copy the current `BTFL_000.bmp` / `BTFL_FHD_000.bmp` to the SD card.

## v1.3 r01 - 2026-11-07 (MK4-2 test build)
- **New layout**, ordered by what matters in flight (see `fonts/hdzero-hacker/frogos_layout_v13_proposal.png`):
  - Left column: power top, then links (LQ, dBm, packet rate, VTX channel and power), then video (`HDZRO` + camera mode) at the bottom.
  - Right column: time and warnings top (warnings moved up from the bottom, empty until something's wrong), then state (ARM, mode, AIR), then performance (throttle, RPM, G), then system (ESC and core temp, flights).
- G meter heats up: green, amber from 1.5 G, red from 2.5 G, red/amber flicker with glitches from 3.5 G. Holds the peak 0.5 s. Shows `!` and a colour chase while beating your all-time best G.
- Appear/vanish: readouts decode in and dissolve out through brief glyph flashes. The whole OSD does it when it comes back after boot, arming, HISCORE or the screensaver.
- Analog effects scaled back so nothing lands in empty space: battery % glitches at LAND / DEAD, no arm sweep or fireworks, text shimmer instead of Matrix rain, plain G number.
- Boot screen `VIDEO HDZERO` (or `ANALOG`) line.
- Only MK4-2 is built so far. MK5-1 and MK4-1 stay on v1.2 r03 until the test flight.

## v1.2 r03 - 2026-11-07
- Mode-change reaction: when flight mode, air mode, ELRS packet rate or VTX power changes, the new text decodes in from coloured noise, then green/amber/red chase along it for 0.8 s before it settles (decode only on analog). Live readouts (volts, timer, G, RPM...) don't react.
- Air mode reads `AIR` when on and is blank when off (was `AIRON` / `NOAIR`).

## v1.2 r02 - 2026-11-07
- Matrix rain screensaver starts after 5 s disarmed and still (was 60 s).
- HISCORE.EXE shows best G only (this flight and the old record). Best RPM is still recorded but no longer shown.
- `BEST LAP --.--` placeholder on HISCORE.EXE, ready for the lap timer.
- The frog flips onto its back whenever the quad is upside down (tilted past 90 degrees), not just in turtle mode.

## v1.2 r01 - 2026-11-07 (arcade)
- **HISCORE.EXE replaces the post-flight stats.** Only the arcade numbers: best G and best motor RPM, with this flight and the old record, plus lifetime flights and air time. It types out like a DOS listing at 10 fps.
- **New record animation:** `NEW HIGH SCORE` decodes in from noise, then green/amber/red chase along it; frogs hop and croak either side, the record flashes amber/red, and fireworks pop in the black bars. Records only count on flights of 15 s or more and are saved with the lifetime stats (`frog_best_g10`, `frog_best_rpm`).
- **Battery noise in the black bars**, in four stages that escalate in colour and amount: SAG (0.20 V/cell+ dip under load, green, 1-4 chars), LOW (below the warning voltage, amber, 4+), LAND (below the minimum voltage, red, 8+), DEAD (0.30 V/cell under the minimum, red flood, 14). Telemetry is drawn over it so numbers stay readable. Position: `osd_frog_noise_pos`. No link-quality noise.
- **Frog moods (HD):** sweats on low battery, flips on its back in turtle mode, squashes flat when pulling 2.5 G or more.
- **Arm (HD):** after the glitch sweep the frog hops along the top bar and lands next to the craft name (arm screen 0.9 s on HD, 0.6 s analog).
- **Matrix rain screensaver:** after 60 s disarmed with the sticks still, green characters fall down the black bars. Any stick movement or arming brings the OSD straight back.
- **Boot:** lines type out with a cursor before their status, plus an `UPTIME ... FLIGHTS` line.
- **Charge-up battery:** when the OSD comes up, the battery % and bar fill from zero like a boot meter.
- OSD at 20 fps (`osd_framerate_hz = 20`). About 390 bytes a frame over MSP at 20 fps is about 7.8 KB/s, within the ~11.5 KB/s that 115200 baud carries.
- Goggle font adds sweat, flip and squash frogs and red noise blocks in the unused compass slots 0x18-0x1F. **HDZero goggles need the new BTFL_000.bmp / BTFL_FHD_000.bmp.**
- Stats PG version 5: the lifetime stats reset (a full chip erase clears them anyway).

## v1.1 r04 - 2026-11-07
- Throttle readout gets the throttle icon back (icon + `45%`) so it can't be mistaken for battery %.
- Flight-time-left estimate removed. `osd_cap_alarm` back to its previous values. Motor RPM moves up into the gap.

## v1.1 r03 - 2026-11-07
- New on every quad: flight time left (`02:10`, estimated from mAh used against `osd_cap_alarm`), average motor RPM (`38K`, one line, from bidirectional DShot), g-force (`2.1G`), and lifetime flight count (`#127`; a flight counts once armed for 15 s, `stats_min_armed_time_s = 15`). Flight count restarts at 0 after a full chip erase.
- HDZero quads also show ESC temperature (`E48`, the hottest ESC; `E--` if the ESC doesn't report it). Left off MK4-1, whose ESC firmware doesn't report temperature.
- `osd_cap_alarm` set to about 80% of the pack: MK5-1 440 (550 mAh). MK4-1 and MK4-2 assume a 300 mAh 1S (240).

## v1.1 r02 - 2026-11-07
- Top bar tag is `FR0G` (DOS-font zero, matching the other zeros).
- Camera mode on the OSD: `osd_custom_msg0`-`3` text and positions can now be set from the CLI, and unset lines show nothing (stock showed `CUSTOM_MSG1`). MK5-1 shows `540P` / `90FPS` / `CROP` middle left.
- VTX power has its own element, `osd_frog_vtxpwr_pos` (`200MW`). The VTX channel element is now just band and channel (`R8`).
- Shared HDZero block in `tools/make_hd_cli.py` gains the camera lines and VTX power. MK5-1 and MK4-2 CLIs regenerated from it.
- MK4-2 camera lines `720P` / `60FPS` / `4:3` (HDZero Eco set to 4:3).
- Layout: link moves to middle left and camera / video format to bottom left, on all three quads.
- MK4-1 (analog) gets the camera block (`ANT` / `NTSC` / `16:9`) and VTX `R8` / `200MW`. Its layout is respaced to fit rows 0-11.

## v1.1 r01 - 2026-11-07 (hacker)
- MK4-1 (analog) moved to v1.1: decoding warnings, BIOS boot, arming glitch and `[ARM]` in mono. `FROG` with a blinking `_` top left, `MK41` top right.
- HDZero hacker font (IBM VGA 8x16, phosphor green) with per-character amber and red copies of the alphabet. The logo shrinks to 24x2.
- New setting `osd_frog_hd_font`. Colour and glyphs only apply on MSP displayport.
- Elements in warning or critical state draw amber or red.
- New warnings decode in from noise.
- New elements: `osd_frog_tag_pos` (FROG + blinking cursor) and `osd_frog_craft_pos` (animated frog + craft name).
- Battery bar glyph. The receiver shows `SCAN` with a spinner until linked.
- `[ARM]` when armed. Arming plays a glitch sweep with `[ARM]` decoding in.
- Boot checks tick in one at a time with coloured status.
- Glitch rows are sent in MSP-sized chunks, because MSP displayport caps one write at 30 characters.
- OSD config PG version 13 to 14.
- MK5-1 moved from Betaflight 2025.12.1. VTX power fixed from 25 mW to 200 mW.
- MK4-2 CLI regenerated with the shared HD block, so its OSD is identical to MK5-1's.
- Top bar names: `FROG`, `MK51`, `MK42`. Four characters plus the cursor or frog fits the 5-character bar.

## v1.0 r03 - 2026-11-06
- Icons and unit glyphs stripped so nothing creeps past the black bars.
- Air mode reads `AIRON` / `NOAIR`.
- All warnings 5 characters; core temp warning is `HOT70`.

## v1.0 r02 - 2026-11-06
- Edge justification anchors to the element's own column, fixing MK4-2's right column landing off the goggle screen.
- MK4-2 canvas 50x18. Layout grouped by category top to bottom.

## v1.0 r01 - 2026-11-06
- First FrogOS build for MK4-1 and MK4-2.
- Live boot status block. ARM / SAFE. Separate flight mode and air mode. ELRS 4 packet rate. Battery %. LQ as `LQ99`. CPU temp as `C45`. Edge justification. Default rates baked in.
- MK4-2 built with `-DUSE_ELRSV4` for its SPI receiver.
