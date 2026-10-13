# Conference paper template contract

Reference: `D:/heart_v/paper/template/springer_reference.docx`, SHA256
`8f13b6162ea653c9728cd5c9b86b53a27bed3a3805dbfdce32c4c52f16a4e3ed`.
It is a macro-free derivative of the conference's Windows sample, source SHA256
`133e67e059945020f64c0c6cc4a22660740d6d319eb575c7611e4687366c0a2e`.
Downloaded 2026-10-13 from https://iciipc.co.in/Downloads/Word%20Template.zip.
Macros and custom ribbon are removed without execution; the original is unchanged.

Reference has two pages and one portrait A4 section. Text margins in twips:
top/bottom 2948, left/right 2494; page 11906 by 16838. Header 2381,
footer 2324. One column, different first page, even/default header page fields.
Body Times New Roman 10 pt, minimum 12 pt lines, justified, subsequent first-line
indent 227 twips. `p1a` is the unindented paragraph after headings and objects.
`papertitle` is centered bold 14 pt. `author` and `address` define centered
metadata. `abstract` and `keywords` use the source inset text block.
First-level headings 12 pt bold; second-level headings 10 pt bold.
Figure captions are below objects; table captions above. Source table uses
horizontal rules and 9-10 pt text; no decorative fills. Reference entries use
9 pt and hanging numbering. No added header branding or conference logos.

The entire sample body is editable and replaced with the research article.
Slot locators are word/document.xml body paragraphs with styles papertitle,
author, address, abstract, keywords, heading1, heading2, p1a, Normal, image,
tablecaption, figurecaption, referenceitem. Their patterns can be repeated to
accommodate the paper within the conference's 6-10-page budget. The source's
placeholder authors, ORCIDs, addresses, bibliography, equation, sample table,
sample chart, and accompanying body prose must be removed. No ORCID or email
will be invented. Actual author names and departments are supplied by the user.

Preserve section geometry, all paragraph styles, numbering definitions, existing
header/footer and theme parts. Package inventory is template/package_inventory.json.
The build patches only document.xml, document relationships, content types,
core properties, and adds required media. Unreferenced sample media may remain
in the package; no sample content remains in the article. Source styles and
all other preserve-only parts are compared byte-for-byte after generation.

Render evidence: qa/template/reference.pdf and page-1.png, page-2.png, both
visually inspected. The packaged render_docx.py failed because bundled
LibreOffice is absent on Windows. Microsoft Word COM exported the document
with macros disabled; bundled Poppler rasterized it. This alternative validates
the actual Word layout without installing a different office engine.

Fidelity gates: identical section geometry and preserve-only package bytes,
legible tables and plot labels, numbered citations and objects, no sample text,
no clipped text, and visual inspection of every exported final page.
