import streamlit as st
import os

@st.dialog("Notice")
def comfirm_delete(selected_files):
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Delete"):
            for file in selected_files:
                os.remove(file)
            st.session_state.success_message = "Deleted successfully."
            st.rerun()
    with col2:
        if st.button("Cancel"):
            st.rerun()

def file_list(TRAINING_DIR):
    st.header("Training Files")
    file_path = TRAINING_DIR.as_posix()
    selected_files = []

    if os.path.exists(file_path):
        files = [f for f in os.listdir(file_path) if f.endswith(('.pdf')) and f != 'knowledge_base.pdf']
        if files:
            for file in files:
                file_name = os.path.join(file_path, file)
                col1, col2 = st.columns([1, 3])
                with col1:
                    selected = st.checkbox(label=" ", key=file)
                    if selected:
                        selected_files.append(file_name)
                with col2:
                    if selected:
                        st.markdown(f"<span style='color: red;'>{file}</span>", unsafe_allow_html=True)
                    else:
                        st.write(file)
            if len(selected_files) > 0:
                if st.button("Delete Selected Files"):
                    comfirm_delete(selected_files)

        else:
            st.write("No files found.")
    else:
        st.write("Folder does not exist.")
    
    if "success_message" in st.session_state:
        st.success(st.session_state.success_message)
