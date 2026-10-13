"""PM Surya Ghar agreement using the supplied three-page format."""
import io
import json
import re
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import HRFlowable, Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ASSETS = Path(__file__).resolve().parent / 'assets'
TERMS = json.loads((ASSETS / 'agreement-terms.json').read_text(encoding='utf-8'))
VENDOR = 'EASTERNBAY SOLAR'
VENDOR_ADDRESS = '1-128/11, Near Hanuman Statue, Raju Gari Beedu, New Colony, Payakaraopeta, Anakapalli District, Andhra Pradesh - 531126'
VENDOR_PHONE = '+91 93468 28227'


def indian_amount(value):
    try:
        amount = Decimal(str(value).replace(',', '').strip())
    except InvalidOperation as exc:
        raise ValueError('Enter a valid project amount.') from exc
    if not amount.is_finite() or amount <= 0 or amount > Decimal('9999999999.99'):
        raise ValueError('Project amount must be positive and below Rs. 10,00,00,00,000.')
    amount = amount.quantize(Decimal('.01'))
    whole, fraction = f'{amount:.2f}'.split('.')
    tail = whole[-3:]
    head = whole[:-3]
    groups = []
    while head:
        groups.insert(0, head[-2:])
        head = head[:-2]
    number = ','.join(groups + [tail])
    return 'Rs. ' + number + ('.' + fraction if fraction != '00' else '') + '/-'


def validate_agreement(d):
    required = {'consumer_name': 'Consumer name', 'consumer_address': 'Consumer address',
                'portal_no': 'National Portal / Application number', 'system_capacity': 'System capacity',
                'mobile': 'Consumer mobile number', 'project_cost': 'Total project cost',
                'agreement_date': 'Agreement date'}
    missing = [label for key, label in required.items() if not str(d.get(key, '')).strip()]
    if missing:
        raise ValueError('Complete: ' + ', '.join(missing))
    indian_amount(d['project_cost'])
    try:
        date.fromisoformat(str(d['agreement_date']))
    except ValueError as exc:
        raise ValueError('Choose a valid agreement date.') from exc


