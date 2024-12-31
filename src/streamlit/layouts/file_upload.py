import streamlit as st
import os

@st.dialog("Notice")
def dialog(error_messages, uploaded_files, TRAINING_DIR):
    # Display the dialog and ask for confirmation
    st.write("\n".join(error_messages))
    col1, col2 = st.columns(2)
    with col1:
        if st.button("OK"):
            process_upload(uploaded_files, TRAINING_DIR)
            st.rerun()
    with col2:
        if st.button("Cancel"):
            st.rerun()

def process_upload(uploaded_files, TRAINING_DIR):
    for uploaded_file in uploaded_files:           
        try:
            file_path = os.path.join(
                TRAINING_DIR.as_posix(), uploaded_file.name
            )
            with open(file_path, "wb") as file:
                file.write(uploaded_file.read())
        except Exception as e:
            st.error(f"An error occurred: {e}")

    st.session_state.success_message = "Upload file successfully."
    st.session_state.uploader_key += 1

def file_upload(TRAINING_DIR):
    st.header("Upload Files")
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 1

    uploaded_files = st.file_uploader(
        label="**Select documents**",
        type=['pdf'],
        accept_multiple_files=True,
        key=st.session_state.uploader_key,
    )
    st.session_state.error_message = ""

    if uploaded_files:
        if st.button("Save"):
            try:
                error_messages = []
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(TRAINING_DIR.as_posix(), uploaded_file.name)
                    if os.path.exists(file_path):
                        error_messages.append(f"File {uploaded_file.name} already exists. Do you want to overwrite it?")

                if len(error_messages) > 0:
                    dialog(error_messages, uploaded_files, TRAINING_DIR)
                else:
                    process_upload(uploaded_files, TRAINING_DIR)
                    st.rerun()

            except Exception as error:
                st.error(f"An error occurred: {error}")

    try:
        if st.session_state.error_message == "" and st.session_state.success_message != "":
            st.success(st.session_state.success_message)
            st.session_state.success_message = ""
    except:
        pass
