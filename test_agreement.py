"""Synthetic fixtures only: no real consumer details are committed."""
import io
import unittest
from datetime import date
from unittest.mock import patch
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader
from streamlit.testing.v1 import AppTest
from agreement_generator import build_agreement_pdf, indian_amount
from agreement_input import extract_image_text, parse_agreement_text

DETAILS = '''Consumer name: SAMPLE CONSUMER
Consumer address: Example House, Sample Street
Example Town, Andhra Pradesh - 000000
Application number: NP-TEST26-12345678
Mobile: 9000000000
System capacity: 3 kW
Project cost: 222000
Agreement date: 13/10/2026'''


class AgreementTests(unittest.TestCase):
    def test_labelled_import_and_amounts(self):
        d = parse_agreement_text(DETAILS)
        self.assertEqual(d['agreement_date'],date(2026,10,13))
        self.assertEqual(d['consumer_name'],'SAMPLE CONSUMER')
        self.assertIn('Example Town',d['consumer_address'])
        self.assertEqual(d['project_cost'],'222000')
        self.assertEqual(indian_amount('2,22,000'),'Rs. 2,22,000/-')
        self.assertNotIn('project_cost',parse_agreement_text('Loan amount: 222000\nLoan status: Not applied'))
        self.assertNotIn('agreement_date',parse_agreement_text('Agreement date: 31/02/2026'))
        for amount in ['0','-1','NaN','Infinity','hello']:
            with self.assertRaises(ValueError):
                indian_amount(amount)

    def test_pdf_terms_and_seal(self):
        d = parse_agreement_text(DETAILS)
        pdf = PdfReader(io.BytesIO(build_agreement_pdf(d)))
        self.assertEqual(len(pdf.pages),3)
        text = '\n'.join(p.extract_text() for p in pdf.pages)
        for expected in ['SAMPLE CONSUMER','NP-TEST26-12345678','Rs. 2,22,000/-','13 / 10 / 2026',
                         '70%','30%','18.','AUTHORIZED SIGNATURE & SEAL','CONSUMER DETAILS & ACCEPTANCE']:
            self.assertIn(expected,text)
        self.assertNotIn('YALLA',text)
        self.assertNotIn('3 kW net eligible',text)
        self.assertEqual(len(pdf.pages[-1].images),1)
        d['consumer_address'] = 'Long address & special <text> ' * 30
        long_pdf = PdfReader(io.BytesIO(build_agreement_pdf(d)))
        self.assertIn('AUTHORIZED SIGNATURE & SEAL',long_pdf.pages[-1].extract_text())
        self.assertEqual(len(long_pdf.pages[-1].images),1)

    def test_real_download_and_fresh_import(self):
        with patch('streamlit.download_button') as download:
            app = AppTest.from_file('app.py').run()
            app.button(key='open_Agreement Generator').click().run()
            app.text_area(key='agreement_import_text').set_value(DETAILS)
            app.button(key='agreement_apply_text').click().run()
            self.assertFalse(app.exception)
            app.button(key='agreement_generate').click().run()
            self.assertFalse(app.exception)
            text = PdfReader(io.BytesIO(download.call_args.kwargs['data'])).pages[0].extract_text()
            self.assertIn('SAMPLE CONSUMER',text)
            app.text_input(key='agreement_consumer_name').set_value('SECOND SAMPLE').run()
            text = PdfReader(io.BytesIO(download.call_args.kwargs['data'])).pages[0].extract_text()
            self.assertIn('SECOND SAMPLE',text)
            self.assertNotIn('SAMPLE CONSUMER',text)
            download.reset_mock()
            app.text_area(key='agreement_import_text').set_value('Consumer name: THIRD SAMPLE')
            app.button(key='agreement_apply_text').click().run()
            self.assertEqual(app.text_input(key='agreement_portal_no').value,'')
            self.assertEqual(download.call_count,0)

    def test_dedicated_page(self):
        app = AppTest.from_file('pages/1_Agreement_Generator.py').run()
        self.assertFalse(app.exception)
        app.radio[0].set_value('Black').run()
        self.assertFalse(app.exception)

    def test_image_ocr(self):
        im = Image.new('RGB',(1300,420),'white')
        draw = ImageDraw.Draw(im)
        font = ImageFont.load_default(size=32)
        lines = ['Consumer name: SAMPLE CONSUMER','Application number: NP-TEST26-12345678',
                 'Mobile: 9000000000','System capacity: 3 kW','Project cost: 222000']
        for i,line in enumerate(lines):
            draw.text((30,25+i*65),line,fill='black',font=font)
        out = io.BytesIO()
        im.save(out,format='PNG')
        text = extract_image_text(out.getvalue())
        d = parse_agreement_text(text)
        self.assertEqual(d['portal_no'],'NP-TEST26-12345678')
        self.assertEqual(d['project_cost'],'222000')

if __name__=='__main__':
    unittest.main()
