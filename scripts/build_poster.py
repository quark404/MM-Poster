#!/usr/bin/env python3
"""Build matching A0 PDF and editable PowerPoint from a shared vector layout."""
from pathlib import Path
import json
import yaml
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

# A white editorial canvas, with one clear narrative and restrained rules.
rect(0,0,W,H,WHITE)
text(30,15,421,'ACM MULTIMEDIA 2026  /  EMBODIED REASONING',22,True,TEAL)
text(28,32,423,'RoboPIN',100,True,NAVY)
logo_placeholder('mm_logo',476,27,244,54)
logo_placeholder('tju_logo',738,11,73,76)
text(30,80,781,'Grounded Embodied Reasoning\nvia Pinned Chain-of-Thought',STYLE['poster_title_font_size'],True,NAVY,leading=1.13,max_h=43)
text(30,126,781,'Yaoting Huang* · Yifu Yuan*† · Linqi Han · Chengwen Li · Shuoheng Zhang',STYLE['poster_author_font_size'],color=GRAY)
text(30,139,781,'Xianze Yao · Hongyao Tang · Yan Zheng · Jianye Hao†',STYLE['poster_author_font_size'],color=GRAY)
text(30,156,781,'Tianjin University   ·   Rio de Janeiro, Brazil   ·   10–14 November 2026',25,True,TEAL)
line(30,179,811,179,TEAL,2.5)

# 01: the original source comparison is the hero, with one focused explanation.
section(30,197,'01','Reason with a persistent visual anchor')
image(ROOT/'assets/figure-1-cot-comparison.png',30,232,484,484*180.96/335.60)
rect(546,232,265,261,NAVY,radius=2)
text(564,250,229,'THE CORE IDEA',23,True,'#90DED5')
text(564,274,229,'One entity.\nOne persistent ID.',37,True,WHITE,leading=1.14,max_h=35)
text(564,317,229,'a = (name, id, view, point)',21,color='#90DED5',mono=True)
for y,title,desc in [
    (343,'Introduce anchor','name · ID · view · point'),
    (411,'Reuse identity','across steps and views'),
]:
    rect(564,y,229,44,'#1B3B54','#4B687D',2)
    text(575,y+8,207,title,28,True,WHITE)
    text(575,y+27,207,desc,25,color='#DEEBF2')
line(678.5,391,678.5,406,'#90DED5',2.5)
line(675,402,678.5,406,'#90DED5',2.5)
line(682,402,678.5,406,'#90DED5',2.5)
text(564,474,229,'Visual evidence stays traceable.',22,color='#90DED5')

# 02: full-width original pipeline and a compact, editable training strip.
section(30,516,'02','How RoboPIN learns to stay grounded')
image(ROOT/'assets/figure-2-data-pipeline.png',40,552,761,761*110.12/493.65)
text(30,742,145,'Three-stage\npost-training',25,True,TEAL,leading=1.1)
for i,(name,desc) in enumerate([('SFT','Embodied knowledge'),('CoT-SFT','Structured reasoning'),('RFT / GRPO','Process alignment')]):
    x=195+i*207
    rect(x,735,195,40,'#F1F6F7',radius=2)
    text(x+5,741,185,name,27,True,TEAL,align='center')
    text(x+5,759,185,desc,23,color=GRAY,align='center')
    if i<2:arrow(x+198,755,x+205)

# 03: identical scientific data, with one accent colour and a larger plotting area.
from statistics import mean
perf=json.loads((ROOT/'performance_data.json').read_text())
section(30,797,'03','Grounding improves embodied reasoning')
for i,model in enumerate(perf['models']):
    model['display_color'] = TEAL if i==3 else TOKENS['baseline_chart_colors'][i]
    lx=[30,229,435,641][i]
    rect(lx,829,7,7,model['display_color'])
    text(lx+11,828,168,model['name'],22,bold=i==3,color=TEAL if i==3 else INK)
