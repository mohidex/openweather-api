from typing import Any
from django.db import models
from openweather.items import WeatherReport
from .managers import WeatherDataManager
from django.utils.translation import gettext as _


class WeatherData(models.Model):
    city = models.CharField(max_length=100)
    temperature = models.DecimalField(max_digits=5, decimal_places=2)
    min_temperature = models.DecimalField(max_digits=5, decimal_places=2)
    max_temperature = models.DecimalField(max_digits=5, decimal_places=2)
    humidity = models.PositiveIntegerField()
    pressure = models.IntegerField()
    wind_speed = models.DecimalField(max_digits=5, decimal_places=2)
    wind_degree = models.IntegerField()
    wind_direction = models.CharField(max_length=20, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = WeatherDataManager()

    class Meta:
        indexes = [
            models.Index(fields=['city', '-timestamp'])
        ]

    def __str__(self):
        return f'{self.city} - {self.temperature}'

    @classmethod
    def from_weather_report(cls, weather_report: WeatherReport):
        return cls(
            **vars(weather_report)
        )

    def get_wind_cardinal_direction(self) -> str:
        """Get cardinal direction based on degrees."""

        directions = {
            (0, 45): _('North'),
            (45, 135): _('East'),
            (135, 225): _('South'),
            (225, 315): _('West'),
            (315, 360): _('North'),
        }
        for angle_range, direction in directions.items():
            if angle_range[0] <= self.wind_degree <= angle_range[1]:
                return direction
        return _('Unknown')

    def save(self, *args, **kwargs):
        self.wind_direction = self.get_wind_cardinal_direction()
        super().save(*args, **kwargs)

    def to_dict(self) -> dict[str, Any]:
        """Serialize WeatherData object to a dictionary."""
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
                'direction': _(self.wind_direction)
            }
        }
