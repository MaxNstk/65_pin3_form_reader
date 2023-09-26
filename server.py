import os
import time
import asyncio

from flask import Flask, request, render_template, redirect, send_from_directory, jsonify, url_for
from image_handler import ImageHandler
from pdf_converter import PDFConverter

class App:

    UPLOAD_FOLDER = 'static/01_pdf_uploads'
    IMAGES_FOLDER = 'static/02_img_results'
    CROPPED_IMAGES = 'static/03_cropped_images'
    EDITED_IMAGES = 'static/04_edited_cropped_images'

    def __init__(self):
        self.app = Flask(__name__)
        
        # Define the upload folder where the files will be saved
        self.app.config['UPLOAD_FOLDER'] = self.UPLOAD_FOLDER
        self.app.config['IMAGE_RESULTS_FOLDER'] = self.IMAGES_FOLDER
        self.app.config['CROPPED_IMAGES_FOLDER'] = self.CROPPED_IMAGES
        self.app.config['EDITED_IMAGES_FOLDER'] = self.EDITED_IMAGES
        self.app.config['CURRENT_FILE'] = None

        # Create the upload folder if it doesn't exist
        if not os.path.exists(self.UPLOAD_FOLDER):
            os.makedirs(self.UPLOAD_FOLDER)
        if not os.path.exists(self.IMAGES_FOLDER):
            os.makedirs(self.IMAGES_FOLDER)
        if not os.path.exists(self.CROPPED_IMAGES):
            os.makedirs(self.CROPPED_IMAGES)
        if not os.path.exists(self.EDITED_IMAGES):
            os.makedirs(self.EDITED_IMAGES)

        self.app.route('/')(self.index)
        self.app.route('/upload', methods=['POST'])(self.upload_file)
        self.app.route('/base-form-configuration/<file_name>')(self.configuration_form)
        self.app.route('/get_image/<file_name>')(self.get_image)
        self.app.route('/get_original_image/<file_name>')(self.get_original_image)
        self.app.route('/set_inital_marker/<file_name>', methods=['POST'])(self.set_initial_marker)

    def get_static_path(self,file_name, original_image=False):
        if original_image:
            if not os.path.exists(os.path.join(self.CROPPED_IMAGES, file_name)):
                return
            return os.path.join(self.CROPPED_IMAGES, file_name)
        
        if not os.path.exists(os.path.join(self.EDITED_IMAGES, file_name)):
            return
        return os.path.join(self.EDITED_IMAGES, file_name)

    def index(self):
        return render_template('index.html')

    def upload_file(self):
        if 'base-form-upload' not in request.files: # or 'json-config-upload' not in request.files:
            return redirect(request.url)

        # json_config_file = request.files['json-config-upload']

        base_form_file = request.files['base-form-upload']

        file_name = f"{time.strftime('%Y%m%d-%H%M%S')}_{base_form_file.filename}"
        upload_pdf_path = os.path.join(self.app.config['UPLOAD_FOLDER'], file_name)
        base_form_file.save(upload_pdf_path)

        file_name_jpg = file_name.replace('.pdf','.jpg')
        file_path_jpg = os.path.join(self.app.config['IMAGE_RESULTS_FOLDER'], file_name_jpg)

        PDFConverter.convert_to_jpg(pdf_path=upload_pdf_path, 
                            result_path=file_path_jpg)

        self.app.config['img_handler'] = ImageHandler(base_image_path=file_path_jpg)

        self.app.config['img_handler'].cropp_image()
        self.app.config['img_handler'].save_cropped_image(os.path.join(self.app.config['CROPPED_IMAGES_FOLDER'], file_name_jpg)) # SAVE THE ORIGINLA PICTURE
        self.app.config['img_handler'].save_cropped_image(os.path.join(self.app.config['EDITED_IMAGES_FOLDER'], file_name_jpg)) # SAVE THE MODIFIED TO SHOW TO USER

        self.app.config['file_path_jpg'] = os.path.join(self.app.config['EDITED_IMAGES_FOLDER'], file_name_jpg)
        self.app.config['file_name_jpg'] = file_name_jpg

        return redirect(url_for("configuration_form",file_name=file_name))

    def configuration_form(self, file_name):
        if not self.get_static_path(file_name):
            return redirect('/')
        return render_template("configuration.html", file_name=file_name)

    def get_image(self, file_name):
        return send_from_directory(self.app.config['EDITED_IMAGES_FOLDER'], self.app.config['file_name_jpg'])

    def get_original_image(self, file_name):
        return send_from_directory(self.app.config['CROPPED_IMAGES_FOLDER'], self.app.config['file_name_jpg'])

    async def set_initial_marker(self, file_name):
        await self.app.config['img_handler'].configure_initial_positions(self.app.config['file_path_jpg'])
        return jsonify({'message': 'Image updated asynchronously'})

    def run(self):
        if __name__ == '__main__':
            self.app.run(debug=True)

if __name__ == '__main__':
    my_app = App()
    my_app.run()