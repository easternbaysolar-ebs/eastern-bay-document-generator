"""Regression coverage for location exports and appearance switching."""
import io
import unittest
from docx import Document
from pypdf import PdfReader
from streamlit.testing.v1 import AppTest
from document_generators import build_annexure_c_docx, build_annexure_c_pdf

class GeneratorTests(unittest.TestCase):
    def test_location_in_both_exports(self):
        app = AppTest.from_file('app.py').run()
        app.button[1].click().run()
        self.assertFalse(app.exception)
        data = {w.label: w.value for w in app.text_input}
        district = next(w for w in app.text_input if w.label == 'District / City')
        district.set_value('KAKINADA & CITY')
        app.button[-1].click().run()
        self.assertFalse(app.exception)
        d = dict(financial_year=data['Financial year'], sanction_letter_no=data['Sanction letter number'], installed_agency=data['Installed agency'], spv_capacity=data['SPV capacity (kWp)'], contact_person=data['Name of contact person'], address=app.text_area[0].value, district_city='KAKINADA & CITY', mobile=data['Mobile'], email=data['Email'], aadhaar=data['Aadhaar card number'], latitude=data['Latitude'], longitude=data['Longitude'], ca_no=data['CA number'], sanction_load=data['Sanction load'], solar_pv_modules=data['Solar PV modules / Make'], power_each_module=data['Power of each PV module (Wp)'], inverter_serial=data['Inverter serial number'], inverter_capacity=data['Inverter capacity'], string1_voc=data['String 1 Voc'])
        pdf=PdfReader(io.BytesIO(build_annexure_c_pdf(d)))
        self.assertEqual(len(pdf.pages),3)
        self.assertIn(d['district_city'],pdf.pages[0].extract_text())
        doc=Document(io.BytesIO(build_annexure_c_docx(d)))
        self.assertIn(d['district_city'], '\n'.join(c.text for t in doc.tables for r in t.rows for c in r.cells))
        app.radio[0].set_value('Black').run()
        self.assertFalse(app.exception)
        self.assertEqual(next(w.value for w in app.text_input if w.label == 'District / City'),d['district_city'])

    def test_all_forms_and_themes(self):
        for theme in ['White','Black']:
            for index in range(3):
                app=AppTest.from_file('app.py').run()
                app.radio[0].set_value(theme).run()
                app.button[index].click().run()
                app.button[-1].click().run()
                self.assertFalse(app.exception)
                app.selectbox[0].set_value('Word (.docx)').run()
                app.button[-1].click().run()
                self.assertFalse(app.exception)

if __name__=='__main__':
    unittest.main()
