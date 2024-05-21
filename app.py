from flask import Flask, request, render_template, send_file, redirect, url_for, session
from PIL import Image
import numpy as np
import io
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    filename = session.pop('filename', None)
    detect_filename = session.pop('detect_filename', None)
    return render_template('index.html', filename=filename, detect_filename=detect_filename)

@app.route('/upload', methods=['POST'])
def upload():
    if 'original_image' not in request.files or 'watermark_image' not in request.files:
        return 'No file part'
    
    original_image = Image.open(request.files['original_image'])
    watermark_image = Image.open(request.files['watermark_image'])
    
    watermarked_image = embed_watermark(original_image, watermark_image)
    
    # Save watermarked image to a file
    filename = 'watermarked_image.png'
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    watermarked_image.save(filepath)
    
    # Save the filename in session
    session['filename'] = filename
    
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    return send_file(filepath, as_attachment=True)

@app.route('/index2')
def index2():
    detect_filename = session.pop('detect_filename', None)
    return render_template('detect.html', detect_filename=detect_filename)

@app.route('/detect', methods=['POST'])
def detect():
    if 'image' not in request.files:
        return 'No file part'
    
    image = Image.open(request.files['image'])
    watermark = extract_watermark(image)
    
    # Save extracted watermark to a file
    detect_filename = 'extracted_watermark.png'
    filepath = os.path.join(UPLOAD_FOLDER, detect_filename)
    watermark.save(filepath)
    
    # Save the detect filename in session
    session['detect_filename'] = detect_filename
    
    return redirect(url_for('index2'))

def embed_watermark(original_image, watermark_image):
    original_array = np.array(original_image)
    watermark_array = np.array(watermark_image.resize(original_image.size))
    
    watermarked_array = original_array.copy()
    for i in range(original_array.shape[0]):
        for j in range(original_array.shape[1]):
            # Mendapatkan nilai pixel dari gambar asli dan watermark
            original_pixel = original_array[i, j]
            watermark_pixel = watermark_array[i, j]
            
            # Mengambil bit terakhir dari nilai pixel watermark
            watermark_bit = watermark_pixel % 2
            
            # Menyembunyikan bit watermark pada bit terakhir nilai pixel gambar asli
            watermarked_array[i, j] = (original_pixel & 0b11111110) | watermark_bit
    
    return Image.fromarray(watermarked_array.astype(np.uint8))

def extract_watermark(image):
    array = np.array(image)
    watermark_array = np.zeros_like(array)
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            # Mendapatkan nilai pixel dari gambar yang sudah diproses
            pixel_value = array[i, j]
            # Ekstraksi bit terakhir yang berisi watermark
            watermark_pixel = pixel_value & 0b00000001
            # Menempatkan nilai pixel watermark pada gambar ekstraksi
            watermark_array[i, j] = watermark_pixel * 255
    
    return Image.fromarray(watermark_array.astype(np.uint8))

if __name__ == "__main__":
    app.run(debug=True)
