import asyncio
from django.conf import settings
from django.core.management.base import BaseCommand
from openweather.client import OpenWeatherAPIClient
from loader.weather_loader import WeatherLoader


class Command(BaseCommand):
    help = 'Populate the weather table by calling the OpenWeather API'
    wc = OpenWeatherAPIClient(api_key=settings.OPEN_WEATHER_API_KEY)
    wl = WeatherLoader(client=wc)

    def handle(self, *args, **options):
        asyncio.run(self.wl.run())
        self.stdout.write(self.style.SUCCESS('Successfully populated the weather table'))
