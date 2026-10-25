#!/usr/bin/env python3
"""Build matching A0 PDF and editable PowerPoint from a shared vector layout."""
from pathlib import Path
import json
import math
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from pptx import Presentation
from pptx.util import Mm, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import MSO_ANCHOR

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output'
OUT.mkdir(exist_ok=True)
CFG = json.loads((ROOT / 'poster_config.json').read_text())
W, H = 841, 1189
MM = 72 / 25.4
NAVY = '#102B46'
TEAL = '#007E87'
MINT = '#E4F3F0'
INK = '#18334B'
GRAY = '#566B7C'
BG = '#F0F4F7'
LINE = '#D5E0E7'
WHITE = '#FFFFFF'
BLUE = '#5782A3'
AMBER = '#B2711D'
font_dir = Path('/usr/share/fonts/truetype/dejavu')
for name, file in [('Regular','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf'),('Mono','DejaVuSansMono.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(font_dir / file)))

prs = Presentation()
prs.slide_width, prs.slide_height = Mm(W), Mm(H)
slide = prs.slides.add_slide(prs.slide_layouts[6])
c = canvas.Canvas(str(OUT / 'RoboPIN_A0_portrait.pdf'), pagesize=(W*MM,H*MM), initialFontName='Regular')
c.setTitle('RoboPIN — Grounded Embodied Reasoning via Pinned Chain-of-Thought')
c.setAuthor('Yaoting Huang et al. — Tianjin University')
c.setSubject('ACM Multimedia 2026 | A0 portrait | official logos | QR placeholder')
audit = []

def rgb(v): return RGBColor.from_string(v.lstrip('#'))

def rect(x,y,w,h,fill=WHITE,stroke=None,radius=0,lw=1):
    c.setFillColor(HexColor(fill))
    c.setLineWidth(lw)
    if stroke: c.setStrokeColor(HexColor(stroke))
    if radius: c.roundRect(x*MM,(H-y-h)*MM,w*MM,h*MM,radius*MM,fill=1,stroke=bool(stroke))
    else: c.rect(x*MM,(H-y-h)*MM,w*MM,h*MM,fill=1,stroke=bool(stroke))
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,Mm(x),Mm(y),Mm(w),Mm(h))
    s.fill.solid(); s.fill.fore_color.rgb=rgb(fill)
    if stroke: s.line.color.rgb=rgb(stroke); s.line.width=Pt(lw)
    else: s.line.fill.background()
    if radius:
        s.adjustments[0]=min(radius/min(w,h),0.15)
    return s

def line(x1,y1,x2,y2,color=LINE,lw=1.5):
    c.setStrokeColor(HexColor(color)); c.setLineWidth(lw)
    c.line(x1*MM,(H-y1)*MM,x2*MM,(H-y2)*MM)
    s=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Mm(x1),Mm(y1),Mm(x2),Mm(y2))
    s.line.color.rgb=rgb(color); s.line.width=Pt(lw)

def text(x,y,w,value,size=28,bold=False,color=INK,leading=1.22,mono=False,align='left',max_h=None):
    font='Mono' if mono else ('Bold' if bold else 'Regular')
    lines=[]
    for para in value.split('\n'):
        if not para:
            lines.append('');continue
        words=para.split(' '); row=''
        for word in words:
            test=(row+' '+word).strip()
            if row and pdfmetrics.stringWidth(test,font,size)>w*MM:
                lines.append(row);row=word
            else:row=test
        lines.append(row)
    height=len(lines)*size*leading/MM
    if max_h is not None and height>max_h:
        raise ValueError(f'Text overflows box: {value[:50]} ({height:.1f}>{max_h} mm)')
    for i,t in enumerate(lines):
        tw=pdfmetrics.stringWidth(t,font,size)
        if tw>w*MM+0.1:raise ValueError(f'Text too wide: {t}')
        tx=x*MM + ((w*MM-tw)/2 if align=='center' else (w*MM-tw if align=='right' else 0))
        c.setFillColor(HexColor(color));c.setFont(font,size)
        c.drawString(tx,(H-y)*MM-size*0.86-i*size*leading,t)
    tb=slide.shapes.add_textbox(Mm(x),Mm(y),Mm(w),Mm(height+4))
    tf=tb.text_frame;tf.clear();tf.word_wrap=False
    tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
    tf.vertical_anchor=MSO_ANCHOR.TOP
    from pptx.enum.text import PP_ALIGN
    for i,t in enumerate(lines):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        p.text=t;p.font.name='DejaVu Sans Mono' if mono else 'DejaVu Sans'
        p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=rgb(color)
        p.space_before=Pt(0);p.space_after=Pt(0);p.line_spacing=Pt(size*leading)
        p.alignment={'left':PP_ALIGN.LEFT,'center':PP_ALIGN.CENTER,'right':PP_ALIGN.RIGHT}[align]
    audit.append({'text':value,'x':x,'y':y,'width':w,'height':height,'size_pt':size})
    return height

