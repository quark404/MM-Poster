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
c.setSubject('ACM Multimedia 2026 | A0 portrait | logo and QR placeholders')
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
rect(0,0,W,176,NAVY)
rect(0,173,W,3,TEAL)
text(26,15,560,'VISUAL GROUNDING × IDENTITY-CONSISTENT REASONING',24,True,'#87DCD1')
text(24,31,580,'RoboPIN',110,True,WHITE)
logo_placeholder('mm_logo',638,22,82,42)
logo_placeholder('tju_logo',733,22,82,42)
text(26,79,789,'Grounded Embodied Reasoning\nvia Pinned Chain-of-Thought',49,True,WHITE,leading=1.14,max_h=45)
text(26,125,789,'Yaoting Huang* · Yifu Yuan*† · Linqi Han · Chengwen Li · Shuoheng Zhang',25,color='#E0EBF2')
text(26,138,789,'Xianze Yao · Hongyao Tang · Yan Zheng · Jianye Hao†',25,color='#E0EBF2')
text(26,154,789,'Tianjin University   |   ACM Multimedia 2026 · Rio de Janeiro, Brazil',26,True,'#87DCD1')

for i,(value,label) in enumerate([('4B','model parameters'),('170K','PinCoT reasoning samples'),('14','evaluation benchmarks'),('+35.4 pp','CrossPoint vs. Mimo-7B')]):
    x=26+i*201
    card(x,188,186,52)
    text(x+10,193,166,value,52,True,TEAL)
    text(x+10,221,166,label,22,color=GRAY)

# Core idea: native text plus two cropped source views, with editable anchors.
card(26,254,789,219)
section(42,267,'01','One entity. One persistent identity.',760)
text(42,294,373,'Why visual reasoning drifts',31,True)
for y,title,desc,fill in [
    (315,'Text CoT','Implicit references can switch objects.',BG),
    (359,'Coordinate CoT','A location alone does not track identity.',BG),
    (403,'PinCoT / ours','Ground once; reuse the same entity ID.',MINT),
]:
    rect(42,y,373,39,fill,radius=2)
    text(52,y+4,353,title,27,True,TEAL if fill==MINT else INK)
    text(52,y+21,353,desc,24,color=GRAY)
text(446,294,157,'VIEW 0',24,True,TEAL)
text(632,294,157,'VIEW 1',24,True,TEAL)
image(ROOT/'assets/view-0.png',446,310,157,118)
image(ROOT/'assets/view-1.png',632,310,157,118)
arrow(608,367,626)
for x,px,py in [(446,.634,.576),(632,.844,.706)]:
    circle(x+157*px,310+118*py,4)
    rect(x+6,316,72,14,TEAL,radius=1)
    text(x+8,317,68,'obj_01',24,True,WHITE,align='center')
text(446,434,348,'Same microwave → same obj_01',27,True,TEAL)
text(446,450,348,'Name + ID + view + point = reasoning anchor',23,color=GRAY)

# Methods, left column.
card(26,487,384,286)
section(42,502,'02','From data to RoboPIN')
text(42,529,352,'Automated PIN-170K construction',27,True,TEAL)
for idx,(y,title,desc) in enumerate([
    (548,'Semantic parsing','Qwen3-VL-32B extracts task-relevant entities.'),
    (591,'Point grounding','Florence-2 + SAM 2.1; reverse verification.'),
    (634,'PinCoT generation','Grounded traces + rule-based quality filtering.'),
]):
    rect(42,y,352,36,BG,radius=2)
    text(50,y+4,23,str(idx+1),29,True,TEAL)
    text(73,y+3,313,title,27,True)
    text(73,y+19,313,desc,22,color=GRAY)
    if idx<2:
        line(218,y+37,218,y+42,TEAL,2)
