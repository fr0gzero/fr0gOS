# fr0gOS HDZero hacker font

Goggle font for fr0gOS v1.1+. Copy `BTFL_000.bmp` and `BTFL_FHD_000.bmp` to `resource/OSD/FC/` on the HDZero goggle SD card.
Made for fr0gOS v1.3 r09+: the boot logo is gone and its slots, plus symbols a whoop never draws (GPS, compass, AH, units), hold the 80-glyph frog. Older fr0gOS builds still run on it but show the wrong frog and logo glyphs.

- 0x20-0x5F green text, 0xD0-0xF8 amber text, red text in unused symbol slots, 0xFC-0xFF cursor and noise, 0x1D-0x1F red noise, 0x11-0x15 battery bar.
- Frog: 0xA0-0xCF, 0xF9-0xFB, 0x18-0x1C, 0x70-0x74, 0x78, 0x7A, 0x7C-0x7F, 0x8A-0x8F, 0x97, 0x9A, 0x02, 0x03, 0x05, 0x08, 0x09 (slot map in `src/main/osd/frog_anim.h`).
- Rebuild with `tools/build_hacker_font.py` (also regenerates `src/main/osd/frog_charmap.h` and `frog_anim.h` for the firmware).

Text glyphs: "IBM VGA 8x16" from The Oldschool PC Font Resource by VileR (https://int10h.org/oldschool-pc-fonts/), licensed CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/); bitmaps taken from susam/pcface. This font file is a modified version and is shared under the same licence. Symbol glyphs from the stock HDZero Betaflight font (hd-zero/hdzero-goggle).
