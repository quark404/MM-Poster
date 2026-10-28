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

# Reference-aligned structure: paired motivation/insight, full method, paired results.
def band(x,y,w,title):
    rect(x,y,w,25,TEAL)
    text(x+8,y+4,w-16,title,STYLE['section_title_font_size'],True,WHITE,align='center',max_h=17)

rect(0,0,W,H,WHITE)
text(20,13,560,'RoboPIN',77,True,NAVY)
text(22,52,600,'Grounded Embodied Reasoning\nvia Pinned Chain-of-Thought',STYLE['poster_title_font_size'],True,NAVY,leading=1.12,max_h=34)
text(22,90,690,'Yaoting Huang* · Yifu Yuan*† · Linqi Han · Chengwen Li · Shuoheng Zhang',STYLE['poster_author_font_size'],color=INK)
text(22,103,690,'Xianze Yao · Hongyao Tang · Yan Zheng · Jianye Hao†',STYLE['poster_author_font_size'],color=INK)
text(22,119,680,'Tianjin University · ACM Multimedia 2026 · Rio de Janeiro, Brazil',24,True,TEAL)
text(22,135,650,'quark404@tju.edu.cn · yuanyf@tju.edu.cn   |   * Equal contribution   † Corresponding authors',19,color=GRAY)
logo_placeholder('mm_logo',598,14,217,49)
logo_placeholder('tju_logo',746,73,70,68)

# Top-left: explicit motivation, grounded in the original comparison and introduction.
band(20,163,392,'Motivation')
image(ROOT/'assets/figure-1-cot-comparison.png',32,201,367,367*180.96/335.60)
text(32,404,367,'Paper Figure 1 · comparing three CoT paradigms',20,color=GRAY)
text(32,425,367,'1. Reference drift',26,True,TEAL)
text(32,443,367,'Textual references can switch between similar objects during multi-step reasoning.',25,max_h=30)
text(32,480,367,'2. Reasoning–answer misalignment',26,True,TEAL)
text(32,498,367,'A correct intermediate analysis can still end on the wrong object, especially across views.',25,max_h=30)

# Top-right: the same visual entity maintains an identity across two views.
band(429,163,392,'Key Insight: Persistent Identity')
for file,x,px,py in [('view-0.png',446,.634,.576),('view-1.png',649,.844,.706)]:
    text(x,200,147,'VIEW 0' if x==446 else 'VIEW 1',22,True,TEAL)
    image(ROOT/'assets'/file,x,216,147,111)
    circle(x+147*px,216+111*py,3.8)
    rect(x+5,221,70,13,TEAL,radius=1)
    text(x+7,222,66,'obj_01',23,True,WHITE,align='center')
arrow(603,269,637)
text(441,341,367,'Same entity. Same ID. Different views.',27,True,TEAL)
text(441,367,367,'Reasoning anchor = name + ID + view + point.',26,True,max_h=27)
text(441,405,367,'Introduce the anchor once; reuse its identity throughout the reasoning chain.',26,max_h=30)
text(441,452,271,'Our insight',26,True,TEAL)
text(441,471,271,'Persistent IDs connect visual grounding, intermediate steps and the final answer.',25,max_h=42)
qr=CFG.get('qr_file')
if qr and (ROOT/qr).is_file():
    image(ROOT/qr,744,448,64,64)
else:
    rect(744,448,64,64,WHITE,LINE,1)
    text(750,467,52,'QR\nPLACEHOLDER',17,True,GRAY,align='center',leading=1.4)
text(738,519,76,'PAPER / CODE',18,True,GRAY,align='center')

# Central full-width method, keeping the original source diagram.
band(20,540,801,'Our Method: RoboPIN / PinCoT')
image(ROOT/'assets/figure-2-data-pipeline.png',32,579,777,777*110.12/493.65)
text(32,782,137,'Three-stage\npost-training',25,True,TEAL,leading=1.1)
for i,(name,desc) in enumerate([('SFT','Embodied knowledge'),('CoT-SFT','Structured reasoning'),('RFT / GRPO','Process alignment')]):
    x=183+i*212
    rect(x,773,199,40,'#EDF5F5',radius=2)
    text(x+5,779,189,name,27,True,TEAL,align='center')
    text(x+5,797,189,desc,23,color=GRAY,align='center')
    if i<2:arrow(x+202,793,x+209)