def build_agreement_pdf(d):
    validate_agreement(d)
    out = io.BytesIO()
    doc = SimpleDocTemplate(out, pagesize=letter, leftMargin=41, rightMargin=41,
                            topMargin=30, bottomMargin=43, title='EASTERNBAY SOLAR - Consumer Vendor Agreement')
    body = ParagraphStyle('body', fontName='Helvetica', fontSize=9, leading=11.4, spaceAfter=4)
    center = ParagraphStyle('center', parent=body, alignment=TA_CENTER)
    heading = ParagraphStyle('section', parent=body, fontName='Helvetica-Bold', textColor=colors.HexColor('#365f91'), spaceBefore=7, spaceAfter=5)
    numbered = ParagraphStyle('numbered', parent=body, leftIndent=11, firstLineIndent=-11)
    width = 518
    def p(text, style=body):
        return Paragraph(text, style)
    def value(key):
        return escape(str(d.get(key, '')).strip()).replace('\n', '<br/>')
    def numbered_items(items, start=1, bold_labels=False):
        result = []
        for n, text in enumerate(items, start):
            safe = escape(text)
            if bold_labels and ':' in safe:
                label, rest = safe.split(':', 1)
                safe = f'<b>{label}:</b>{rest}'
            result.append(p(f'<b>{n}.</b> {safe}', numbered))
        return result
    def table(rows, green_header=False, padding=5):
        t = Table(rows, colWidths=[width/2, width/2], hAlign='LEFT')
        styles = [('GRID', (0,0), (-1,-1), .55, colors.black), ('VALIGN',(0,0),(-1,-1),'TOP'),
                  ('LEFTPADDING',(0,0),(-1,-1),padding), ('RIGHTPADDING',(0,0),(-1,-1),padding),
                  ('TOPPADDING',(0,0),(-1,-1),padding), ('BOTTOMPADDING',(0,0),(-1,-1),padding)]
        if green_header:
            styles.append(('BACKGROUND',(0,0),(-1,0),colors.HexColor('#d9ead3')))
        t.setStyle(TableStyle(styles))
        return t
    day = date.fromisoformat(str(d['agreement_date'])).strftime('%d / %m / %Y')
    vendor_details = f'<b>{VENDOR}</b><br/>Registered Office: {escape(VENDOR_ADDRESS)}<br/>Mobile: {VENDOR_PHONE}'
    story = [p(f'<b>{VENDOR}</b>', ParagraphStyle('brand', parent=center, fontSize=14, leading=17)),
             p('Registered Office: 1-128/11, Near Hanuman Statue, Raju Gari Beedu, New Colony,<br/>'
               f'Payakaraopeta, Anakapalli District, Andhra Pradesh - 531126 | Ph: {VENDOR_PHONE}', ParagraphStyle('office', parent=center, fontSize=7.5, leading=9)),
             p('<b>CONSUMER - VENDOR AGREEMENT</b>', ParagraphStyle('title', parent=center, fontSize=14, leading=17, textColor=colors.HexColor('#17365d'), spaceAfter=5)),
             HRFlowable(width='100%',thickness=.4,color=colors.HexColor('#4472c4'),spaceAfter=13),
             p('<b>FOR INSTALLATION OF GRID-CONNECTED ROOFTOP SOLAR (RTS) SYSTEM<br/>UNDER PM SURYA GHAR: MUFT BIJLI YOJANA</b>', ParagraphStyle('subtitle', parent=center, fontSize=10, leading=12, spaceAfter=6)),
             table([[p(f'<b>Agreement Date: {day}</b>'),p(f'<b>National Portal / Application No.: {value("portal_no")}</b>')]]),
             p('<b>Purpose of Agreement.</b> ' + escape(TERMS['purpose'])),
             p('1. PARTIES TO THE AGREEMENT', heading),
             table([[p('<b>FIRST PARTY - CONSUMER</b>',center),p('<b>SECOND PARTY - VENDOR</b>',center)],
                    [p(f'Consumer Name: {value("consumer_name")}<br/><br/>Consumer Address:<br/>{value("consumer_address")}'),p(vendor_details)]], True),
             p('<b>Recitals.</b> ' + escape(TERMS['recitals'])),
             p('2. OBLIGATIONS OF THE CONSUMER', heading)]
    story += numbered_items(TERMS['consumer'])
    story += [p('3. OBLIGATIONS OF THE VENDOR', heading)]
    story += numbered_items(TERMS['vendor'][:6], bold_labels=True)
    story += [PageBreak()]
    story += numbered_items(TERMS['vendor'][6:], start=7, bold_labels=True)
    capacity = value('system_capacity')
    if d.get('capacity_note', '').strip():
        capacity += ' (' + value('capacity_note') + ')'
    project_rows = [
        ['Proposed RTS System Capacity', capacity],
        ['Project / Installation Address', value('installation_address') or value('consumer_address')],
        ['Total Project Cost (including applicable taxes, unless stated otherwise)', indian_amount(d['project_cost'])],
        ['Advance Payment', '70% against order confirmation / Proforma Invoice before dispatch, unless otherwise mutually agreed in writing.'],
        ['Balance Payment', '30% after installation and commissioning, unless otherwise mutually agreed in writing.'],
        ['Additional / Customized Work', 'Only as required by site conditions and mutually approved; to be billed separately with applicable GST.'],
    ]
    story += [p('4. PROJECT DETAILS AND COMMERCIAL TERMS', heading),
              table([[p('<b>'+escape(label)+'</b>'),p(text)] for label,text in project_rows]),
              p('5. GENERAL TERMS', heading)]
    story += numbered_items(TERMS['general'][:1])
    story += [PageBreak()]
    story += numbered_items(TERMS['general'][1:], start=2)
    consumer = [p(f'Consumer Name: {value("consumer_name")}<br/><br/>Mobile Number: {value("mobile")}<br/><br/>'
                  f'Consumer Address:<br/>{value("consumer_address")}<br/><br/>Date: {day}<br/><br/>'
                  'Consumer Signature / E-Signature:<br/><br/>_____________________________')]
    seal = Image(str(ASSETS / 'agreement-seal.jpg'), width=48, height=48)
    seal_block = Table([[seal]],colWidths=[width/2-12])
    seal_block.setStyle(TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)]))
    vendor = [p(f'<b>{VENDOR}</b>',center), p(f'<b>Registered Office:</b><br/>{escape(VENDOR_ADDRESS)}<br/>'
              f'<b>Mobile: {VENDOR_PHONE}<br/>Authorized Signatory: {VENDOR}</b><br/>Date: {day}'),
              Spacer(1,10),p('<b>AUTHORIZED SIGNATURE &amp; SEAL</b>',center),seal_block,Spacer(1,5)]
    signature = table([[p('<b>CONSUMER DETAILS &amp; ACCEPTANCE</b>',center),p(f'<b>FOR {VENDOR} (VENDOR)</b>',center)],
                       [consumer,vendor]],True,padding=6)
    story += [KeepTogether([p('6. EXECUTION / SIGNATURES', heading),
                           p('<i>'+escape(TERMS['execution'])+'</i>'), signature])]
    def footer(canvas, document):
        canvas.saveState()
        canvas.setFont('Helvetica',7)
        canvas.drawCentredString(306,23,'EASTERNBAY SOLAR - Consumer/Vendor RTS Agreement | PM Surya Ghar: Muft Bijli Yojana')
        canvas.restoreState()
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    return out.getvalue()
