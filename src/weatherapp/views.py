import logging
from typing import Any, Optional
from django.core.cache import cache
from django.views.generic import View
from django.http import JsonResponse
from django.utils.translation import gettext as _

from .models import WeatherData

logger = logging.getLogger(__name__)


class WeatherApiView(View):
    """
    API View to retrieve weather information for a given city.
    This view supports GET requests with the 'city' parameter in the query string.
    """

    error_messages: dict[int: str] = {
        400: _('Bad Request: No city provided.'),
        404: _('Not Found: No city found with the provided query.'),
    }
    weather_report: Optional[dict[str, Any]] = None

    async def _get_weather_report(self, city: str) -> None:
        """Asynchronously fetch weather information for the given city."""
        city_name = city.lower()

        # Check if the response is cached; if so, return it from the cache
        if (response := await cache.aget(city_name)) and response:
            self.weather_report = response
            return

        try:
            weather_data: WeatherData = await WeatherData.objects.aget_latest(city=city_name)
        except WeatherData.DoesNotExist:
            return
        wr_json = weather_data.to_dict()

        # Cache the response for future use
        await cache.aset(city.lower(), wr_json)
        self.weather_report = wr_json

    async def get(self, request):
        """Handle GET requests to retrieve weather information for a given city."""

        if (city := request.GET.get('city')) and city:
            await self._get_weather_report(city=city)
        else:
            err_response = {'status': 'error', 'message': _(self.error_messages[400])}
            return JsonResponse(err_response, status=400)

        if not self.weather_report:
            err_response = {'status': 'error', 'message': _(self.error_messages[404])}
            return JsonResponse(err_response, status=404)

        success_response = {'status': 'success', 'data': self.weather_report}
        return JsonResponse(success_response, status=200)
