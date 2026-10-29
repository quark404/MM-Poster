#!/usr/bin/env python3
"""Build matching A0 PDF and editable PowerPoint from a shared vector layout."""
from pathlib import Path
import json
import yaml
import argparse
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from pptx import Presentation
from pptx.util import Mm, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import MSO_ANCHOR
from html_poster import HTMLPoster

ROOT = Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--variant',choices=['source'],default='source')
parser.add_argument('--output-dir',default='output')
ARGS=parser.parse_args()
OUT=ROOT/ARGS.output_dir
VARIANT=ARGS.variant
OUT.mkdir(parents=True,exist_ok=True)
CFG = json.loads((ROOT / 'poster_config.json').read_text())
STYLE = yaml.safe_load((ROOT/'assets/poster.yaml').read_text())
TOKENS = STYLE['robopin']
W, H = TOKENS['width_mm'], TOKENS['height_mm']
MM = 72 / 25.4
NAVY = '#'+''.join(f'{v:02X}' for v in STYLE['title_text_color'])
TEAL = '#'+''.join(f'{v:02X}' for v in TOKENS['accent_rgb'])
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
html = HTMLPoster(W,H)

def rgb(v): return RGBColor.from_string(v.lstrip('#'))

def rect(x,y,w,h,fill=WHITE,stroke=None,radius=0,lw=1):
    html.rect(x,y,w,h,fill,stroke,radius,lw)
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
    html.line(x1,y1,x2,y2,color,lw)
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
    html.text(x,y,w,lines,size,bold,color,leading,mono,align)
    return height

def image(file,x,y,w,h):
    html.image(file,x,y,w,h)
    c.drawImage(str(file),x*MM,(H-y-h)*MM,w*MM,h*MM,mask='auto')
    slide.shapes.add_picture(str(file),Mm(x),Mm(y),Mm(w),Mm(h))

def circle(x,y,r,fill=TEAL,stroke=WHITE):
    html.circle(x,y,r,fill,stroke)
    c.setFillColor(HexColor(fill));c.setStrokeColor(HexColor(stroke));c.setLineWidth(3)
    c.circle(x*MM,(H-y)*MM,r*MM,fill=1,stroke=1)
    s=slide.shapes.add_shape(MSO_SHAPE.OVAL,Mm(x-r),Mm(y-r),Mm(r*2),Mm(r*2))
    s.fill.solid();s.fill.fore_color.rgb=rgb(fill);s.line.color.rgb=rgb(stroke);s.line.width=Pt(3)

def arrow(x1,y,x2,color=TEAL):
    line(x1,y,x2,y,color,3)
    line(x2-4,y-3,x2,y,color,3);line(x2-4,y+3,x2,y,color,3)

def card(x,y,w,h):rect(x,y,w,h,WHITE,radius=4)

def section(x,y,num,title,w=781):
    text(x,y+2,23,num,24,True,TEAL)
    text(x+31,y,w-31,title,STYLE['section_title_font_size'],True,NAVY,max_h=17)
    line(x,y+21,x+w,y+21,LINE,1.2)

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

# Rebuild the user's AI mockup with native gradients, cards and scientific content.
import math

def gradient_box(x,y,w,h,left=TOKENS['gradient_start'],right=TOKENS['gradient_end'],radius=9):
    html.gradient(x,y,w,h,left,right,radius)
    c.saveState()
    path=c.beginPath();path.roundRect(x*MM,(H-y-h)*MM,w*MM,h*MM,radius*MM)
    c.clipPath(path,stroke=0)
    c.linearGradient(x*MM,0,(x+w)*MM,0,[HexColor(left),HexColor(right)],extend=True)
    c.restoreState()
    sh=slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Mm(x),Mm(y),Mm(w),Mm(h))
    sh.adjustments[0]=min(radius/min(w,h),.2)
    sh.fill.gradient();sh.fill.gradient_angle=0
    stops=sh.fill.gradient_stops
    stops[0].position=0;stops[0].color.rgb=rgb(left)
    stops[1].position=1;stops[1].color.rgb=rgb(right)
    sh.line.fill.background()

