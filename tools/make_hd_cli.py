#!/usr/bin/env python3
"""Build a FrogOS HDZero CLI file from a quad's pre-FrogOS diff all.

Every HDZero quad gets exactly the same OSD block (FROGOS_HD_BLOCK below);
only the hardware, tune, rates and names come from the quad's own diff.

usage: make_hd_cli.py <diff_all.txt> <out.txt> <craft name> <hex name> [extra command ...]

Extra commands starting with "aux" (or "# air") go after the aux lines; the rest go after the OSD block.
"""
import sys

DIFF, OUT, CRAFT, HEX = sys.argv[1:5]
EXTRA = sys.argv[5:]


def a(x, y):
    return 2048 + (x & 31) + (((x >> 5) & 1) << 10) + (y << 5)


L, R = 0, 49
LAYOUT = [
    ("# top: FROG + cursor | frog + craft name", None),
    ("osd_frog_tag_pos", a(L, 0)), ("osd_frog_craft_pos", a(R, 0)),
    ("# power, top left", None),
    ("osd_vbat_pos", a(L, 2)), ("osd_current_pos", a(L, 3)), ("osd_mah_drawn_pos", a(L, 4)), ("osd_frog_batt_pos", a(L, 5)),
    ("# link, middle left", None),
    ("osd_link_quality_pos", a(L, 7)), ("osd_rssi_dbm_pos", a(L, 8)), ("osd_frog_rate_pos", a(L, 9)),
    ("# camera / video format, bottom left (text from osd_custom_msg0-2, blank if unset)", None),
    ("osd_custom_msg0_pos", a(L, 13)), ("osd_custom_msg1_pos", a(L, 14)), ("osd_custom_msg2_pos", a(L, 15)),
    ("# time, top right", None),
    ("osd_tim_2_pos", a(R, 2)), ("osd_throttle_pos", a(R, 3)),
    ("# state, middle right", None),
    ("osd_disarmed_pos", a(R, 7)), ("osd_flymode_pos", a(R, 8)), ("osd_frog_air_pos", a(R, 9)),
    ("# system, bottom right", None),
    ("osd_core_temp_pos", a(R, 13)), ("osd_vtx_channel_pos", a(R, 14)), ("osd_frog_vtxpwr_pos", a(R, 15)),
    ("osd_warnings_pos", a(R, 16)),
]
FROGOS_HD_BLOCK = "\n".join([
    "# ---- FrogOS HDZero hacker layout (identical on every HD quad) ----",
    "# 50x18 canvas; x=0 left-justified, x=49 right-justified; everything else hidden",
    "set pilot_name = FR0G",
    f"set craft_name = {CRAFT}",
    "set vcd_video_system = HD",
    "set osd_displayport_device = MSP",
    "set osd_canvas_width = 50",
    "set osd_canvas_height = 18",
    "set osd_frog_hd_font = ON",
    "set osd_warn_bitmask = 794623",
] + [k if v is None else f"set {k} = {v}" for k, v in LAYOUT])

SKIP_PREFIX = ("mcu_id", "signature", "# version", "# Betaflight", "# config rev", "# start the command",
               "# reset configuration", "# name:", "# save configuration", "# restore original", "save", "batch",
               "# diff all", "set craft_name", "set pilot_name", "set osd_", "set vcd_video_system")

body = []
for raw in open(DIFF):
    line = raw.rstrip()
    if not line.strip() or line.startswith(SKIP_PREFIX) or line in ("# master", "# feature", "# serial", "# aux",
                                                                    "# vtxtable", "# dma", "# beeper", "# beacon",
                                                                    "# resources") or line.startswith("# profile ") or line.startswith("# rateprofile ") or line.startswith("# battery_profile "):
        continue
    body.append(line)

# OSD block goes where the master section ends (before the first profile)
first_profile = next(i for i, l in enumerate(body) if l.startswith("profile "))
AUX_EXTRA = [e for e in EXTRA if e.startswith(("aux ", "# air"))]
OSD_EXTRA = [e for e in EXTRA if e not in AUX_EXTRA]
# aux extras (e.g. air mode switch) go after the last aux line
if AUX_EXTRA:
    last_aux = max(i for i, l in enumerate(body[:first_profile]) if l.startswith("aux "))
    body[last_aux + 1:last_aux + 1] = AUX_EXTRA
    first_profile += len(AUX_EXTRA)
# everything else (per-quad overrides) goes straight after the shared block
body[first_profile:first_profile] = ["", FROGOS_HD_BLOCK] + (["# ---- this quad ----"] + OSD_EXTRA if OSD_EXTRA else []) + [""]

head = [f"# FrogOS v1.1 r02 (hacker) - {CRAFT}",
        "# 1. Goggle SD card: fonts/hdzero-hacker/BTFL_000.bmp + BTFL_FHD_000.bmp in resource/OSD/FC/",
        f"# 2. Flash {HEX} with Full chip erase ticked",
        "# 3. Paste this whole file into the CLI, then recalibrate the accelerometer",
        "", "batch start"]
open(OUT, "w").write("\n".join(head + body + ["", "batch end", "save", ""]))
print("ok", OUT)
