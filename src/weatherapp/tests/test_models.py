from django.test import TestCase
from ..models import WeatherReport


class TestWeatherReport(TestCase):
    def setUp(self):
        # Mock OpenWeatherMap API response for testing
        self.mock_json_data = {
            "coord": {"lon": 10.99, "lat": 44.34},
            "weather": [{"id": 501, "main": "Rain", "description": "moderate rain", "icon": "10d"}],
            "base": "stations",
            "main": {"temp": 298.48, "feels_like": 298.74, "temp_min": 297.56, "temp_max": 300.05, "pressure": 1015, "humidity": 64, "sea_level": 1015, "grnd_level": 933},
            "visibility": 10000,
            "wind": {"speed": 0.62, "deg": 349, "gust": 1.18},
            "rain": {"1h": 3.16},
            "clouds": {"all": 100},
            "dt": 1661870592,
            "sys": {"type": 2, "id": 2075663, "country": "IT", "sunrise": 1661834187, "sunset": 1661882248},
            "timezone": 7200,
            "id": 3163858,
            "name": "Zocca",
            "cod": 200,
        }

    def test_from_openweather_response_success(self):
        # Test successful creation of WeatherReport from API response
        weather_report = WeatherReport.from_openweather_response(self.mock_json_data)

        self.assertIsNotNone(weather_report)
        self.assertEqual(weather_report.city, "Zocca")
        self.assertEqual(weather_report.temperature, 298.48)
        self.assertEqual(weather_report.min_temperature, 297.56)
        self.assertEqual(weather_report.max_temperature, 300.05)
        self.assertEqual(weather_report.humidity, 64)
        self.assertEqual(weather_report.pressure, 1015)
        self.assertEqual(weather_report.wind_speed, 0.62)
        self.assertEqual(weather_report.wind_direction, "North")
        self.assertEqual(weather_report.description, "moderate rain")

    def test_to_dict(self):
        # Test serialization to dictionary
        weather_report = WeatherReport.from_openweather_response(self.mock_json_data)
        serialized_data = weather_report.to_dict()

        expected_data = {
            "city": "Zocca",
            "temperature": {"current": 298.48, "minimum": 297.56, "maximum": 300.05},
            "humidity": 64,
            "pressure": 1015,
            "wind": {"speed": 0.62, "direction": "North"},
            "description": "moderate rain",
        }

        self.assertEqual(serialized_data, expected_data)

    def test_from_openweather_response_missing_data(self):
        # Test failure when required data is missing in the API response
        incomplete_json_data = {"coord": {"lat": 44.34}}  # Missing "name" key
        weather_report = WeatherReport.from_openweather_response(incomplete_json_data)
        self.assertIsNone(weather_report)

    def test_from_openweather_response_invalid_data(self):
        # Test failure when data types are incorrect in the API response
        invalid_json_data = {"name": "Zocca", "main": {"temp": "invalid"}}  # "temp" should be a float
        weather_report = WeatherReport.from_openweather_response(invalid_json_data)
        self.assertIsNone(weather_report)

    def test_from_openweather_response_unexpected_structure(self):
        # Test failure when the API response structure is unexpected
        unexpected_json_data = {"message": "Unexpected structure"}  # Missing required keys
        weather_report = WeatherReport.from_openweather_response(unexpected_json_data)
        self.assertIsNone(weather_report)