def badge(kind,cx,cy,r=18):
    if kind!='bulb':circle(cx,cy,r,'#006B7C','#006B7C')
    if kind=='bulb':
        circle(cx,cy-1,8,'#F6CF42','#F6CF42')
        rect(cx-4,cy+6,8,6,'#F6CF42',radius=1)
        line(cx-3,cy+14,cx+3,cy+14,'#F6CF42',3)
        for a in range(0,360,45):
            ang=math.radians(a);line(cx+12*math.cos(ang),cy-1+12*math.sin(ang),cx+16*math.cos(ang),cy-1+16*math.sin(ang),'#F6CF42',2)
    elif kind=='target':
        for rad in [12,8,4]:circle(cx,cy,rad,'#006B7C',WHITE)
        line(cx,cy,cx+13,cy-14,WHITE,4)
        line(cx+8,cy-14,cx+13,cy-14,WHITE,3);line(cx+13,cy-14,cx+13,cy-9,WHITE,3)
    elif kind=='gear':
        for a in range(0,360,45):
            ang=math.radians(a);line(cx+8*math.cos(ang),cy+8*math.sin(ang),cx+13*math.cos(ang),cy+13*math.sin(ang),WHITE,7)
        circle(cx,cy,9,WHITE,WHITE);circle(cx,cy,3.4,'#006B7C','#006B7C')
    elif kind=='clipboard':
        rect(cx-9,cy-11,18,23,'#006B7C',WHITE,2,lw=2.5)
        rect(cx-5,cy-13,10,5,WHITE,radius=1)
        for dy in [-4,2,8]:
            line(cx-4,cy+dy,cx+6,cy+dy,WHITE,2)
            circle(cx-6.5,cy+dy,.7,WHITE,WHITE)
    else:
        line(cx-11,cy+11,cx-11,cy-10,WHITE,3);line(cx-11,cy+11,cx+12,cy+11,WHITE,3)
        for x1,y1,x2,y2 in [(-7,5,-1,-3),(-1,-3,5,1),(5,1,11,-9)]:line(cx+x1,cy+y1,cx+x2,cy+y2,WHITE,3)
        for dx,dy in [(-7,5),(-1,-3),(5,1),(11,-9)]:circle(cx+dx,cy+dy,1.6,WHITE,WHITE)

def panel(x,y,w,h,title,kind,size=34):
    rect(x,y,w,h,WHITE,'#BDE5E7',10,lw=1)
    gradient_box(x,y,w,43,radius=10)
    rect(x+.7,y+33,w-1.4,h-33.7,WHITE,radius=10)
    # Smaller contained marks keep all module headings aligned.
    text(x+18,y+7,w-30,title,min(size,34),True,WHITE,max_h=19)

rect(0,0,W,H,WHITE)
image(ROOT/'assets/rio-wave-background.png',0,0,W,H)
# Header is quieter in all variants; compact versions return space to evidence.
compact=True
text(22,10,550,'RoboPIN',112 if compact else 138,True,'#00576B')
text(24,57 if compact else 70,590,'Grounded Embodied Reasoning\nvia Pinned Chain-of-Thought',36 if compact else 41,True,NAVY,leading=1.07,max_h=35)
text(24,91 if compact else 109,610,'Yaoting Huang* · Yifu Yuan*† · Linqi Han · Chengwen Li · Shuoheng Zhang',23,color=INK)
text(24,104 if compact else 122,610,'Xianze Yao · Hongyao Tang · Yan Zheng · Jianye Hao†',23,color=INK)
text(24,120 if compact else 139,612,'Tianjin University · ACM Multimedia 2026 · Rio de Janeiro, Brazil',23,True,TEAL)
text(24,135 if compact else 154,612,'quark404@tju.edu.cn · yuanyf@tju.edu.cn   |   * Equal contribution   † Corresponding authors',18,color=GRAY)
logo_placeholder('mm_logo',596,16,227,47)
seal_y=73 if compact else 91
from PIL import Image
with Image.open(ROOT/CFG['tju_logo_file']) as seal: seal_h=64*seal.height/seal.width
seal_top=seal_y+(64-seal_h)/2
c.saveState();mask=c.beginPath();mask.circle(679*MM,(H-seal_y-32)*MM,32*MM);c.clipPath(mask,stroke=0)
c.drawImage(str(ROOT/CFG['tju_logo_file']),647*MM,(H-seal_top-seal_h)*MM,64*MM,seal_h*MM,mask='auto');c.restoreState()
seal_pic=slide.shapes.add_picture(str(ROOT/CFG['tju_logo_file']),Mm(647),Mm(seal_top),Mm(64),Mm(seal_h))
seal_pic._pic.spPr.prstGeom.set('prst','ellipse')
html.image(ROOT/CFG['tju_logo_file'],647,seal_top,64,seal_h,round_image=True)
text(718,90 if compact else 108,111,'Tianjin University',26,True,NAVY)

