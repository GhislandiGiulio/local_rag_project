import streamlit as st
from pdf_scraping import scrape_pdf

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize file upload status in session state
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False
if "file_scraped" not in st.session_state:
    st.session_state.file_scraped = False

st.title("PDF Search Engine")

file = st.file_uploader("Upload a PDF", type=["pdf"])

if file is not None:
    st.session_state.file_uploaded = True
else:
    st.session_state.file_uploaded = False
    st.session_state.file_scraped = False  # Reset analysis state when file is removed

# 🔄 Use st.empty() for dynamic button removal
analyze_placeholder = st.empty()

if st.session_state.file_uploaded and not st.session_state.file_scraped:
    with analyze_placeholder:  # Use placeholder for the button
        if st.button("Analyze"):
            st.session_state.file_scraped = True
            with st.spinner("Processing..."):
                scrape_pdf(file)
            analyze_placeholder.empty()  # Clear the button after processing

# Show chat input only when a file is uploaded and analyzed
if st.session_state.file_scraped:
    if user_input := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Display messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Placeholder AI response (replace with your logic)
        response = f"You can find out more about your question at page:"

        # Append AI response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Display AI response
        with st.chat_message("assistant"):
            st.markdown(response)
else:
    st.write("Analyze a PDF to enable search.")
