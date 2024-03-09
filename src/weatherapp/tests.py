import logging
from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache
from .models import WeatherData


SUCCESS_RESPONSE = {
    'status': 'success',
    'data': {
        'city': 'testcity2',
        'temperature': {'current': '298.48', 'minimum': '297.56', 'maximum': '300.05'},
        'humidity': 64, 'pressure': 1015, 'wind': {'speed': '0.62', 'direction': 'North'},
    }
}


class WeatherApiViewTest(TestCase):
    def setUp(self) -> None:
        self.url = reverse('weather-api')
        WeatherData.objects.create(
            city='TestCity1'.lower(), temperature=298.48, min_temperature=297.56, max_temperature=300.05,
            humidity=64, pressure=1015, wind_speed=0.62, wind_degree=0, wind_direction='North'
        )
        WeatherData.objects.create(
            city='TestCity2'.lower(), temperature=298.48, min_temperature=297.56, max_temperature=300.05,
            humidity=64, pressure=1015, wind_speed=0.62, wind_degree=0, wind_direction='North'
        )
        logging.disable(logging.CRITICAL)

    def test_weather_api_view_returns_200(self):
        city = 'TestCity1'
        lang = 'en-us'
        response = self.client.get(self.url, {'city': city}, HTTP_ACCEPT_LANGUAGE=lang)
        self.assertEqual(response.status_code, 200)

    def test_weather_api_view_response_success(self):
        city = 'TestCity2'
        response = self.client.get(self.url, {'city': city})
        self.assertEqual(response.json(), SUCCESS_RESPONSE)

    def test_weather_api_view_returns_400_no_city(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)

    def test_weather_api_view_response_no_city(self):
        response_json = self.client.get(self.url).json()
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'Bad Request: No city provided.')

    def test_weather_api_view_response_no_city_in_de(self):
        response_json = self.client.get(self.url, HTTP_ACCEPT_LANGUAGE='de').json()
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'Schlechte Anfrage: Keine Stadt angegeben.')

    def test_weather_api_view_response_no_city_in_bn(self):
        response_json = self.client.get(self.url, HTTP_ACCEPT_LANGUAGE='bn').json()
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'খারাপ অনুরোধ: কোন শহর প্রদান করা হয়েছে.')

    def test_weather_api_view_returns_404(self):
        city = 'NoCity'
        response = self.client.get(self.url, {'city': city})
        self.assertEqual(response.status_code, 404)

    def test_weather_api_view_not_found_response(self):
        city = 'NoCity'
        response_json = self.client.get(self.url, {'city': city}).json()
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'Not Found: No city found with the provided query.')

    def test_weather_api_view_not_found_response_de(self):
        city = 'NoCity'
        response_json = self.client.get(self.url, {'city': city}, HTTP_ACCEPT_LANGUAGE='de').json()
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'Nicht gefunden: Mit der bereitgestellten Abfrage wurde keine Stadt gefunden.')

    def tearDown(self) -> None:
        logging.disable(logging.NOTSET)
        cache.delete('testcity1')
        cache.delete('testcity2')
