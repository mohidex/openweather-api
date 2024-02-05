import logging
from typing import Any
from django.conf import settings
from django.core.cache import cache
from django.views.generic import View
from django.http import JsonResponse
from django.utils.translation import gettext as _

from .models import WeatherReport
from openweather import OpenWeatherAPIClient
from openweather.exceptions import UnauthorizedError, UnexpectedError, TooManyRequestError, NotFoundError

logger = logging.getLogger(__name__)


class WeatherApiView(View):
    """
    API View to retrieve weather information for a given city.
    This view supports GET requests with the 'city' parameter in the query string.
    """

    wc = OpenWeatherAPIClient(api_key=settings.OPEN_WEATHER_API_KEY)
    error_messages = {
        400: _('Bad Request: No city provided.'),
        404: _('Not Found: No city found with the provided query.'),
        503: _('Service Unavailable: The service is currently unavailable. Please try again later.')
    }

    async def _get_weather_report(self, city: str, lang: str) -> tuple[int, dict[str, Any]]:
        """Asynchronously fetch weather information for the given city."""

        cache_key_expr = f'{city}:{lang}'.lower()

        # Check if the response is cached; if so, return it from the cache
        if (response := await cache.aget(cache_key_expr)) and response:
            return 200, response
        try:
            response = await self.wc.get_weather_by_city(city_name=city, lang=lang)

            # Process the API response and create a WeatherReport object
            wr = WeatherReport.from_openweather_response(response)
            wr_json = wr.to_dict()

            # Prepare a response for caching
            cached_response = {
                'status': 'success',
                'data': wr_json
            }

            # Cache the response for future use
            await cache.aset(cache_key_expr, cached_response)
            return 200, cached_response

        except ValueError as e:
            logging.error(f'Data Error: {str(e)}')
            return 400, {}

        except (UnauthorizedError, UnexpectedError, TooManyRequestError) as e:
            logging.error(f'Error from source: {str(e)}')
            return 503, {}

        except NotFoundError as e:
            logging.warning(f'Not found: {str(e)}')
            return 404, {}

    async def get(self, request):
        """Handle GET requests to retrieve weather information for a given city."""

        city = request.GET.get('city')
        lang = request.headers.get('Accept-Language', 'en-us').split('-')[0]

        # Check if 'city' is not provided in the query string; return a 400 Bad Request response
        if not city:
            err_response = {'status': 'error', 'message': _(self.error_messages[400])}
            return JsonResponse(err_response, status=400)

        status, response = await self._get_weather_report(city=city, lang=lang)
        if status == 200:
            return JsonResponse(response, status=status)

        err_response = {'status': 'error', 'message': _(self.error_messages[status])}
        return JsonResponse(err_response, status=status)
