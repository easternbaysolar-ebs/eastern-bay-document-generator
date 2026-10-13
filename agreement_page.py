"""Agreement page, shared by the dashboard and Streamlit page navigation."""
from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit as st
from agreement_generator import build_agreement_pdf
from agreement_input import extract_image_text, parse_agreement_text


@st.cache_resource(show_spinner=False)
def ocr_engine():
    from rapidocr_onnxruntime import RapidOCR
    return RapidOCR()


def apply_imported_details(text):
    data = parse_agreement_text(text)
    if data:
        for key in ('consumer_name','consumer_address','installation_address','portal_no','mobile','system_capacity','capacity_note','project_cost'):
            st.session_state['agreement_'+key] = data.get(key,'')
        st.session_state['agreement_agreement_date'] = data.get('agreement_date',datetime.now(ZoneInfo('Asia/Kolkata')).date())
    return data


def render_agreement_page():
    st.session_state.setdefault('agreement_agreement_date',datetime.now(ZoneInfo('Asia/Kolkata')).date())
    st.subheader('Agreement Generator')
    st.caption('PM Surya Ghar consumer-vendor agreement - supplied three-page format with company seal.')
    with st.expander('Import details from an image or pasted text', expanded=True):
        image = st.file_uploader('Upload a portal screenshot or details image', type=['png','jpg','jpeg','webp'], key='agreement_image')
        if st.button('Read image details', key='agreement_read_image'):
            st.session_state['agreement_ready'] = False
            if image is None:
                st.warning('Upload an image first.')
            else:
                try:
                    with st.spinner('Reading image text...'):
                        extracted = extract_image_text(image.getvalue(),ocr_engine())
                        st.session_state['agreement_import_text'] = extracted
                        imported = apply_imported_details(extracted)
                    if imported:
                        st.success(f'Read image and filled {len(imported)} fields below. Review the applicant name and address before generating.')
                    else:
                        st.warning('Text was read, but no supported details were found. Review the extracted text or fill the fields below.')
                except Exception as exc:
                    st.error(f'Could not read the image: {exc}. You can paste details or fill the fields below.')
        text = st.text_area('Details text', key='agreement_import_text', height=160,
                            placeholder='Consumer name: ...\nConsumer address: ...\nApplication number: ...\nMobile: ...\nSystem capacity: 3 kW\nProject cost: 222000\nAgreement date: 13/10/2026')
        if st.button('Apply details to fields', key='agreement_apply_text'):
            st.session_state['agreement_ready'] = False
            data = apply_imported_details(text)
            if not data:
                st.warning('No labelled details found. Use labels such as Consumer name, Address, Application number, Mobile, System capacity, Project cost and Agreement date.')
            else:
                st.success(f'Applied {len(data)} fields. Check all details before generating.')
            if 'loan' in text.lower():
                st.info('Loan details are not treated as the project cost. Enter the agreed total project cost below.')
    st.markdown('### Review agreement details')
    left,right = st.columns(2)
    with left:
        name = st.text_input('Consumer name', key='agreement_consumer_name')
        address = st.text_area('Consumer address', key='agreement_consumer_address',height=110)
        installation = st.text_area('Installation address (leave blank to use consumer address)',key='agreement_installation_address')
        mobile = st.text_input('Consumer mobile number',key='agreement_mobile')
    with right:
        portal = st.text_input('National Portal / Application number',key='agreement_portal_no')
        capacity = st.text_input('Proposed RTS system capacity',key='agreement_system_capacity',placeholder='3 kW')
        note = st.text_input('Capacity note (optional)',key='agreement_capacity_note',placeholder='Only add a portal eligibility note when applicable')
        cost = st.text_input('Total project cost (Rs.)',key='agreement_project_cost',placeholder='222000')
        agreement_date = st.date_input('Agreement date',key='agreement_agreement_date',format='DD/MM/YYYY')
    st.caption('The template includes 70% advance, 30% balance, five-year operation and maintenance, separate signature blocks and the original vendor seal.')
    data = dict(consumer_name=name,consumer_address=address,installation_address=installation,mobile=mobile,
                portal_no=portal,system_capacity=capacity,capacity_note=note,project_cost=cost,agreement_date=agreement_date.isoformat())
    labels = {'consumer_name':'Consumer name','consumer_address':'Consumer address','portal_no':'Application number',
              'mobile':'Consumer mobile number','system_capacity':'System capacity','project_cost':'Total project cost (Rs.)'}
    missing = [label for key,label in labels.items() if not str(data[key]).strip()]
    if missing:
        st.warning('To generate the PDF, complete: ' + ', '.join(missing) + '.')
        if not cost.strip():
            st.caption('The portal may leave Total Cost of RTS Installation blank. Enter your agreed project amount in Total project cost (Rs.).')
    st.caption('Select Generate Agreement PDF, then use Download Agreement PDF. Finish editing a field by pressing Tab before downloading.')
    # Rebuild on every committed field edit after the first generation, avoiding stale downloads.
    generate = st.button('Generate Agreement PDF',key='agreement_generate',use_container_width=True,disabled=bool(missing))
    if generate:
        st.session_state['agreement_ready'] = True
    if st.session_state.get('agreement_ready'):
        try:
            payload = build_agreement_pdf(data)
        except ValueError as exc:
            st.warning(str(exc))
        else:
            safe = ''.join(c if c.isalnum() or c in '_-' else '_' for c in name).strip('_') or 'consumer'
            st.caption(f'PDF ready for {name} | {portal} | {agreement_date.strftime("%d/%m/%Y")}')
            st.download_button('Download Agreement PDF', data=payload,file_name=f'{safe}_PM_Surya_Ghar_Agreement.pdf',mime='application/pdf',key='agreement_download',use_container_width=True)