text(42,687,352,'Three-stage post-training',28,True,TEAL)
for i,(name,desc) in enumerate([('SFT','Embodied\nknowledge'),('CoT-SFT','Structured\nreasoning'),('RFT / GRPO','Process\nalignment')]):
    x=42+i*122
    rect(x,706,108,47,MINT,radius=2)
    text(x+4,712,100,name,25,True,TEAL,align='center')
    text(x+4,729,100,desc,22,color=GRAY,align='center',leading=1.05)
    if i<2:arrow(x+111,729,x+120)

# Benchmark results, right column: editable table with precise source values.
card(431,487,384,286)
section(447,502,'03','Benchmark highlights')
text(447,529,352,'RoboPIN 4B vs. Mimo-Embodied 7B',27,True,TEAL)
rect(447,550,352,23,NAVY,radius=1)
for x,w,t in [(453,145,'Benchmark'),(601,54,'7B'),(662,61,'4B / ours'),(737,57,'Δ pp')]:
    text(x,556,w,t,23,True,WHITE,align='left' if x==453 else 'right')
rows=[('EmbSpatial',76.2,83.1),('RoboSpatial',61.8,66.6),('CrossPoint',36.8,72.2),('BLINK · multi-view',26.3,72.9),('RoboRefit',82.3,89.0),('RoboAfford',69.8,72.8)]
for i,(label,a,b) in enumerate(rows):
    y=575+i*22
    if i%2==0:rect(447,y-1,352,22,MINT if i==2 else BG)
    text(453,y+3,148,label,24,bold=i==2)
    text(601,y+3,54,f'{a:.1f}',26,align='right')
    text(662,y+3,61,f'{b:.1f}',26,True,TEAL,align='right')
    text(737,y+3,57,f'+{b-a:.1f}',25,True,TEAL,align='right')
text(447,716,352,'Strong cross-view correspondence\nwith a smaller parameter budget.',28,True,max_h=30)
text(447,752,352,'Selected results, Tables 1–2; Δ is percentage points.',21,color=GRAY)

# Process analysis, left bottom.
card(26,787,384,254)
section(42,802,'04','Why process rewards help')
text(42,830,352,'Reward the process and the answer.',27,True,TEAL)
rect(42,850,352,35,MINT,radius=2)
text(50,857,336,'Format + consistency + pin + accuracy',25,True,TEAL,align='center')
text(42,897,352,'Cross-step identity coverage · EmbSpatial',25,True)
for y,label,value,color in [(921,'w/o RFT',18.8,BLUE),(946,'RoboPIN',99.9,TEAL)]:
    text(42,y,85,label,24,bold=label=='RoboPIN',color=color)
    rect(132,y+1,202,10,BG,radius=1)
    rect(132,y+1,202*value/100,10,color,radius=1)
    text(341,y-1,53,f'{value:.1f}%',25,True,color,align='right')
text(42,974,352,'RFT enforces persistent ID reuse, beyond\nlocalizing anchors correctly.',27,True,max_h=28)
text(42,1015,352,'Anchor correctness: 89.1%   |   Table 7',23,color=GRAY)

# Real-world validation, right bottom.
card(431,787,384,254)
section(447,802,'05','Zero-shot robot transfer')
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
    'All text, bars, tables, nodes, pins and logo placeholders are editable; scene/robot photographs are cropped from the supplied paper. '
    'Tables 1–2: selected comparisons only. Table 7: cross-step identity coverage. '
    'Robot trial counts follow Table 3 and Section 4.3; the Table 3 caption says 5 trials and requires author confirmation. '
    'Conference and Tianjin University logos and paper/code QR are intentional placeholders. '
    'The 12% abstract claim is omitted because the aggregate weighting is not specified. '
    'See README.md and SOURCES.md for provenance, editing and build instructions.'
)
prs.save(str(OUT/'RoboPIN_A0_editable.pptx'))
(OUT/'layout-audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False))
print(f'Built {OUT}/RoboPIN_A0_portrait.pdf and RoboPIN_A0_editable.pptx ({len(audit)} text blocks).')
