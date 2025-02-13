import streamlit as st
from pdf_scraping import new_scrape_pdf
from embedder_db import EmbedderDB
import chat_saving
import dotenv

# Load environment variables
@st.cache_data
def load_env():
    dotenv.load_dotenv()
    return True

load_env()

# main logo of app
st.logo("assets/icon.svg")

# Embedding models
EMBEDDING_MODELS = {
    "SentenceTransformers - all-MiniLM-L6-v2": "all-MiniLM-L6-v2",
    "OpenAI - text-embedding-3-small": "text-embedding-3-small"
}

def upload_sequence():
    st.caption(f":page_facing_up: **{st.session_state.file.name}**")
    st.session_state.pdf_name = st.session_state.file.name
    
    with st.spinner("Processing your PDF..."):
        paragraphs_with_pages, num_pages, st.session_state.sha256_code = new_scrape_pdf(st.session_state.file)

    with st.spinner(f"Embedding using {st.session_state.selected_model}..."):
        st.session_state.embedder = EmbedderDB(embedding_model=st.session_state.selected_model)
        success = st.session_state.embedder.embed_and_load(
            paragraphs_with_pages=paragraphs_with_pages, 
            num_pages=num_pages, 
            collection_name=st.session_state.sha256_code
        )
    
    if success:
        st.session_state.messages = chat_saving.get_messages(st.session_state.sha256_code)
        st.session_state.state = "chat"
        st.success("✅ PDF uploaded and embedded successfully!")
        st.rerun()
    else:
        st.error("❗ This PDF has already been saved in the database.")


def load_sidebar():
    st.sidebar.title(":speech_balloon: Chat Menu")
    st.sidebar.write("**Select a chat** to view history or start a new one.")
    
    st.session_state.chat_history = chat_saving.get_chats()
    if st.sidebar.button("➕ New Chat", key="new_chat"):
        st.session_state.state = "upload"
        st.rerun()
    
    st.sidebar.divider()
    st.sidebar.subheader(":open_file_folder: Your Chats")
    
    for i, (pdf_name, sha256_code, model_name) in enumerate(st.session_state.chat_history):
        if st.sidebar.button(f"📄 {pdf_name} | 🧠 {model_name}", key=f"chat_{i}"):
            st.session_state.sha256_code = sha256_code
            st.session_state.messages = chat_saving.get_messages(sha256_code)
            st.session_state.pdf_name = pdf_name
            st.session_state.state = "chat"
            st.session_state.selected_model = model_name
            st.rerun()
    
    st.sidebar.divider()
    if st.sidebar.button("🗑 Manage Chats", key="manage_chats"):
        st.session_state.state = "removal"
        st.session_state.file = None
        st.rerun()

# Initialize session state variables
if "state" not in st.session_state:
    st.session_state.state = "initial"
if "file" not in st.session_state:
    st.session_state.file = None
if "chat_history" not in st.session_state:
    with st.spinner("Retrieving your chats..."):
        st.session_state.chat_history = chat_saving.get_chats()
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "all-MiniLM-L6-v2"

st.title("📖 PDF Search Engine")

if st.session_state.state in ["initial", "upload"]:
    st.session_state.file = None
    st.session_state.file = st.file_uploader("📂 Upload a PDF", type=["pdf"])
    
    st.session_state.selected_model = st.selectbox(
        "🔍 Choose an embedding model:",
        options=list(EMBEDDING_MODELS.keys()),
        format_func=lambda x: x,
        index=0,
    )
    st.session_state.selected_model = EMBEDDING_MODELS[st.session_state.selected_model]

    if st.session_state.file and st.button("🚀 Start Embedding", key="start_embedding"):
        upload_sequence()
    
    load_sidebar()

if st.session_state.state == "chat":
    st.write(f"💬 Chatting with **{st.session_state.pdf_name}** (Model: **{st.session_state.selected_model}**)\n")
    load_sidebar()
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if user_input := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        query_result = st.session_state.embedder.search(user_input, collection_name=st.session_state.sha256_code)
        response = "\n".join([f"- 📄 Page: {page} | Score: {score}" for page, score in query_result])
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        chat_saving.save_message(st.session_state.sha256_code, st.session_state.pdf_name, st.session_state.selected_model, "user", user_input)
        chat_saving.save_message(st.session_state.sha256_code, st.session_state.pdf_name, st.session_state.selected_model, "assistant", response)
        
        with st.chat_message("assistant"):
            st.markdown(response)

if st.session_state.state == "removal":
    selected_chats = []
    for chat_i, (pdf_name, sha256_code, model_name) in enumerate(st.session_state.chat_history):
        if st.checkbox(f"🗂 {pdf_name} | {model_name}", key=f"remove_{chat_i}"):
            selected_chats.append(sha256_code)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ Back", key="back"):
            st.session_state.state = "upload"
            st.rerun()
    with col2:
        if st.button("🗑 Remove Chats", key="remove_chats") and selected_chats:
            for sha256_code in selected_chats:
                print("removing")
                chat_saving.remove_chat(sha256_code)
                st.session_state.embedder.delete_collection(collection_name=sha256_code)
                st.session_state.chat_history = chat_saving.get_chats()
                st.session_state.state = "upload"
                st.rerun()
        else:
            st.error("❗ Select at least one chat to remove.")
