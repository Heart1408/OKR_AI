import yaml
from yaml.loader import SafeLoader
import streamlit as st
import streamlit_authenticator as stauth
from src.screen.layouts.file_upload import file_upload
from src.screen.layouts.file_list import file_list
import subprocess
from pathlib import Path

TRAINING_DIR = Path(__file__).resolve().parent.joinpath("data_source", "training_datas")
LOCAL_VECTOR_STORE_DIR = Path(__file__).resolve().parent.joinpath("data_source", "vector_stores")

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
    file_path = "./data_source/generative_ai"
    with tab1:
        file_list(file_path)
    with tab2:
        file_upload(TRAINING_DIR, LOCAL_VECTOR_STORE_DIR)

    if "run_command" in st.session_state and st.session_state["run_command"]:
        command = 'uvicorn src.app:app --host "0.0.0.0" --port 5000 --reload'
        subprocess.run(command, shell=True)
        st.session_state["run_command"] = False
elif st.session_state['authentication_status'] == False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] == None:
    st.warning('Please enter your username and password')