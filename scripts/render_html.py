#!/usr/bin/env python3
"""Render and validate the standalone HTML in Chromium, including offline mode."""
from pathlib import Path
import argparse
import json
import fitz
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--output-dir',default='output')
args=parser.parse_args()
out=root/args.output_dir
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1510,'height':2200},device_scale_factor=1,offline=True)
    page=context.new_page()
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.set_content((out/'RoboPIN_A0.html').read_text(),wait_until='load')
    page.evaluate('document.fonts.ready')
    page.wait_for_function('Array.from(document.images).every(i=>i.complete && i.naturalWidth>0)')
    report=page.evaluate('''()=>{
      const poster=document.querySelector('#poster'),box=poster.getBoundingClientRect();
      const texts=[...document.querySelectorAll('.copy')];
      const bounds=texts.filter(e=>{const b=e.getBoundingClientRect();return b.left<box.left-1||b.top<box.top-1||b.right>box.right+1||b.bottom>box.bottom+1}).map(e=>e.textContent);
      const overflow=texts.filter(e=>e.scrollWidth>e.clientWidth+1||e.scrollHeight>e.clientHeight+1).map(e=>e.textContent);
      return {native_text_blocks:texts.length,images:document.images.length,bounds_issues:bounds,overflow_issues:overflow,external_assets:[...document.images].filter(i=>!i.src.startsWith('data:')).map(i=>i.src),body_text:poster.innerText};
    }''')
    assert not errors,errors
    assert not report['bounds_issues'],report['bounds_issues']
    assert not report['overflow_issues'],report['overflow_issues']
    assert not report['external_assets'],report['external_assets']
    body_text=report.pop('body_text')
    assert 'cross-step' not in body_text.lower()
    assert all(label not in body_text for label in ['PLACEHOLDER','PAPER / CODE','A. How PinCoT Reasons','B. Data Construction & Training'])
    page.locator('#frame').screenshot(path=str(out/'RoboPIN_HTML_preview.png'))
    page.pdf(path=str(out/'RoboPIN_A0_HTML.pdf'),prefer_css_page_size=True,print_background=True)
    # Also check screen layout at a phone width.
    page.set_viewport_size({'width':390,'height':844})
    page.wait_for_function('document.querySelector("#frame").getBoundingClientRect().width<=innerWidth')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    browser.close()
doc=fitz.open(out/'RoboPIN_A0_HTML.pdf')
assert len(doc)==1
size=[v*25.4/72 for v in (doc[0].rect.width,doc[0].rect.height)]
assert abs(size[0]-841)<.2 and abs(size[1]-1189)<.2,size
# Chromium rounds CSS print dimensions to device units; normalize the media box
# by <0.2 mm without rasterizing or scaling its text and image content.
doc[0].set_mediabox(fitz.Rect(0,0,841*72/25.4,1189*72/25.4))
normalized=out/'html-normalized.tmp.pdf'
doc.save(normalized,garbage=4,deflate=True)
doc.close()
normalized.replace(out/'RoboPIN_A0_HTML.pdf')
doc=fitz.open(out/'RoboPIN_A0_HTML.pdf')
size=[v*25.4/72 for v in (doc[0].rect.width,doc[0].rect.height)]
assert all(abs(a-b)<.01 for a,b in zip(size,[841,1189]))
report.update(pdf_pages=len(doc),page_mm=size,media_box_normalized=True,offline='passed',mobile_fit='passed',browser_errors=errors)
(out/'html-validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
