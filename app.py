import streamlit as st
from pdf_scraping import new_scrape_pdf
from embedder_db import EmbedderDB
import chat_saving
import dotenv

@st.cache_data
def load_env():
    dotenv.load_dotenv()
    return True

# Loading API keys
load_env()

# Available embedding models
EMBEDDING_MODELS = {
    "SentenceTransformers - all-MiniLM-L6-v2": "all-MiniLM-L6-v2",
    "OpenAI - text-embedding-3-small": "text-embedding-3-small"
}

def upload_sequence():
    # Display uploaded file name
    st.caption(st.session_state.file.name)
    
    # Store PDF name in session state
    st.session_state.pdf_name = st.session_state.file.name
    
    with st.spinner("Processing..."):
        # Extract paragraphs and compute SHA256 hash of the document
        paragraphs_with_pages, num_pages, st.session_state.sha256_code = new_scrape_pdf(st.session_state.file)

    with st.spinner(f"Embedding using {st.session_state.selected_model} and uploading to DB..."):
        # Initialize the embedder with the selected model
        st.session_state.embedder = EmbedderDB(embedding_model=st.session_state.selected_model)
        success = st.session_state.embedder.embed_and_load(
            paragraphs_with_pages=paragraphs_with_pages, 
            num_pages=num_pages, 
            collection_name=st.session_state.sha256_code
        )

    # Check if PDF has already been uploaded
    if success:
        # Retrieve chat history
        st.session_state.messages = chat_saving.get_messages(st.session_state.sha256_code)
        st.session_state.state = "chat"
        st.rerun()
    
    st.error("The PDF file has already been saved in the DB.")

def load_sidebar():
    st.sidebar.title("Embedded PDFs")
    st.sidebar.write("**Select one** to retrieve chat history...")
    st.sidebar.write("or start a **new conversation**.")
    
    # Always refresh chat history before displaying buttons
    st.session_state.chat_history = chat_saving.get_chats()

    # New chat button
    if st.sidebar.button("**New Chat**", use_container_width=True, key="new_chat"):
        st.session_state.state = "upload"
        st.session_state.file = None
        st.rerun()
    
    # Load chat history buttons
    for i, (pdf_name, sha256_code, model_name) in enumerate(st.session_state.chat_history):
        if st.sidebar.button(f"{pdf_name} | **{model_name}**", use_container_width=True, key=f"chat_{i}"):
            st.session_state.sha256_code = sha256_code
            st.session_state.messages = chat_saving.get_messages(sha256_code)
            st.session_state.pdf_name = pdf_name
            st.session_state.state = "chat"
            st.session_state.selected_model = model_name
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
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "all-MiniLM-L6-v2"  # Default model

st.title("PDF Search Engine")

if st.session_state.state == "initial" or st.session_state.state == "upload":
    # File uploader
    st.session_state.file = st.file_uploader("Upload a PDF", type=["pdf"])
    
    # Embedding model selection dropdown
    st.session_state.selected_model = st.selectbox(
        "Choose an embedding model:",
        options=list(EMBEDDING_MODELS.keys()),
        format_func=lambda x: x,
        index=0,
    )
    st.session_state.selected_model = EMBEDDING_MODELS[st.session_state.selected_model]

    # Button to start embedding
    if st.session_state.file is not None:
        if st.button("Start Embedding", key="start_embedding"):
            upload_sequence()

    # Load sidebar with chat history
    load_sidebar()

if st.session_state.state == "chat":
    # Display active PDF chat
    st.write(f"Chatting with **{st.session_state.pdf_name}**, embedded using **{st.session_state.selected_model}**")
    
    load_sidebar()
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Handle user input
    if user_input := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Search PDF content using embedding model
        query_result = st.session_state.embedder.search(user_input, collection_name=st.session_state.sha256_code)
        response = f"You can find out more about your question at pages: \n{''.join(['- ' + str(page) + '\n' + 'Score: ' + str(score) + '\n' for page, score in query_result])}"
        
        # Store assistant response in session state
        st.session_state.messages.append({"role": "assistant", "content": response})
        chat_saving.save_message(st.session_state.sha256_code, st.session_state.pdf_name, st.session_state.selected_model, "user", user_input)
        chat_saving.save_message(st.session_state.sha256_code, st.session_state.pdf_name, st.session_state.selected_model, "assistant", response)
        
        with st.chat_message("assistant"):
            st.markdown(response)