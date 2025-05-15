import os
import mimetypes
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_cors import CORS
from werkzeug.utils import secure_filename
from google_drive_utils import upload_file_to_drive, list_files_from_drive,download_file_from_drive
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from docx import Document
from io import BytesIO
import google.generativeai as gen_ai
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise RuntimeError("Missing GOOGLE_API_KEY in environment variables.")

gen_ai.configure(api_key=API_KEY)
MODEL = gen_ai.GenerativeModel('gemini-2.0-flash')
chat_session = MODEL.start_chat(history=[])

app = Flask(__name__)
CORS(app)
app.secret_key = "secret"


def extract_text(file_stream: BytesIO, filename: str) -> str:
    if filename.endswith(".txt"):
        return file_stream.read().decode("utf-8")
    elif filename.endswith(".pdf"):
        reader = PdfReader(file_stream)
        return "\n".join(page.extract_text() or '' for page in reader.pages)
    elif filename.endswith(".docx"):
        doc = Document(file_stream)
        return "\n".join(p.text for p in doc.paragraphs)
    return ""

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_prompt = data.get("prompt", "")

    try:
        drive_files = list_files_from_drive()
        full_context = ""

        for file in drive_files:
            file_id = file['id']
            filename = file['name']
            if filename.endswith(('.pdf', '.docx', '.txt')):
                file_stream = download_file_from_drive(file_id)
                file_text = extract_text(file_stream, filename)
                full_context += f"\n\n{file_text}"
        print("full_context")
        base_instruction = f"""
        You are an assistant that only answers based on the following content give response very fast with in milisecond.
        If a user greets you, reply politely.
        If the question isn't covered, respond: " I couldn't find an answer for that topic. You can reach our support team directly for further help."
        Content:
        {full_context}
        """

        final_prompt = f"{base_instruction}\n\n{user_prompt}"

        response = chat_session.send_message(final_prompt)
        return jsonify({"response": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/upload", methods=["POST"])
def upload_document():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    files = request.files.getlist("file")
    if not files:
        return jsonify({"error": "No file selected"}), 400

    uploaded_files = []
    unsupported_files = []

    for file in files:
        if file and file.filename.lower().endswith((".pdf", ".docx", ".txt")):
            filename = secure_filename(file.filename)
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'

            # Ensure stream is at start
            file.stream.seek(0)
            result = upload_file_to_drive(file.stream, filename, mimetype)

            uploaded_files.append({
                "filename": filename,
                "drive_file_id": result["id"],
                "drive_link": result["webViewLink"]
            })
        else:
            unsupported_files.append(file.filename)

    return jsonify({
        "uploaded": uploaded_files,
        "unsupported": unsupported_files
    })

@app.route("/api/drive-files", methods=["GET"])
def get_drive_files():
    try:
        files = list_files_from_drive()
        return jsonify(files)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET", "POST"])
def admin_upload_ui():
    if request.method == "POST":
        files = request.files.getlist("file")
        if not files:
            flash("No files selected.")
            return redirect(request.url)

        uploaded = []
        unsupported = []

        for file in files:
            if file.filename.lower().endswith((".pdf", ".docx", ".txt")):
                filename = secure_filename(file.filename)
                mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
                file.stream.seek(0)
                upload_file_to_drive(file.stream, filename, mimetype)
                uploaded.append(filename)
            else:
                unsupported.append(file.filename)

        if uploaded:
            flash(f"Uploaded: {', '.join(uploaded)}")
        if unsupported:
            flash(f"Unsupported: {', '.join(unsupported)}")
        return redirect(url_for("admin_upload_ui"))
    return render_template("upload.html")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
