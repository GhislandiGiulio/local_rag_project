from tinydb import TinyDB, Query
from datetime import datetime

# Initialize the database (stored as a JSON file)
db = TinyDB("db/chatbot.json")
chat_history = db.table("chat_history")
Message = Query()  # TinyDB query object

# Insert a message
def save_message(pdf_hash, pdf_name, model_name, role, message):
    chat_history.insert({
        "pdf_hash": pdf_hash,
        "pdf_name": pdf_name,
        "model_name": model_name,
        "role": role,
        "content": message,
        "timestamp": datetime.now().isoformat()
    })
    
# Retrieve messages filtered by pdf_file
def get_messages(pdf_hash):
    return chat_history.search(Message.pdf_hash == pdf_hash)


def get_chats():
    result = list({(chat["pdf_name"], chat["pdf_hash"], chat["model_name"]) for chat in chat_history.all()})
    return result

def remove_chat(sha256_code):
    chat_history.remove(Message.pdf_hash == sha256_code)