from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from .swagger_view import swagger_json


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('weatherapp.urls')),
    path('swagger.json/', swagger_json, name='schema-url'),
    path('docs/', TemplateView.as_view(template_name='swagger-ui.html'), name='swagger-ui')
]
