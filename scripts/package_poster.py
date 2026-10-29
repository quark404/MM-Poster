#!/usr/bin/env python3
"""Bundle current deliverables and reproducible source, avoiding duplicate renders."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
root=Path(__file__).resolve().parents[1]
with ZipFile(root/'output/RoboPIN_fonts.zip','w',ZIP_DEFLATED) as z:
    for path in sorted((root/'assets/fonts').iterdir()):
        if path.is_file():z.write(path,path.name)
bundle=root/'output/RoboPIN_poster_package.zip'
main_outputs={'RoboPIN_A0.html','RoboPIN_A0_editable.pptx','RoboPIN_A0_portrait.pdf','RoboPIN_preview.png'}
with ZipFile(bundle,'w',ZIP_DEFLATED,compresslevel=6) as z:
    for path in sorted(root.rglob('*')):
        rel=path.relative_to(root)
        if not path.is_file() or any(p in {'.git','.venv','__pycache__'} for p in rel.parts):continue
        if rel.parts[0]=='output' and not (len(rel.parts)==2 and (path.name in main_outputs or path.suffix=='.json')):continue
        if rel.parts[0]=='design' and path.suffix!='.md':continue
        z.write(path,str(rel))
with ZipFile(bundle) as z:
    assert z.testzip() is None
print(f'{bundle.name}: {bundle.stat().st_size/1024**2:.2f} MiB')
