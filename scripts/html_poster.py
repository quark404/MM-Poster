"""Native HTML/CSS rendering of the shared poster layout; no PDF screenshots."""
from pathlib import Path
from html import escape
import base64
import mimetypes
import math

class HTMLPoster:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.nodes = []
        self.assets = {}

    def box(self, x, y, w, h):
        return f'position:absolute;left:{x}mm;top:{y}mm;width:{w}mm;height:{h}mm;'

    def rect(self, x, y, w, h, fill, stroke=None, radius=0, lw=1):
        self.nodes.append(f'<div aria-hidden="true" style="{self.box(x,y,w,h)}background:{fill};border-radius:{radius}mm;border:{lw if stroke else 0}pt solid {stroke or fill};box-sizing:border-box"></div>')

    def gradient(self, x, y, w, h, left, right, radius):
        self.rect(x,y,w,h,f'linear-gradient(90deg,{left},{right})',radius=radius)

    def line(self, x1, y1, x2, y2, color, lw):
        angle = math.degrees(math.atan2(y2-y1,x2-x1))
        length = math.hypot(x2-x1,y2-y1)
        self.nodes.append(f'<div aria-hidden="true" style="{self.box(x1,y1,length,0)}border-top:{lw}pt solid {color};transform-origin:0 0;transform:rotate({angle}deg)"></div>')

    def text(self, x, y, w, lines, size, bold, color, leading, mono, align):
        family = 'PosterMono' if mono else 'PosterSans'
        css = self.box(x,y,w,len(lines)*size*leading*25.4/72)
        self.nodes.append(f'<div class="copy" style="{css}font-family:{family};font-size:{size}pt;font-weight:{700 if bold else 400};color:{color};line-height:{size*leading}pt;text-align:{align};white-space:pre">'+escape('\n'.join(lines))+'</div>')

    def image(self, file, x, y, w, h, round_image=False):
        file = Path(file)
        if file not in self.assets:
            mime=mimetypes.guess_type(file.name)[0] or 'application/octet-stream'
            self.assets[file]=f'data:{mime};base64,'+base64.b64encode(file.read_bytes()).decode()
        self.nodes.append(f'<img alt="{escape(file.stem)}" data-asset="{escape(file.name)}" src="{self.assets[file]}" style="{self.box(x,y,w,h)}object-fit:contain;'+('border-radius:50%;' if round_image else '')+'">')

    def circle(self, x, y, r, fill, stroke):
        self.rect(x-r,y-r,r*2,r*2,fill,stroke,r,3)

    def save(self, path, font_dir):
        fonts=''
        for family, filename, weight in [('PosterSans','DejaVuSans.ttf',400),('PosterSans','DejaVuSans-Bold.ttf',700),('PosterMono','DejaVuSansMono.ttf',400)]:
            encoded=base64.b64encode((font_dir/filename).read_bytes()).decode()
            fonts+=f'@font-face{{font-family:{family};font-weight:{weight};src:url(data:font/ttf;base64,{encoded}) format("truetype");}}'
        html='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>RoboPIN · A0 Poster</title><style>'''+fonts+f'''
*{{box-sizing:border-box}}body{{margin:0;background:#e6edef;font-family:PosterSans,sans-serif}}nav{{height:56px;display:flex;gap:18px;align-items:center;justify-content:center;font-size:14px}}button{{border:0;border-radius:6px;background:#007e89;color:white;padding:8px 16px;cursor:pointer}}#frame{{margin:0 auto 24px;position:relative;box-shadow:0 4px 28px #14384922}}#poster{{position:relative;width:{self.width}mm;height:{self.height}mm;background:white;transform-origin:top left;overflow:hidden}}.copy{{margin:0;padding:0}}img{{display:block}}
@page{{size:{self.width}mm {self.height}mm;margin:0}}
@media print{{html,body{{margin:0;background:white;width:{self.width}mm;height:{self.height}mm}}nav{{display:none}}#frame{{width:{self.width}mm!important;height:{self.height}mm!important;margin:0;box-shadow:none}}#poster{{transform:none!important}}*{{print-color-adjust:exact;-webkit-print-color-adjust:exact}}}}
</style></head><body><nav><strong>RoboPIN · A0</strong><span>841 × 1189 mm</span><button onclick="window.print()">Print / Save PDF</button></nav><main id="frame"><article id="poster" aria-label="RoboPIN research poster">'''+''.join(self.nodes)+'''</article></main><script>
function fitPoster(){const p=document.getElementById('poster'),f=document.getElementById('frame');const s=Math.min(1,(innerWidth-32)/p.offsetWidth);p.style.transform=`scale(${s})`;f.style.width=p.offsetWidth*s+'px';f.style.height=p.offsetHeight*s+'px'}addEventListener('resize',fitPoster);document.fonts.ready.then(fitPoster);fitPoster();
</script></body></html>'''
        Path(path).write_text(html)
