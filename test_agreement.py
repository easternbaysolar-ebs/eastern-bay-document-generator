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

# Mirrors National Portal labels and OCR reading order, using synthetic values.
PORTAL_DETAILS = '''ApplicationNumber:NP-TEST26-12345678
Application Details
State:
Andhra Pradesh
SC/ST Status:
Name of Discom:
Example Discom
Circle Name:
Example District
Full NameofPremisesOwnerPerson:
EXAMPLE APPLICANT
Division Name:
EXAMPLE DIVISION
Gender:
Female
Subdivision Name:
Example Town
Address of Premises for installation:
1-00 Example Road Sample
Scheme Name:
PM Surya Ghar: Muft Bijli Yojana
Village
Bank Name:
Pincode:
000000
IFSC Code:
Type of Location:
Account Holder Name:
Consumer Account Number (CA No.):
0000000000000000
Name as per Bank:
Mobile:
9000000000
Account Number:
Email:
Bank Remarks:
District:
Example District
Give Up Subsidy:
No
Application Submission Date:
12/10/2026
DCR Category Type:
With DCR
Bank Account Type:
Total Cost of RTS Installation:
Solar Rooftop Details
Sanctioned Load (kw):
4.000
Category Name:
Residential
Proposed Capacity (kWp):
3.000
Existing Installed Capacity (kWp):
0.000
Latitude:
Net Eligible Capacity (kWp):
3.000
Longitude:
Name of Vendor:
EASTERNBAY SOLAR'''


class AgreementTests(unittest.TestCase):
    def test_national_portal_import_and_download(self):
        d = parse_agreement_text(PORTAL_DETAILS)
        self.assertEqual(d['consumer_name'],'EXAMPLE APPLICANT')
        self.assertEqual(d['system_capacity'],'3 kW')
        self.assertEqual(d['mobile'],'9000000000')
        self.assertNotIn('project_cost',d)
        self.assertNotIn('agreement_date',d)
        for part in ['1-00 Example Road Sample','Village','Example District','Andhra Pradesh','000000']:
            self.assertIn(part,d['consumer_address'])
        self.assertNotIn('PM Surya',d['consumer_address'])
        with patch('streamlit.download_button') as download:
            app=AppTest.from_file('pages/1_Agreement_Generator.py').run()
            app.text_area(key='agreement_import_text').set_value(PORTAL_DETAILS)
            app.button(key='agreement_apply_text').click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.text_input(key='agreement_consumer_name').value,'EXAMPLE APPLICANT')
            self.assertIn('Village',app.text_area(key='agreement_consumer_address').value)
            self.assertTrue(app.button(key='agreement_generate').disabled)
            app.text_input(key='agreement_project_cost').set_value('Rs. 2,22,000/-').run()
            self.assertFalse(app.button(key='agreement_generate').disabled)
            app.button(key='agreement_generate').click().run()
            self.assertFalse(app.exception)
            pdf=PdfReader(io.BytesIO(download.call_args.kwargs['data']))
            self.assertEqual(len(pdf.pages),3)
            self.assertIn('EXAMPLE APPLICANT',pdf.pages[0].extract_text())
            self.assertIn('Rs. 2,22,000/-',pdf.pages[1].extract_text())

    def test_image_read_fills_review_without_apply_button(self):
        uploaded=io.BytesIO(b'synthetic image placeholder')
        with patch('streamlit.file_uploader',return_value=uploaded), patch('agreement_page.ocr_engine',return_value=object()), patch('agreement_page.extract_image_text',return_value=PORTAL_DETAILS):
            app=AppTest.from_file('pages/1_Agreement_Generator.py').run()
            app.button(key='agreement_read_image').click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.text_input(key='agreement_consumer_name').value,'EXAMPLE APPLICANT')
            self.assertIn('Village',app.text_area(key='agreement_consumer_address').value)

    def test_labelled_import_and_amounts(self):
        d = parse_agreement_text(DETAILS)
        self.assertEqual(d['agreement_date'],date(2026,10,13))
        self.assertEqual(d['consumer_name'],'SAMPLE CONSUMER')
        self.assertIn('Example Town',d['consumer_address'])
        self.assertEqual(d['project_cost'],'222000')
        self.assertEqual(parse_agreement_text('Consumername:IMAGESAMPLE')['consumer_name'],'IMAGESAMPLE')
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
