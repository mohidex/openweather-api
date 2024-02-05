import logging
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from django.core.cache import cache
from openweather.exceptions import UnauthorizedError, NotFoundError

from asgiref.sync import async_to_sync
from weatherapp.views import WeatherApiView
from .example_response import SOURCE_RESPONSE, SUCCESS_RESPONSE


class MockWeatherViewSync(WeatherApiView):
    """
    MockWeatherViewSync class is created to convert the WeatherApiView async view into a sync view.
    While some tests may not cover all aspects of async, they can still provide a reasonable level of confidence.
    """
    def get(self, requests):
        get_view = async_to_sync(super(MockWeatherViewSync, self).get)
        return get_view(requests)


class WeatherApiViewTest(TestCase):

    def setUp(self) -> None:
        from weatherapp.urls import urlpatterns
        urlpatterns[0].callback = MockWeatherViewSync.as_view()
        self.mock_response = SOURCE_RESPONSE
        self.url = reverse('weather-api')
        logging.disable(logging.CRITICAL)

    @patch('weatherapp.views.OpenWeatherAPIClient.get_weather_by_city')
    def test_weather_api_view_returns_200(self, mock_get_weather_by_city):
        city = 'TestCity1'
        lang = 'en-us'
        # Mock the response from OpenWeatherAPIClient
        mock_get_weather_by_city.return_value = self.mock_response
        response = self.client.get(self.url, {'city': city}, HTTP_ACCEPT_LANGUAGE=lang)
        self.assertEqual(response.status_code, 200)

    @patch('weatherapp.views.OpenWeatherAPIClient.get_weather_by_city')
    def test_weather_api_view_response_success(self, mock_get_weather_by_city):
        city = 'TestCity2'
        # Mock the response from OpenWeatherAPIClient
        mock_get_weather_by_city.return_value = self.mock_response
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

    @patch('weatherapp.views.OpenWeatherAPIClient.get_weather_by_city')
    def test_weather_api_view_returns_503(self, mock_get_weather_by_city):
        city = 'TestCity'
        # Mock the response from OpenWeatherAPIClient
        mock_get_weather_by_city.side_effect = UnauthorizedError("Some error message")
        response = self.client.get(self.url, {'city': city})
        self.assertEqual(response.status_code, 503)

    @patch('weatherapp.views.OpenWeatherAPIClient.get_weather_by_city')
    def test_weather_api_view_response_wrong_apikey(self, mock_get_weather_by_city):
        city = 'TestCity'
        # Mock the response from OpenWeatherAPIClient
        mock_get_weather_by_city.side_effect = UnauthorizedError("Some error message")
        response_json = self.client.get(self.url, {'city': city}).json()
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'],
                         'Service Unavailable: The service is currently unavailable. Please try again later.')

    @patch('weatherapp.views.OpenWeatherAPIClient.get_weather_by_city')
    def test_weather_api_view_response_wrong_apikey_in_de(self, mock_get_weather_by_city):
        city = 'TestCity'
        # Mock the response from OpenWeatherAPIClient
        mock_get_weather_by_city.side_effect = UnauthorizedError("Some error message")
        response_json = self.client.get(self.url, {'city': city}, HTTP_ACCEPT_LANGUAGE='de').json()
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'],
                         'Dienst nicht verfügbar: Der Dienst ist derzeit nicht verfügbar.'
                         ' Bitte versuchen Sie es später noch einmal.')

    @patch('weatherapp.views.OpenWeatherAPIClient.get_weather_by_city')
    def test_weather_api_view_returns_404(self, mock_get_weather_by_city):
        city = 'TestCity'
        # Mock the response from OpenWeatherAPIClient
        mock_get_weather_by_city.side_effect = NotFoundError("Some error message")
        response = self.client.get(self.url, {'city': city})
        self.assertEqual(response.status_code, 404)

    @patch('weatherapp.views.OpenWeatherAPIClient.get_weather_by_city')
    def test_weather_api_view_not_found_response(self, mock_get_weather_by_city):
        city = 'TestCity'
        # Mock the response from OpenWeatherAPIClient
        mock_get_weather_by_city.side_effect = NotFoundError("Some error message")
        response_json = self.client.get(self.url, {'city': city}).json()
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'Not Found: No city found with the provided query.')

    @patch('weatherapp.views.OpenWeatherAPIClient.get_weather_by_city')
    def test_weather_api_view_returns_200_with_cache(self, mock_get_weather_by_city):
        city = 'TestCity3'
        cache.set('testcity3:en', SUCCESS_RESPONSE)
        self.assertEqual(cache.get('testcity3:en'), SUCCESS_RESPONSE)
        response = self.client.get(self.url, {'city': city})
        mock_get_weather_by_city.assert_not_called()
        self.assertEqual(response.status_code, 200)

    @patch('weatherapp.views.OpenWeatherAPIClient.get_weather_by_city')
    def test_weather_api_view_returns_200_with_no_cache(self, mock_get_weather_by_city):
        city = 'TestCity4'
        # Mock the response from OpenWeatherAPIClient
        mock_get_weather_by_city.return_value = self.mock_response
        self.assertEqual(cache.get('testcity4:en'), None)
        response = self.client.get(self.url, {'city': city})
        mock_get_weather_by_city.assert_called_once_with(city_name=city, lang='en')
        self.assertEqual(cache.get('testcity4:en'), SUCCESS_RESPONSE)
        self.assertEqual(response.status_code, 200)

    def tearDown(self) -> None:
        logging.disable(logging.NOTSET)
        cache.delete('testcity1:en')
        cache.delete('testcity2:en')
        cache.delete('testcity3:en')
        cache.delete('testcity4:en')
