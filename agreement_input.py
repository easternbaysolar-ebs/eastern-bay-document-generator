"""Local screenshot OCR and conservative, label-based agreement field import."""
import io
import re
from datetime import datetime

LABELS = {
    'consumer_name': r'(?:name of (?:the )?(?:consumer|applicant)|(?:consumer|applicant|beneficiary) name|name)',
    'consumer_address': r'(?:consumer address|applicant address|residential address|address of consumer|address)',
    'installation_address': r'(?:project / installation address|installation address|site address)',
    'portal_no': r'(?:national portal\s*(?:/\s*application)?\s*(?:no\.?|number|id)?|application\s*(?:no\.?|number|id)|registration\s*(?:no\.?|number|id))',
    'mobile': r'(?:(?:consumer )?mobile(?: number| no\.?)?|contact(?: number| no\.?)?|phone(?: number| no\.?)?)',
    'system_capacity': r'(?:proposed (?:rts system|solar plant|solar|system) capacity(?:\s*\(kw\))?|(?:solar|system|plant) capacity(?:\s*\(kw\))?|capacity(?:\s*\(kw\))?)',
    'capacity_note': r'(?:capacity note|capacity remarks)',
    'project_cost': r'(?:total project cost|project cost|project amount|total amount|installation cost)',
    'agreement_date': r'(?:agreement date|date of agreement)',
}
ALL_LABELS = ('|'.join(LABELS.values()) + r'|district(?: / city)?|state|pin(?: code)?|loan(?: amount| status)?|aadhaar(?: number)?|email|category|discom|sanction(?:ed)? load').replace(' ',r'\s*')


def parse_agreement_text(text):
    """Unknown/unlabelled values stay blank; loan amount never becomes project cost."""
    text = text.replace('\r','').strip()
    result = {}
    for field, pattern in LABELS.items():
        # Screenshot OCR can join label words, e.g. "Consumername".
        pattern = pattern.replace(' ',r'\s*')
        match = re.search(r'(?im)^\s*(?:'+pattern+r')\s*(?::|=|\t|$)\s*',text)
        if not match:
            continue
        remaining = text[match.end():]
        stop = re.search(r'(?im)^\s*(?:'+ALL_LABELS+r')\s*(?::|=|\t|$)',remaining)
        block = remaining[:stop.start()] if stop else remaining
        value = block.strip()
        if field not in ('consumer_address','installation_address'):
            value = value.split('\n',1)[0].strip()
        if not value:
            continue
        if field == 'mobile':
            phone = re.search(r'(?:\+?91[\s-]*)?([6-9](?:[\s-]*\d){9})(?!\d)',value)
            if not phone:
                continue
            value = re.sub(r'\D','',phone.group(1))
        if field == 'project_cost':
            amount = re.search(r'\d[\d,]*(?:\.\d{1,2})?', value)
            if not amount:
                continue
            value = amount.group().replace(',','')
        if field == 'agreement_date':
            parsed = None
            for fmt in ('%d/%m/%Y','%d-%m-%Y','%Y-%m-%d','%d.%m.%Y'):
                try:
                    parsed = datetime.strptime(re.sub(r'\s','',value),fmt).date()
                    break
                except ValueError:
                    pass
            if parsed is None:
                continue
            result[field] = parsed
            continue
        result[field] = value
    portal = re.search(r'\bNP-[A-Z0-9]+-[A-Z0-9]+\b',text,re.I)
    if portal:
        result['portal_no'] = portal.group().upper()
    return result


def extract_image_text(image_bytes, engine=None):
    from PIL import Image, ImageOps
    import numpy as np
    if engine is None:
        from rapidocr_onnxruntime import RapidOCR
        engine = RapidOCR()
    with Image.open(io.BytesIO(image_bytes)) as source:
        if source.width * source.height > 25000000:
            raise ValueError('Image is too large. Upload an image below 25 megapixels.')
        im = ImageOps.exif_transpose(source).convert('RGB')
        im.thumbnail((2500,2500))
        result, _ = engine(np.array(im))
    if not result:
        raise ValueError('No text was found. Use a clearer screenshot or enter the text fields.')
    return '\n'.join(str(row[1]) for row in result)
