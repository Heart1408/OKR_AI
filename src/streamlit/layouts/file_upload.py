import streamlit as st
import os

def file_upload(TRAINING_DIR):
    st.header("Upload Files")
    uploaded_files = st.file_uploader("**Select documents**", type=['pdf'], accept_multiple_files=True)
    if uploaded_files:
        if st.button("Save"):
            with st.spinner("Creating vectorstore..."):
                error_message = []
                if len(error_message) == 1:
                    st.session_state.error_message = error_message[0]
                elif len(error_message) > 1:
                    st.session_state.error_message = "\n".join(error_message)
                else:
                    st.session_state.error_message = ""
                    try:
                        # Upload selected documents to training data directory
                        if uploaded_files is not None:
                            for uploaded_file in uploaded_files:
                                error_message = ""
                                try:
                                    file_path = os.path.join(
                                        TRAINING_DIR.as_posix(), uploaded_file.name
                                    )
                                    with open(file_path, "wb") as file:
                                        file.write(uploaded_file.read())
                                except Exception as e:
                                    error_message = f"{e}"
                            if error_message != "":
                                st.warning(f"Error: {error_message}")

                            st.rerun()
                            st.info(
                                f"Upload file succussfully."
                            )
                    except Exception as error:
                        st.error(f"An error occurred: {error}")
    try:
        if st.session_state.error_message != "":
            st.warning(st.session_state.error_message)
    except:
        pass
