
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from itp_forms.core.views import BaseConfigurationView, IndexView, interpret_answers_view, save_current_config, set_marker, update_image

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('base_configuration_view/<str:image_name>/', BaseConfigurationView.as_view(), name='base_configuration_view'),
    path('set_marker/<str:image_name>/', set_marker, name='set_marker'),
    path('update_image/<str:image_name>/', update_image, name='update_image'),
    path('render_answers/', interpret_answers_view, name='render_answers'),
    path('save_config/', save_current_config, name='save_config'),
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
