import io
from datetime import date
from xml.sax.saxutils import escape

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def fmt_date(v):
    if isinstance(v, date):
        return v.strftime('%d/%m/%Y')
    return str(v or '')


def _set_doc_defaults(doc, top=0.45, bottom=0.45, left=0.55, right=0.55, font=10.5):
    sec = doc.sections[0]
    sec.top_margin = Inches(top)
    sec.bottom_margin = Inches(bottom)
    sec.left_margin = Inches(left)
    sec.right_margin = Inches(right)
    doc.styles['Normal'].font.name = 'Times New Roman'
    doc.styles['Normal'].font.size = Pt(font)


def _set_cell_text(cell, text, bold=False, size=9, align=None):
    cell.text = ''
    p = cell.paragraphs[0]
    if align is not None:
        p.alignment = align
    r = p.add_run(str(text))
    r.bold = bold
    r.font.name = 'Times New Roman'
    r.font.size = Pt(size)
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER


def build_annexure_a_docx(d):
    doc = Document(); _set_doc_defaults(doc, 0.52, 0.52, 0.65, 0.65, 11.2)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('Annexure-A'); r.bold = True; r.font.size = Pt(13)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('Undertaking/Self-Declaration for domestic content requirement fulfilment'); r.bold = True; r.font.size = Pt(12)
    doc.add_paragraph('')
    p = doc.add_paragraph(); p.add_run('This is to certify that M/S '); r = p.add_run(d['installer']); r.bold = True
    p.add_run(f" has installed {d['plant_capacity']} grid connected rooftop solar pv power plant for {d['consumer_name']} at {d['address']} under sanction number {d['sanction_no']} dated ")
    r = p.add_run(d['sanction_date']); r.bold = True
    p.add_run(' issued by Eastern Power Distribution Company of AP LTD.')
    doc.add_paragraph('2. IT is here by confirms that the PV modules installed for the above mentioned project are domestically manufactured using DCR cells. The details of installed PV modules follows')
    for label, value in [
        ('2.1 PV module capacity : ', d['module_capacity']),
        ('2.2 Number of PV modules : ', d['module_count']),
        ('2.3 Serial numbers for PV module :', ''),
    ]:
        p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(1); p.add_run(label); p.add_run(str(value))
    serials = d.get('serials', []) or ['']
    cols = min(3, max(1, len(serials))); rows = max(1, (len(serials) + cols - 1) // cols)
    table = doc.add_table(rows=rows, cols=cols); table.style = 'Table Grid'; table.alignment = WD_TABLE_ALIGNMENT.CENTER
    i = 0
    for row in table.rows:
        for cell in row.cells:
            _set_cell_text(cell, serials[i] if i < len(serials) else '', bold=True, size=9.5, align=WD_ALIGN_PARAGRAPH.CENTER); i += 1
    doc.add_paragraph('')
    for label, value, bold in [
        ('4. PV module make : ', d['module_make'], True),
        ('5. Purchase Order number : ', d['po_number'], False),
        ('6. Purchase order or invoice date : ', d['po_date'], False),
        ('7. Cell manufacturer name : ', d['cell_manufacturer'], True),
        ('8. Cell GST invoice Number : ', d['cell_gst_invoice'], False),
    ]:
        p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(1); p.add_run(label); r = p.add_run(value); r.bold = bold
    doc.add_paragraph('')
    doc.add_paragraph('9. The above undertaking is based on the certificate issued by PV Module manufacturer/supplier while supplying the above-mentioned order.')
    p = doc.add_paragraph(); p.add_run('10. I Mrs '); p.add_run(d['declaration_consumer_name']); p.add_run(' on behalf of M/S ')
    r = p.add_run(d['installation_company']); r.bold = True
    p.add_run(' further declare that the information given above is true and correct and nothing has been concealed therein. If anything is found incorrect at any stage then the due Central Financial Assistance (CFA) that I have not charged from the consumer can be withheld and appropriate action may be taken against me and my company for wrong declaration. Supporting documents and proof of the above information will be provided as and when requested by MNRE.')
    doc.add_paragraph(''); doc.add_paragraph('')
    t = doc.add_table(rows=1, cols=2); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = t.cell(0,1); c.text = ''; p = c.paragraphs[0]
    p.add_run('(Signature With official Seal) For\n'); r = p.add_run('M/S ' + d['sign_company'] + '\n'); r.bold = True
    p.add_run('Name: '); r = p.add_run(d['sign_name'] + '\n'); r.bold = True
    p.add_run('Designation: ' + d['designation'] + '\nPhone: ' + d['phone'] + '\nEmail: ' + d['email'])
    out = io.BytesIO(); doc.save(out); return out.getvalue()


def build_annexure_a_pdf(d):
    out = io.BytesIO(); pdf = SimpleDocTemplate(out, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=15*mm, bottomMargin=14*mm)
    styles = getSampleStyleSheet(); body = ParagraphStyle('a_body', parent=styles['Normal'], fontName='Times-Roman', fontSize=10.7, leading=13.6, spaceAfter=6)
    center = ParagraphStyle('a_center', parent=body, alignment=TA_CENTER, fontName='Times-Bold', fontSize=12.2, spaceAfter=11)
    story = [Paragraph('<b>Annexure-A</b>', center), Paragraph('<b>Undertaking/Self-Declaration for domestic content requirement fulfilment</b>', center), Spacer(1, 8*mm)]
    story.append(Paragraph(f"This is to certify that M/S <b>{escape(d['installer'])}</b> has installed {escape(d['plant_capacity'])} grid connected rooftop solar pv power plant for {escape(d['consumer_name'])} at {escape(d['address'])} under sanction number {escape(d['sanction_no'])} dated <b>{escape(d['sanction_date'])}</b> issued by Eastern Power Distribution Company of AP LTD.", body))
    story.append(Paragraph('2. IT is here by confirms that the PV modules installed for the above mentioned project are domestically manufactured using DCR cells. The details of installed PV modules follows', body))
    story.append(Paragraph(f"2.1 PV module capacity : {escape(str(d['module_capacity']))}<br/>2.2 Number of PV modules : {escape(str(d['module_count']))}<br/>2.3 Serial numbers for PV module :", body))
    serials = d.get('serials', []) or ['']; cols = min(3, max(1, len(serials))); rows = max(1, (len(serials)+cols-1)//cols)
    data=[]; i=0
    for _ in range(rows):
        row=[]
        for _ in range(cols): row.append(serials[i] if i < len(serials) else ''); i += 1
        data.append(row)
    tbl = Table(data, colWidths=[165*mm/cols]*cols, rowHeights=8*mm)
    tbl.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.8,colors.black),('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),'Courier-Bold'),('FONTSIZE',(0,0),(-1,-1),9)])); story += [tbl, Spacer(1,4*mm)]
    story.append(Paragraph(f"4. PV module make : <b>{escape(d['module_make'])}</b><br/>5. Purchase Order number : {escape(d['po_number'])}<br/>6. Purchase order or invoice date : {escape(d['po_date'])}<br/>7. Cell manufacturer name : <b>{escape(d['cell_manufacturer'])}</b><br/>8. Cell GST invoice Number : {escape(d['cell_gst_invoice'])}", body))
    story.append(Spacer(1,3*mm)); story.append(Paragraph('9. The above undertaking is based on the certificate issued by PV Module manufacturer/supplier while supplying the above-mentioned order.', body))
    story.append(Paragraph(f"10. I Mrs {escape(d['declaration_consumer_name'])} on behalf of M/S <b>{escape(d['installation_company'])}</b> further declare that the information given above is true and correct and nothing has been concealed therein. If anything is found incorrect at any stage then the due Central Financial Assistance (CFA) that I have not charged from the consumer can be withheld and appropriate action may be taken against me and my company for wrong declaration. Supporting documents and proof of the above information will be provided as and when requested by MNRE.", body))
    story.append(Spacer(1,10*mm))
    sign = ParagraphStyle('a_sign', parent=body, fontSize=10.2, leading=13)
    sign_html = f"(Signature With official Seal) For<br/><b>M/S {escape(d['sign_company'])}</b><br/>Name: <b>{escape(d['sign_name'])}</b><br/>Designation: {escape(d['designation'])}<br/>Phone: {escape(d['phone'])}<br/>Email: {escape(d['email'])}"
    story.append(Table([['', Paragraph(sign_html, sign)]], colWidths=[90*mm,75*mm])); pdf.build(story); return out.getvalue()


def _annex_c_page1_rows(d):
    cumulative = '3.30'
    return [
        ['Financial year:', d['financial_year'], '', ''],
        ['Sanction Letter No.:', d['sanction_letter_no'], '', ''],
        ['Proposal Title:', 'PMSURYAGHARMUFTBIJLIYOJANA-ROOFTOPSOLAR', '', ''],
        ['Installed by agency:', d['installed_agency'], '', ''],
        ['Title of the Project:', 'ROOFTOPSOLAR', 'SPV Capacity (kWp):', d['spv_capacity']],
        ['Category of the organization/beneficiary:', 'DOMESTIC', 'Name of the contact person:', d['contact_person']],
        ['Address of contact person:', d['address'], '', ''],
        ['State:', 'Andhra Pradesh', 'District/City:', 'ANAKAPALLI'],
        ['Mobile:', d['mobile'], 'Email:', d['email']],
        ['Aadhaar Card Number (For Residential)', d['aadhaar'], 'Latitude:', d['latitude']],
        ['', '', 'Longitude:', d['longitude']],
        ['DISCOM', 'APEPDCL', 'Sanction Load', d['sanction_load']],
        ['CA No.', d['ca_no'], '', ''],
        ['SECTION', 'Technology Description & System Design/Specification', '', ''],
        ['SECTION', '(Compliance to BIS/IEC Standards is mandatory)', '', ''],
        ['SECTION', '1. Solar PV Module: ' + d['solar_pv_modules'], '', ''],
        ['Power of each PV Module/Nos. (Wp) / Make', d['power_each_module'], 'six', d['solar_pv_modules']],
        ['Cumulative Capacity of Modules (kWp):', cumulative, '', ''],
        ['Solar cell technology:', 'monoperc', 'Tilt Angle of Modules:', '17°'],
        ['Module efficiency (in %):', '22.63', 'Azimuth', '180°'],
        ['Indigenous or imported (Cell)', 'DCR', 'RFID passed inside or outside:', 'INSIDE'],
        ['Indigenous or imported (Module)', 'DCR', '*Supported by Appropriate documentation', ''],
        ['SECTION', '2. Inverters: DEYE', '', ''],
        ['Type of inverter:', 'Grid-TIED SOLAR INVERTER', '', ''],
        ['Power of each PCU/Nos. of inverters (KVA) / Make', 'ONE', '3.6', ''],
        ['Capacity/Power of PCU/inverters (KVA):', '3.6', 'Type of Charge Controller/MPPT', 'MPPT'],
        ['Inverter efficiency (in %)', '97.5', '', ''],
    ]


def build_annexure_c_docx(d):
    doc = Document(); _set_doc_defaults(doc, 0.35, 0.35, 0.35, 0.35, 8.5)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; r=p.add_run('Annexure-C'); r.bold=True; r.font.size=Pt(11)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; r=p.add_run('Project Completion Report for Grid-Connected Rooftop'); r.bold=True; r.underline=True; r.font.size=Pt(10)
    rows=_annex_c_page1_rows(d)
    t=doc.add_table(rows=len(rows), cols=4); t.style='Table Grid'; t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for i,row in enumerate(rows):
        if row[0]=='SECTION':
            merged=t.cell(i,0).merge(t.cell(i,3)); _set_cell_text(merged,row[1],bold=True,size=8.3,align=WD_ALIGN_PARAGRAPH.CENTER if 'Technology' in row[1] or 'Compliance' in row[1] else WD_ALIGN_PARAGRAPH.LEFT)
            continue
        for j,txt in enumerate(row): _set_cell_text(t.cell(i,j),txt,bold=(j%2==0),size=8.1)
    # Page 2 fixed
    doc.add_page_break()
    fixed2=[
        ['Grid connectivity level phase','Single Phase','Grid connectivity level Voltage','230V'],
        ['SECTION','3. Mounting Structures','',''],
        ['Type','GI','Surface Finish','80 MICRONS'],['Material','Galvanized Iron','Wind Speed Tolerance','150KM/H'],
        ['SECTION','4. Cables:','',''],['DC Cable Make','POLYCAB','Size','4 Sq mm'],['AC Cable Make (Inverter to ACDB)','POLYCAB','Size','4 Sqmm'],['AC Cable Make (ACDB to Electric Panel)','POLYCAB','Size','4 Sqmm'],['Conductor','','Insulation/Sheath','PVC/XLPE'],
        ['SECTION','5. JUNCTION BOX & DISTRIBUTION BOARDS','',''],['ACDB','SPD, MCB, Contactor','Nos.','One'],['DCDB','SPD, MCB, FUSE','Nos.','One'],
        ['SECTION','6. EARTHING & LIGHTNING PROTECTION EQUIPMENT EARTHING','',''],['AC (Nos.)','','Earth Resistance',''],['DC (Nos.)','ONE','Earth Resistance','3 Ohms'],['','ONE','Earth Resistance','3 Ohms'],['LIGHTNING ARRESTORS (LA)','','',''],['Type','COPPER COATED','',''],['LA (Nos.)','ONE','Earth Resistance','3 Ohms'],
        ['SECTION','7. Online Monitoring Mechanism:','',''],['Web Portal:','','',''],['USER ID:','','Password:',''],['SECTION','8. Weather monitoring:','',''],['Solar Irradiance (Pyranometer-Class II not better)','','Temperature','Ambient & Module'],['Windspeed sensor','','',''],['SECTION','9. Fire Fighting Device/System','',''],['SECTION','10. Danger Board','','']
    ]
    t2=doc.add_table(rows=len(fixed2),cols=4); t2.style='Table Grid'
    for i,row in enumerate(fixed2):
        if row[0]=='SECTION':
            c=t2.cell(i,0).merge(t2.cell(i,3)); _set_cell_text(c,row[1],bold=True,size=8.5)
        else:
            for j,txt in enumerate(row): _set_cell_text(t2.cell(i,j),txt,bold=(j%2==0),size=8)
    doc.add_paragraph('Date: ......03-09-2026......')
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.RIGHT; p.add_run('(Signature of Vendor)\nWith Stamp')
    p=doc.add_paragraph(); p.add_run('Annex:\n\n1. Copy of System test & Earth test reports (annexed)')
    # Page 3 fixed except 3 fields
    doc.add_page_break()
    doc.add_paragraph('Inverter Testing (DC)\nSide: No. Of Inverters\n1 Nos')
    t3=doc.add_table(rows=2,cols=5); t3.style='Table Grid'
    hdr=['Inverter S. No','Capacity','String 1: Voc','String 2: Voc','Remark']
    vals=[d['inverter_serial'],d['inverter_capacity'],d['string1_voc'],'NA','']
    for j,x in enumerate(hdr): _set_cell_text(t3.cell(0,j),x,bold=True,size=8,align=WD_ALIGN_PARAGRAPH.CENTER)
    for j,x in enumerate(vals): _set_cell_text(t3.cell(1,j),x,size=8,align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph('Inverter Testing (AC side) Phase - 1')
    t4=doc.add_table(rows=2,cols=8); t4.style='Table Grid'; hdr=['Inverter S. No','Capacity','R-Y/P-N','Y-B','B-R','R-N','Y-N','B-N']; vals=[d['inverter_serial'],d['inverter_capacity'],'550','NA','NA','NA','NA','NA']
    for j,x in enumerate(hdr): _set_cell_text(t4.cell(0,j),x,bold=True,size=7.6,align=WD_ALIGN_PARAGRAPH.CENTER)
    for j,x in enumerate(vals): _set_cell_text(t4.cell(1,j),x,size=7.6,align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph('ACDB & Meter Panel Testing - 1 Phase')
    t5=doc.add_table(rows=2,cols=7); t5.style='Table Grid'; hdr=['','R-Y/P-N','Y-B','B-R','R-N','Y-N','B-N']; vals=['ACDB(V)','230','NA','NA','NA','NA','NA']
    for j,x in enumerate(hdr): _set_cell_text(t5.cell(0,j),x,bold=True,size=7.8,align=WD_ALIGN_PARAGRAPH.CENTER)
    for j,x in enumerate(vals): _set_cell_text(t5.cell(1,j),x,size=7.8,align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph('Earthing Pit Details: No Of Earth Pits 3 Nos')
    t6=doc.add_table(rows=2,cols=4); t6.style='Table Grid'; hdr=['','Earthing AC','Earthing DC','Earthing LA']; vals=['Earth test Value(Ohm)','3.1*','4.1','4.75']
    for j,x in enumerate(hdr): _set_cell_text(t6.cell(0,j),x,bold=True,size=8,align=WD_ALIGN_PARAGRAPH.CENTER)
    for j,x in enumerate(vals): _set_cell_text(t6.cell(1,j),x,size=8,align=WD_ALIGN_PARAGRAPH.CENTER)
    p=doc.add_paragraph('\nDate: 19 / 08 / 2026                              (Signature of Vendor)       With Stamp')
    out=io.BytesIO(); doc.save(out); return out.getvalue()


def _pdf_table(data, widths, fontsize=7.2, row_heights=None):
    t=Table(data,colWidths=widths,rowHeights=row_heights)
    t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.55,colors.black),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('FONTNAME',(0,0),(-1,-1),'Times-Roman'),('FONTSIZE',(0,0),(-1,-1),fontsize),('LEADING',(0,0),(-1,-1),fontsize+1.3),('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3),('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2)]))
    return t


def build_annexure_c_pdf(d):
    out=io.BytesIO(); pdf=SimpleDocTemplate(out,pagesize=A4,leftMargin=9*mm,rightMargin=9*mm,topMargin=8*mm,bottomMargin=8*mm)
    styles=getSampleStyleSheet(); small=ParagraphStyle('csmall',parent=styles['Normal'],fontName='Times-Roman',fontSize=7.3,leading=8.5); sec=ParagraphStyle('csec',parent=small,fontName='Times-Bold',alignment=TA_CENTER)
    story=[Paragraph('<b>Annexure-C</b>',ParagraphStyle('cc',parent=small,alignment=TA_CENTER,fontSize=10.5,leading=12)),Paragraph('<u><b>Project Completion Report for Grid-Connected Rooftop</b></u>',ParagraphStyle('cc2',parent=small,alignment=TA_CENTER,fontSize=9.5,leading=11)),Spacer(1,2*mm)]
    rows=_annex_c_page1_rows(d); data=[]
    for row in rows:
        if row[0]=='SECTION': data.append([Paragraph('<b>'+escape(row[1])+'</b>',sec),'','',''])
        else: data.append([Paragraph('<b>'+escape(str(row[0]))+'</b>',small),Paragraph(escape(str(row[1])),small),Paragraph('<b>'+escape(str(row[2]))+'</b>',small),Paragraph(escape(str(row[3])),small)])
    t=_pdf_table(data,[56*mm,48*mm,39*mm,48*mm],6.6)
    spans=[]
    for i,row in enumerate(rows):
        if row[0]=='SECTION': spans.append(('SPAN',(0,i),(3,i)))
        elif row[0] in ('Financial year:','Sanction Letter No.:','Proposal Title:','Installed by agency:','Address of contact person:','CA No.'):
            spans.append(('SPAN',(1,i),(3,i)))
    t.setStyle(TableStyle(spans)); story += [t,PageBreak()]
    fixed2=[['Grid connectivity level phase','Single Phase','Grid connectivity level Voltage','230V'],['3. Mounting Structures','','',''],['Type','GI','Surface Finish','80 MICRONS'],['Material','Galvanized Iron','Wind Speed Tolerance','150KM/H'],['4. Cables:','','',''],['DC Cable Make','POLYCAB','Size','4 Sq mm'],['AC Cable Make (Inverter to ACDB)','POLYCAB','Size','4 Sqmm'],['AC Cable Make (ACDB to Electric Panel)','POLYCAB','Size','4 Sqmm'],['Conductor','','Insulation/Sheath','PVC/XLPE'],['5. JUNCTION BOX & DISTRIBUTION BOARDS','','',''],['ACDB','SPD, MCB, Contactor','Nos.','One'],['DCDB','SPD, MCB, FUSE','Nos.','One'],['6. EARTHING & LIGHTNING PROTECTION EQUIPMENT EARTHING','','',''],['AC (Nos.)','','Earth Resistance',''],['DC (Nos.)','ONE','Earth Resistance','3 Ohms'],['','ONE','Earth Resistance','3 Ohms'],['LIGHTNING ARRESTORS (LA)','','',''],['Type','COPPER COATED','',''],['LA (Nos.)','ONE','Earth Resistance','3 Ohms'],['7. Online Monitoring Mechanism:','','',''],['Web Portal:','','',''],['USER ID:','','Password:',''],['8. Weather monitoring:','','',''],['Solar Irradiance (Pyranometer-Class II not better)','','Temperature','Ambient & Module'],['Windspeed sensor','','',''],['9. Fire Fighting Device/System','','',''],['10. Danger Board','','','']]
    data2=[]; section_rows=[]
    for i,row in enumerate(fixed2):
        if row[1]=='' and row[2]=='' and row[3]=='' and (row[0][0].isdigit() or row[0].startswith('LIGHTNING')):
            data2.append([Paragraph('<b>'+escape(row[0])+'</b>',small),'','','']); section_rows.append(i)
        else:data2.append([Paragraph('<b>'+escape(row[0])+'</b>',small),Paragraph(escape(row[1]),small),Paragraph('<b>'+escape(row[2])+'</b>',small),Paragraph(escape(row[3]),small)])
    t2=_pdf_table(data2,[66*mm,45*mm,39*mm,41*mm],7.0)
    if section_rows:t2.setStyle(TableStyle([('SPAN',(0,i),(3,i)) for i in section_rows]))
    story += [t2,Spacer(1,3*mm),Paragraph('Date: ......03-09-2026......',small),Spacer(1,8*mm),Table([['',Paragraph('(Signature of Vendor)<br/>With Stamp',small)]],colWidths=[130*mm,60*mm]),Spacer(1,8*mm),Paragraph('<b>Annex:</b><br/><br/>1. Copy of System test &amp; Earth test reports (annexed)',small),PageBreak()]
    story += [Paragraph('<b>Inverter Testing (DC)</b><br/>Side: No. Of Inverters<br/>1 Nos',small)]
    dc=[['Inverter S. No','Capacity','String 1: Voc','String 2: Voc','Remark'],[d['inverter_serial'],d['inverter_capacity'],d['string1_voc'],'NA','']]; story += [_pdf_table(dc,[42*mm,32*mm,40*mm,38*mm,39*mm],7.1),Spacer(1,6*mm)]
    story += [Paragraph('<b>Inverter Testing (AC side) Phase - 1</b>',small)]
    ac=[['Inverter S. No','Capacity','R-Y/P-N','Y-B','B-R','R-N','Y-N','B-N'],[d['inverter_serial'],d['inverter_capacity'],'550','NA','NA','NA','NA','NA']]; story += [_pdf_table(ac,[37*mm,25*mm,24*mm,21*mm,21*mm,21*mm,21*mm,21*mm],6.8),Spacer(1,5*mm)]
    story += [Paragraph('<b>ACDB &amp; Meter Panel Testing - 1 Phase</b>',small)]
    mp=[['','R-Y/P-N','Y-B','B-R','R-N','Y-N','B-N'],['ACDB(V)','230','NA','NA','NA','NA','NA']]; story += [_pdf_table(mp,[34*mm,30*mm,25*mm,25*mm,25*mm,25*mm,25*mm],7),Spacer(1,5*mm)]
    story += [Paragraph('<b>Earthing Pit Details: No Of Earth Pits 3 Nos</b>',small)]
    er=[['','Earthing AC','Earthing DC','Earthing LA'],['Earth test Value(Ohm)','3.1*','4.1','4.75']]; story += [_pdf_table(er,[47*mm,42*mm,42*mm,42*mm],7.2),Spacer(1,14*mm),Paragraph('Date: 19 / 08 / 2026                       (Signature of Vendor)            With Stamp',small)]
    pdf.build(story); return out.getvalue()


def build_sync_docx(d):
    doc=Document(); _set_doc_defaults(doc,0.55,0.55,0.65,0.65,10.2)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run('EASTERN POWER DISTRIBUTION COMPANY OF A.P. LIMITED'); r.bold=True; r.font.size=Pt(10.5)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run('CORPORATE OFFICE :: VISAKHAPATNAM\nCIN : U40109AP2000SGC034117\n(A Govt. of A.P. Enterprises & An ISO 9001:2015 & ISO 27001:2013 Certified Company)').font.size=Pt(8.5)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; r=p.add_run('SYNCHRONIZATION CERTIFICATE'); r.bold=True; r.underline=True
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; r=p.add_run('Synchronization With the DISCO grid, installation of meter(s) and COD'); r.bold=True; r.underline=True
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run('(To be filled by the discom)')
    doc.add_paragraph('To,')
    details=[('Applicant\'s name',d['applicant_name']),('D.NO',d['address']),('CONSUMER NO',d['consumer_no']),('PMSG REF NO',d['pmsg_ref_no'])]
    for a,b in details:
        p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(1); p.add_run(a+' : ').bold=True; p.add_run(b)
    doc.add_paragraph('Sir/madam,')
    p=doc.add_paragraph(); p.add_run('Sub :').bold=True
    doc.add_paragraph('1. synchronization with the discom grid\n2. installation of meter(s)\n3. commercial operation date')
    p=doc.add_paragraph(); p.add_run(f"Synchronization test of solar rooftop PV system {d['system_capacity']} system installed there of by " ); r=p.add_run(d['installation_company']); r.bold=True
    p.add_run(' Bearing application no: ' + d['pmsg_ref_no'] + ' has been conducted and your ' + d['system_capacity'] + ' system found satisfactory and successfully synchronized with the discom grid meter with ' + d['inverter_make'] + ' inverter serial no ' + d['inverter_serial'] + ' has been installed and sealed on dt : ' + d['seal_date'])
    doc.add_paragraph('\nYour\'s faithfully\n\n\n(Signature of officer)\nName and designation:\nDate :\nStamp:')
    out=io.BytesIO(); doc.save(out); return out.getvalue()


def build_sync_pdf(d):
    out=io.BytesIO(); pdf=SimpleDocTemplate(out,pagesize=A4,leftMargin=21*mm,rightMargin=21*mm,topMargin=15*mm,bottomMargin=15*mm)
    styles=getSampleStyleSheet(); body=ParagraphStyle('sbody',parent=styles['Normal'],fontName='Times-Roman',fontSize=10.2,leading=14,spaceAfter=5); center=ParagraphStyle('sc',parent=body,alignment=TA_CENTER)
    story=[Paragraph('<b>EASTERN POWER DISTRIBUTION COMPANY OF A.P. LIMITED</b>',center),Paragraph('CORPORATE OFFICE :: VISAKHAPATNAM<br/>CIN : U40109AP2000SGC034117<br/>(A Govt. of A.P. Enterprises &amp; An ISO 9001:2015 &amp; ISO 27001:2013 Certified Company)',ParagraphStyle('sc2',parent=center,fontSize=8.3,leading=10)),Spacer(1,3*mm),Paragraph('<u><b>SYNCHRONIZATION CERTIFICATE</b></u>',center),Paragraph('<u><b>Synchronization With the DISCO grid, installation of meter(s) and COD</b></u>',center),Paragraph('(To be filled by the discom)',center),Spacer(1,4*mm),Paragraph('To,',body)]
    for a,b in [('Applicant\'s name',d['applicant_name']),('D.NO',d['address']),('CONSUMER NO',d['consumer_no']),('PMSG REF NO',d['pmsg_ref_no'])]: story.append(Paragraph(f"<b>{escape(a)} :</b> {escape(b)}",body))
    story += [Paragraph('Sir/madam,',body),Paragraph('<b>Sub :</b>',body),Paragraph('1. synchronization with the discom grid<br/>2. installation of meter(s)<br/>3. commercial operation date',body)]
    txt=f"Synchronization test of solar rooftop PV system {d['system_capacity']} system installed there of by <b>{escape(d['installation_company'])}</b> Bearing application no: {escape(d['pmsg_ref_no'])} has been conducted and your {escape(d['system_capacity'])} system found satisfactory and successfully synchronized with the discom grid meter with {escape(d['inverter_make'])} inverter serial no {escape(d['inverter_serial'])} has been installed and sealed on dt : {escape(d['seal_date'])}"
    story += [Paragraph(txt,body),Spacer(1,12*mm),Paragraph("Your's faithfully",body),Spacer(1,16*mm),Paragraph('(Signature of officer)<br/>Name and designation:<br/>Date :<br/>Stamp:',body)]
    pdf.build(story); return out.getvalue()
