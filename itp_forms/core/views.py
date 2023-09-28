import time
from typing import Any
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView

from itp_forms.core.forms import ConfigurationForm, IndexForm
import os
from python.config import Config
from python.image_handler import ImageHandler

from python.pdf_converter import PDFConverter

UPLOAD_PDF_FOLDER = os.path.join(settings.MEDIA_ROOT, '01_pdf_uploads')
PARSED_IMAGES_FOLDER = os.path.join(settings.MEDIA_ROOT, '02_img_results')
CROPPED_IMAGES_FOLDER = os.path.join(settings.MEDIA_ROOT, '03_cropped_images')
EDITED_IMAGES_FOLDER = os.path.join(settings.MEDIA_ROOT, '04_edited_cropped_images')

def create_initial_files():

    if not os.path.exists(UPLOAD_PDF_FOLDER):
        os.makedirs(UPLOAD_PDF_FOLDER)
    if not os.path.exists(PARSED_IMAGES_FOLDER):
        os.makedirs(PARSED_IMAGES_FOLDER)
    if not os.path.exists(CROPPED_IMAGES_FOLDER):
        os.makedirs(CROPPED_IMAGES_FOLDER)
    if not os.path.exists(EDITED_IMAGES_FOLDER):
        os.makedirs(EDITED_IMAGES_FOLDER)

class IndexView(TemplateView):

    template_name = "index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        create_initial_files()

        ctx = super().get_context_data(**kwargs)
        ctx['form'] = IndexForm()
        return ctx

    def post(self,request, *args, **kwargs):
        
        form = IndexForm(request.POST, request.FILES)
        if not form.is_valid():
            return redirect('index')     
        
        file = form.cleaned_data['base_form_upload']
        file_name = f"{time.strftime('%Y%m%d-%H%M%S')}_{file.name}"
        file_pdf_path = os.path.join(UPLOAD_PDF_FOLDER, file_name)

        with open(file_pdf_path, 'wb') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
                
        file_jpeg_name = file_name.replace('.pdf','.jpg')
        file_jpeg_path = os.path.join(PARSED_IMAGES_FOLDER, file_jpeg_name)

        PDFConverter.convert_to_jpg(pdf_path=file_pdf_path, 
                            result_path=file_jpeg_path)
        

        handler = ImageHandler(base_image_path=file_jpeg_path)
        handler.cropp_image()
        handler.save_cropped_image(os.path.join(CROPPED_IMAGES_FOLDER, file_jpeg_name))
        handler.save_cropped_image(os.path.join(EDITED_IMAGES_FOLDER, file_jpeg_name)) 
    
        return redirect(reverse('base_configuration_view', kwargs={'image_name':file_jpeg_name}))
        
class BaseConfigurationView(TemplateView):

    template_name = "base_configuration.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx =  super().get_context_data(**kwargs)
        ctx['image_name'] = kwargs['image_name']
        ctx['image_path'] = os.path.join(settings.MEDIA_URL, '04_edited_cropped_images', kwargs['image_name'])
        ctx['form'] = ConfigurationForm(self.request.POST or None)
        return ctx

def set_marker(request,image_name):
    handler = ImageHandler(cropped_image_path=os.path.join(CROPPED_IMAGES_FOLDER, image_name))
    handler.save_cropped_image(path=os.path.join(EDITED_IMAGES_FOLDER, image_name))
    positions = handler.configure_initial_positions(path=os.path.join(EDITED_IMAGES_FOLDER, image_name))
    Config.reset()
    Config.instance().set_template_size(template_path=os.path.join(EDITED_IMAGES_FOLDER, image_name))
    Config.instance().set_initial_marker(positions)
    if positions:
        return JsonResponse({'positions':positions})
    return JsonResponse({})
