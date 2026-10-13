"""Produce a macro-free copy of the conference supplied Springer sample."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
import hashlib, json

ROOT = Path(__file__).resolve().parent
src = ROOT/'template/word/splnproc1703.docm'
dest = ROOT/'template/springer_reference.docx'
with ZipFile(src) as zin, ZipFile(dest,'w',ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        name = item.filename
        if 'vba' in name.lower() or name.startswith('customUI/'):
            continue
        data = zin.read(name)
        if name.endswith('.rels') or name == '[Content_Types].xml':
            tree = E.fromstring(data)
            for el in list(tree):
                if any(x in str(dict(el.attrib)).lower() for x in ['vba','customui','ui/extensibility']):
                    tree.remove(el)
            if name == '[Content_Types].xml':
                for el in tree:
                    if el.get('PartName') == '/word/document.xml':
                        el.set('ContentType','application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml')
            data = E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
        zout.writestr(item,data)
with ZipFile(dest) as z:
    inventory = {n:dict(bytes=len(z.read(n)),sha256=hashlib.sha256(z.read(n)).hexdigest()) for n in z.namelist()}
(ROOT/'template/package_inventory.json').write_text(json.dumps(inventory,indent=2))
print(dest)
print('source_sha256',hashlib.sha256(src.read_bytes()).hexdigest())
print('reference_sha256',hashlib.sha256(dest.read_bytes()).hexdigest())
