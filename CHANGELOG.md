# Changelog

All builds are on Betaflight 2026.6.2.

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
