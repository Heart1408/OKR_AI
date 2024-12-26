import streamlit as st
import os
import sys

sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from rag.file_loader import document_loader, split_documents_to_chunks
from base.llm_model import get_model_embedding
from rag.vectorstore import create_vectorstore

def file_upload(TRAINING_DIR, LOCAL_VECTOR_STORE_DIR):
    st.header("Upload Files")
    st.session_state.uploaded_files = st.file_uploader("**Select documents**", type=['pdf'], accept_multiple_files=True)

    if st.session_state.uploaded_files:
        st.button("Create Vectorstore", on_click=createVectorstore(TRAINING_DIR, LOCAL_VECTOR_STORE_DIR))
        try:
            if st.session_state.error_message != "":
                st.warning(st.session_state.error_message)
        except:
            pass
        
def createVectorstore(TRAINING_DIR, LOCAL_VECTOR_STORE_DIR):
    with st.spinner("Creating vectorstore..."):
        error_message = []
        if not st.session_state.uploaded_files:
            error_message.append("Please upload documents.")
        if len(error_message) == 1:
            st.session_state.error_message = error_message[0]
        elif len(error_message) > 1:
            st.session_state.error_message = "\n".join(error_message)
        else:
            st.session_state.error_message = ""
            try:
                # Upload selected documents to training data directory
                if st.session_state.uploaded_files is not None:
                    for uploaded_file in st.session_state.uploaded_files:
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
                    
                    # Load documents from training data directory
                    documents = document_loader(TRAINING_DIR)

                    # Split documents to chunks
                    chunks = split_documents_to_chunks(documents)

                    # Get model embeddings
                    embeddings = get_model_embedding()

                    # Create a vectorstore
                    persist_directory = LOCAL_VECTOR_STORE_DIR.as_posix()

                    try:
                        st.session_state.vectorstore = create_vectorstore(
                            chunks, embeddings, persist_directory
                        )
                        st.info(
                            f"Vectorstore is created succussfully."
                        )
                    except Exception as e:
                        st.error(e)

            except Exception as error:
                st.error(f"An error occurred: {error}")
    # if not os.path.exists(file_save_path):
    #     os.makedirs(file_save_path)

    #     for uploaded_file in uploaded_files:
    #         file_name = os.path.join(file_save_path, uploaded_file.name)
    #         st.write(f"Processing file: {file_name}")
    #         with open(file_name, "wb") as f:
    #             f.write(uploaded_file.getbuffer())
    #         st.write(f"File {uploaded_file.name} saved at {file_name}")

    #         # if uploaded_file.type == "text/plain":
    #         #     content = uploaded_file.read().decode("utf-8")
    #         #     st.text_area(f"File Content: {uploaded_file.name}", content, height=300)
    #         # elif uploaded_file.type == "application/pdf":
    #         #     st.write(f"PDF file uploaded: {uploaded_file.name}. You can process it as needed.")
    #         # else:
    #         #     st.error(f"Unsupported file type: {uploaded_file.name}. Please upload a text or PDF file.")

    #     st.session_state["run_command"] = True
    #     uploaded_files = None
    #     st.rerun()
