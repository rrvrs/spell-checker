# app.py

import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from backend.utils.spellchecker import SpellChecker
from backend.utils.file_handler import process_text_file, process_docx_file
import yaml

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

spellchecker = SpellChecker(config)
app = Flask(__name__, static_folder='frontend/static')
UPLOAD_FOLDER = config.get("upload_dir", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/api/spellcheck", methods=["POST"])
def api_spellcheck():
    data = request.get_json()
    text = data.get("text", "")
    model_type = data.get("model_type", "bigram")
    result = spellchecker.check_text(text, model_type)
    return jsonify(result)

@app.route("/api/upload", methods=["POST"])
def api_upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    model_type = request.form.get("model_type", "bigram")
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    if filename.endswith(".txt"):
        text = process_text_file(filepath)
    elif filename.endswith(".docx"):
        text = process_docx_file(filepath)
    else:
        return jsonify({"error": "Unsupported file type"}), 400

    result = spellchecker.check_text(text, model_type)
    return jsonify(result)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.static_folder),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/", methods=["GET"])
def serve_ui():
    return send_from_directory("frontend", "index.html")

if __name__ == '__main__':
    app.run(debug=True)