def image(file,x,y,w,h):
    c.drawImage(str(file),x*MM,(H-y-h)*MM,w*MM,h*MM,mask='auto')
    slide.shapes.add_picture(str(file),Mm(x),Mm(y),Mm(w),Mm(h))

def circle(x,y,r,fill=TEAL,stroke=WHITE):
    c.setFillColor(HexColor(fill));c.setStrokeColor(HexColor(stroke));c.setLineWidth(3)
    c.circle(x*MM,(H-y)*MM,r*MM,fill=1,stroke=1)
    s=slide.shapes.add_shape(MSO_SHAPE.OVAL,Mm(x-r),Mm(y-r),Mm(r*2),Mm(r*2))
    s.fill.solid();s.fill.fore_color.rgb=rgb(fill);s.line.color.rgb=rgb(stroke);s.line.width=Pt(3)

def arrow(x1,y,x2,color=TEAL):
    line(x1,y,x2,y,color,3)
    line(x2-4,y-3,x2,y,color,3);line(x2-4,y+3,x2,y,color,3)

def card(x,y,w,h):rect(x,y,w,h,WHITE,radius=4)

def section(x,y,num,title,w=352):
    rect(x,y,15,15,TEAL,radius=2)
    text(x,y+2.2,15,num,24,True,WHITE,align='center')
    text(x+21,y+1,w-21,title,33,True,max_h=17)

def logo_placeholder(key,x,y,w,h):
    file=CFG.get(key+'_file')
    if file and (ROOT/file).is_file():
        from PIL import Image
        with Image.open(ROOT/file) as im:iw,ih=im.size
        scale=min(w/iw,h/ih)
        image(ROOT/file,x+(w-iw*scale)/2,y+(h-ih*scale)/2,iw*scale,ih*scale)
    else:
        rect(x,y,w,h,'#1C3B56','#55748B',2)
        text(x+3,y+9,w-6,CFG[key+'_label'],18,True,'#D8E5ED',align='center',max_h=h-10)

# Header and a clear four-number summary.
rect(0,0,W,H,BG)
rect(0,0,W,176,WHITE)
rect(0,173,W,3,TEAL)
text(26,15,450,'VISUAL GROUNDING × IDENTITY-CONSISTENT REASONING',24,True,TEAL)
text(24,31,440,'RoboPIN',110,True,NAVY)
logo_placeholder('mm_logo',478,22,240,54)
logo_placeholder('tju_logo',735,10,80,78)
text(26,79,789,'Grounded Embodied Reasoning\nvia Pinned Chain-of-Thought',49,True,NAVY,leading=1.14,max_h=45)
text(26,125,789,'Yaoting Huang* · Yifu Yuan*† · Linqi Han · Chengwen Li · Shuoheng Zhang',25,color=GRAY)
text(26,138,789,'Xianze Yao · Hongyao Tang · Yan Zheng · Jianye Hao†',25,color=GRAY)
text(26,154,789,'Tianjin University   |   ACM Multimedia 2026 · Rio de Janeiro, Brazil',26,True,TEAL)

for i,(value,label) in enumerate([('4B','model parameters'),('170K','PinCoT reasoning samples'),('14','evaluation benchmarks'),('+35.4 pp','CrossPoint vs. Mimo-7B')]):
    x=26+i*201
    card(x,188,186,52)
    text(x+10,193,166,value,52,True,TEAL)
    text(x+10,221,166,label,22,color=GRAY)

# Core idea: use Figure 1's original comparison artwork, excluding its result panels.
card(26,254,789,270)
section(42,267,'01','One entity. One persistent identity.',760)
image(ROOT/'assets/figure-1-cot-comparison.png',42,293,414,414*180.96/335.60)
text(483,298,306,'Ground reasoning in\npersistent visual anchors.',33,True,TEAL,max_h=34)
for y,title,desc in [
    (341,'Text CoT','Implicit entity references can drift.'),
    (382,'Coordinate CoT','Spatial coordinates alone do not preserve identity.'),
    (429,'PinCoT / ours','Bind every step to an explicit, trackable entity.'),
]:
    text(483,y,306,title,27,True,TEAL if 'ours' in title else INK)
    text(483,y+16,306,desc,25,color=GRAY,max_h=27)
text(483,481,306,'Name + ID + view + point',27,True,TEAL)
text(483,499,306,'Original comparison: paper Figure 1 (left).',21,color=GRAY)

# A full-width Figure 2 keeps the original source images and pipeline legible.
card(26,538,789,239)
section(42,551,'02','From data to RoboPIN',760)
image(ROOT/'assets/figure-2-data-pipeline.png',70,573,700,700*110.12/493.65)
text(42,738,168,'Three-stage\npost-training',25,True,TEAL,leading=1.1)
for i,(name,desc) in enumerate([('SFT','Embodied knowledge'),('CoT-SFT','Structured reasoning'),('RFT / GRPO','Process alignment')]):
    x=225+i*195
    rect(x,735,179,30,MINT,radius=2)
    text(x+4,738,171,name,25,True,TEAL,align='center')
    text(x+4,752,171,desc,22,color=GRAY,align='center')
    if i<2:arrow(x+182,750,x+192)

