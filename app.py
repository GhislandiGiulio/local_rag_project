import streamlit as st

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize file upload status in session state
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False

st.title("PDF Search Engine")

file = st.file_uploader("Upload a PDF", type=["pdf"])

if file:
    st.session_state.file_uploaded = True  # Mark file as uploaded
else:
    st.session_state.file_uploaded = False

# Show chat input only when a file is uploaded
if st.session_state.file_uploaded:
    # Chat input for user
    if user_input := st.chat_input("Ask a question..."):
        # Append user's message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Display messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(message["content"])
            if message["role"] == "assistant":
                with st.chat_message("assistant"):
                    st.markdown(message["content"])

        # Placeholder AI response (replace with your logic)
        response = f"You can find out more about you question at page:"

        # Append AI response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Display AI response
        with st.chat_message("assistant"):
            st.markdown(response)
else:
    st.write("Upload a PDF to enable search.")