panel(14,153,434,328,'Motivation','bulb',36)
image(ROOT/'assets/figure-1-cot-comparison.png',39,195,384,384*180.96/335.60)
for yy,num,title,desc in [
    (413,'1','Reference drift','Entity references can switch between similar objects across reasoning steps.'),
    (445,'2','Reasoning–answer misalignment','The final answer can point to a different entity from the one analyzed.'),
]:
    gradient_box(26,yy,410,27,'#EFF8FA','#F4F9FB',radius=4)
    circle(43,yy+13.5,9,TEAL,TEAL)
    text(34,yy+5,18,num,25,True,WHITE,align='center')
    text(62,yy+2,361,title,25,True,TEAL)
    text(62,yy+17,361,desc,21,max_h=10)

panel(456,153,371,328,'Key Insight: Persistent Identity','target',32)
for file,x,px,py in [('view-0.png',469,.634,.576),('view-1.png',665,.844,.706)]:
    text(x,198,148,'VIEW 0' if x==469 else 'VIEW 1',22,True,TEAL,align='center')
    image(ROOT/'assets'/file,x,214,148,113)
    circle(x+148*px,214+113*py,3.8)
    rect(x+5,219,69,13,TEAL,radius=1)
    text(x+7,220,65,'obj_01',23,True,WHITE,align='center')
arrow(627,269,653)
gradient_box(468,337,347,61,'#EDF8FA','#F3F8FB',radius=5)
text(479,345,325,'Same entity. Same ID. Different views.',27,True,TEAL)
text(479,366,325,'Anchor = name + ID + view + point.',25,True)
text(479,385,325,'Keep identity stable across steps and viewpoints.',21)
gradient_box(468,406,264,65,'#EDF8F3','#F4FAF7',radius=5)
text(480,414,240,'Our insight',27,True,TEAL)
text(480,436,240,'Persistent IDs connect visual evidence, intermediate steps and the final answer.',23,max_h=30)
qr=CFG.get('qr_file')
if qr and (ROOT/qr).is_file():image(ROOT/qr,751,407,60,60)
else:
    rect(746,407,70,60,WHITE,LINE,4)
    text(751,430,60,'QR\nPLACEHOLDER',17,True,GRAY,align='center',leading=1.3)
text(742,470,78,'PAPER / CODE',17,True,NAVY,align='center')

panel(14,491,813,234,'Our Method: RoboPIN / PinCoT','gear',35)
image(ROOT/'assets/figure-2-data-pipeline.png',70,532,700,700*110.12/493.65)
text(37,696,137,'Three-stage\npost-training',25,True,TEAL,leading=1.1)
for i,(name,desc) in enumerate([('SFT','Embodied knowledge'),('CoT-SFT','Structured reasoning'),('RFT / GRPO','Process alignment')]):
    xx=[190,403,624][i]
    gradient_box(xx,692,186,28,'#E1F5F6','#EEF9FA',radius=4)
    text(xx+4,694,178,name,25,True,TEAL,align='center')
    text(xx+4,708,178,desc,21,color=INK,align='center')
    if i<2:arrow(xx+192,706,xx+207)

