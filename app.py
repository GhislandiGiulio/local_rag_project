import streamlit as st
from pdf_scraping import new_scrape_pdf
from embedder_db import EmbedderDB
import chat_saving

def upload_sequence():
    st.caption(st.session_state.file.name)
    
    st.session_state.pdf_name = st.session_state.file.name
    
    with st.spinner("Processing..."):
        paragraphs_with_pages, num_pages, st.session_state.sha256_code = new_scrape_pdf(st.session_state.file)

    with st.spinner("Embedding and uploading to DB..."):
        success = st.session_state.embedder.embed_and_load(
            paragraphs_with_pages=paragraphs_with_pages, 
            num_pages=num_pages, 
            collection_name=st.session_state.sha256_code
        )

    if not success:
        st.error("The PDF file has already been uploaded. Chat history reloaded.")
    
    st.session_state.messages = chat_saving.get_messages(st.session_state.sha256_code)
    st.session_state.state = "chat"
    st.rerun()
    

def load_sidebar():
    st.sidebar.title("Embedded PDFs")
    st.sidebar.write("**Select one** to retrieve chat history...")
    st.sidebar.write("or start a **new conversation**.")
    
    # Always refresh chat history before displaying buttons
    st.session_state.chat_history = chat_saving.get_chats()

    if st.sidebar.button("**New Chat**", use_container_width=True, key="new_chat"):
        st.session_state.state = "upload"
        st.session_state.file = None
        st.rerun()
    
    for i, (pdf_name, sha256_code) in enumerate(st.session_state.chat_history):
        if st.sidebar.button(pdf_name, use_container_width=True, key=f"chat_{i}"):
            st.session_state.sha256_code = sha256_code
            st.session_state.messages = chat_saving.get_messages(sha256_code)
            st.session_state.pdf_name = pdf_name
            st.session_state.state = "chat"
            st.rerun()

# Initialize session state variables
if "state" not in st.session_state:
    st.session_state.state = "initial"
if "file" not in st.session_state:
    st.session_state.file = None
if "chat_history" not in st.session_state:
    with st.spinner("Retrieving your chats..."):
        st.session_state.chat_history = chat_saving.get_chats()
    if st.session_state.chat_history:
        st.session_state.state = "upload"
if "embedder" not in st.session_state:
    with st.spinner("Loading Embedding Model..."):
        st.session_state.embedder = EmbedderDB()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sha256_code" not in st.session_state:
    st.session_state.sha256_code = ""
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = ""

st.title("PDF Search Engine")

if st.session_state.state == "initial":
    st.session_state.file = st.file_uploader("Upload a PDF", type=["pdf"])
    if st.session_state.file is not None:
        upload_sequence()

if st.session_state.state == "upload":
    st.session_state.file = st.file_uploader("Upload a PDF", type=["pdf"])
    if st.session_state.file is not None:
        upload_sequence()
        
    load_sidebar()

if st.session_state.state == "chat":
    
    st.write(f"Chatting with **{st.session_state.pdf_name}**")
    
    load_sidebar()
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if user_input := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        query_result = st.session_state.embedder.search(user_input, collection_name=st.session_state.sha256_code)
        response = f"You can find out more about your question at pages: \n{''.join(['- ' + str(page) + '\n' + "Score: " + str(score) + "\n" for page, score in query_result])}"
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        chat_saving.save_message(st.session_state.sha256_code, st.session_state.pdf_name, "user", user_input)
        chat_saving.save_message(st.session_state.sha256_code, st.session_state.pdf_name, "assistant", response)
        
        with st.chat_message("assistant"):
            st.markdown(response)
