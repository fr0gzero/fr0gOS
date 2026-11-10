#!/usr/bin/env python3
"""Verify the v3 font from the baked BMP: mascot + AA FreeSans telemetry + the 8 stick-data glyphs."""
import sys, re
from PIL import Image, ImageDraw, ImageFont
FONT, MASC, OUT = sys.argv[1:4]
font = Image.open(FONT).convert("RGB"); GW,GH=font.width//16,font.height//32
TRANS=(127,127,127)
CS="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-!%:"; AMAP={c:0xD0+i for i,c in enumerate(CS)}
mascot=[[int(x,16) for x in re.findall(r"0x[0-9A-Fa-f]{2}",ln)] for ln in open(MASC) if re.match(r"\s*\{ 0x",ln)]
STICKDATA=[0x02,0x03,0x05,0x08,0x09,0x0B,0x0C,0x0F]
CW,CH=30,44
def cell(code):
    g=font.crop(((code%16)*GW,(code//16)*GH,(code%16+1)*GW,(code//16+1)*GH)).resize((CW,CH),Image.LANCZOS)
    m=Image.new("L",g.size,0); mp=m.load(); gp=g.load()
    for y in range(g.height):
        for x in range(g.width):
            if gp[x,y]!=TRANS: mp[x,y]=255
    return g,m
def put(img,code,cx,cy):
    if code==0x20: return
    g,m=cell(code); img.paste(g,(cx*CW,cy*CH),m)
def say(img,s,cx,cy,amap=False):
    for i,ch in enumerate(s):
        if ch==' ': continue
        put(img,(AMAP.get(ch,ord(ch)) if amap else ord(ch)),cx+i,cy)
COLS,ROWS=12,10
img=Image.new("RGB",(COLS*CW,ROWS*CH),(8,9,12))
# mascot idle 2x2
for i,code in enumerate(mascot[0]): put(img,code,i%2,i//2)
say(img,"MK4-2",3,0)
# telemetry (base amber), one lavender via amap
for i,(l,v,amap) in enumerate([("VBT","16.4",False),("CEL","51",False),("MAH","1250",False),("AMP","24.3",False),("TMP","73",True),("LQ","98",False)]):
    say(img,l,0,2+i,amap); say(img,v,4,2+i)
# stick-data glyph row at the bottom
for i,code in enumerate(STICKDATA): put(img,code,i,9)
say(img,"STK",8,9)
sheet=Image.new("RGB",(COLS*CW,ROWS*CH+34),(14,16,20)); d=ImageDraw.Draw(sheet)
try: cf=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",15)
except Exception: cf=None
d.text((12,9),"v3: FreeSans Bold anti-aliased + mascot + stick-data glyphs (bottom row)",fill=(170,220,185),font=cf)
sheet.paste(img,(0,34)); sheet.save(OUT); print("ok",OUT)
