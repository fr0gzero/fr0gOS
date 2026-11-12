#!/usr/bin/env python3
"""fr0gOS song cues: cue sheet (text) -> src/main/osd/frog_song.h, baked into the firmware.

The cue timer starts when the SONG switch (Betaflight mode USER1) turns on; the radio starts the song with the
same switch, so the two stay in sync.

Cue sheet:
    title  SANDSTORM          # up to 20 characters, shown when the song starts
    start  boot               # optional: run the cues from power-on every time (no SONG switch; arming doesn't matter)
    tick   1.0                # seconds between the 3 / 2 / 1 of a countdown (or: bpm 174 -> one bar)
    0:58.0 DROP               # "DROP IN 3 2 1", then DROP
    1:30   CHORUS
    2:10.5 BIGDROP            # "BIG DROP IN 3 2 1", then a bigger DROP
    2:40   EVENT CLIMB | 3        # your own word, up to 12 characters: "CLIMB IN 3 2 1", then CLIMB (count 0-9, default 3)
    1:00   TEXT SEND IT       # your own words, up to 9 characters
    3:05   END                # OUTRO
    0:00   PHASE TREE DANCE                    # a flight phase: shown top centre and kept up
    0:30   PHASE ORBITS | EXIT TREE IN | 5     # "EXIT TREE IN 5 4 3 2 1", then ORBITS stays up
    0:50   PHASE CLIMB | CLIMB IN | 4          # name | count-in words | count (ticks, 0-9; 0 = no count-in)
Phase names and count-in words: up to 12 characters each. Leave the words out and they default to "<NAME> IN";
leave the count out and it's 5. The phase holds until the next phase's count-in, an END, or the switch going off.
    artist SOMEONE            # accepted (the Songbook writes it); the firmware shows the title
Times are m:ss(.s) or plain seconds. # starts a comment. A TEXT with | (several lines) keeps its first line.

usage: make_song.py <cue sheet> <frog_song.h>
"""
import re
import sys

TYPES = {"DROP": "DROP", "BIGDROP": "BIGDROP", "CHORUS": "CHORUS", "END": "END", "OUTRO": "END",
         "BREAK": "TEXT", "TEXT": "TEXT", "PHASE": "PHASE", "EVENT": "EVENT"}
# On screen (all centred): row 1 = EVENT / PHASE count-ins and names, row 3 = TEXT notes,
# bottom = the music (title, DROP IN 3 2 1 / DROP, BIG DROP, CHORUS, OUTRO).
CHARSET = set(" !#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_")


def secs(t):
    if ":" in t:
        m, s = t.split(":", 1)
        return int(m) * 60 + float(s)
    return float(t)


def clean(text, n):
    text = text.upper()
    bad = sorted(set(c for c in text if c not in CHARSET))
    if bad:
        raise SystemExit(f"characters the OSD font can't show: {''.join(bad)!r} in {text!r}")
    if len(text) > n:
        raise SystemExit(f"{text!r} is longer than {n} characters")
    return text


