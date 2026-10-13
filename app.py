from datetime import date
import streamlit as st
from document_generators import *

st.set_page_config(page_title='Eastern Bay Document Generator', page_icon='📄', layout='wide')
from appearance import ASSETS, theme_css

theme = st.radio('Appearance', ['White', 'Black'], horizontal=True, key='appearance')
st.markdown(theme_css(theme), unsafe_allow_html=True)
st.image(str(ASSETS / ('logo-light.png' if theme == 'White' else 'logo-dark.jpeg')), width=110)

st.title('📄 Eastern Bay Document Generator')
st.caption('Choose a document, enter only the required details, then download as PDF or Word.')

docs=['Annexure A','Annexure C','Synchronization Certificate']
cols=st.columns(3)
for col,name in zip(cols,docs):
    with col:
        st.markdown(f"<div class='card'><div class='badge'>Ready</div><div class='title'>{name}</div><div class='small'>Generate PDF or Word</div></div>",unsafe_allow_html=True)
        if st.button('Open '+name,key='open_'+name,use_container_width=True): st.session_state['doc']=name

def download_output(name, fmt, payload, person='document'):
    ext='pdf' if fmt.startswith('PDF') else 'docx'; mime='application/pdf' if ext=='pdf' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    safe=''.join(c if c.isalnum() or c in ('_','-') else '_' for c in person).strip('_') or 'document'
    st.download_button(f'⬇️ Download {ext.upper()}',data=payload,file_name=f'{name.replace(" ","_")}_{safe}.{ext}',mime=mime,use_container_width=True)

selected=st.session_state.get('doc')
if selected=='Annexure A':
    st.divider(); st.subheader('Annexure A')
    with st.form('a'):
        c1,c2=st.columns(2)
        with c1:
            installer=st.text_input('Company name','EASTERN BAY SOLAR'); plant_capacity=st.text_input('Plant capacity','3KW'); consumer_name=st.text_input('Consumer name',''); address=st.text_area('Address',''); sanction_no=st.text_input('Sanction number',''); sanction_date=st.date_input('Sanction date',date(2026,7,13),format='DD/MM/YYYY')
        with c2:
            module_capacity=st.text_input('PV module capacity','585'); module_count=st.number_input('Number of modules',1,1000,6); serial_text=st.text_area('PV module serial numbers - one per line','WS06269073077693\nWS06269073077700\nWS06269073077701\nWS07269073842710\nWS07269073842713\nWS07269073842714',height=130); module_make=st.text_input('Panel company','Waaree Energies Limited'); po_number=st.text_input('Purchase order / invoice number','E B S 9 2'); po_date=st.date_input('Purchase order / invoice date',date(2026,9,10),format='DD/MM/YYYY'); cell_manufacturer=st.text_input('Cell manufacturer name','Waaree Energies Limited'); cell_gst_invoice=st.text_input('Cell GST invoice number',''); declaration_name=st.text_input('Declaration consumer name',''); installation_company=st.text_input('Installation company','EASTERN BAY SOLAR')
        st.markdown('**Fixed signature section**'); s1,s2,s3=st.columns(3)
        with s1: sign_company=st.text_input('Signature company','EASTERN BAY SOLAR'); sign_name=st.text_input('Authorized signatory','')
        with s2: designation=st.text_input('Designation','Managing Director'); phone=st.text_input('Phone','')
        with s3: email=st.text_input('Email',''); fmt=st.selectbox('Download format',['PDF (.pdf)','Word (.docx)'])
        go=st.form_submit_button('Generate Annexure A',use_container_width=True)
    if go:
        d=dict(installer=installer,plant_capacity=plant_capacity,consumer_name=consumer_name,address=address,sanction_no=sanction_no,sanction_date=fmt_date(sanction_date),module_capacity=module_capacity,module_count=str(module_count),serials=[x.strip() for x in serial_text.splitlines() if x.strip()],module_make=module_make,po_number=po_number,po_date=fmt_date(po_date),cell_manufacturer=cell_manufacturer,cell_gst_invoice=cell_gst_invoice,declaration_consumer_name=declaration_name,installation_company=installation_company,sign_company=sign_company,sign_name=sign_name,designation=designation,phone=phone,email=email)
        payload=build_annexure_a_pdf(d) if fmt.startswith('PDF') else build_annexure_a_docx(d); download_output('Annexure A',fmt,payload,consumer_name)

