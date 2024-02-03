from django.urls import path
from .views import WeatherApiView

urlpatterns = [
    path('weather/', WeatherApiView.as_view(), name='weather-api'),
]
