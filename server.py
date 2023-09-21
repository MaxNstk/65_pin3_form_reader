import os
import time
import asyncio

from flask import Flask, request, render_template, redirect, send_from_directory,jsonify
from image_handler import ImageHandler

from pdf_converter import PDFConverter
import threading

app = Flask(__name__)

# Define the upload folder where the files will be saved
UPLOAD_FOLDER = 'static/01_pdf_uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

IMAGES_FOLDER = 'static/02_img_results'
app.config['IMAGE_RESULTS_FOLDER'] = IMAGES_FOLDER

CROPPED_IMAGES = 'static/03_cropped_images'
app.config['CROPPED_IMAGES_FOLDER'] = CROPPED_IMAGES

EDITED_IMAGES = 'static/04_edited_cropped_images'
app.config['EDITED_IMAGES_FOLDER'] = EDITED_IMAGES

app.config['CURRENT_FILE'] = None

# Create the upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(IMAGES_FOLDER):
    os.makedirs(IMAGES_FOLDER)
if not os.path.exists(CROPPED_IMAGES):
    os.makedirs(CROPPED_IMAGES)
if not os.path.exists(EDITED_IMAGES):
    os.makedirs(EDITED_IMAGES)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'base-form-upload' not in request.files: # or 'json-config-upload' not in request.files:
        return redirect(request.url)

    # json_config_file = request.files['json-config-upload']

    base_form_file = request.files['base-form-upload']
    
    file_name = f"{time.strftime('%Y%m%d-%H%M%S')}_{base_form_file.filename}"
    upload_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    base_form_file.save(upload_pdf_path)

    file_name_jpg = file_name.replace('.pdf','.jpg')
    file_path_jpg = os.path.join(app.config['IMAGE_RESULTS_FOLDER'], file_name_jpg)

    PDFConverter.convert_to_jpg(pdf_path=upload_pdf_path, 
                        result_path=file_path_jpg)
    
    app.config['img_handler'] = ImageHandler(base_image_path=file_path_jpg)

    app.config['img_handler'].cropp_image()
    app.config['img_handler'].save_cropped_image(os.path.join(app.config['CROPPED_IMAGES_FOLDER'], file_name_jpg)) # SAVE THE ORIGINLA PICTURE
    app.config['img_handler'].save_cropped_image(os.path.join(app.config['EDITED_IMAGES_FOLDER'], file_name_jpg)) # SAVE THE MODIFIED TO SHOW TO USER

    app.config['file_path_jpg'] = os.path.join(app.config['EDITED_IMAGES_FOLDER'], file_name_jpg)
    app.config['file_name_jpg'] = file_name_jpg

    return redirect(f"/base-form-configuration/")

@app.route('/base-form-configuration/')
def configuration_form():
    if not os.path.exists(app.config['file_path_jpg']):
        return redirect('/')
    
    return render_template("configuration.html")

@app.route('/update_image/')
def update_image():
    return send_from_directory(app.config['EDITED_IMAGES_FOLDER'], app.config['file_name_jpg'])

@app.route('/set_inital_marker/',  methods=['POST'])
def set_initial_marker():
    
    asyncio.run(app.config['img_handler'].configure_initial_positions(app.config['file_path_jpg']))
    return jsonify({'message': 'Image updated asynchronously'})

if __name__ == '__main__':
    app.run(debug=True)