elif selected=='Annexure C':
    st.divider(); st.subheader('Annexure C')
    st.info('Page 2 is fully fixed. On Page 3, only Inverter Serial Number, Inverter Capacity and String 1 Voc are editable.')
    with st.form('c'):
        st.markdown('### Page 1 - Editable fields')
        c1,c2=st.columns(2)
        with c1:
            financial_year=st.text_input('Financial year','2025-2026'); sanction_letter_no=st.text_input('Sanction letter number',''); installed_agency=st.text_input('Installed agency','EASTERN BAY SOLAR'); spv_capacity=st.text_input('SPV capacity (kWp)','3.0'); contact_person=st.text_input('Name of contact person',''); address=st.text_area('Address of contact person',''); district_city=st.text_input('District / City','ANAKAPALLI', key='district_city')
        with c2:
            mobile=st.text_input('Mobile',''); email=st.text_input('Email',''); aadhaar=st.text_input('Aadhaar card number',''); latitude=st.text_input('Latitude',''); longitude=st.text_input('Longitude',''); ca_no=st.text_input('CA number',''); sanction_load=st.text_input('Sanction load','4.000'); solar_pv_modules=st.text_input('Solar PV modules / Make','Renew Photovoltaics Private Limited'); power_each_module=st.text_input('Power of each PV module (Wp)','550')
        st.markdown('### Page 3 - Editable fields')
        p31,p32,p33=st.columns(3)
        with p31: inverter_serial=st.text_input('Inverter serial number','270602C14F')
        with p32: inverter_capacity=st.text_input('Inverter capacity','4 KW')
        with p33: string1_voc=st.text_input('String 1 Voc','550V')
        fmt=st.selectbox('Download format',['PDF (.pdf)','Word (.docx)'],key='cfmt'); go=st.form_submit_button('Generate Annexure C',use_container_width=True)
    if go:
        d=locals().copy(); payload=build_annexure_c_pdf(d) if fmt.startswith('PDF') else build_annexure_c_docx(d); download_output('Annexure C',fmt,payload,contact_person)

elif selected=='Synchronization Certificate':
    st.divider(); st.subheader('Synchronization Certificate')
    with st.form('s'):
        c1,c2=st.columns(2)
        with c1:
            applicant_name=st.text_input('Applicant name',''); address=st.text_area('Address / D.No',''); consumer_no=st.text_input('Consumer number',''); pmsg_ref_no=st.text_input('PMSG reference number',''); installation_company=st.text_input('Installation company / Agency','EASTERN BAY SOLAR')
        with c2:
            system_capacity=st.text_input('System capacity','3 kW'); inverter_make=st.text_input('Inverter make / brand',''); inverter_serial=st.text_input('Inverter serial number',''); seal_date=st.text_input('Synchronization / sealing date',''); fmt=st.selectbox('Download format',['PDF (.pdf)','Word (.docx)'],key='sfmt')
        go=st.form_submit_button('Generate Synchronization Certificate',use_container_width=True)
    if go:
        d=locals().copy(); payload=build_sync_pdf(d) if fmt.startswith('PDF') else build_sync_docx(d); download_output('Synchronization Certificate',fmt,payload,applicant_name)

else:
    st.info('Select one of the three documents above to begin.')

st.divider(); st.caption('Eastern Bay Document Generator - Annexure A, Annexure C and Synchronization Certificate')
