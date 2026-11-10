#!/usr/bin/env python3
"""Compare font edge treatments at goggle scale: current (outline) vs crisp-no-outline vs soft-no-outline.
Renders the telemetry from each baked FHD BMP onto a BLACK sidebar (where the text actually lives)."""
import sys
from PIL import Image, ImageDraw, ImageFont
OUT=sys.argv[-1]; FONTS=sys.argv[1:-1]  # list of (label=path) pairs as label:path
TRANS=(127,127,127)
CS="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-!%:"; AMAP={c:0xD0+i for i,c in enumerate(CS)}
LINES=[("VBT","6.5V",False),("CEL","100%",False),("MAH","0",False),("TMP","46",True),("MOD","ACRO",False),("LQ","100",False)]
CW,CH=36,54
def panel(path):
    f=Image.open(path).convert("RGB"); GW,GH=f.width//16,f.height//32
    img=Image.new("RGB",(8*CW,len(LINES)*CH),(0,0,0))
    def put(code,cx,cy):
        g=f.crop(((code%16)*GW,(code//16)*GH,(code%16+1)*GW,(code//16+1)*GH)).resize((CW,CH),Image.LANCZOS)
        m=Image.new("L",g.size,0); mp=m.load(); gp=g.load()
        for y in range(g.height):
            for x in range(g.width):
                if gp[x,y]!=TRANS: mp[x,y]=255
        img.paste(g,(cx*CW,cy*CH),m)
    def say(s,cx,cy,amap):
        for i,ch in enumerate(s):
            if ch==' ':continue
            put((AMAP.get(ch,ord(ch)) if amap else ord(ch)),cx+i,cy)
    for r,(l,v,am) in enumerate(LINES):
        say(l,0,r,am); say(v,3,r,False)
    # scale up 1.5x to show how it looks magnified (goggle scaling)
    return img.resize((int(img.width*1.4),int(img.height*1.4)),Image.BILINEAR)
items=[(p.split('=',1)[0],p.split('=',1)[1]) for p in FONTS]
panels=[(lbl,panel(p)) for lbl,p in items]
pad=16; lblh=28; W=sum(p.width for _,p in panels)+pad*(len(panels)+1); H=panels[0][1].height+lblh+pad*2
sheet=Image.new("RGB",(W,H),(16,18,22)); d=ImageDraw.Draw(sheet)
try: cf=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",15)
except Exception: cf=None
x=pad
for lbl,p in panels:
    d.text((x,8),lbl,fill=(170,220,185),font=cf); sheet.paste(p,(x,lblh)); x+=p.width+pad
sheet.save(OUT); print("ok",OUT,sheet.size)
