from typing import Any
from dataclasses import dataclass


DIRECTIONS = {
    (0, 360): 'North',
    (1, 89): 'North-East',
    (90, 179): 'South-East',
    (180, 269): 'South',
    (270, 359): 'North-West',
}


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
    def from_openweather_response(cls, json_data):
        """Create a WeatherReport instance from OpenWeatherMap API response."""

        try:
            city = json_data['name']
            temperature = float(json_data['main']['temp'])
            min_temperature = float(json_data['main']['temp_min'])
            max_temperature = float(json_data['main']['temp_max'])
            humidity = int(json_data['main']['humidity'])
            pressure = int(json_data['main']['pressure'])
            wind_speed = float(json_data['wind']['speed'])
            wind_direction = str(json_data['wind']['deg'])
            description = json_data['weather'][0]['description']

            return cls(
                city=city,
                temperature=temperature,
                min_temperature=min_temperature,
                max_temperature=max_temperature,
                humidity=humidity,
                pressure=pressure,
                wind_speed=wind_speed,
                wind_direction=wind_direction,
                description=description,
            )
        except (KeyError, IndexError, TypeError) as e:
            # Handle failures, log the error, or raise a custom exception
            print(f'Error creating WeatherReport from JSON: {e}')
            return None

    @staticmethod
    def _get_cardinal_direction(degrees: int) -> str:
        """Get cardinal direction based on degrees."""

        for angle_range, direction in DIRECTIONS.items():
            if angle_range[0] <= degrees <= angle_range[1]:
                return direction
        return 'Unknown'

    def __post_init__(self):
        """Post-initialization steps."""

        self.wind_direction = self._get_cardinal_direction(int(self.wind_direction))

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
                'direction': self.wind_direction,
            },
            'description': self.description,
        }
