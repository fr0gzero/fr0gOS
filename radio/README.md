# FrogOS tone pack for EdgeTX (RadioMaster Pocket)

Every English voice file on the radio is replaced by a tone with the same filename. Every event still makes a sound, just no voice.

The sound is soft and deadmau5-style: detuned saw plucks with a sine sub, a filter that snaps shut, and a dotted-eighth echo at 128 BPM, all in F minor.

| Sound | Means |
|---|---|
| rolled F minor add9 stab | radio start |
| 3 notes rising | ARMED |
| 3 notes falling | DISARMED |
| 2 notes rising | on / active / connected / recovered |
| 2 notes falling | off / disabled / lost |
| 3 quick beeps | warning (signal low, battery low, throttle or switch warning) |
| dark 3-note fall, twice | critical (telemetry lost, signal critical, failsafe) |
| 2 short plucks, low / mid / high | angle / horizon / acro (low to high, like the OSD) |
| high note + rising / falling | air mode on / off |
| filter riser + rising | turtle on |
| soft F minor chord + pluck | timer elapsed |
| silence | numbers and units, so spoken values disappear |

## Install

1. Plug the Pocket into the computer by USB and choose USB Storage (SD).
2. **Back up first:** copy `SOUNDS/en` to `SOUNDS_voice_backup/en`.
3. Unzip `frogos_tonepack_edgetx_en.zip` onto the SD card root and overwrite when asked. It only touches `SOUNDS/en/...`.
4. Eject and restart the radio.

To undo, copy the backup back over `SOUNDS/en`.

Regenerate with `python3 make_tone_pack.py <edgetx-sdcard-sounds/SOUNDS/en> <out>`. Filenames come from [EdgeTX/edgetx-sdcard-sounds](https://github.com/EdgeTX/edgetx-sdcard-sounds).
