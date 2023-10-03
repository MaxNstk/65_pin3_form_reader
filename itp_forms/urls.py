"""
URL configuration for itp_forms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from itp_forms.core.views import BaseConfigurationView, IndexView, interpret_answers_view, set_marker, update_image

urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('base_configuration_view/<str:image_name>/', BaseConfigurationView.as_view(), name='base_configuration_view'),
    path('set_marker/<str:image_name>/', set_marker, name='set_marker'),
    path('update_image/<str:image_name>/', update_image, name='update_image'),
    path('render_answers/', interpret_answers_view, name='render_answers'),
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
