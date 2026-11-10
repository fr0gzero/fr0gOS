#!/usr/bin/env python3
"""Grid-accurate preview of the fr0gOS v2 font: the trimmed idle mascot, the LCARS side columns, and the new
custom high-res stick boxes (bright live dot + dim trace) drawn from the REAL baked glyphs."""
import sys, re
from PIL import Image, ImageDraw, ImageFont
FONT, MASC, STK, OUT = sys.argv[1:5]
font = Image.open(FONT).convert("RGB"); GW, GH = font.width//16, font.height//32
TRANS=(127,127,127)
CS="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-!%:"
AMBER={c:0xD0+i for i,c in enumerate(CS)}
mascot=[[int(x,16) for x in re.findall(r"0x[0-9A-Fa-f]{2}",ln)] for ln in open(MASC) if re.match(r"\s*\{ 0x",ln)]
txt_stk=open(STK).read()
def grab(name):
    m=re.search(name+r".*?\{(.*?)\};",txt_stk,re.S);
    rows=[[int(x,16) for x in re.findall(r"0x[0-9A-Fa-f]{2}",r)] for r in re.findall(r"\{([^{}]*)\}",m.group(1))]
    return rows
BR=grab("frogStickDot"); DM=grab("frogStickDotDim")
CROSS=int(re.search(r"FROG_STICK_CROSS 0x([0-9A-Fa-f]{2})",txt_stk).group(1),16)
COLS,ROWS=53,20; CW,CH=22,31
AMB=(255,178,74); LAV=(190,162,232); TAN=(232,185,106); RUST=(194,123,74); GRN=(123,216,143)
def newimg():
    img=Image.new("RGB",(COLS*CW,ROWS*CH),(0,0,0)); d=ImageDraw.Draw(img)
    for yy in range(ROWS*CH):
        t=yy/(ROWS*CH); c=(int(16+40*(1-t)),int(26+40*(1-t)),int(40+26*t)) if t<0.52 else (int(30+16*t),int(22+10*t),14)
        d.line([(8*CW,yy),(45*CW,yy)],fill=c)
    return img,d
def cell(code):
    g=font.crop(((code%16)*GW,(code//16)*GH,(code%16+1)*GW,(code//16+1)*GH)).resize((CW,CH),Image.LANCZOS)
    m=Image.new("L",g.size,0); mp=m.load(); gp=g.load()
    for yy in range(g.height):
        for xx in range(g.width):
            if gp[xx,yy]!=TRANS: mp[xx,yy]=255
    return g,m
def put(img,code,cx,cy):
    if code==0x20: return
    g,m=cell(code); img.paste(g,(cx*CW,cy*CH),m)
def say(img,s,cx,cy,pal=None):
    for i,ch in enumerate(s):
        if ch==' ': continue
        put(img,(pal.get(ch,ord(ch)) if pal else ord(ch)),cx+i,cy)
def capbar(d,cx,cy,w,color): d.rectangle([cx*CW+2,cy*CH+3,(cx+w)*CW-3,(cy+1)*CH-3],fill=color)

# a stick box: 3x3 cells, bright dot at (gx,gy) sub (sx,sy), dim trace list of (gx,gy,sx,sy)
def stickbox(img,x0,y0,live,trace):
    for cy in range(3):
        for cx in range(3):
            code=CROSS
            for (gx,gy,sx,sy) in trace:
                if gx==cx and gy==cy and not(gx==live[0] and gy==live[1]): code=DM[sy][sx]; break
            if cx==live[0] and cy==live[1]: code=BR[live[3]][live[2]]
            put(img,code,x0+cx,y0+cy)

img,d=newimg()
# mascot top-left (idle frame 0)
for i,code in enumerate(mascot[0]): put(img,code,i%2,i//2)
say(img,"MK5-1",3,0,AMBER)
# left power column
capbar(d,0,2,8,TAN)
for i,(lab,val) in enumerate([("VBT","16.4"),("CEL","78%"),("MAH","1250"),("AMP","24.3"),("TMP","41")]):
    say(img,lab,0,3+i,AMBER); say(img,val,3,3+i)
# right flight/link/motion column (mirrored labels outer)
capbar(d,45,0,8,AMB)
R=[("MOD","ACRO",1),("AIR","ON",2),("ARM","0412",3),("LQ","98",5),("THR","68%",10),("RPM","22K",11),("G","3.4",12)]
for lab,val,y in R:
    say(img,lab,47,y,AMBER); say(img,val,46-len(val)+1,y)
# combat log left, rows 9-13
capbar(d,0,8,8,RUST)
for i,(ln,pal) in enumerate([("FLIP",None),("PERCH",None),("2.1G",AMBER),("PUNCH",None)]):
    say(img,ln,0,9+i,pal)
# custom sticks bottom corners - left mid-low with a fast flick trace; right near centre
stickbox(img,1,16,(0,2,1,3),[(1,1,2,2),(1,1,0,1),(0,2,3,3)])   # throttle low, yaw swinging left: trace
stickbox(img,49,16,(1,1,2,1),[(1,1,1,2),(2,1,0,0)])             # right stick near centre, small trace
capbar(d,1,15,3,AMB); capbar(d,49,15,3,AMB)
try: cf=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",15)
except Exception: cf=None
pad=14; sheet=Image.new("RGB",(img.width,img.height+40),(14,16,20)); dd=ImageDraw.Draw(sheet)
dd.text((pad,8),"fr0gOS V1.4 R37  -  trimmed idle mascot + custom high-res stick boxes (bright dot + dim trace)",fill=(170,220,185),font=cf)
sheet.paste(img,(0,34)); sheet.save(OUT); print("ok",OUT,sheet.size)
