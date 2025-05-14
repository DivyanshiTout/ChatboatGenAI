# app.py
import os
from flask import Flask, request, jsonify,render_template, redirect, url_for, flash
from flask_cors import CORS
from pathlib import Path
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
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
FILE_LIST_PATH = "data/file_list.txt"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs("data", exist_ok=True)
app.secret_key = "secret"  # Required for flashing messages
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR

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
        You are an assistant that only answers based on the following content.
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


@app.route("/api/upload", methods=["POST"])
def upload_document():
    if "file" not in request.files:
        return jsonify({"error": "No files part in the request"}), 400

    files = request.files.getlist("file")

    if not files:
        return jsonify({"error": "No file selected"}), 400

    uploaded_files = []
    unsupported_files = []

    for file in files:
        if file and file.filename.lower().endswith((".pdf", ".docx", ".txt")):
            filename = secure_filename(file.filename)
            save_path = os.path.join(UPLOAD_DIR, filename)
            file.save(save_path)
            uploaded_files.append(filename)

            # Update file_list.txt
            if os.path.exists(FILE_LIST_PATH):
                with open(FILE_LIST_PATH, "r") as f:
                    existing = f.read().splitlines()
            else:
                existing = []

            if filename not in existing:
                with open(FILE_LIST_PATH, "a") as f:
                    f.write(filename + "\n")
        else:
            unsupported_files.append(file.filename)
    print(len(uploaded_files))
    return jsonify({
        "uploaded": uploaded_files,
        "unsupported": unsupported_files
    }), 200

# ✅ Admin UI
@app.route("/", methods=["GET", "POST"])
def admin_upload_ui():
    if request.method == "POST":
        files = request.files.getlist("file")
        
        if not files:
            flash("No files selected.")
            return redirect(request.url)

        uploaded_files = []
        unsupported_files = []
        
        for file in files:
            if file.filename.lower().endswith((".pdf", ".docx", ".txt")):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_DIR, filename))
                uploaded_files.append(filename)

                # Update file_list.txt
                if os.path.exists(FILE_LIST_PATH):
                    with open(FILE_LIST_PATH, "r") as f:
                        existing = f.read().splitlines()
                else:
                    existing = []

                if filename not in existing:
                    with open(FILE_LIST_PATH, "a") as f:
                        f.write(filename + "\n")
            else:
                unsupported_files.append(file.filename)

        if uploaded_files:
            flash(f"Files uploaded successfully: {', '.join(uploaded_files)}")
        if unsupported_files:
            flash(f"Unsupported files: {', '.join(unsupported_files)}")

        return redirect(url_for("admin_upload_ui"))
    return render_template("upload.html")
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Default to port 5000 if not set
    app.run(debug=True, host="0.0.0.0", port=port)

