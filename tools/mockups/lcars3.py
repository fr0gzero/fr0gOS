#!/usr/bin/env python3
"""LCARS redesign: the side bars become real LCARS panels - a solid outer rail, rounded elbows top and
bottom, colour-block section headers, canonical Starfleet palette. Composited over a real goggle frame
(dimmed in the live-video area) so it reads in context. Grid-accurate 53x20, real DS9 font for the text."""
import sys, re
from PIL import Image, ImageDraw, ImageFont
FONT, BG, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
font = Image.open(FONT).convert("RGB"); GW, GH = font.width//16, font.height//32
TRANS=(127,127,127)
CS="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-!%:"
COLS,ROWS=53,20
# canvas sized to the 16:9 goggle, 5:4 video pillarboxed in the middle
W,H=1280,720
bg=Image.open(BG).convert("RGB").resize((W,H))
CW=W//COLS; CH=H//ROWS
# dim the whole thing a touch, video area stays, bars go near-black
d=ImageDraw.Draw(bg,"RGBA")
d.rectangle([0,0,W,H],fill=(0,0,0,70))
d.rectangle([0,0,8*CW,H],fill=(0,0,0,205)); d.rectangle([45*CW,0,W,H],fill=(0,0,0,205))

# --- canonical LCARS palette ---
ORANGE=(255,153,0); GOLD=(255,204,102); MAUVE=(204,153,204); PERI=(153,153,255)
PEACH=(255,153,102); RED=(214,92,72); ICE=(170,204,255); TEXT=(255,221,170)

def block(cx,cy,w,color,h=1,r=0):
    x0,y0,x1,y1=cx*CW,cy*CH,(cx+w)*CW,(cy+h)*CH
    d.rounded_rectangle([x0+1,y0+2,x1-2,y1-2],radius=r,fill=color)
def cell(code):
    g=font.crop(((code%16)*GW,(code//16)*GH,(code%16+1)*GW,(code//16+1)*GH)).resize((CW,CH),Image.LANCZOS)
    m=Image.new("L",g.size,0); mp=m.load(); gp=g.load()
    for yy in range(g.height):
        for xx in range(g.width):
            if gp[xx,yy]!=TRANS: mp[xx,yy]=255
    return g,m
def recolor(code,color):
    g,m=cell(code); solid=Image.new("RGB",g.size,color); return solid,m
def say(s,cx,cy,color):
    for i,ch in enumerate(s):
        if ch==' ': continue
        g,m=recolor(ord(ch),color); bg.paste(g,((cx+i)*CW,cy*CH),m)

# ======== LEFT PANEL ========
# outer rail + elbows (orange frame)
d.rectangle([0,2*CH+2,1*CW+CW//2,18*CH-2],fill=ORANGE)       # vertical rail (1.5 cells)
block(0,2,6,ORANGE,r=16)                                     # top elbow bar
block(0,18,5,ORANGE,r=16)                                    # bottom elbow bar
# header label on the gold elbow
say("MK4-2",2,2,(20,16,8))
# section tag: POWER (mauve pill) then the readings
block(0,4,2,MAUVE,r=12)
rows=[("VBT","16.4",ORANGE),("CEL","51",ORANGE),("MAH","1250",ORANGE),("AMP","24.3",ORANGE),("TMP","73",RED)]
for i,(lab,val,vc) in enumerate(rows):
    y=4+i
    if i>0: d.rectangle([CW//3,y*CH+CH//3,CW,y*CH+2*CH//3],fill=PERI)  # little rib off the rail
    say(lab,2,y,MAUVE); say(val,5,y,vc)
# combat log under a peach header
block(0,10,6,PEACH,r=12); say("LOG",2,10,(20,16,8))
for i,ln in enumerate(["FLIP","PERCH","2.1G","PUNCH"]):
    say(ln,2,11+i,TEXT)
# left stick box bottom
d.rectangle([0,16*CH+2,1*CW+CW//2,18*CH-2],fill=ORANGE)

# ======== RIGHT PANEL (mirrored) ========
d.rectangle([52*CW-CW//2,2*CH+2,53*CW,18*CH-2],fill=ORANGE)
block(47,2,6,ORANGE,r=16); block(48,18,5,ORANGE,r=16)
block(51,4,2,MAUVE,r=12)
rr=[("MOD","ACRO",ORANGE),("AIR","ON",ORANGE),("ARM","0412",ORANGE),("LQ","98",ORANGE),("THR","68%",ORANGE),("RPM","22K",ORANGE),("G","3.4",ORANGE)]
for i,(lab,val,vc) in enumerate(rr):
    y=2+i if i<3 else 4+i  # small gap
    say(lab,50,y,MAUVE); say(val,49-len(val)+1,y,vc)
# mascot top-left over the elbow (2x2) - leave the real frog; here just a placeholder note
# stick boxes already rendered elsewhere; show frame only
# title strip
sheet=Image.new("RGB",(W,H+34),(12,14,18)); dd=ImageDraw.Draw(sheet)
try: cf=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",15)
except Exception: cf=None
dd.text((14,9),"LCARS redesign - framed side panels: orange rail + elbows, mauve labels, colour-block headers, canonical palette",fill=(170,220,185),font=cf)
sheet.paste(bg,(0,34)); sheet.save(OUT); print("ok",OUT)
