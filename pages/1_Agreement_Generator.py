"""Dedicated Agreement Generator page."""
import streamlit as st
from appearance import ASSETS, theme_css
from agreement_page import render_agreement_page

st.set_page_config(page_title='Agreement Generator - Eastern Bay Solar',page_icon='📄',layout='wide')
theme = st.radio('Appearance',['White','Black'],horizontal=True,key='appearance')
st.markdown(theme_css(theme),unsafe_allow_html=True)
st.image(str(ASSETS / ('logo-light.png' if theme == 'White' else 'logo-dark.jpeg')),width=110)
render_agreement_page()
