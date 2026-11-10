#!/usr/bin/env python3
"""Font options for the minimal OSD: render the left-bar telemetry column in each candidate typeface the
exact way the goggle bakes it - crisp 1-bit glyphs at the real HD cell size (24x36), amber on black.
Plus the CURRENT flown font (from the baked BMP) for comparison. One labelled comparison sheet."""
import sys
from PIL import Image, ImageDraw, ImageFont
CURRENT_BMP = sys.argv[1]; OUT = sys.argv[2]
TRANS=(127,127,127)
AMBER=(255,178,74); LAV=(190,162,232); WHITE=(235,235,235)
CW,CH=36,54                 # FHD cell (HDZero HD uses the FHD font) - shows the high-res look
AA=True                     # anti-aliased smooth edges, not 1-bit
# the minimal left-column content
LINES=[("MK4-2",WHITE),("VBT 16.4",AMBER),("CEL 51",AMBER),("MAH 1250",AMBER),
       ("AMP 24.3",AMBER),("TMP 73",LAV),("LQ 98",AMBER),("THR 68",AMBER)]
COLS=9; ROWS=len(LINES)

S=4  # supersample
def crisp_glyph_ttf(ch, font, color):
    """one cell: char rendered from a TTF, hard 1-bit threshold, target colour on black."""
    big=Image.new("L",(CW*S,CH*S),0); db=ImageDraw.Draw(big)
    db.text((CW*S//2, CH*S//2), ch, fill=255, font=font, anchor="mm")
    small=big.resize((CW,CH),Image.LANCZOS)
    out=Image.new("RGB",(CW,CH),(0,0,0)); op=out.load(); sp=small.load()
    for y in range(CH):
        for x in range(CW):
            v=sp[x,y]
            if AA:
                if v: op[x,y]=(color[0]*v//255,color[1]*v//255,color[2]*v//255)  # smooth amber-over-black
            elif v>=112: op[x,y]=color
    return out

def load_face(path):
    try: return ImageFont.truetype(path, int(CH*S*0.80))   # face sized to ~0.8 of the cell height
    except Exception: return None

def render_ttf_panel(path,px=None):
    img=Image.new("RGB",(COLS*CW,ROWS*CH),(0,0,0))
    face=load_face(path)
    if not face: return None
    for r,(txt,col) in enumerate(LINES):
        for c,ch in enumerate(txt):
            if ch==' ': continue
            img.paste(crisp_glyph_ttf(ch,face,col),(c*CW,r*CH))
    return img

# CURRENT font from the baked BMP
cur=Image.open(CURRENT_BMP).convert("RGB"); GW,GH=cur.width//16,cur.height//32
CSAMP="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-!%:"; AMAP={c:0xD0+i for i,c in enumerate(CSAMP)}
def cur_cell(code,color=None):
    g=cur.crop(((code%16)*GW,(code//16)*GH,(code%16+1)*GW,(code//16+1)*GH)).resize((CW,CH),Image.LANCZOS)
    out=Image.new("RGB",(CW,CH),(0,0,0)); op=out.load(); gp=g.load()
    for y in range(CH):
        for x in range(CW):
            if gp[x,y]!=TRANS: op[x,y]=color if color else gp[x,y]
    return out
def render_current():
    img=Image.new("RGB",(COLS*CW,ROWS*CH),(0,0,0))
    for r,(txt,col) in enumerate(LINES):
        for c,ch in enumerate(txt):
            if ch==' ': continue
            code=AMAP.get(ch,ord(ch)) if col==LAV else ord(ch)
            img.paste(cur_cell(code, None if col!=LAV else None),(c*CW,r*CH))
    return img

CANDS=[
 ("CURRENT  (flown DS9 condensed)", render_current()),
 ("DejaVu Sans Condensed Bold",     render_ttf_panel("/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf", 30)),
 ("Noto Sans Medium",               render_ttf_panel("/usr/share/fonts/opentype/noto/NotoSans-Medium.ttf", 28) or render_ttf_panel("/usr/share/fonts/truetype/noto/NotoSans-Medium.ttf",28)),
 ("Liberation Sans Bold",           render_ttf_panel("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 28)),
 ("DejaVu Sans Mono Bold",          render_ttf_panel("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 30)),
 ("FreeSans Bold",                  render_ttf_panel("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", 30)),
]
CANDS=[(n,p) for n,p in CANDS if p is not None]
pad=18; lblw=330; pw=COLS*CW
W=lblw+pw+pad*2; rowh=ROWS*CH+20
H=rowh*len(CANDS)+pad
sheet=Image.new("RGB",(W,H),(14,16,20)); d=ImageDraw.Draw(sheet)
try: cf=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",17); cs=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",13)
except Exception: cf=cs=None
y=pad
for name,panel in CANDS:
    d.text((pad,y+rowh//2-14),name,fill=(180,225,195),font=cf)
    sheet.paste(panel,(lblw,y))
    y+=rowh
sheet.save(OUT); print("ok",OUT,sheet.size,"candidates:",len(CANDS))
