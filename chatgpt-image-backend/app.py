from flask import Flask, request, jsonify
from flask_cors import CORS
from gtts import gTTS
import base64
import io,os
from dotenv import load_dotenv
import fal_client
import requests
from PIL import Image
import pytesseract
from faster_whisper import WhisperModel

app = Flask(__name__)
CORS(app)
load_dotenv()
# client = InferenceClient(token=os.getenv("HF_TOKEN") )

# @app.route('/generate', methods=['POST'])
# def generate():
#     prompt = request.json.get('prompt')
#     print("prompt:", prompt)

#     # Generate image
#     image = client.text_to_image(
#         prompt=prompt,
#         model="black-forest-labs/FLUX.1-dev"
#     )

#     buffered = io.BytesIO()
#     image.save(buffered, format="PNG")
#     img_str = base64.b64encode(buffered.getvalue()).decode()



#     return jsonify({'image': img_str})


@app.route('/generate', methods=['POST'])
def generate():
    try:
        prompt = request.json.get("prompt")

        if not prompt:
            return jsonify({
                "status": "error",
                "message": "No prompt provided"
            }), 400

        print("Prompt received:", prompt)

        # Generate image using fal_client
        result = fal_client.subscribe(
            "fal-ai/flux/schnell",
            arguments={"prompt": prompt},
        )

        image_info = result.get("images", [])
        if not image_info or "url" not in image_info[0]:
            return jsonify({
                "status": "error",
                "message": "No image URL returned from model"
            }), 500

        image_url = image_info[0]["url"]

        # Fetch the image
        response = requests.get(image_url)
        if response.status_code != 200:
            return jsonify({
                "status": "error",
                "message": "Failed to fetch image from URL"
            }), 500

        # Convert image to base64
        image_base64 = base64.b64encode(response.content).decode("utf-8")

        return jsonify({'image': image_base64})

    except Exception as e:
        print("Error generating image:", e)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
@app.route('/audio', methods=['POST'])
def audio():
    prompt = request.json.get('prompt')
    print("prompt:", prompt)
    # Text-to-Speech
    tts = gTTS(text=prompt)
    audio_buf = io.BytesIO()
    tts.write_to_fp(audio_buf)
    audio_str = base64.b64encode(audio_buf.getvalue()).decode()
    return jsonify({'audio': audio_str})

@app.route('/image-to-text', methods=['POST'])
def image_to_text():
    file = request.files.get('image')

    if not file:
        return jsonify({'error': 'No image provided'}), 400

    try:
        image = Image.open(file)
        text = pytesseract.image_to_string(image)
        clean_text = text.strip()

        if not clean_text:
            return jsonify({'text': '', 'message': 'No readable text found in the image.'})
        else:
            return jsonify({'text': clean_text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

model = WhisperModel("base")

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    audio_file = request.files['audio']
    file_path = os.path.join("temp", audio_file.filename)

    # Save the uploaded file
    os.makedirs("temp", exist_ok=True)
    audio_file.save(file_path)

    try:
        segments, info = model.transcribe(file_path)
        transcription = "".join([segment.text for segment in segments])

        return jsonify({
            "status": "success",
            "text": transcription
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    app.run(debug=True, port=5003)
