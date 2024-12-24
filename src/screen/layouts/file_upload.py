import streamlit as st
import os

def file_upload(file_save_path):
    st.header("Upload Files")
    uploaded_files = st.file_uploader("Choose files", type=['txt', 'pdf'], accept_multiple_files=True)
    
    if uploaded_files:
        if st.button('OK'):
            if not os.path.exists(file_save_path):
                os.makedirs(file_save_path)

            for uploaded_file in uploaded_files:
                file_name = os.path.join(file_save_path, uploaded_file.name)
                st.write(f"Processing file: {file_name}")
                with open(file_name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.write(f"File {uploaded_file.name} saved at {file_name}")

                # if uploaded_file.type == "text/plain":
                #     content = uploaded_file.read().decode("utf-8")
                #     st.text_area(f"File Content: {uploaded_file.name}", content, height=300)
                # elif uploaded_file.type == "application/pdf":
                #     st.write(f"PDF file uploaded: {uploaded_file.name}. You can process it as needed.")
                # else:
                #     st.error(f"Unsupported file type: {uploaded_file.name}. Please upload a text or PDF file.")

            st.session_state["run_command"] = True
            uploaded_files = None
            st.rerun()
