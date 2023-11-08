import time
from typing import Any
import cv2
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from itp_forms.core.answers_interpreter import AnswersInterpreter
from itp_forms.core.config import Config
import os
from django.http import FileResponse

from itp_forms.core.forms import AnswersForm, ConfigurationForm, IndexForm
from itp_forms.core.image_handler import ImageHandler

from itp_forms.core.pdf_converter import PDFConverter

UPLOAD_PDF_FOLDER = os.path.join(settings.MEDIA_ROOT, '01_pdf_uploads')
PARSED_IMAGES_FOLDER = os.path.join(settings.MEDIA_ROOT, '02_img_results')
CROPPED_IMAGES_FOLDER = os.path.join(settings.MEDIA_ROOT, '03_cropped_images')
EDITED_IMAGES_FOLDER = os.path.join(settings.MEDIA_ROOT, '04_edited_cropped_images')
PDF_ANSWERS_FOLDER = os.path.join(settings.MEDIA_ROOT, '05_pdf_answers_folder')
IMAGES_ANSWERS_FOLDER = os.path.join(settings.MEDIA_ROOT, '06_images_answers_folder')

def create_initial_files():

    if not os.path.exists(UPLOAD_PDF_FOLDER):
        os.makedirs(UPLOAD_PDF_FOLDER)
    if not os.path.exists(PARSED_IMAGES_FOLDER):
        os.makedirs(PARSED_IMAGES_FOLDER)
    if not os.path.exists(CROPPED_IMAGES_FOLDER):
        os.makedirs(CROPPED_IMAGES_FOLDER)
    if not os.path.exists(EDITED_IMAGES_FOLDER):
        os.makedirs(EDITED_IMAGES_FOLDER)
    if not os.path.exists(PDF_ANSWERS_FOLDER):
        os.makedirs(PDF_ANSWERS_FOLDER)
    if not os.path.exists(IMAGES_ANSWERS_FOLDER):
        os.makedirs(IMAGES_ANSWERS_FOLDER)


class IndexView(TemplateView):

    template_name = "index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        create_initial_files()

        ctx = super().get_context_data(**kwargs)
        ctx['form'] = IndexForm()
        return ctx

    def post(self,request, *args, **kwargs):
        create_initial_files()
        
        form = IndexForm(request.POST, request.FILES)
        if not form.is_valid():
            return redirect('index')     
        
        if form.cleaned_data.get('json_config_upload'):
            Config.from_json(form.cleaned_data.get('json_config_upload'))
            return redirect('render_answers')
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
        create_initial_files()
        ctx =  super().get_context_data(**kwargs)
        ctx['image_name'] = kwargs['image_name']
        ctx['image_path'] = os.path.join(settings.MEDIA_URL, '04_edited_cropped_images', kwargs['image_name'])
        ctx['form'] = ConfigurationForm(self.request.POST or None)
        return ctx

def set_marker(request,image_name,marker_id):
    create_initial_files()
    handler = ImageHandler(cropped_image_path=os.path.join(CROPPED_IMAGES_FOLDER, image_name))
    handler.save_cropped_image(path=os.path.join(EDITED_IMAGES_FOLDER, image_name))

    if marker_id == 1:
        Config.reset()
        positions = handler.configure_initial_positions(path=os.path.join(EDITED_IMAGES_FOLDER, image_name))
        Config.instance().set_template_size(template_path=os.path.join(CROPPED_IMAGES_FOLDER, image_name))
        Config.instance().set_initial_marker(positions)
    else:
        positions = handler.configure_positions(path=os.path.join(EDITED_IMAGES_FOLDER, image_name))
        setattr(Config.instance(),f'grouping_{marker_id}_x1', positions[0]) 
        setattr(Config.instance(),f'grouping_{marker_id}_y1', positions[1]) 
        
    Config.instance().draw_positions(os.path.join(EDITED_IMAGES_FOLDER, image_name))
    
    if positions:
        return JsonResponse({'positions':positions})
    return JsonResponse({})


@csrf_exempt
def update_image(request, image_name):
    create_initial_files()
    config = Config.instance()
    config.column_amount = int(request.POST.get('column_amount'))
    config.y_space_between_cells = int(request.POST.get('y_space_between_cells'))
    config.x_space_between_cells = int(request.POST.get('x_space_between_cells'))

    try: config.grouping_1_row_amount = int(request.POST.get('first_group_row_amount', None))
    except: config.grouping_1_row_amount = None
    try: config.grouping_2_row_amount = int(request.POST.get('second_group_row_amount', None))
    except: config.grouping_2_row_amount = None
    try: config.grouping_3_row_amount = int(request.POST.get('third_group_row_amount', None))
    except: config.grouping_3_row_amount = None
    try: config.grouping_4_row_amount = int(request.POST.get('fourth_group_row_amount', None))
    except: config.grouping_4_row_amount = None
    
    reset_edited_image(image_name)  
    config.draw_positions(os.path.join(EDITED_IMAGES_FOLDER, image_name))
    return JsonResponse({})


def reset_edited_image(image_name):
    create_initial_files()
    ImageHandler(cropped_image_path=os.path.join(CROPPED_IMAGES_FOLDER, image_name)
                 ).save_cropped_image(os.path.join(EDITED_IMAGES_FOLDER, image_name))


@csrf_exempt
def interpret_answers_view(request):
    create_initial_files()

    if Config.is_empty():
        return redirect('index')   
    
    form = AnswersForm(request.POST or None, request.FILES or None)
    if request.method == 'GET':
        return render(request, 'results_form_upload_view.html', {'form':form})
    
    if not form.is_valid():
        return form.invalid()    

    Config.instance().fill_precentage_to_consider_filled = form.cleaned_data['fill_precentage_to_consider_filled']
    Config.instance().fill_precentage_to_consider_doubtful = form.cleaned_data['fill_precentage_to_consider_doubtful']
        
    file = form.cleaned_data['file']
    file_name = f"{time.strftime('%Y%m%d-%H%M%S')}_{file.name}"
    file_pdf_path = os.path.join(PDF_ANSWERS_FOLDER, file_name)

    with open(file_pdf_path, 'wb') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    

    jpg_list_folder = os.path.join(IMAGES_ANSWERS_FOLDER, file_name.replace('.pdf', ''))
    Config.instance().result_forms_path = jpg_list_folder
    os.makedirs(jpg_list_folder)
    PDFConverter.convert_to_pdf_massive(
        pdf_path=file_pdf_path, 
        folder=jpg_list_folder
    )
    
    interpreter = AnswersInterpreter(jpg_list_folder)
    try:
        return interpreter.interpret_answers()
    except Exception as e:
        print(e)
    return redirect('render_answers')
    

@csrf_exempt
def save_current_config(request):
    create_initial_files()
    Config.instance().to_json(os.path.join(settings.BASE_DIR, 'utils','configs'))
    return JsonResponse({})

def results_view(request):
    """ View que renderiza os resultados"""
    if Config.is_empty():
        return redirect('index')   
    
    # manda as questões ordenadas por contexto
    return render(request, 'final_results.html', {'pages_infos': 
            dict(sorted(Config.instance().question_results.items()))
        })

def get_result(self):
    return FileResponse(open(Config.instance().results_path, 'rb'))

def get_form(self, page):
    return FileResponse(open(os.path.join(Config.instance().result_forms_path, f'p{page}.jpeg'), 'rb'))