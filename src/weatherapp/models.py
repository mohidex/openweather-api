from typing import Any
from dataclasses import dataclass
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy


DIRECTIONS = {
    (0, 45): _('North'),
    (45, 135): _('East'),
    (135, 225): _('South'),
    (225, 315): _('West'),
    (315, 360): _('North'),
}
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
    wind_direction: str
    description: str

    @classmethod
    def from_openweather_response(cls, json_data: dict[str, Any]):
        """Create a WeatherReport instance from OpenWeatherMap API response."""

        data, is_valid = cls._validate_data(json_data)
        if not is_valid:
            raise ValueError('Response got from source is not valid.')
        return cls(**data)

    def __post_init__(self):
        """Post-initialization steps."""

        self.wind_direction = self._get_cardinal_direction(int(self.wind_direction))

    @staticmethod
    def _validate_data(json_data: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        """Validate and extract relevant data from the OpenWeatherMap API response."""

        # Check if all required fields are present in json_data
        if not all(key in json_data for key in REQUIRED_FIELDS):
            return {}, False

        # Check if 'main', 'wind', and 'weather' fields are dictionaries
        if not all(isinstance(json_data[key], dict) for key in DICT_FIELDS):
            return {}, False

        # Extract individual dictionaries and handle potential null values
        main_dict, wind_dict = json_data['main'], json_data['wind']
        weathers = json_data.get('weather')
        description_str = weathers[0].get('description') if isinstance(weathers, list) else ''

        # Create a validated_data dictionary with extracted values
        validated_data = {
            'city': json_data['name'],
            'temperature': main_dict.get('temp'),
            'min_temperature': main_dict.get('temp_min'),
            'max_temperature': main_dict.get('temp_max'),
            'humidity': main_dict.get('humidity'),
            'pressure': main_dict.get('pressure'),
            'wind_speed': wind_dict.get('speed'),
            'wind_direction': wind_dict.get('deg'),
            'description': description_str
        }
        return validated_data, True

    @staticmethod
    def _get_cardinal_direction(degrees: int) -> str:
        """Get cardinal direction based on degrees."""

        for angle_range, direction in DIRECTIONS.items():
            if angle_range[0] <= degrees <= angle_range[1]:
                return direction
        return _('Unknown')

    def to_dict(self) -> dict[str, Any]:
        """Serialize WeatherReport object to a dictionary."""
        return {
            'city': self.city,
            'temperature': {
                'current': self.temperature,
                'minimum': self.min_temperature,
                'maximum': self.max_temperature,
            },
            'humidity': self.humidity,
            'pressure': self.pressure,
            'wind': {
                'speed': self.wind_speed,
                'direction': _(self.wind_direction),
            },
            'description': self.description,
        }
