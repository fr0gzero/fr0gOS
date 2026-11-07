#!/usr/bin/env python3
"""Build a fr0gOS HDZero CLI file from a quad's pre-fr0gOS diff all.

Every HDZero quad gets exactly the same OSD block (FR0GOS_HD_BLOCK below);
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
# v1.3 r07 layout options (same elements, different spacing). A is the default.
HIDDEN = ["osd_frog_batt_pos", "osd_rssi_dbm_pos", "osd_esc_tmp_pos", "osd_core_temp_pos", "osd_total_flights_pos",
          "osd_custom_msg0_pos", "osd_custom_msg1_pos", "osd_custom_msg2_pos", "osd_custom_msg3_pos"]
OPTIONS = {
    # A MIRRORED: both sides share one grid, groups start on rows 0 / 4 / 9 / 13
    "A": dict(left=dict(osd_frog_feed_pos=0, osd_vbat_pos=4, osd_mah_drawn_pos=5, osd_current_pos=6,
                        osd_link_quality_pos=9, osd_frog_rate_pos=10, osd_vtx_channel_pos=13, osd_frog_vtxpwr_pos=14),
              right=dict(osd_frog_craft_pos=0, osd_tim_2_pos=1, osd_warnings_pos=2, osd_disarmed_pos=4,
                         osd_flymode_pos=5, osd_frog_air_pos=6, osd_throttle_pos=9, osd_esc_rpm_pos=11,
                         osd_g_force_pos=13)),
    # B EYE LINE: the numbers you read sit in the middle third, corners stay quiet
    "B": dict(left=dict(osd_frog_feed_pos=0, osd_vbat_pos=6, osd_mah_drawn_pos=7, osd_current_pos=8,
                        osd_link_quality_pos=10, osd_frog_rate_pos=11, osd_vtx_channel_pos=13, osd_frog_vtxpwr_pos=14),
              right=dict(osd_frog_craft_pos=0, osd_tim_2_pos=2, osd_warnings_pos=3, osd_disarmed_pos=5,
                         osd_flymode_pos=6, osd_frog_air_pos=7, osd_throttle_pos=9, osd_esc_rpm_pos=11,
                         osd_g_force_pos=13)),
    # C CORNERS (chosen, v1.3 r08): 5-line feed under the frog, power under it, links bottom left;
    # name / time / warnings / state top right, THR + RPM + G cluster in the bottom right corner
    "C": dict(left=dict(osd_frog_feed_pos=0, osd_vbat_pos=7, osd_mah_drawn_pos=8, osd_current_pos=9,
                        osd_link_quality_pos=13, osd_frog_rate_pos=14, osd_vtx_channel_pos=15, osd_frog_vtxpwr_pos=16),
              right=dict(osd_frog_craft_pos=0, osd_tim_2_pos=1, osd_warnings_pos=2, osd_disarmed_pos=3,
                         osd_flymode_pos=4, osd_frog_air_pos=5, osd_throttle_pos=12, osd_esc_rpm_pos=14,
                         osd_g_force_pos=16)),
}


def layout(opt):
    out = [("# layout option %s: frog + activity feed top left (frog hops around the bars), craft name top right" % opt, None)]
    out += [(k, a(L, y)) for k, y in OPTIONS[opt]["left"].items()]
    out += [(k, a(R, y)) for k, y in OPTIONS[opt]["right"].items()]
    out += [("# hidden: battery %, RSSI dBm, ESC temp, core temp, flight count, camera / HDZRO lines", None)] + [(k, 0) for k in HIDDEN]
    return out


LAYOUT = layout("C")
FR0GOS_HD_BLOCK = "\n".join([
    "# ---- fr0gOS HDZero hacker layout (identical on every HD quad) ----",
    "# 50x18 canvas; x=0 left-justified, x=49 right-justified; everything else hidden",
    "set pilot_name = FR0G",
    f"set craft_name = {CRAFT}",
    "set vcd_video_system = HD",
    "set osd_displayport_device = MSP",
    "set osd_canvas_width = 50",
    "set osd_canvas_height = 18",
    "set osd_frog_hd_font = ON",
    "set osd_warn_bitmask = 794623",
    "# count a flight when armed 15 s or more (flight counter, saved on disarm)",
    "set stats_min_armed_time_s = 15",
    "# 20 fps OSD: ~25 elements x ~15 B over MSP is ~390 B/frame, ~7.8 KB/s of the ~11.5 KB/s at 115200 baud",
    "set osd_framerate_hz = 20",
    "# battery noise in the bars retired in v1.3 r04 (battery stages show on voltage, % and bar instead)",
    "set osd_frog_noise_pos = 0",
    "set osd_custom_msg3 = HDZRO",
    "# core temp warning at 75C",
    "set osd_core_temp_alarm = 75",
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

# extras that set something the diff already sets (e.g. battery profile voltages) replace it in place
for e in list(EXTRA):
    if e.startswith("set ") and " = " in e:
        key = e.split(" = ")[0] + " ="
        hits = [i for i, l in enumerate(body) if l.startswith(key)]
        if hits:
            for i in hits:
                body[i] = e
            EXTRA.remove(e)

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
body[first_profile:first_profile] = ["", FR0GOS_HD_BLOCK] + (["# ---- this quad ----"] + OSD_EXTRA if OSD_EXTRA else []) + [""]

head = [f"# fr0gOS v1.3 r12 (hacker) - {CRAFT}",
        "# 1. Goggle SD card: fonts/hdzero-hacker/BTFL_000.bmp + BTFL_FHD_000.bmp in resource/OSD/FC/",
        f"# 2. Flash {HEX} with Full chip erase ticked",
        "# 3. Paste this whole file into the CLI, then recalibrate the accelerometer",
        "# Note: v1.2 resets the lifetime stats (flights, air time) and starts the high-score table at zero",
        "", "batch start"]
open(OUT, "w").write("\n".join(head + body + ["", "batch end", "save", ""]))
print("ok", OUT)
