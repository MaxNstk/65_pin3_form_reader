import os
import time
from flask import Flask, request, render_template, redirect
from image_handler import ImageHandler

from pdf_converter import PDFConverter

app = Flask(__name__)

# Define the upload folder where the files will be saved
UPLOAD_FOLDER = 'static/01_pdf_uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

UPLOAD_FOLDER = 'static/02_img_results'
app.config['IMAGE_RESULTS_FOLDER'] = UPLOAD_FOLDER

CROPPED_IMAGES = 'static/03_cropped_images'
app.config['CROPPED_IMAGES_FOLDER'] = CROPPED_IMAGES


# Create the upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
    
    img_handler = ImageHandler(base_image_path=file_path_jpg)

    img_handler.cropp_image(path_to_save=os.path.join(app.config['CROPPED_IMAGES_FOLDER'], file_name_jpg))
    
    return redirect(f"/base-form-configuration/{file_name_jpg}")

@app.route('/base-form-configuration/<file_name>')
def configuration_form(file_name):
    if not os.path.exists(os.path.join(app.config['CROPPED_IMAGES_FOLDER'], file_name)):
        return redirect('/')
    return render_template("configuration.html",image_path=f'03_cropped_images/{file_name}')


if __name__ == '__main__':
    app.run(debug=True)