def parse(path):
    title, tick, cues, boot = "SONG", 1.0, [], False
    for no, raw in enumerate(open(path, encoding="utf-8"), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        word, _, rest = line.partition(" ")
        rest = rest.strip()
        if word.lower() == "title":
            title = clean(rest, 20)
        elif word.lower() == "start":
            if rest.lower() not in ("boot", "switch"):
                raise SystemExit(f"line {no}: start is 'boot' (from power-on) or 'switch' (the SONG switch)")
            boot = rest.lower() == "boot"
        elif word.lower() == "artist":
            pass                                     # the Songbook writes it; the firmware shows the title only
        elif word.lower() == "tick":
            tick = float(rest)
        elif word.lower() == "bpm":
            tick = 4 * 60.0 / float(rest)            # one bar of 4/4
        else:
            m = re.match(r"^(\d+(?::\d+(?:\.\d+)?)?|\d*\.\d+)$", word)
            if not m:
                raise SystemExit(f"line {no}: can't read the time {word!r}")
            kind, _, label = rest.partition(" ")
            kind = kind.upper()
            if kind == "BREAK" and not label:
                label = "BREAK"
            if kind == "BUILD":
                raise SystemExit(f"line {no}: BUILD is gone - use EVENT <WORD> | <count>, e.g. EVENT CLIMB | 3")
            if kind not in TYPES:
                raise SystemExit(f"line {no}: unknown cue {kind!r} (DROP BIGDROP CHORUS END TEXT PHASE EVENT)")
            if TYPES[kind] == "EVENT":
                parts = [p.strip() for p in label.split("|")]
                name = clean(parts[0], 12)
                if not name:
                    raise SystemExit(f"line {no}: an EVENT needs a word, e.g. EVENT CLIMB | 3")
                count = int(parts[1]) if len(parts) > 1 and parts[1] else 3
                if not 0 <= count <= 9:
                    raise SystemExit(f"line {no}: the count-in has to be 0-9 ticks")
                cues.append((secs(word), "EVENT", name, "", count))
                continue
            if TYPES[kind] == "PHASE":
                parts = [p.strip() for p in label.split("|")]
                name = clean(parts[0], 12)
                if not name:
                    raise SystemExit(f"line {no}: a PHASE needs a name")
                count = int(parts[2]) if len(parts) > 2 and parts[2] else 5
                if not 0 <= count <= 9:
                    raise SystemExit(f"line {no}: the count-in has to be 0-9 ticks")
                if secs(word) == 0:
                    count = 0                        # the opening phase: nothing to count in to
                if len(parts) > 1 and parts[1]:
                    prompt = clean(parts[1], 12)
                elif count == 0 or len(name) <= 9:
                    prompt = name + " IN" if len(name) <= 9 else ""
                else:
                    raise SystemExit(f"line {no}: '{name} IN' won't fit in 12 characters: give the count-in words, "
                                     f"e.g. PHASE {name} | NEXT IN | {count}")
                cues.append((secs(word), "PHASE", name, prompt, count))
                continue
            if TYPES[kind] == "TEXT":
                lines = [clean(x.strip(), 30) for x in label.split("|") if x.strip()][:2] or ["BREAK"]
                label = "|".join(lines)                  # up to two lines of 30
            else:
                label = clean(label.split("|")[0].strip() or {"END": "OUTRO"}.get(TYPES[kind], kind), 9)
            cues.append((secs(word), TYPES[kind], label, "", 0))
    cues.sort()
    if not 0.1 <= tick <= 5.0:
        raise SystemExit("tick must be between 0.1 and 5 seconds")
    return title, tick, cues, boot


def header(title, tick, cues, src, boot=False):
    out = ["// Generated by tools/make_song.py from %s - do not edit by hand." % src,
           "// fr0gOS song cues (see the cue sheet for the times).", "#pragma once", "",
           '#define FROG_SONG_TITLE "%s"' % title, "#define FROG_SONG_TICK_MS %d" % round(tick * 1000),
           "#define FROG_SONG_CUES %d" % len(cues), "#define FROG_SONG_START_BOOT %d" % (1 if boot else 0), "",
           "#ifdef FROG_SONG_TABLES"]
    body = ",\n".join('    { %d, FROG_CUE_%s, "%s", "%s", %d }' % (round(t * 1000), k, lab, pr, n) for t, k, lab, pr, n in cues) \
        or '    { 0, FROG_CUE_NONE, "", "", 0 }'
    out += ["static const frogCue_t frogSongCues[] = {", body, "};", "#endif", ""]
    return "\n".join(out)


if __name__ == "__main__":
    title, tick, cues, boot = parse(sys.argv[1])
    open(sys.argv[2], "w").write(header(title, tick, cues, sys.argv[1].split("/")[-1], boot))
    for t, k, lab, pr, n in cues:
        words = pr if k == "PHASE" else lab + " IN"
        print("%5d:%04.1f  %-8s %s" % (t // 60, t % 60, k, lab) + ("   (count-in: %s %d..1)" % (words, n) if k in ("PHASE", "EVENT") and n else ""))
    print(f"{title}: {len(cues)} cues, countdown tick {tick:.2f} s, starts {'at power-on' if boot else 'on the SONG switch'}")
