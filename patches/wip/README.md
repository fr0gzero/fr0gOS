# Work in progress

`frogos-v1.3-wip_on_v1.2-r03.patch` applies on top of `frogos-v1.2-r03_betaflight-2026.6.2.patch`. It isn't flashed or released yet.

- G meter heat: green, amber from 1.5 G, red from 2.5 G, red/amber flicker with glitches from 3.5 G. Holds the peak for 0.5 s. Shows `!` with a colour chase while beating your all-time best G.
- Analog scale-back: no glyphs in empty space.
  - Battery % glitches at LAND and DEAD instead of noise in the bars.
  - No arm noise sweep; no HISCORE fireworks.
  - Text shimmer instead of Matrix rain.
  - Plain G number.
- Appear/vanish: readouts decode in and dissolve out through brief glyph flashes. The whole OSD does it when it comes back after boot, arming, HISCORE or the screensaver.
- Boot screen `VIDEO HDZERO` / `ANALOG` line.

Builds clean for all three targets. It ships as v1.3 together with the layout in `fonts/hdzero-hacker/frogos_layout_v13_proposal.png`.
