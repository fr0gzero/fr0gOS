#!/usr/bin/env python3
"""Verify the r39 de-mirrored layout on the real 53x20 grid with the real font: left power column anchored
left, right flight/link/motion column anchored at col 45 (label 45-47, value 48+), both clean and in-bar."""
import sys, re
from PIL import Image, ImageDraw, ImageFont
FONT, MASC, OUT = sys.argv[1:4]
font=Image.open(FONT).convert("RGB"); GW,GH=font.width//16,font.height//32
TRANS=(127,127,127)
CS="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-!%:"; AMAP={c:0xD0+i for i,c in enumerate(CS)}
mascot=[[int(x,16) for x in re.findall(r"0x[0-9A-Fa-f]{2}",ln)] for ln in open(MASC) if re.match(r"\s*\{ 0x",ln)]
STICKDATA=[0x02,0x03,0x05,0x08,0x09,0x0B,0x0C,0x0F]
COLS,ROWS=53,20; CW,CH=22,31
img=Image.new("RGB",(COLS*CW,ROWS*CH),(0,0,0)); d=ImageDraw.Draw(img)
for yy in range(ROWS*CH):
    t=yy/(ROWS*CH); c=(int(14+34*(1-t)),int(22+34*(1-t)),int(34+22*t)) if t<0.52 else (int(26+14*t),int(18+8*t),12)
    d.line([(8*CW,yy),(45*CW,yy)],fill=c)
def cell(code):
    g=font.crop(((code%16)*GW,(code//16)*GH,(code%16+1)*GW,(code//16+1)*GH)).resize((CW,CH),Image.LANCZOS)
    m=Image.new("L",g.size,0); mp=m.load(); gp=g.load()
    for y in range(g.height):
        for x in range(g.width):
            if gp[x,y]!=TRANS: mp[x,y]=255
    return g,m
def put(code,cx,cy):
    if code==0x20 or cx>=COLS: return
    g,m=cell(code); img.paste(g,(cx*CW,cy*CH),m)
def say(s,cx,cy,amap=False):
    for i,ch in enumerate(s):
        if ch==' ': continue
        put((AMAP.get(ch,ord(ch)) if amap else ord(ch)),cx+i,cy)
# mascot + craft
for i,code in enumerate(mascot[0]): put(code,i%2,i//2)
say("MK5-1",3,0,True)
# left power (label x0 lavender, value x3 amber)
for lab,val,y in [("VBT","7.0V",3),("CEL","99%",4),("MAH","1",5),("AMP","0.2",6),("TMP","42",7)]:
    say(lab,0,y,True); say(val,3,y)
# right column de-mirrored: label x45 lavender, value x48 amber
for lab,val,y in [("MOD","ACRO",1),("AIR","OFF",2),("ARM","00:00",3),("LQ","100",5),("THR","100%",10),("RPM","22K",11),("G","3.4",12)]:
    say(lab,45,y,True); say(val,48,y)
# combat log
for i,ln in enumerate(["FLIP","PERCH","2.1G","PUNCH"]): say(ln,0,9+i)
# stick-data glyphs bottom corners
for i,code in enumerate(STICKDATA[:5]): put(code,i,19)
for i,code in enumerate(STICKDATA[:5]): put(code,48+i,19)
# col markers
for cx in (44,45,52): d.line([(cx*CW,0),(cx*CW,ROWS*CH)],fill=(40,40,48))
sheet=Image.new("RGB",(COLS*CW,ROWS*CH+30),(14,16,20)); dd=ImageDraw.Draw(sheet)
try: cf=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",14)
except Exception: cf=None
dd.text((10,8),"r39: right column de-mirrored (label 45-47, value 48+). Longest value 00:00 fits 48-52. Lines @ col 44/45/52.",fill=(170,220,185),font=cf)
sheet.paste(img,(0,30)); sheet.save(OUT); print("ok",OUT)
