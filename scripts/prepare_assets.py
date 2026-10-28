#!/usr/bin/env python3
"""Extract paper crops without executing any content embedded in the paper."""
from pathlib import Path
import json
import fitz

root = Path(__file__).resolve().parents[1]
doc = fitz.open(root / 'assets/paper.pdf')
crops = {
    'figure-1-cot-comparison': (0, (53.80, 337.88, 389.40, 518.84)),
    'figure-2-data-pipeline': (2, (57.83, 84.48, 551.48, 194.60)),
    'view-0': (2, (60.82, 229.00, 120.23, 275.05)),
    'view-1': (2, (124.20, 229.00, 180.32, 275.05)),
    'figure-4-qualitative': (7, (53.80, 363.32, 294.05, 509.52)),
    'robot-demo': (7, (53.80, 83.69, 558.20, 238.4)),
}
for name, (page, box) in crops.items():
    doc[page].get_pixmap(matrix=fitz.Matrix(5, 5), clip=fitz.Rect(box), alpha=False).save(
        root / 'assets' / f'{name}.png'
    )
(root / 'assets/crop-provenance.json').write_text(json.dumps({
    name: {'page': page+1, 'bbox_pdf_points': box}
    for name, (page, box) in crops.items()
}, indent=2))
print('Extracted the original CoT comparison, data pipeline, camera views and robot demonstration.')
