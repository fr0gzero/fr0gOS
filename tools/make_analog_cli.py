#!/usr/bin/env python3
"""Build a fr0gOS ANALOG CLI file (MAX7456 / AT7456E OSD, NTSC 30x13) from a quad's pre-fr0gOS diff all.

Same idea as make_hd_cli.py: the shared analog OSD block below, plus the quad's own hardware, tune, rates and
names. Analog has no frog, no colour and no stick code; the event log, combo, tricks, song cues, battery stages
and transitions all run (plain white, effects only over existing text).

usage: make_analog_cli.py <diff_all.txt> <out.txt> <craft name> <hex name> [extra command ...]

Extra commands starting with "aux" (or "# air") go after the aux lines; the rest go after the OSD block.
"""
import sys

DIFF, OUT, CRAFT, HEX = sys.argv[1:5]
EXTRA = sys.argv[5:]


def a(x, y):
    return 2048 + (x & 31) + (((x >> 5) & 1) << 10) + (y << 5)


L, R = 0, 29
HIDDEN = ["osd_frog_batt_pos", "osd_rssi_dbm_pos", "osd_esc_tmp_pos", "osd_core_temp_pos", "osd_total_flights_pos",
          "osd_custom_msg0_pos", "osd_custom_msg1_pos", "osd_custom_msg2_pos", "osd_custom_msg3_pos",
          "osd_frog_noise_pos", "osd_rssi_pos", "osd_tim_1_pos", "osd_remaining_time_estimate_pos",
          "osd_home_dist_pos", "osd_flight_dist_pos", "osd_avg_cell_voltage_pos", "osd_pit_ang_pos", "osd_rol_ang_pos"]
OPTIONS = {
    # layout C squeezed into 13 rows: feed 0-4, combo 5-6 (automatic), power 7-9, links 10-12 on the left;
    # name / time / warnings / state top right, THR + RPM + G + VTX power bottom right
    "C": dict(left=dict(osd_frog_feed_pos=0, osd_vbat_pos=7, osd_mah_drawn_pos=8, osd_current_pos=9,
                        osd_link_quality_pos=10, osd_frog_rate_pos=11, osd_vtx_channel_pos=12),
              right=dict(osd_frog_craft_pos=0, osd_tim_2_pos=1, osd_warnings_pos=2, osd_disarmed_pos=3,
                         osd_flymode_pos=4, osd_frog_air_pos=5, osd_throttle_pos=7, osd_esc_rpm_pos=9,
                         osd_g_force_pos=11, osd_frog_vtxpwr_pos=12)),
}


def layout(opt):
    out = [("# analog layout %s: event log + combo top left, craft name top right" % opt, None)]
    out += [(k, a(L, y)) for k, y in OPTIONS[opt]["left"].items()]
    out += [(k, a(R, y)) for k, y in OPTIONS[opt]["right"].items()]
    out += [("# hidden: everything else", None)] + [(k, 0) for k in HIDDEN]
    return out


LAYOUT = layout("C")
FR0GOS_HD_BLOCK = "\n".join([
    "# ---- fr0gOS analog layout (identical on every analog quad) ----",
    "# NTSC 30x13; x=0 left-justified, x=29 right-justified; everything else hidden",
    "set pilot_name = FR0G",
    f"set craft_name = {CRAFT}",
    "set vcd_video_system = NTSC",
    "set osd_displayport_device = MAX7456",
    "set osd_frog_hd_font = OFF",
    "set osd_warn_bitmask = 794623",
    "# count a flight when armed 15 s or more (flight counter, saved on disarm)",
    "set stats_min_armed_time_s = 15",
    "set osd_framerate_hz = 20",
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
first_profile = next((i for i, l in enumerate(body) if l.startswith("profile ")), len(body))
AUX_EXTRA = [e for e in EXTRA if e.startswith(("aux ", "# air"))]
OSD_EXTRA = [e for e in EXTRA if e not in AUX_EXTRA]
# aux extras (e.g. air mode switch) go after the last aux line
if AUX_EXTRA:
    last_aux = max(i for i, l in enumerate(body[:first_profile]) if l.startswith("aux "))
    body[last_aux + 1:last_aux + 1] = AUX_EXTRA
    first_profile += len(AUX_EXTRA)
# everything else (per-quad overrides) goes straight after the shared block
body[first_profile:first_profile] = ["", FR0GOS_HD_BLOCK] + (["# ---- this quad ----"] + OSD_EXTRA if OSD_EXTRA else []) + [""]

head = [f"# fr0gOS v1.3 r27 (analog) - {CRAFT}",
        f"# 1. Flash {HEX} with Full chip erase ticked",
        "# 2. Paste this whole file into the CLI, then recalibrate the accelerometer",
        "# Analog: stock OSD font, no frog / colour / stick code; everything else runs in plain white",
        "", "batch start"]
open(OUT, "w").write("\n".join(head + body + ["", "batch end", "save", ""]))
print("ok", OUT)
