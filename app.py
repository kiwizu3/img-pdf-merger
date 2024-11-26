from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
import os
import uuid

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')  # Serve the HTML file

@app.route('/merge', methods=['POST'])
def merge_images_to_pdf():
    if 'images' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400

    files = request.files.getlist('images')
    images = []
    for file in files:
        if file.filename.lower().endswith('.jpg'):
            img = Image.open(file).convert('RGB')
            images.append(img)

    if not images:
        return jsonify({'error': 'No valid JPG files found'}), 400

    pdf_filename = f"{uuid.uuid4().hex}.pdf"
    pdf_path = os.path.join(OUTPUT_FOLDER, pdf_filename)
    images[0].save(pdf_path, save_all=True, append_images=images[1:])
    
    pdf_path = os.path.join('pdfs', 'merged.pdf')
    pdf_url = request.url_root + pdf_path
    app.logger.info(f"PDF URL generated: {pdf_url}")  
    return jsonify({'pdf_url': pdf_url})

  
    # return jsonify({'pdf_url': f'/download/{pdf_filename}'})


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

