from django.contrib import admin
from .models import WeatherData, City


class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ('city', 'temperature', 'humidity', 'pressure', 'wind_speed', 'wind_direction', 'timestamp')
    search_fields = ('city',)
    list_filter = ('city', 'timestamp')


class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'latitude', 'longitude', 'active', 'last_update')
    search_fields = ('name', 'country')
    list_filter = ('country',)


admin.site.register(WeatherData, WeatherDataAdmin)
admin.site.register(City, CityAdmin)
