#!/usr/bin/env python3
"""Three grid-accurate LCARS layout options for the goggle (53x20, 5:4 video, ~8-col side columns), drawn
from the real DS9 font. Readings grouped by category with coloured divider caps, the combat log (frog feed)
kept, and bigger stick-overlay boxes. Stacked into one comparison image."""
import sys, re
from PIL import Image, ImageDraw, ImageFont

FONT, HDR, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
font = Image.open(FONT).convert("RGB")
GW, GH = font.width // 16, font.height // 32
TRANS = (127, 127, 127)
CS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-!%:"
AMBERMAP = {c: 0xD0 + i for i, c in enumerate(CS)}
RED_SLOTS = (list(range(0x60, 0x70)) + [0x77] + list(range(0x80, 0x8A)) +
             list(range(0x90, 0x97)) + [0x98, 0x99] + list(range(0x9B, 0xA0)))
REDMAP = {c: RED_SLOTS[i] for i, c in enumerate(CS)}
mascot = [[int(x, 16) for x in re.findall(r"0x[0-9A-Fa-f]{2}", ln)]
          for ln in open(HDR) if re.match(r"\s*\{ 0x", ln)]
IDLE = mascot[0]
COLS, ROWS = 53, 20
CW, CH = 22, 31
AMB=(255,178,74); LAV=(190,162,232); TAN=(232,185,106); RUST=(194,123,74); GRN=(123,216,143); REDC=(224,83,60)

def new_osd():
    img = Image.new("RGB", (COLS*CW, ROWS*CH), (0,0,0)); d=ImageDraw.Draw(img)
    for yy in range(ROWS*CH):
        t=yy/(ROWS*CH)
        c=(int(16+40*(1-t)),int(26+40*(1-t)),int(40+26*t)) if t<0.52 else (int(30+16*t),int(22+10*t),14)
        d.line([(8*CW,yy),(45*CW,yy)],fill=c)
    return img,d

def gcell(code):
    g=font.crop(((code%16)*GW,(code//16)*GH,(code%16+1)*GW,(code//16+1)*GH)).resize((CW,CH),Image.LANCZOS)
    m=Image.new("L",g.size,0); mp=m.load(); gp=g.load()
    for yy in range(g.height):
        for xx in range(g.width):
            if gp[xx,yy]!=TRANS: mp[xx,yy]=255
    return g,m

def put(img,code,cx,cy):
    g,m=gcell(code); img.paste(g,(cx*CW,cy*CH),m)

def txt(img,s,cx,cy,pal=None):
    for i,ch in enumerate(s):
        if ch==' ': continue
        code=pal.get(ch,ord(ch)) if pal else ord(ch); put(img,code,cx+i,cy)

def cap(d,cx,cy,w,color,h=1): d.rectangle([cx*CW+2,cy*CH+3,(cx+w)*CW-3,(cy+h)*CH-3],fill=color)

def stickbox(d,cx,cy,w,h,dotx=0.4,doty=-0.3):
    x0,y0,x1,y1=cx*CW+4,cy*CH+3,(cx+w)*CW-4,(cy+h)*CH-4
    d.rectangle([x0,y0,x1,y1],outline=AMB,width=3)
    mx,my=(x0+x1)/2,(y0+y1)/2
    d.line([x0+8,my,x1-8,my],fill=(70,64,86),width=2); d.line([mx,y0+8,mx,y1-8],fill=(70,64,86),width=2)
    r=(x1-x0)*0.5-10
    d.ellipse([mx+dotx*r-9,my+doty*r-9,mx+dotx*r+9,my+doty*r+9],fill=AMB)

# ---- the three layouts. each is (left_items, right_items). item kinds below. ----
def draw(spec):
    img,d=new_osd()
    for side,(x0) in (("L",0),("R",45)):
        items=spec[side]
        y=0
        for it in items:
            k=it[0]
            if k=="mascot":
                for i,code in enumerate(IDLE): put(img,code,x0+i%2,y+i//2)
                txt(img,it[1],x0+3,y); y+=2
            elif k=="div":
                cap(d,x0,y,8,it[1]); y+=1
            elif k=="row":
                _,lab,val,lc=it; txt(img,lab,x0,y,AMBERMAP if lc=="lav" else (REDMAP if lc=="red" else None))
                txt(img,val,x0+3,y, REDMAP if lc=="redval" else None); y+=1
            elif k=="log":
                for ln,sev in it[1]:
                    txt(img,ln,x0,y, REDMAP if sev=="red" else (AMBERMAP if sev=="lav" else None)); y+=1
            elif k=="stick":
                _,w,h=it; cap(d,x0,ROWS-h-1,8,RUST); stickbox(d,x0+(8-w)//2,ROWS-h,w,h, *it[3:] if len(it)>3 else (0.4,-0.3)); y=ROWS
            elif k=="gap": y+=it[1]
            elif k=="topcap": cap(d,x0,0,8,it[1]); y=max(y,1)
    return img

# shared data
POWER=[("row","VBT","16.4V","lav"),("row","CEL","78%","lav"),("row","MAH","1250","lav"),("row","AMP","24.3","lav"),("row","TMP","41","redval")]
LINK=[("row","RTE","F1000",None),("row","LQ","98","lav"),("row","VTX","R2","lav"),("row","PWR","200","lav")]
MOTION=[("row","THR","68%",None),("row","RPM","22K","lav"),("row","G","3.4","lav")]
FLIGHT=[("row","MOD","ACRO",None),("row","AIR","ON","lav"),("row","ARM","0412","lav")]
LOG=[("FLIP","ok"),("PERCH","ok"),("2.1G","lav"),("X7","lav")]

A={"L":[("topcap",AMB),("mascot","MK4-2")]+FLIGHT+[("div",AMB)]+POWER+[("stick",6,6)],
   "R":[("topcap",AMB)]+LINK+[("div",LAV)]+MOTION+[("div",TAN),("log",LOG),("stick",6,6)]}
B={"L":[("topcap",AMB),("mascot","MK4-2")]+POWER+[("div",TAN),("log",LOG),("stick",7,5)],
   "R":[("topcap",AMB)]+FLIGHT+[("div",LAV)]+LINK+[("div",AMB)]+MOTION+[("stick",7,5)]}
C={"L":[("topcap",AMB),("mascot","MK4-2")]+FLIGHT+POWER+[("stick",8,7)],
   "R":[("topcap",AMB)]+LINK+MOTION+[("div",TAN),("log",LOG),("stick",8,7)]}

opts=[("A  Grouped Ops - flight+power left, link+motion+log right, 6x6 sticks",A),
      ("B  Log left - power+log left, flight+link+motion right, wide 7x5 sticks",B),
      ("C  Big sticks - compact telemetry, log right, 8x7 sticks",C)]
pad=16; imgs=[(lbl,draw(s)) for lbl,s in opts]
W=COLS*CW; H=sum(im.height for _,im in imgs)+40*len(imgs)+pad*2
sheet=Image.new("RGB",(W,H),(14,16,20)); d=ImageDraw.Draw(sheet)
try: cf=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",17)
except Exception: cf=None
y=pad
for lbl,im in imgs:
    d.text((pad,y),lbl,fill=(170,220,185),font=cf); y+=26
    sheet.paste(im,(0,y)); y+=im.height+14
sheet.save(OUT); print("ok",OUT,sheet.size)
