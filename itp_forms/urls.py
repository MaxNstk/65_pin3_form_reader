
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from itp_forms.core.views import BaseConfigurationView, IndexView, get_form, get_interpreted_form, get_result, interpret_answers_view, results_view, save_current_config, set_marker, update_image

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('base_configuration_view/<str:image_name>/', BaseConfigurationView.as_view(), name='base_configuration_view'),
    path('set_marker/<str:image_name>/<int:marker_id>', set_marker, name='set_marker'),
    path('update_image/<str:image_name>/', update_image, name='update_image'),
    path('render_answers/', interpret_answers_view, name='render_answers'),
    path('save_config/', save_current_config, name='save_config'),
    path('results_view/', results_view, name='results_view'),
    path('get_result/', get_result, name='get_result'),
    path('get_form/<str:page>', get_form, name='get_form'),  
    path('get_interpreted_form/<str:page>', get_interpreted_form, name='get_interpreted_form'),  

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
