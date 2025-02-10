from tinydb import TinyDB, Query
from datetime import datetime

# Initialize the database (stored as a JSON file)
db = TinyDB("db/chatbot.json")
chat_history = db.table("chat_history")
Message = Query()  # TinyDB query object

# Insert a message
def save_message(pdf_file, role, message):
    chat_history.insert({
        "pdf_file": pdf_file,
        "role": role,
        "content": message,
        "timestamp": datetime.now().isoformat()
    })
    
# Retrieve messages filtered by pdf_file
def get_messages(pdf_file):
    return chat_history.search(Message.pdf_file == pdf_file)