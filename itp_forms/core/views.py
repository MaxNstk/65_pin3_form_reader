import time
from typing import Any
import cv2
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt

from itp_forms.core.forms import AnswersForm, ConfigurationForm, IndexForm
import os
from python.config import Config
from python.image_handler import ImageHandler

from python.pdf_converter import PDFConverter

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
    Config.instance().set_template_size(template_path=os.path.join(CROPPED_IMAGES_FOLDER, image_name))
    Config.instance().set_initial_marker(positions)
    Config.instance().draw_positions(os.path.join(EDITED_IMAGES_FOLDER, image_name))
    
    if positions:
        return JsonResponse({'positions':positions})
    return JsonResponse({})


@csrf_exempt
def update_image(request, image_name):
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
    ImageHandler(cropped_image_path=os.path.join(CROPPED_IMAGES_FOLDER, image_name)
                 ).save_cropped_image(os.path.join(EDITED_IMAGES_FOLDER, image_name))


@csrf_exempt
def interpret_answers_view(request):
    form = AnswersForm(request.POST or None, request.FILES or None)
    if request.method == 'GET':
        return render(request, 'interpret_view.html', {'form':form})
    
    if not form.is_valid():
        return form.invalid()     
        
    file = form.cleaned_data['file']
    file_name = f"{time.strftime('%Y%m%d-%H%M%S')}_{file.name}"
    file_pdf_path = os.path.join(PDF_ANSWERS_FOLDER, file_name)

    with open(file_pdf_path, 'wb') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    destination_folder = os.path.join(IMAGES_ANSWERS_FOLDER, file_name.replace('.pdf', ''))
    os.makedirs(destination_folder)
    PDFConverter.convert_to_pdf_massive(
        pdf_path=file_pdf_path, 
        folder=destination_folder
    )
    for page in os.listdir(destination_folder):
        file = os.path.join(destination_folder, page)    
        image = cv2.imread(file)

        w = Config.instance().cell_size_x_px
        h = Config.instance().cell_size_y_px
        x = Config.instance().grouping_1_x1
        y = Config.instance().grouping_1_y1
        
        roi = image[y:y+h, x:x+w]

        # Calculate the mean color within the ROI
        mean_color = cv2.mean(roi)

        # Check if the mean color is close to gray or black
        # You can adjust the threshold values as needed
        gray_threshold = 100  # Adjust this threshold for gray
        black_threshold = 20  # Adjust this threshold for black

        if mean_color[0] <= black_threshold:
            print("The ROI is filled with black.")
        elif mean_color[0] <= gray_threshold:
            print("The ROI is filled with gray.")
        else:
            print("The ROI is neither black nor gray.")

        # Display the ROI and its mean color (for visualization purposes)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Draw a green rectangle around the ROI
        cv2.imshow("Image with ROI", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
