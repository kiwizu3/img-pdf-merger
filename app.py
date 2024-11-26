from flask import Flask, request, jsonify, send_from_directory
import os
from PIL import Image
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
PDF_FOLDER = 'pdfs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PDF_FOLDER, exist_ok=True)

@app.route('/merge', methods=['POST'])
def merge():
    try:
        # Save uploaded images
        uploaded_files = request.files.getlist("images")
        if not uploaded_files:
            return jsonify({"error": "No images provided"}), 400

        image_paths = []
        for file in uploaded_files:
            filename = f"{uuid.uuid4().hex}.jpg"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            image_paths.append(filepath)

        # Create PDF
        images = [Image.open(img).convert("RGB") for img in image_paths]
        pdf_filename = f"merged_{uuid.uuid4().hex}.pdf"
        pdf_path = os.path.join(PDF_FOLDER, pdf_filename)
        images[0].save(pdf_path, save_all=True, append_images=images[1:])

        # Cleanup image files after merging
        for img_path in image_paths:
            os.remove(img_path)

        # Return the PDF URL
        return jsonify({"pdf_url": f"/download/{pdf_filename}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    # Serve the PDF file for download
    return send_from_directory(PDF_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
