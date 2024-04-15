from typing import Any
from dataclasses import dataclass
from .exceptions import InvalidResponse

REQUIRED_FIELDS = ['name', 'main', 'wind']
DICT_FIELDS = ['main', 'wind']


@dataclass
class WeatherReport:
    """Represents a weather report."""
    city: str
    temperature: float
    min_temperature: float
    max_temperature: float
    humidity: int
    pressure: int
    wind_speed: float
    wind_degree: int

    @classmethod
    def from_json_response(cls, json_data: dict[str, Any]):
        """Create a WeatherReport instance from OpenWeatherMap API response."""

        if not (is_valid := cls.is_valid(json_data)):
            raise InvalidResponse('Response got from source is not valid.')

        # Extract individual dictionaries and handle potential null values
        main_dict, wind_dict = json_data['main'], json_data['wind']

        # Create a validated_data dictionary with extracted values
        data = {
            'city': json_data['name'],
            'temperature': main_dict.get('temp'),
            'min_temperature': main_dict.get('temp_min'),
            'max_temperature': main_dict.get('temp_max'),
            'humidity': main_dict.get('humidity'),
            'pressure': main_dict.get('pressure'),
            'wind_speed': wind_dict.get('speed'),
            'wind_degree': wind_dict.get('deg'),
        }

        return cls(**data)

    @staticmethod
    def is_valid(json_data: dict[str, Any]) -> bool:
        """Validate data that got from the OpenWeatherMap API response."""

        # Check if all required fields are present in json_data
        if not all(key in json_data for key in REQUIRED_FIELDS):
            return False

        # Check if 'main', and 'wind' fields are dictionaries
        if not all(isinstance(json_data[key], dict) for key in DICT_FIELDS):
            return False

        return True