panel(14,735,400,420,'Experimental Results','clipboard',33)
# Preserve the actual published plot, including its original legend and labels.
image(ROOT/'assets/performance-original.png',34,779,360,360*106.12/166.2)
text(26,1021,376,'Ablation studies',29,True,TEAL)
# Two compact, editable tables. Values come from Tables 5 and 6, not Table 7.
text(26,1044,179,'Reward design',25,True,NAVY)
text(222,1044,180,'Training stages',25,True,NAVY)
rect(26,1060,178,15,'#EDF5F6',radius=2)
rect(222,1060,180,15,'#EDF5F6',radius=2)
text(31,1063,112,'Setting',20,True)
text(148,1063,51,'EmbSpatial',17,True,align='right')
text(227,1063,70,'Stage',20,True)
text(299,1063,45,'Spatial',19,True,align='right')
text(351,1063,46,'Point',19,True,align='right')
for i,(name,value) in enumerate([('Full reward','84.7'),('w/o Pin','82.0'),('w/o Consistency','82.7')]):
    yy=1081+i*19
    text(31,yy,117,name,22,bold=i==0,color=TEAL if i==0 else INK)
    text(151,yy,48,value,24,bold=i==0,color=TEAL if i==0 else INK,align='right')
for i,(name,spatial,point) in enumerate([('SFT','57.0','66.0'),('+ CoT-SFT','62.0','63.6'),('+ RFT','67.7','67.9')]):
    yy=1081+i*19
    text(227,yy,70,name,21,bold=i==2,color=TEAL if i==2 else INK)
    text(299,yy,45,spatial,24,bold=i==2,color=TEAL if i==2 else INK,align='right')
    text(351,yy,46,point,24,bold=i==2,color=TEAL if i==2 else INK,align='right')
line(214,1047,214,1133,LINE,1)
text(26,1140,376,'Spatial reasoning: +10.7 points from SFT to RFT.',21,True,TEAL)

panel(422,735,405,420,'Qualitative Results','chart',34)
image(ROOT/'assets/robot-three-rows.png',435,779,379,379*231.81/497.2)
text(435,966,379,'Zero-shot xArm · successes / 20',24,True,TEAL)
for i,(label,val) in enumerate([('Spatial','20 / 20'),('Multi-view','14 / 20'),('Long-horizon','11 / 20')]):
    xx=435+i*128
    text(xx,984,119,val,29,True,TEAL,align='center')
    text(xx,1000,119,label,21,align='center')
image(ROOT/'assets/figure-4-two-examples.png',463,1015,323,323*96.68/240.25)
text(45,1170,751,'Persistent visual anchors make embodied reasoning traceable.',27,True,WHITE,align='center')

for item in audit:
    if item['x']<0 or item['y']<0 or item['x']+item['width']>W+.01 or item['y']+item['height']>H:
        raise ValueError(f'Content outside page: {item}')
c.showPage();c.save()
slide.notes_slide.notes_text_frame.text=(
    'A0 portrait 841 × 1189 mm. HTML/CSS and native PowerPoint share the same layout. '
    'Performance is the untouched plot cropped from paper Figure 1. Robot visualization includes all three rows of Figure 3. '
    'Reward ablation: Table 5, controlled EmbSpatial setting (84.7 / 82.0 / 82.7). '
    'Cumulative training: Table 6, Spatial 57.0 / 62.0 / 67.7, Point 66.0 / 63.6 / 67.9. '
    'The controlled ablation averages are distinct from the headline results; Point does not improve monotonically. '
    'No cross-step coverage panel. Text and ablation tables are editable; paper images and logos are replaceable pictures. '
    'Trial-count discrepancy in the source caption remains documented in SOURCES.md. QR is a placeholder.'
)
prs.save(str(OUT/'RoboPIN_A0_editable.pptx'))
html.save(OUT/'RoboPIN_A0.html',font_dir)
(OUT/'layout-metadata.json').write_text(json.dumps({'variant':VARIANT,'chart_region':[14,735,414,1155],'qualitative_asset':'assets/figure-4-two-examples.png','performance_asset':'assets/performance-original.png','robot_asset':'assets/robot-three-rows.png'},indent=2))
(OUT/'layout-audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False))
print(f'Built {OUT}/RoboPIN_A0_portrait.pdf and RoboPIN_A0_editable.pptx ({len(audit)} text blocks).')
