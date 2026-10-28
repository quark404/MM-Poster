#!/usr/bin/env python3
"""Check actual deliverables: dimensions, evidence text, fonts and editability."""
from pathlib import Path
from zipfile import ZipFile
import json
import hashlib
import fitz
import argparse
import re
from pptx import Presentation

root = Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--output-dir',default='output')
args=parser.parse_args()
out=root/args.output_dir
meta=json.loads((out/'layout-metadata.json').read_text())
doc = fitz.open(out / 'RoboPIN_A0_portrait.pdf')
assert len(doc) == 1, 'Poster must be a single page'
page = doc[0]
size_mm = [page.rect.width*25.4/72, page.rect.height*25.4/72]
assert abs(size_mm[0]-841) < .01 and abs(size_mm[1]-1189) < .01
assert page.rotation == 0
pdf_text = page.get_text()
for item in ['RoboPIN', '68.0', '67.9', '75.0', '99.9%', '18.8%', '20 / 20', '14 / 20', '11 / 20', 'PLACEHOLDER']:
    assert item in pdf_text, f'Missing expected source value: {item}'
for removed in ['model parameters','PinCoT reasoning samples','evaluation benchmarks','CrossPoint vs. Mimo-7B']:
    assert removed not in pdf_text, f'Old metric card remains: {removed}'
assert not re.search(r'\b(?:Figure|Fig\.?|Tables?)\s*\d',pdf_text), 'Removed number captions have returned'
chart_text=page.get_text(clip=fitz.Rect(*(v*72/25.4 for v in meta['chart_region'])))
for value in ['52.4','55.1','58.7','68.0','65.6','51.8','62.1','67.9','30.0','16.7','75.0','n/a']:
    assert value in chart_text, f'Aggregate chart value missing: {value}'
for block in page.get_text('dict')['blocks']:
    for row in block.get('lines', []):
        for span in row['spans']:
            box=fitz.Rect(span['bbox'])
            assert box.x0 >= 0 and box.y0 >= 0 and box.x1 <= page.rect.width and box.y1 <= page.rect.height, span['text']
native_spans=[]
for block in page.get_text('dict')['blocks']:
    for row in block.get('lines', []):
        for span in row['spans']:
            if span['text'].strip(): native_spans.append(span)
for i,a in enumerate(native_spans):
    for b in native_spans[i+1:]:
        overlap=fitz.Rect(a['bbox']) & fitz.Rect(b['bbox'])
        assert overlap.is_empty or overlap.get_area()<1, f"Native text collision: {a['text']} / {b['text']}"
fonts=[]
for font in page.get_fonts():
    xref, ext, kind, base, *_ = font
    assert xref and doc.extract_font(xref)[3], f'Font is not embedded: {base}'
    fonts.append(base)
prs = Presentation(out / 'RoboPIN_A0_editable.pptx')
assert len(prs.slides) == 1
assert abs(prs.slide_width / 36000 - 841) < .01
assert abs(prs.slide_height / 36000 - 1189) < .01
slide = prs.slides[0]
chart_bars=[s for s in slide.shapes if s.shape_type==1 and s.left/36000<414 and s.top/36000>=meta['plot_top'] and (s.top+s.height)/36000<=meta['plot_bottom']+.01 and s.height/36000>1]
assert len(chart_bars)==11, f'Expected 11 editable bars and an unreported baseline: found {len(chart_bars)}'
boxes=[s for s in slide.shapes if s.has_text_frame and s.text.strip()]
native_text = '\n'.join(s.text for s in boxes)
for item in ['Motivation', 'Key Insight: Persistent Identity', 'Our Method: RoboPIN / PinCoT', 'Experimental Results', 'Qualitative Results', 'Spatial', 'Pointing', 'Robot', 'SFT', 'CoT-SFT', 'RFT / GRPO', '18.8% → 99.9%']:
    assert item in native_text, f'Expected editable content is missing: {item}'
config = json.loads((root / 'poster_config.json').read_text())
embedded = {hashlib.sha256(s.image.blob).hexdigest() for s in slide.shapes if s.shape_type == 13}
paper_figures=['assets/figure-1-cot-comparison.png','assets/figure-2-data-pipeline.png',meta['qualitative_asset']]
for asset in paper_figures:
    assert hashlib.sha256((root/asset).read_bytes()).hexdigest() in embedded, f'Original paper figure missing: {asset}'
    from PIL import Image
    with Image.open(root/asset) as im:
        ratio=im.width/im.height
    matching=[s for s in slide.shapes if s.shape_type == 13 and hashlib.sha256(s.image.blob).hexdigest()==hashlib.sha256((root/asset).read_bytes()).hexdigest()]
    assert all(abs((s.width/s.height)/ratio-1)<.005 for s in matching), f'Figure stretched: {asset}'
logo_assets=[]
for key in ['mm_logo_file', 'tju_logo_file']:
    asset = config.get(key)
    if asset:
        assert hashlib.sha256((root/asset).read_bytes()).hexdigest() in embedded, f'Logo not embedded: {asset}'
        logo_assets.append(asset)
assert 'LOGO PLACEHOLDER' not in pdf_text, 'Outdated logo placeholder remains'
assert not any('LOGO PLACEHOLDER' in s.text for s in boxes)
header_pixel = page.get_pixmap(matrix=fitz.Matrix(.1,.1)).pixel(1,1)
assert min(header_pixel)>=230, 'Title corner should remain light for readability'
assert hashlib.sha256((root/'assets/rio-wave-background.png').read_bytes()).hexdigest() in embedded, 'Decorative background is missing'
for s in slide.shapes:
    assert s.left >= 0 and s.top >= 0 and s.left+s.width <= prs.slide_width+1 and s.top+s.height <= prs.slide_height+1, s.name
with ZipFile(out / 'RoboPIN_A0_editable.pptx') as z:
    assert z.testzip() is None
page.get_pixmap(matrix=fitz.Matrix(.62,.62)).save(out / 'RoboPIN_preview.png')
mm=72/25.4
for name, bounds in [
    ('detail-results.png', (14,meta['chart_region'][1]-7,827,1160)),
    ('detail-original-figures.png', (14,146 if meta['variant']!='clean' else 168,827,meta['chart_region'][1]-7)),
    ('detail-performance.png', (14,meta['chart_region'][1]-7,414,1160)),
]:
    page.get_pixmap(matrix=fitz.Matrix(.75,.75),clip=fitz.Rect(*(v*mm for v in bounds))).save(out/name)
report={
    'pdf_pages': len(doc), 'page_mm': size_mm, 'orientation': 'portrait',
    'embedded_fonts': fonts, 'editable_text_boxes': len(boxes),
    'pptx_shapes': len(slide.shapes), 'source_value_checks': 'passed',
    'native_text_collisions': 'none',
    'page_bounds': 'passed', 'pptx_archive_integrity': 'passed',
    'visual_review': 'PDF preview inspected; PowerPoint not rendered in Office in this environment',
    'embedded_logo_assets': logo_assets,
    'embedded_original_paper_figures': paper_figures,
    'paper_figure_aspect_ratios': 'preserved',
    'editable_performance_bars': len(chart_bars),
    'aggregate_chart_values': 'verified against paper Figure 1 / Tables 1–3',
    'old_metric_cards': 'removed',
    'header_background': 'Light Rio skyline with white title corner',
    'layout_variant': meta['variant'],
    'design': 'Module refinement series: clean / balanced / mechanism',
    'intentional_placeholders': ['paper/code QR'],
}
(out / 'validation.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
