import yaml
from yaml.loader import SafeLoader
import streamlit as st
import streamlit_authenticator as stauth
from pathlib import Path
import sys
import os

sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.streamlit.layouts.file_upload import file_upload
from src.streamlit.layouts.file_list import file_list

TRAINING_DIR = Path(__file__).resolve().parent.parent.joinpath("data_source", "generative_ai")

with open('credential_config.yaml', 'r') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

try:
    authenticator.login()
except Exception as e:
    st.error(e)

if st.session_state['authentication_status']:
    authenticator.logout()

    tab1, tab2 = st.tabs(["List Files", "Upload Files"])
    with tab1:
        file_list(TRAINING_DIR)
    with tab2:
        file_upload(TRAINING_DIR)
elif st.session_state['authentication_status'] == False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] == None:
    st.warning('Please enter your username and password')
