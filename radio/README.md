# fr0gOS tone pack for EdgeTX (RadioMaster Pocket)

Every English voice file on the radio is replaced by a tone with the same filename. Every event still makes a sound, just no voice.

The sound is soft and deadmau5-style: rounded saw plucks with a sine sub, a gentle filter pluck and one quiet dotted-eighth echo at 128 BPM, all in F minor. v3 (2026-11-08) is half the volume of v2 (about -14 dBFS peak), darker and about half as long, and the critical alert plays once.

| Sound | Means |
|---|---|
| rolled F minor add9 stab | radio start |
| 3 notes rising | ARMED |
| 3 notes falling | DISARMED |
| 2 notes rising | on / active / connected / recovered |
| 2 notes falling | off / disabled / lost |
| 3 quick beeps | warning (signal low, battery low, throttle or switch warning) |
| dark 3-note fall | critical (telemetry lost, signal critical, failsafe) |
| 2 short plucks, low / mid / high | angle / horizon / acro (low to high, like the OSD) |
| high note + rising / falling | air mode on / off |
| filter riser + rising | turtle on |
| soft F minor chord + pluck | timer elapsed |
| silence | numbers and units, so spoken values disappear |

## Install

1. Plug the Pocket into the computer by USB and choose USB Storage (SD).
2. **Back up first:** copy `SOUNDS/en` to `SOUNDS_voice_backup/en`.
3. Unzip `fr0gOS_tonepack_edgetx_en.zip` onto the SD card root and overwrite when asked. It only touches `SOUNDS/en/...`.
4. Eject and restart the radio.

To undo, copy the backup back over `SOUNDS/en`.

Regenerate with `python3 make_tone_pack.py <edgetx-sdcard-sounds/SOUNDS/en> <out>`. Filenames come from [EdgeTX/edgetx-sdcard-sounds](https://github.com/EdgeTX/edgetx-sdcard-sounds).

## Ten sound themes (2026-11-08)

`make_tone_themes.py` builds ten tone packs from completely different inspirations. They all share the same event vocabulary, so any of them can replace the voice pack.

Each audition in `themes/` plays: startup, armed, disarmed, angle, horizon, acro, air on, air off, turtle, telemetry recovered, telemetry lost (critical), warning, timer, trim tick.

| # | Theme | Inspiration |
|---|---|---|
| 01 | baroque | Harpsichord in D major. Cadences resolve when good; a diminished organ chord when bad. |
| 02 | starship | Sci-fi bridge computer: gliding sine chirps, ring-mod sparkle, pulsing alert. |
| 03 | dashboard | Cars: indicator relay, door-chime bongs, engine start and rev blips, reverse beeper. |
| 04 | gameshow | TV game show: marimba dings, soft buzzer, tick-tock clock, slide whistle. |
| 05 | 8bit | Chiptune pulse waves and a noise channel. |
| 06 | sonar | Submarine pings, Doppler drops, depth-charge thump, bubbles. |
| 07 | zen | Singing bowls, small bells, wood-block knocks. |
| 08 | dialup | 90s computer: DTMF keypad, PC speaker, floppy clicks, modem screech. |
| 09 | lounge | FM electric-piano jazz chords, vibraphone tremolo, brushes. |
| 10 | pond | Ribbits, croaks, crickets, water drops, a splash. |

To build the SD-card pack for one theme: `python3 make_tone_themes.py pack <theme> <edgetx-sdcard-sounds/SOUNDS/en> <out>`.
All original sounds; no theme tunes are copied.

**In use: pond** (`fr0gOS_tonepack_pond_edgetx_en.zip`), chosen 2026-11-08.