# Benchmark table and a compact process-supervision finding.
card(26,791,384,250)
section(42,804,'03','Results & process analysis')
text(42,830,352,'RoboPIN 4B vs. Mimo-Embodied 7B',26,True,TEAL)
rect(42,848,352,21,NAVY,radius=1)
for x,w,t in [(48,145,'Benchmark'),(196,54,'7B'),(257,61,'4B / ours'),(332,57,'Δ pp')]:
    text(x,853,w,t,23,True,WHITE,align='left' if x==48 else 'right')
rows=[('EmbSpatial',76.2,83.1),('RoboSpatial',61.8,66.6),('CrossPoint',36.8,72.2),('BLINK · multi-view',26.3,72.9),('RoboRefit',82.3,89.0),('RoboAfford',69.8,72.8)]
for i,(label,a,b) in enumerate(rows):
    y=872+i*18
    if i%2==0:rect(42,y-1,352,18,MINT if i==2 else BG)
    text(48,y+2,148,label,24,bold=i==2)
    text(196,y+2,54,f'{a:.1f}',26,align='right')
    text(257,y+2,61,f'{b:.1f}',26,True,TEAL,align='right')
    text(332,y+2,57,f'+{b-a:.1f}',25,True,TEAL,align='right')
text(42,985,352,'Selected results, Tables 1–2; Δ in percentage points.',21,color=GRAY)
rect(42,1001,352,28,MINT,radius=2)
text(50,1004,336,'Cross-step ID coverage: 18.8% → 99.9%',25,True,TEAL)
text(50,1018,336,'Without RFT → RoboPIN · EmbSpatial, Table 7',21,color=GRAY)

# Real-world validation, right bottom.
card(431,791,384,250)
section(447,806,'04','Zero-shot robot transfer')
text(447,830,352,'xArm · static + wrist RGB cameras',26,True,TEAL)
image(ROOT/'assets/robot-demo.png',447,850,352,108)
text(447,966,352,'Successful executions / 20 per task',23,True,color=GRAY)
for i,(label,val) in enumerate([('Spatial','20 / 20'),('Multi-view','14 / 20'),('Long-horizon','11 / 20')]):
    x=447+i*122
    text(x,984,108,val,35,True,TEAL,align='center')
    text(x,1005,108,label,23,align='center')
text(447,1025,352,'Paper Figure 3 and Table 3',21,color=GRAY)

# Takeaway and replaceable publishing assets.
rect(26,1055,789,108,NAVY,radius=4)
text(42,1068,619,'Ground every step. Preserve every identity.',36,True,WHITE)
text(42,1090,619,'PinCoT makes visual evidence trackable across reasoning steps\nand viewpoints, supporting reliable embodied decisions.',27,color='#DAE7EF',max_h=30)
text(42,1124,619,'Contact: quark404@tju.edu.cn   |   yuanyf@tju.edu.cn',23,color='#87DCD1')
text(42,1141,619,'* Equal contribution   † Corresponding authors: Yifu Yuan, Jianye Hao',21,color='#DAE7EF')
qr=CFG.get('qr_file')
if qr and (ROOT/qr).is_file():
    rect(717,1071,78,78,WHITE,radius=1)
    image(ROOT/qr,721,1075,70,70)
else:
    rect(717,1071,78,78,'#1C3B56','#55748B',2)
    text(723,1090,66,'PAPER / CODE\nQR PLACEHOLDER',21,True,'#D8E5ED',align='center',leading=1.4)

for item in audit:
    if item['x']<0 or item['y']<0 or item['x']+item['width']>W+.01 or item['y']+item['height']>H:
        raise ValueError(f'Content outside page: {item}')
c.showPage();c.save()
slide.notes_slide.notes_text_frame.text=(
    'A0 portrait (841 × 1189 mm), verified against the ACM Multimedia 2026 presenter guidelines. '
    'Text, the results table and the training nodes are editable; original paper figures and logos are separate replaceable images. '
    'Sections 01 and 02 use the original Figure 1 left comparison and Figure 2 upper data pipeline from the supplied paper. '
    'Tables 1–2: selected comparisons only. Table 7: cross-step identity coverage. '
    'Robot trial counts follow Table 3 and Section 4.3; the Table 3 caption says 5 trials and requires author confirmation. '
    'Conference and Tianjin University logos use unmodified official assets matching the supplied designs on a white header. '
    'Only the paper/code QR remains an intentional placeholder. '
    'The 12% abstract claim is omitted because the aggregate weighting is not specified. '
    'See README.md and SOURCES.md for provenance, editing and build instructions.'
)
prs.save(str(OUT/'RoboPIN_A0_editable.pptx'))
(OUT/'layout-audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False))
print(f'Built {OUT}/RoboPIN_A0_portrait.pdf and RoboPIN_A0_editable.pptx ({len(audit)} text blocks).')
