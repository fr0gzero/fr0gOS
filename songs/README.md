# fr0gOS songs

Cue points for a track, baked into the firmware so the OSD calls the song while you fly.

1. **Mark it:** open the fr0gOS Songbook page, drop the track in, fix the suggested cues (it finds the drops, choruses, build-ups and the outro from the audio, and works out the BPM), check them on the goggle preview.
2. **Send it:** "Send to Dax" (or copy the cue sheet). The sheet lands here as `songs/<title>.txt`.
3. **Build it:** `python3 tools/make_song.py songs/<title>.txt src/main/osd/frog_song.h`, then build the firmware.
4. **Radio:** "Save radio pack" gives `SOUNDS/en/<NAME>.wav` (32 kHz mono). On the Pocket: CH9 (AUX 5) from the SONG switch, and a Special Function on the same switch: Play Track <NAME>, 1x.

In the air: flip the SONG switch, the radio starts the track and fr0gOS starts the cue clock (Betaflight mode USER1 on AUX 5). Flip it back to stop the cues.

| Cue | On screen |
|---|---|
| `DROP` | amber `DROP IN 3 2 1` (one tick apart), then a red `DROP` |
| `BIGDROP` | red `BIG DROP IN 3 2 1`, then `>>>DROP<<<` swapping red / amber |
| `CHORUS` | amber `CHORUS` |
| `BUILD` | green `BUILD...` |
| `TEXT xxx` | your own words (up to 9 characters) |
| `END` | green `OUTRO` |

The tick is one bar at the song's BPM (`bpm 174`) or a time in seconds (`tick 1.0`). `test.txt` is the test song in the r23 build: no music needed, flip the switch and watch.