for panel,(key,title,sub) in enumerate([
    ('spatial','Spatial reasoning','13 capability columns · 9 benchmarks'),
    ('pointing','Pointing','5 benchmark mean'),
    ('robot','Real-world robots','60 executions · 3 tasks'),
]):
    x=30+panel*267
    text(x+25,849,224,title,29,True,NAVY)
    text(x+25,867,224,sub,20,color=GRAY)
    for tick in [0,50,100]:
        yy=981-94*tick/100
        line(x+25,yy,x+247,yy,'#DDE6EB',1)
        text(x,yy-4,19,str(tick),20,color=GRAY,align='right')
    for i,model in enumerate(perf['models']):
        if key=='robot':
            counts=model['robot_successes']
            value=None if counts is None else 100*sum(counts)/(perf['robot_trials_per_task']*perf['robot_task_count'])
        else:
            value=mean(model[key])
        bx=x+36+i*50
        if value is None:
            text(bx-4,968,38,'n/a',21,color=GRAY,align='center')
            continue
        bh=94*value/100
        rect(bx,981-bh,33,bh,model['display_color'])
        text(bx-6,981-bh-13,45,f'{value:.1f}',29,bold=i==3,color=TEAL if i==3 else INK,align='center')
text(30,993,781,'Scores (%) · Tables 1–3 / Figure 1. Spatial and pointing: arithmetic means. Robot: overall execution success.',21,color=GRAY)

# 04: deployment evidence and process consistency share a compact closing band.
section(30,1020,'04','Reliable execution and consistent entity tracking')
image(ROOT/'assets/robot-demo.png',30,1053,300,300*154.71/504.40)
text(30,1151,300,'Zero-shot xArm execution · Figure 3',21,color=GRAY)
text(355,1049,315,'Successful executions / 20 per task',22,True,GRAY)
for i,(label,val) in enumerate([('Spatial','20 / 20'),('Multi-view','14 / 20'),('Long-horizon','11 / 20')]):
    x=355+i*108
    text(x,1070,100,val,32,True,TEAL,align='center')
    text(x,1090,100,label,22,align='center')
rect(355,1112,315,42,'#EDF5F5',radius=2)
text(365,1117,295,'18.8% → 99.9%',34,True,TEAL)
text(365,1138,295,'Cross-step ID coverage · w/o RFT → RoboPIN',21,color=GRAY)
qr=CFG.get('qr_file')
text(717,1049,94,'PAPER / CODE',20,True,GRAY,align='center')
if qr and (ROOT/qr).is_file():
    image(ROOT/qr,724,1067,80,80)
else:
    rect(724,1067,80,80,WHITE,LINE,1)
    text(731,1090,66,'QR\nPLACEHOLDER',20,True,GRAY,align='center',leading=1.35)
line(30,1168,811,1168,LINE,1.2)
text(30,1175,410,'quark404@tju.edu.cn  ·  yuanyf@tju.edu.cn',21,color=GRAY)
text(459,1175,352,'* Equal contribution   † Corresponding authors',18,color=GRAY,align='right')

for item in audit:
    if item['x']<0 or item['y']<0 or item['x']+item['width']>W+.01 or item['y']+item['height']>H:
        raise ValueError(f'Content outside page: {item}')
c.showPage();c.save()
slide.notes_slide.notes_text_frame.text=(
    'A0 portrait 841 × 1189 mm. Iterated using the upstream Paper2Poster lightweight skill and visual review. '
    'The external API-based PosterAgent generator was not run. '
    'The original Figure 1 comparison is the main visual; Figure 2 upper pipeline is preserved. '
    'Three grouped bar charts reproduce paper Figure 1 and Tables 1–3: spatial mean over 13 capability columns, '
    'pointing mean over 5 benchmarks, robot successes over 60 trials. Missing robot baseline is n/a. '
    'The detailed selected-benchmark table is retained in the source notes rather than repeated on this poster. '
    'The robot trial-count caption conflict in the source paper still requires author confirmation. '
    'Logos are original official images; paper/code QR remains an intentional placeholder. '
    'Chart bars, values, axes, text and training nodes are editable; source figures are replaceable images.'
)
prs.save(str(OUT/'RoboPIN_A0_editable.pptx'))
(OUT/'layout-audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False))
print(f'Built {OUT}/RoboPIN_A0_portrait.pdf and RoboPIN_A0_editable.pptx ({len(audit)} text blocks).')
