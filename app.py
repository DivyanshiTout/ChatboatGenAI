# app.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as gen_ai

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise RuntimeError("Missing GOOGLE_API_KEY in environment variables.")

gen_ai.configure(api_key=API_KEY)
MODEL = gen_ai.GenerativeModel('gemini-2.0-flash')
chat_session = MODEL.start_chat(history=[])

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

UPLOAD_DIR = "data/uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs("data", exist_ok=True)

def read_file_content(file_path: str) -> str:
    if file_path.endswith(".txt"):
        return Path(file_path).read_text(encoding="utf-8")
    elif file_path.endswith(".pdf"):
        from PyPDF2 import PdfReader
        with open(file_path, "rb") as f:
            return "\n".join(page.extract_text() or '' for page in PdfReader(f).pages)
    elif file_path.endswith(".docx"):
        import docx
        doc = docx.Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)
    return ""

def get_uploaded_files():
    try:
        with open("data/file_list.txt", "r") as f:
            filenames = f.read().strip().split("\n")
            return [os.path.join("data/uploaded_files", name) for name in filenames]
    except FileNotFoundError:
        return []

def merge_all_files(filepaths):
    return "\n\n".join(read_file_content(path) for path in filepaths)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_prompt = data.get("prompt", "")
    
    files = get_uploaded_files()
    context = merge_all_files(files)
    
    base_instruction = f"""
        You are an assistant that only answers based on the following content and you give the response very fast within seconds.
        If a user greets you, reply politely.
        If the question isn't covered, respond: " I couldn't find an answer for that topic.You can reach our support team directly for further help."
        Content:
        {context}
    """
    final_prompt = f"{base_instruction}\n\n{user_prompt}"
    
    try:
        response = chat_session.send_message(final_prompt)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ New API: Upload documents
@app.route("/api/upload", methods=["POST"])
def upload_document():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.lower().endswith((".pdf", ".docx", ".txt")):
        return jsonify({"error": "Unsupported file type"}), 400

    filename = file.filename
    save_path = os.path.join(UPLOAD_DIR, filename)
    file.save(save_path)

    # Add to file_list.txt if not already listed
    file_list_path = "data/file_list.txt"
    if os.path.exists(file_list_path):
        with open(file_list_path, "r") as f:
            existing = f.read().splitlines()
    else:
        existing = []

    if filename not in existing:
        with open(file_list_path, "a") as f:
            f.write(filename + "\n")

    return jsonify({"message": f"File '{filename}' uploaded successfully."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Default to port 5000 if not set
    app.run(debug=True, host="0.0.0.0", port=port)

