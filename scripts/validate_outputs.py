#!/usr/bin/env python3
"""Check actual deliverables: dimensions, evidence text, fonts and editability."""
from pathlib import Path
from zipfile import ZipFile
import json
import fitz
from pptx import Presentation

root = Path(__file__).resolve().parents[1]
out = root / 'output'
doc = fitz.open(out / 'RoboPIN_A0_portrait.pdf')
assert len(doc) == 1, 'Poster must be a single page'
page = doc[0]
size_mm = [page.rect.width*25.4/72, page.rect.height*25.4/72]
assert abs(size_mm[0]-841) < .01 and abs(size_mm[1]-1189) < .01
assert page.rotation == 0
pdf_text = page.get_text()
for item in ['RoboPIN', '170K', '35.4', '72.2', '83.1', '99.9%', '18.8%', '20 / 20', '14 / 20', '11 / 20', 'PLACEHOLDER']:
    assert item in pdf_text, f'Missing expected source value: {item}'
for block in page.get_text('dict')['blocks']:
    for row in block.get('lines', []):
        for span in row['spans']:
            box=fitz.Rect(span['bbox'])
            assert box.x0 >= 0 and box.y0 >= 0 and box.x1 <= page.rect.width and box.y1 <= page.rect.height, span['text']
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
boxes=[s for s in slide.shapes if s.has_text_frame and s.text.strip()]
assert len(boxes) >= 100, 'PowerPoint appears flattened'
assert any('CrossPoint' in s.text for s in boxes)
for s in slide.shapes:
    assert s.left >= 0 and s.top >= 0 and s.left+s.width <= prs.slide_width+1 and s.top+s.height <= prs.slide_height+1, s.name
with ZipFile(out / 'RoboPIN_A0_editable.pptx') as z:
    assert z.testzip() is None
page.get_pixmap(matrix=fitz.Matrix(.62,.62)).save(out / 'RoboPIN_preview.png')
report={
    'pdf_pages': len(doc), 'page_mm': size_mm, 'orientation': 'portrait',
    'embedded_fonts': fonts, 'editable_text_boxes': len(boxes),
    'pptx_shapes': len(slide.shapes), 'source_value_checks': 'passed',
    'page_bounds': 'passed', 'pptx_archive_integrity': 'passed',
    'visual_review': 'PDF preview inspected; PowerPoint not rendered in Office in this environment',
    'intentional_placeholders': ['ACM Multimedia logo','Tianjin University logo','paper/code QR'],
}
(out / 'validation.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
