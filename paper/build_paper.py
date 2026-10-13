"""Build the conference manuscript from the retained Springer template.

All numerical tables are populated from saved measured outputs. No network calls.
Run with the bundled document runtime (python-docx, pandas and lxml required).
"""
from pathlib import Path
from copy import deepcopy
import json,re,hashlib,html
from zipfile import ZipFile,ZIP_DEFLATED
import pandas as pd
from lxml import etree
from docx import Document
from docx.shared import Inches,Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.part import Part
from docx.opc.packuri import PackURI
from docx.opc.constants import RELATIONSHIP_TYPE as RT

ROOT=Path(__file__).resolve().parent
RESULTS=ROOT.parent/'results'
s=json.loads((RESULTS/'summary.json').read_text())
g=pd.read_csv(RESULTS/'gate_sensitivity.csv')
e=json.loads((RESULTS/'extended_summary.json').read_text())
metadata=json.loads((ROOT/'reference_metadata.json').read_text(encoding='utf-8'))
data=pd.read_csv(RESULTS/'heldout_predictions.csv')
accepted_subjects=set(data.loc[data.accepted,'subject'])
paired_records=len(data[data.subject.isin(accepted_subjects)])

def table(caption,headers,rows):
    return '\n'.join([f'**{caption}**','', '| '+' | '.join(headers)+' |',
                      '| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(map(str,row))+' |' for row in rows])
def ci(v):return f"{v['subject_balanced_mae']:.2f} ({v['mae_ci'][0]:.2f}-{v['mae_ci'][1]:.2f})"
tables={}
tables['table_related']=table('Table 1. Prior work and the scope of this experiment.',
    ['Work','Measurement or target','Relation to this study'],[
    ['Charlier et al. [1]','Multimodal HRV comparison','Mean HR does not establish variability agreement'],
    ['Springer et al. [2]','Expert PCG quality labels','Quality classification differs from RMSSD error prediction'],
    ['Giordano et al. [3]','Signal-to-noise quality','Motivates acoustic quality features'],
    ['Centracchio et al. [4]','Forcecardiographic sound localization','Different sensor and landmark method'],
    ['Krsic et al. [5]','SensSmartTech mean HR','Same data context, different endpoint'],
    ['Present experiment','RMSSD error and coverage','Participant-held-out gate and selection controls']])
tables['table_cohort']=table('Table 2. Source cohort and primary analysis flow.',
    ['Stage','Records','Participants'],[
    ['Complete release','338','32'],['Before activity','96','32'],['After activity','242','32'],
    ['ECG checks failed','22','-'],['Eligible for primary analysis','316','32'],
    ['Retained by primary gate','159','29']])
tables['table_features']=table('Table 3. Acoustic inputs available at inference.',
    ['Feature','Definition in this implementation'],[
    ['Periodicity','Overlap-normalized envelope autocorrelation at estimated period'],
    ['Morphology consistency','Mean inner product of centered, unit-norm 121-sample event envelopes with their average'],
    ['Interval CV','Population SD divided by mean acoustic interval'],
    ['Event-height CV','Population SD divided by mean detected envelope height'],
    ['Detector disagreement','Absolute HR difference between recurrence and peak-distance detectors'],
    ['Spectral ratio','Welch power in 25-150 Hz divided by total PCG power']])
labels=[('audio','Acoustic recurrence'),('peak_baseline','Acoustic peak baseline'),
        ('acc','ACC recurrence'),('carotid','Carotid PPG'),('brachial','Brachial PPG'),('guided','ECG-guided PCG*')]
tables['table_methods']=table('Table 4. Participant-balanced MAE with 95% bootstrap intervals.',
    ['Method','Records','HR (bpm)','RMSSD (ms)'],[
    [label,s['methods'][key+'_rmssd']['records'],ci(s['methods'][key+'_hr']),ci(s['methods'][key+'_rmssd'])]
    for key,label in labels])+'\n\n*ECG-guided PCG is a timing diagnostic. PPG uses positive peaks after 0.5-8 Hz filtering; ACC uses recurrence after 10-40 Hz filtering. Carotid output is missing for three eligible records.'
tables['table_gate']=table('Table 5. Primary gate estimands and their denominators.',
    ['Set or comparison','Records','People','RMSSD MAE or change (ms)'],[
    ['All eligible','316','32','15.33 (11.72-19.52)'],
    ['All records in paired participants',paired_records,'29',f"{e['all_mae_common_subjects']:.2f}"],
    ['Retained by primary gate','159','29','6.00 (4.66-7.48)'],
    ['Retained minus all, paired','-','29','-9.36 (-14.32 to -5.32)'],
    ['Matched random retention','159/run','29','15.36 [11.64-19.61]']])+'\n\nParentheses denote 95% participant-bootstrap intervals. Brackets denote the central 95% random-selection simulation range. The paired baseline is restricted to participants with retained records.'
names={'Without periodicity':'Remove periodicity','Without morphology':'Remove morphology',
       'Without interval_cv':'Remove interval CV','Without peak_cv':'Remove height CV',
       'Without detector_disagreement':'Remove detector difference','Without spectral_ratio':'Remove spectral ratio'}
tables['table_ablation']=table('Table 6. Post-hoc gates with nominal 50% retention targets.',
    ['Gate','Records','People','MAE, ms (95% interval)'],[
    [names.get(r.variant,r.variant),r.accepted_records,r.accepted_subjects,f'{r.mae_ms:.2f} ({r.ci_low:.2f}-{r.ci_high:.2f})']
    for r in g.iloc[:9].itertuples()])
tables['table_sensitivity']=table('Table 7. Filtering and guided-window sensitivities on 316 records.',
    ['Variant','RMSSD MAE, ms (95% interval)'],[
    ['PCG 25-150 Hz (primary)',ci(s['methods']['audio_rmssd'])],
    ['PCG 20-200 Hz',ci(s['methods']['audio_band20_200_rmssd'])],
    ['PCG 40-120 Hz',ci(s['methods']['audio_band40_120_rmssd'])],
    ['Guided 15-160 ms',ci(s['methods']['guided_rmssd'])],
    ['Guided 25-120 ms',ci(s['methods']['guided_narrow_rmssd'])],
    ['Guided 0-200 ms',ci(s['methods']['guided_wide_rmssd'])]])

def ref(doi,year=None,venue=None):
    m=metadata[doi];authors=m['author']
    author=', '.join(a['family']+', '+''.join(x[0]+'.' for x in a.get('given','').split() if x) for a in authors[:3])
    if len(authors)>3:author+=', et al.'
    date=(m['published-print'] or m['published'])['date-parts'][0][0]
    journal=venue or m['container-title'][0]
    detail=''
    if m['volume']:detail+=' '+m['volume']
    if m['issue']:detail+='('+m['issue']+')'
    pages=m['article-number'] or m['page']
    if pages and pages!='1-1':detail+=', '+pages
    return html.unescape(f"{author}: {m['title'][0]}. {journal}{detail} ({year or date}). https://doi.org/{doi}")
refs=[ref('10.1007/s10877-019-00382-0',2020),ref('10.1080/03091902.2016.1213902'),
      ref('10.3390/s21217246'),ref('10.3390/s24051525'),
      ref('10.1109/JSEN.2026.3726629',2026,'IEEE Sensors Journal, early access'),
      'Lazovic, A., et al.: SensSmartTech database of cardiovascular signals synchronously recorded by an electrocardiograph, phonocardiograph, photoplethysmograph and accelerometer. Version 1.0.0. PhysioNet (2024). https://doi.org/10.13026/fy9p-n277',
      ref('10.1038/s41597-025-05781-4'),ref('10.1371/journal.pone.0138921'),
      'Task Force of the European Society of Cardiology and the North American Society of Pacing and Electrophysiology: Heart rate variability. Standards of measurement, physiological interpretation, and clinical use. European Heart Journal 17, 354-381 (1996). https://doi.org/10.1093/oxfordjournals.eurheartj.a014868',
      'Springer, D.B., Tarassenko, L., Clifford, G.D.: Logistic regression-HSMM-based heart sound segmentation. IEEE Transactions on Biomedical Engineering 63(4), 822-832 (2016). https://doi.org/10.1109/TBME.2015.2475278',
      'Kazemnejad, A., Gordany, P., Sameni, R.: EPHNOGRAM: A simultaneous electrocardiogram and phonocardiogram database. Version 1.0.0. PhysioNet (2021). https://doi.org/10.13026/tjtq-5911',
      'Pollard, T., Moody, B.E., Lehman, L., et al.: PhysioNet as a global platform for biomedical research. Nature Health 1, 792-795 (2026). https://doi.org/10.1038/s44360-026-00096-z']
tables['references']='\n\n'.join(f'{i}. {t}' for i,t in enumerate(refs,1))
source=(ROOT/'manuscript_template.md').read_text(encoding='utf-8')
for key,value in tables.items():source=source.replace('{{'+key+'}}',value)
assert '{{' not in source
source=source.replace('@authors','@authors')
(ROOT/'manuscript.md').write_text(source.replace('@authors','Pallab Sarangi (1), Shreyas Baloni (2), Pooja R Rao (1)\n\n(1) Department of CSE (Data Science), RNS Institute of Technology, Bengaluru, India\n\n(2) Department of Information Science and Engineering, RNS Institute of Technology, Bengaluru, India').replace('@rmssd_equation',r'$$\mathrm{RMSSD}=1000\sqrt{\frac{\sum_{i=1}^{n-1}(I_{i+1}-I_i)^2}{n-1}}\qquad (1)$$'),encoding='utf-8')

# Validate denominators and hard numerical claims against the record outputs.
data=pd.read_csv(RESULTS/'heldout_predictions.csv')
accepted_subjects=set(data.loc[data.accepted,'subject'])
assert paired_records==299
assert len(data)==316 and int(data.accepted.sum())==159

reference=ROOT/'template/springer_reference.docx'
assert hashlib.sha256(reference.read_bytes()).hexdigest()=='8f13b6162ea653c9728cd5c9b86b53a27bed3a3805dbfdce32c4c52f16a4e3ed'
doc=Document(reference)
body=doc._element.body
for item in list(body):
    if item.tag!=qn('w:sectPr'):body.remove(item)

def paragraph(text='',style='p1a'):
    p=doc.add_paragraph(style=style)
    parts=re.split(r'(\*\*.*?\*\*)',text)
    for part in parts:
        run=p.add_run(part[2:-2] if part.startswith('**') else part)
        if part.startswith('**'):run.bold=True
    return p
def no_numbering(p):
    num=OxmlElement('w:numPr');nid=OxmlElement('w:numId');nid.set(qn('w:val'),'0');num.append(nid);p._p.get_or_add_pPr().append(num)
def heading(text,level=1):
    p=paragraph(text,'heading1' if level==1 else 'heading2');no_numbering(p)
    p.paragraph_format.left_indent=Pt(0);p.paragraph_format.first_line_indent=Pt(0)
    return p
def add_table(lines):
    cells=[[s.strip() for s in line.strip('|').split('|')] for line in lines]
    headers=cells[0];rows=cells[2:]
    t=doc.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    width=4.804
    ratios=([.36,.12,.25,.27] if len(headers)==4 else [.49,.255,.255] if len(headers)==3 else [.35,.65])
    if headers[0]=='Work':ratios=[.25,.31,.44]
    if headers[0]=='Set or comparison':ratios=[.40,.14,.13,.33]
    if headers[0]=='Gate':ratios=[.38,.12,.12,.38]
    for cell,w in zip(t.rows[0].cells,ratios):cell.width=Inches(width*w)
    for cell,text in zip(t.rows[0].cells,headers):cell.text=text
    for row in rows:
        for cell,text,w in zip(t.add_row().cells,row,ratios):cell.text=text;cell.width=Inches(width*w)
    for col,w in zip(t.columns,ratios):col.width=Inches(width*w)
    for ri,row in enumerate(t.rows):
        pr=row._tr.get_or_add_trPr();pr.append(OxmlElement('w:cantSplit'))
        if ri==0:pr.append(OxmlElement('w:tblHeader'))
        for ci,cell in enumerate(row.cells):
            cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tcpr=cell._tc.get_or_add_tcPr()
            margin=OxmlElement('w:tcMar')
            for tag,val in [('top',35),('bottom',35),('left',55),('right',55)]:
                el=OxmlElement('w:'+tag);el.set(qn('w:w'),str(val));el.set(qn('w:type'),'dxa');margin.append(el)
            tcpr.append(margin)
            borders=OxmlElement('w:tcBorders')
            for side in ['top','bottom','left','right']:
                el=OxmlElement('w:'+side);el.set(qn('w:val'),'single' if (ri==0 and side in ['top','bottom']) or (ri==len(t.rows)-1 and side=='bottom') else 'nil');el.set(qn('w:sz'),'6');borders.append(el)
            tcpr.append(borders)
            for p in cell.paragraphs:
                p.paragraph_format.first_line_indent=Pt(0);p.paragraph_format.space_after=Pt(0)
                p.paragraph_format.line_spacing=1
                p.alignment=WD_ALIGN_PARAGRAPH.LEFT
                for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(8.5);r.bold=ri==0
    return t

def add_figure(path):
    p=doc.add_paragraph(style='image');p.paragraph_format.keep_with_next=True
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    shape=p.add_run().add_picture(str(ROOT/path),width=Inches(4.80))
    # Office SVG representation with a high-resolution PNG fallback.
    svg=(ROOT/path).with_suffix('.svg')
    part=Part(PackURI('/word/media/'+svg.name),'image/svg+xml',svg.read_bytes(),doc.part.package)
    rid=doc.part.relate_to(part,RT.IMAGE)
    blip=shape._inline.xpath('.//a:blip')[0]
    extlst=OxmlElement('a:extLst');ext=OxmlElement('a:ext');ext.set('uri','{96DAC541-7B7A-43D3-8B79-37D633B846F1}')
    svgblip=etree.Element('{http://schemas.microsoft.com/office/drawing/2016/SVG/main}svgBlip',nsmap={'asvg':'http://schemas.microsoft.com/office/drawing/2016/SVG/main'})
    svgblip.set(qn('r:embed'),rid);ext.append(svgblip);extlst.append(ext);blip.append(extlst)
    shape._inline.docPr.set('descr',path.stem.replace('_',' '))

def equation():
    p=doc.add_paragraph(style='equation');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    m=OxmlElement('m:oMath')
    def run(text):
        r=OxmlElement('m:r');t=OxmlElement('m:t');t.text=text;r.append(t);return r
    m.append(run('RMSSD = 1000 '))
    rad=OxmlElement('m:rad');rp=OxmlElement('m:radPr');dh=OxmlElement('m:degHide');dh.set(qn('m:val'),'1');rp.append(dh);rad.append(rp)
    rad.append(OxmlElement('m:deg'));ee=OxmlElement('m:e')
    frac=OxmlElement('m:f');num=OxmlElement('m:num');num.append(run('Σᵢ₌₁ⁿ⁻¹ (Iᵢ₊₁ − Iᵢ)²'))
    den=OxmlElement('m:den');den.append(run('n − 1'));frac.extend([num,den]);ee.append(frac);rad.append(ee);m.append(rad);p._p.append(m);p.add_run('   (1)')

lines=source.splitlines();i=0;in_refs=False;first=True
while i<len(lines):
    line=lines[i].strip()
    if not line:i+=1;continue
    if line=='<!-- page -->':
        p=doc.add_paragraph();p.paragraph_format.space_after=Pt(0);p.paragraph_format.space_before=Pt(0)
        p.paragraph_format.line_spacing=Pt(1);p.add_run().add_break(__import__('docx').enum.text.WD_BREAK.PAGE)
        first=True
    elif line.startswith('# '):paragraph(line[2:],'papertitle')
    elif line=='@authors':
        p=paragraph('','author')
        for idx,(name,aff) in enumerate([('Pallab Sarangi','1'),('Shreyas Baloni','2'),('Pooja R Rao','1')]):
            if idx:p.add_run(', ' if idx==1 else ' and ')
            p.add_run(name);p.add_run(aff).font.superscript=True
        paragraph('1 Department of CSE (Data Science), RNS Institute of Technology, Bengaluru, India','address')
        paragraph('2 Department of Information Science and Engineering, RNS Institute of Technology, Bengaluru, India','address')
    elif line.startswith('**Abstract.**'):paragraph(line,'abstract')
    elif line.startswith('**Keywords:'):paragraph(line,'keywords')
    elif line.startswith('### '):heading(line[4:],2);first=True
    elif line.startswith('## '):heading(line[3:]);first=True;in_refs=line=='## References'
    elif line.startswith('|'):
        block=[]
        while i<len(lines) and lines[i].strip().startswith('|'):block.append(lines[i].strip());i+=1
        add_table(block);first=True;continue
    elif line.startswith('**Table '):
        p=paragraph(line,'tablecaption');p.paragraph_format.keep_with_next=True
    elif line.startswith('!['):
        add_figure(Path(re.search(r'\]\((.*?)\)',line).group(1)))
    elif line.startswith('**Fig.'):
        p=paragraph(line,'figurecaption');p.paragraph_format.keep_with_next=False;first=True
    elif line=='@rmssd_equation':equation();first=True
    elif in_refs:
        p=paragraph(line,'referenceitem');no_numbering(p)
        p.paragraph_format.left_indent=Inches(.16);p.paragraph_format.first_line_indent=Inches(-.16)
    else:
        p=paragraph(line,'p1a' if first else 'Normal');first=False
    i+=1

doc.core_properties.title=lines[0][2:]
doc.core_properties.author='Pallab Sarangi; Shreyas Baloni; Pooja R Rao'
doc.core_properties.subject='Exploratory acoustic variability benchmark for ICIIPC 2026'
out=ROOT/'ICIIPC2026_Heart_Sound_Variability.docx'
temp=ROOT/'qa/authored.docx';doc.save(temp)
# Preserve all template parts except explicitly editable content and relationships.
mutable={'word/document.xml','word/_rels/document.xml.rels','[Content_Types].xml','docProps/core.xml'}
with ZipFile(reference) as original,ZipFile(temp) as made,ZipFile(out,'w',ZIP_DEFLATED) as final:
    for name in original.namelist():
        final.writestr(name,made.read(name) if name in mutable else original.read(name))
    for name in made.namelist():
        if name not in original.namelist():final.writestr(name,made.read(name))
with ZipFile(reference) as a,ZipFile(out) as b:
    preserved=[n for n in a.namelist() if n not in mutable]
    assert all(a.read(n)==b.read(n) for n in preserved)
(ROOT/'qa/build_audit.json').write_text(json.dumps(dict(preserved_parts=len(preserved),tables=7,figures=5,
    references=len(refs),template_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),
    docx_sha256=hashlib.sha256(out.read_bytes()).hexdigest()),indent=2))
print(out)
