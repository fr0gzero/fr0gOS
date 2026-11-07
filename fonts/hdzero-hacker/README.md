# FrogOS HDZero hacker font

Goggle font for FrogOS v1.1+. Copy `BTFL_000.bmp` and `BTFL_FHD_000.bmp` to `resource/OSD/FC/` on the HDZero goggle SD card.
Needs FrogOS v1.1 firmware on every Betaflight HDZero quad (it moves the logo to 24x2 and reuses unused symbol slots for colour).

- 0x20-0x5F green text, 0xA0-0xCF logo, 0xD0-0xF8 amber text, red text in unused symbol slots, 0xF9-0xFF frog/cursor/noise, 0x11-0x15 battery bar.
- Rebuild with `tools/build_hacker_font.py` (also regenerates `src/main/osd/frog_charmap.h` for the firmware).

Text glyphs: "IBM VGA 8x16" from The Oldschool PC Font Resource by VileR (https://int10h.org/oldschool-pc-fonts/), licensed CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/); bitmaps taken from susam/pcface. This font file is a modified version and is shared under the same licence. Symbol glyphs from the stock HDZero Betaflight font (hd-zero/hdzero-goggle).
