# PDF Embed Search 🔍📄

<div style="display: flex; align-items: center;">
  <img src="assets/workflow.webp" alt="Workflow Diagram" width="200" style="margin-right: 20px;">
  <p>A lightweight application that extracts, indexes, and searches PDF content using embeddings and Qdrant, all within a Streamlit-powered chat interface.</p>
</div>

## Features 🚀
- **PDF Parsing**: Extracts and processes text from multi-page PDFs.
- **Embedding Model**: Utilizes a small, efficient embedding model for text vectorization.
- **Qdrant Indexing**: Stores and retrieves document chunks with high-speed vector search.
- **Chat Interface**: A user-friendly Streamlit UI for natural language queries.

<img src="assets/interface.png" alt="Interface Screenshot" width="500" style="margin-right: 20px;">

## Tech Stack 🛠
- **Python 3.13**
- **Qdrant** for fast vector search
- **Streamlit** for interactive chat UI
- **Small Embedding Model** (all-MiniLM-L6-v2)

## Usage 💡
### Run the App
#### PowerShell (Windows)
```powershell
streamlit run app.py
```

#### macOS/Linux
```sh
streamlit run app.py
```
### Inside the app
3. Upload a PDF
4. The app extracts and indexes text into Qdrant
5. Ask questions in the chat, and the app retrieves relevant chunks