text(32,829,777,'PinCoT binds visual evidence to persistent identities. PIN-170K supplies structured traces; process rewards supervise grounding and identity consistency.',27,True,leading=1.16,max_h=30)

# Bottom-left: quantitative evidence in three grouped, editable mini-charts.
from statistics import mean
perf=json.loads((ROOT/'performance_data.json').read_text())
band(20,868,392,'Experimental Results')
for i,model in enumerate(perf['models']):
    model['display_color']=TEAL if i==3 else TOKENS['baseline_chart_colors'][i]
    lx=32+(i%2)*196; ly=906+(i//2)*16
    rect(lx,ly+1,6,6,model['display_color'])
    text(lx+10,ly,177,model['name'],20,bold=i==3,color=TEAL if i==3 else INK)
for panel,(key,title) in enumerate([('spatial','Spatial'),('pointing','Pointing'),('robot','Robot')]):
    x=28+panel*127
    text(x+16,948,107,title,24,True,NAVY,align='center')
    for tick in [0,50,100]:
        yy=1075-100*tick/100
        line(x+16,yy,x+119,yy,'#DDE6EB',1)
        text(x-2,yy-3,14,str(tick),16,color=GRAY,align='right')
    for i,model in enumerate(perf['models']):
        if key=='robot':
            counts=model['robot_successes']
            value=None if counts is None else 100*sum(counts)/(perf['robot_trials_per_task']*perf['robot_task_count'])
        else:value=mean(model[key])
        bx=x+20+i*25
        if value is None:
            text(bx-3,1061,22,'n/a',18,color=GRAY,align='center');continue
        bh=value
        rect(bx,1075-bh,18,bh,model['display_color'])
        text(bx-4,1075-bh-11,26,f'{value:.1f}',20,bold=i==3,color=TEAL if i==3 else INK,align='center')
text(32,1087,367,'Scores (%) · Figure 1 / Tables 1–3. Spatial: 13-column mean; pointing: 5-benchmark mean; robot: success over 60 trials.',20,color=GRAY,max_h=28)
rect(32,1122,367,35,'#EDF5F5',radius=2)
text(42,1126,347,'18.8% → 99.9% cross-step ID coverage',25,True,TEAL)
text(42,1143,347,'Without RFT → RoboPIN · EmbSpatial, Table 7',20,color=GRAY)

# Bottom-right: original physical execution and grounded reasoning examples.
band(429,868,392,'Qualitative Results')
image(ROOT/'assets/robot-demo.png',441,907,367,367*154.71/504.40)
image(ROOT/'assets/figure-4-qualitative.png',441,1030,201,201*146.20/240.25)
text(660,1032,148,'Zero-shot xArm',25,True,TEAL)
for i,(label,val) in enumerate([('Spatial','20 / 20'),('Multi-view','14 / 20'),('Long-horizon','11 / 20')]):
    yy=1055+i*25
    text(660,yy,148,label,21,color=GRAY)
    text(660,yy+10,148,val,25,True,TEAL)
text(660,1133,148,'Successes per task\nTable 3',19,color=GRAY,leading=1.1)
text(441,1156,367,'Figure 3: execution · Figure 4: grounded reasoning',18,color=GRAY)

# Reference-style closing statement, without character decorations.
rect(0,1170,W,19,TEAL)
text(20,1173,801,'Persistent visual anchors make embodied reasoning traceable.',26,True,WHITE,align='center')

for item in audit:
    if item['x']<0 or item['y']<0 or item['x']+item['width']>W+.01 or item['y']+item['height']>H:
        raise ValueError(f'Content outside page: {item}')
c.showPage();c.save()
slide.notes_slide.notes_text_frame.text=(
    'A0 portrait 841 × 1189 mm. Layout aligned to the user-supplied SDO poster screenshot: Motivation and Key Insight above a full-width Method, then Experimental and Qualitative Results. Character decorations and all SDO-specific scientific content are excluded. '
    'The external API-based PosterAgent generator was not run. '
    'Original Figure 1 comparison and Figure 2 pipeline are preserved. The qualitative panel adds the original Figure 4 reasoning examples. '
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
