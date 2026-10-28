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

ROOT = Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--variant',choices=['clean','balanced','mechanism'],default='mechanism')
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

# Rebuild the user's AI mockup with native gradients, cards and scientific content.
import math

def gradient_box(x,y,w,h,left=TOKENS['gradient_start'],right=TOKENS['gradient_end'],radius=9):
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
if VARIANT=='clean':
    rect(0,0,W,171,WHITE)
# Header is quieter in all variants; compact versions return space to evidence.
compact=VARIANT!='clean'
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
text(718,90 if compact else 108,111,'Tianjin University',26,True,NAVY)

if VARIANT=='clean':
    # Motivation: mockup-aligned wide left card with two numbered callouts.
    panel(14,175,434,359,'Motivation','bulb',38)
    image(ROOT/'assets/figure-1-cot-comparison.png',26,216,410,410*180.96/335.60)
    for yy,num,title,desc in [
        (459,'1','Reference drift','Textual references can switch between similar objects during multi-step reasoning.'),
        (495,'2','Reasoning–answer misalignment','A correct intermediate analysis can still end on the wrong object, especially across views.'),
    ]:
        gradient_box(26,yy,410,32,'#E9F7FA','#F0F8FD',radius=6)
        gradient_box(37,yy+3,24,26,'#13A6AE','#00748B',radius=12)
        text(37,yy+6,24,num,28,True,WHITE,align='center')
        text(69,yy+3,354,title,25,True,TEAL)
        text(69,yy+18,354,desc,20,max_h=14)

    # Key insight: paired views, blue explanation card, mint callout and dashed QR frame.
    panel(456,175,371,359,'Key Insight: Persistent Identity','target',33)
    for file,x,px,py in [('view-0.png',469,.634,.576),('view-1.png',665,.844,.706)]:
        text(x,222,148,'VIEW 0' if x==469 else 'VIEW 1',23,True,TEAL,align='center')
        image(ROOT/'assets'/file,x,237,148,113)
        circle(x+148*px,237+113*py,3.8)
        rect(x+5,242,69,13,TEAL,radius=1)
        text(x+7,243,65,'obj_01',23,True,WHITE,align='center')
    arrow(627,292,653)
    gradient_box(468,360,347,71,'#E7F7FA','#EDF6FD',radius=7)
    text(479,370,325,'Same entity. Same ID. Different views.',29,True,TEAL)
    text(479,393,325,'Reasoning anchor = name + ID + view + point.',25,True)
    text(479,413,325,'Introduce the anchor; reuse its identity throughout the reasoning chain.',21,max_h=15)
    gradient_box(468,447,264,80,'#E8F7EF','#EDF9F5',radius=7)
    for ang_deg in range(0,360,45):
        ang=math.radians(ang_deg);line(487+6*math.cos(ang),465+6*math.sin(ang),487+10*math.cos(ang),465+10*math.sin(ang),TEAL,5)
    circle(487,465,7,TEAL,TEAL);circle(487,465,2.5,'#E8F7EF','#E8F7EF')
    text(507,456,213,'Our insight',30,True,TEAL)
    text(480,487,237,'Persistent IDs connect visual grounding, intermediate steps and the final answer.',23,max_h=34)
    qr=CFG.get('qr_file')
    if qr and (ROOT/qr).is_file():image(ROOT/qr,751,451,60,60)
    else:
        from pptx.enum.dml import MSO_LINE_DASH_STYLE
        c.saveState();c.setDash(4,3);c.setStrokeColor(HexColor('#9DB6C7'));c.setLineWidth(1.5)
        c.roundRect(746*MM,(H-451-60)*MM,70*MM,60*MM,4*MM,fill=0,stroke=1);c.restoreState()
        q=slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Mm(746),Mm(451),Mm(70),Mm(60))
        q.fill.background();q.line.color.rgb=rgb('#9DB6C7');q.line.width=Pt(1.5);q.line.dash_style=MSO_LINE_DASH_STYLE.DASH
        text(751,474,60,'QR\nPLACEHOLDER',17,True,GRAY,align='center',leading=1.3)
    text(742,518,78,'PAPER / CODE',18,True,NAVY,align='center')

    # Full-width method card.
    panel(14,544,813,304,'Our Method: RoboPIN / PinCoT','gear',37)
    image(ROOT/'assets/figure-2-data-pipeline.png',26,585,789,789*110.12/493.65)
    text(42,787,132,'Three-stage\npost-training',25,True,TEAL,leading=1.1)
    for i,(name,desc) in enumerate([('SFT','Embodied knowledge'),('CoT-SFT','Structured reasoning'),('RFT / GRPO','Process alignment')]):
        xx=[190,403,624][i]
        gradient_box(xx,780,186,41,'#D0F2F4','#E8F9FB',radius=5)
        text(xx+4,786,178,name,26,True,TEAL,align='center')
        text(xx+4,804,178,desc,22,color=INK,align='center')
        if i<2:arrow(xx+192,800,xx+207)
    text(26,831,789,'PinCoT binds visual evidence to persistent identities. PIN-170K supplies structured traces; process rewards supervise grounding and identity consistency.',23,True,max_h=15)

    # Experimental results and qualitative results share the bottom row.
    from statistics import mean
    perf=json.loads((ROOT/'performance_data.json').read_text())
    panel(14,858,400,297,'Experimental Results','clipboard',35)
    for i,model in enumerate(perf['models']):
        model['display_color']=TEAL if i==3 else TOKENS['baseline_chart_colors'][i]
        lx=37+(i%2)*180;ly=901+(i//2)*16
        rect(lx,ly+1,6,6,model['display_color'])
        text(lx+10,ly,169,model['name'],19,bold=i==3,color=TEAL if i==3 else INK)
    for pp,(key,title) in enumerate([('spatial','Spatial'),('pointing','Pointing'),('robot','Robot')]):
        xx=26+pp*124
        text(xx+16,943,105,title,23,True,NAVY,align='center')
        for tick in [0,50,100]:
            yy=1054-83*tick/100
            line(xx+16,yy,xx+117,yy,'#DDE6EB',1)
            text(xx-2,yy-3,14,str(tick),16,color=GRAY,align='right')
        for i,model in enumerate(perf['models']):
            if key=='robot':
                counts=model['robot_successes']
                value=None if counts is None else 100*sum(counts)/(perf['robot_trials_per_task']*perf['robot_task_count'])
            else:value=mean(model[key])
            bx=xx+20+i*24
            if value is None:text(bx-3,1042,22,'n/a',18,color=GRAY,align='center');continue
            bh=.83*value
            rect(bx,1054-bh,18,bh,model['display_color'])
            text(bx-4,1054-bh-11,26,f'{value:.1f}',20,bold=i==3,color=TEAL if i==3 else INK,align='center')
    text(26,1068,376,'Scores (%) · Spatial: 13-column mean; pointing: 5-benchmark mean; robot: success over 60 trials.',19,color=GRAY,max_h=23)
    gradient_box(26,1096,376,47,'#E8F7F5','#EDF9FC',radius=6)
    text(38,1105,352,'18.8% → 99.9% cross-step ID coverage',27,True,TEAL)
    text(38,1127,352,'Without RFT → RoboPIN · EmbSpatial',21,color=GRAY)

    panel(422,858,405,297,'Qualitative Results','chart',36)
    image(ROOT/'assets/robot-demo.png',435,902,379,379*154.71/504.40)
    image(ROOT/'assets/figure-4-qualitative.png',435,1025,198,198*146.20/240.25)
    text(691,1025,123,'Zero-shot xArm',24,True,TEAL)
    for i,(label,val) in enumerate([('Spatial','20 / 20'),('Multi-view','14 / 20'),('Long-horizon','11 / 20')]):
        yy=1049+i*27
        text(691,yy,123,label,20,color=GRAY)
        text(691,yy+11,123,val,27,True,TEAL)
    text(691,1134,123,'Successes per task',18,color=GRAY,leading=1.05)

    # The wave art stays visible at the page edge, with a native conclusion on top.
    text(45,1170,751,'Persistent visual anchors make embodied reasoning traceable.',27,True,WHITE,align='center')

else:
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
    if VARIANT=='mechanism':
        text(479,344,325,'One identity, view-specific grounding',26,True,TEAL)
        text(479,365,325,'obj_01 · view 0 · point [634, 576]',22,mono=True)
        text(479,383,325,'obj_01 · view 1 · point [844, 706]',22,mono=True)
    else:
        text(479,345,325,'Same entity. Same ID. Different views.',27,True,TEAL)
        text(479,366,325,'Anchor = name + ID + view + point.',25,True)
        text(479,385,325,'Keep identity stable across steps and viewpoints.',21)
    gradient_box(468,406,264,65,'#EDF8F3','#F4FAF7',radius=5)
    if VARIANT=='mechanism':
        text(480,414,240,'Track identity. Verify grounding.',25,True,TEAL)
        text(480,436,240,'Introduce each entity with a full anchor; reuse its ID and update view-specific coordinates.',23,max_h=30)
    else:
        text(480,414,240,'Our insight',27,True,TEAL)
        text(480,436,240,'Persistent IDs connect visual evidence, intermediate steps and the final answer.',23,max_h=30)
    qr=CFG.get('qr_file')
    if qr and (ROOT/qr).is_file():image(ROOT/qr,751,407,60,60)
    else:
        rect(746,407,70,60,WHITE,LINE,4)
        text(751,430,60,'QR\nPLACEHOLDER',17,True,GRAY,align='center',leading=1.3)
    text(742,470,78,'PAPER / CODE',17,True,NAVY,align='center')

    panel(14,491,813,265,'Our Method: RoboPIN / PinCoT','gear',35)
    image(ROOT/'assets/figure-2-data-pipeline.png',45,531,750,750*110.12/493.65)
    text(37,714,137,'Three-stage\npost-training',25,True,TEAL,leading=1.1)
    for i,(name,desc) in enumerate([('SFT','Embodied knowledge'),('CoT-SFT','Structured reasoning'),('RFT / GRPO','Process alignment')]):
        xx=[190,403,624][i]
        gradient_box(xx,710,186,31,'#E1F5F6','#EEF9FA',radius=4)
        text(xx+4,713,178,name,25,True,TEAL,align='center')
        text(xx+4,730,178,desc,21,color=INK,align='center')
        if i<2:arrow(xx+192,726,xx+207)
    if VARIANT=='mechanism':
        text(26,744,789,'Process-supervised RFT rewards format, identity consistency, pin localization and final-answer correctness.',23,True,max_h=10)
    else:
        text(26,744,789,'PIN-170K supplies grounded reasoning traces; progressive training couples visual evidence to the final answer.',23,True,max_h=10)

    from statistics import mean
    perf=json.loads((ROOT/'performance_data.json').read_text())
    panel(14,766,400,389,'Experimental Results','clipboard',33)
    for i,model in enumerate(perf['models']):
        model['display_color']=TEAL if i==3 else TOKENS['baseline_chart_colors'][i]
        lx=37+(i%2)*180;ly=810+(i//2)*16
        rect(lx,ly+1,6,6,model['display_color'])
        text(lx+10,ly,169,model['name'],20,bold=i==3,color=TEAL if i==3 else INK)
    for pp,(key,title) in enumerate([('spatial','Spatial'),('pointing','Pointing'),('robot','Robot')]):
        xx=26+pp*124
        text(xx+16,851,105,title,25,True,NAVY,align='center')
        for tick in [0,50,100]:
            yy=985-110*tick/100
            line(xx+16,yy,xx+117,yy,'#DDE6EB',1)
            text(xx-2,yy-3,14,str(tick),17,color=GRAY,align='right')
        for i,model in enumerate(perf['models']):
            if key=='robot':
                counts=model['robot_successes']
                value=None if counts is None else 100*sum(counts)/(perf['robot_trials_per_task']*perf['robot_task_count'])
            else:value=mean(model[key])
            bx=xx+20+i*24
            if value is None:text(bx-3,973,22,'n/a',19,color=GRAY,align='center');continue
            bh=1.1*value
            rect(bx,985-bh,20,bh,model['display_color'])
            text(bx-4,985-bh-12,28,f'{value:.1f}',22,bold=i==3,color=TEAL if i==3 else INK,align='center')
    text(26,996,376,'Scores (%): spatial mean over 13 columns; pointing mean over 5 benchmarks; robot success over 60 trials.',19,color=GRAY,max_h=23)
    text(26,1024,376,'Selected benchmarks · score (%)',24,True,TEAL)
    rect(26,1041,376,12,'#F0F5F7')
    for xx,ww,label in [(33,155,'Benchmark'),(196,61,'Mimo-7B'),(264,65,'RoboPIN'),(337,57,'Δ pp')]:
        text(xx,1043,ww,label,19,True,align='left' if xx==33 else 'right')
    for i,(label,a,b) in enumerate([('CrossPoint',36.8,72.2),('BLINK multi-view',26.3,72.9),('EmbSpatial',76.2,83.1)]):
        yy=1058+i*16
        text(33,yy,155,label,23)
        text(196,yy,61,f'{a:.1f}',23,align='right')
        text(264,yy,65,f'{b:.1f}',23,True,TEAL,align='right')
        text(337,yy,57,f'+{b-a:.1f}',23,True,TEAL,align='right')
    gradient_box(26,1111,376,32,'#EDF7F5','#F2F9FC',radius=4)
    text(38,1115,352,'18.8% → 99.9% cross-step ID coverage',25,True,TEAL)
    text(38,1131,352,'Without RFT → RoboPIN · EmbSpatial',20,color=GRAY)

    panel(422,766,405,389,'Qualitative Results','chart',34)
    image(ROOT/'assets/robot-demo.png',435,810,379,379*154.71/504.40)
    text(435,936,379,'Zero-shot xArm · successful executions / 20',24,True,TEAL)
    for i,(label,val) in enumerate([('Spatial','20 / 20'),('Multi-view','14 / 20'),('Long-horizon','11 / 20')]):
        xx=435+i*128
        text(xx,958,119,val,31,True,TEAL,align='center')
        text(xx,979,119,label,22,align='center')
    image(ROOT/'assets/figure-4-two-examples.png',435,1001,379,379*96.68/240.25)
    text(45,1170,751,'Persistent visual anchors make embodied reasoning traceable.',27,True,WHITE,align='center')

for item in audit:
    if item['x']<0 or item['y']<0 or item['x']+item['width']>W+.01 or item['y']+item['height']>H:
        raise ValueError(f'Content outside page: {item}')
c.showPage();c.save()
slide.notes_slide.notes_text_frame.text=(
    f'A0 portrait 841 × 1189 mm. Module refinement variant: {VARIANT}. The clean variant reduces decorative load; balanced expands evidence and qualitative examples; mechanism adds source-published anchor coordinates and the four reward components. Scientific figures and text remain grounded in the paper. '
    'The external API-based PosterAgent generator was not run. '
    'Original Figure 1 comparison and Figure 2 pipeline are preserved. The qualitative panel adds the original Figure 4 reasoning examples. '
    'Three grouped bar charts reproduce paper Figure 1 and Tables 1–3: spatial mean over 13 capability columns, '
    'pointing mean over 5 benchmarks, robot successes over 60 trials. Missing robot baseline is n/a. '
    'Compact variants include three explicitly selected benchmark comparisons: CrossPoint, BLINK multi-view and EmbSpatial; these do not assert universal superiority. '
    'The robot trial-count caption conflict in the source paper still requires author confirmation. '
    'Logos are original official images; paper/code QR remains an intentional placeholder. '
    'Chart bars, values, axes, text and training nodes are editable; source figures are replaceable images.'
)
prs.save(str(OUT/'RoboPIN_A0_editable.pptx'))
(OUT/'layout-metadata.json').write_text(json.dumps({'variant':VARIANT,'chart_region':[14,858,414,1155] if VARIANT=='clean' else [14,766,414,1155],'plot_top':971 if VARIANT=='clean' else 875,'plot_bottom':1054 if VARIANT=='clean' else 985,'qualitative_asset':'assets/figure-4-qualitative.png' if VARIANT=='clean' else 'assets/figure-4-two-examples.png'},indent=2))
(OUT/'layout-audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False))
print(f'Built {OUT}/RoboPIN_A0_portrait.pdf and RoboPIN_A0_editable.pptx ({len(audit)} text blocks).')
