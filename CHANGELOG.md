# Changelog

All builds are on Betaflight 2026.6.2.

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
