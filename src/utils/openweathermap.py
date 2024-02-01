import aiohttp
import asyncio
from typing import Optional, Any


class UnauthorizedError(Exception):
    """Exception raised when the API request is unauthorized."""
    pass


class NotFoundError(Exception):
    """Exception raised when the requested resource is not found."""
    pass


class TooManyRequestError(Exception):
    """Exception raised when there are too many requests in a given time frame."""
    pass


class UnexpectedError(Exception):
    """Exception raised when an unexpected error occurs during the API request."""
    pass


class OpenWeatherAPIClient:
    """Asynchronous client for the OpenWeatherMap API.

    Attributes:
        api_key (str): The API key for accessing the OpenWeatherMap API.
        unit (str): The unit system for temperature values (default is 'metric').
        lang (str): The language for the API response (default is 'en').
    """

    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(
            self,
            api_key: str,
            unit: Optional[str] = None,
            lang: Optional[str] = None
    ):
        """Initialize the OpenWeatherAPIClient."""
        self.api_key = api_key
        self.unit = unit or 'metric'
        self.lang = lang or 'en'

    async def _make_request(self, params: dict[str: Any]) -> dict[str, Any]:
        """Make an asynchronous request to the OpenWeatherMap API."""

        params.update({
            'lang': self.lang,
            'units': self.unit,
            'appid': self.api_key,
        })
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.BASE_URL, params=params) as response:
                    match response.status:
                        case 200:
                            return await response.json()
                        case 401:
                            raise UnauthorizedError('Please provide a valid access token')
                        case 404:
                            raise NotFoundError('No report found for your queries')
                        case 429:
                            raise TooManyRequestError('You are making too many requests, please try again later')
                        case _:
                            raise UnexpectedError('Something unexpected happens, please contact the source')
            except (asyncio.TimeoutError, aiohttp.ClientConnectionError):
                raise UnexpectedError('Something unexpected happens, please check your network')

    async def get_weather_by_city(self, city_name: str) -> dict[str, Any]:
        """Get weather data for a city by making an asynchronous API request."""

        params = {'q': city_name}
        return await self._make_request(params)

    async def get_weather_by_lat_lon(self, lat: float, lon: float) -> dict[str, Any]:
        """Get weather data for a location by latitude and longitude."""

        params = {
            'lat': lat,
            'lon': lon,
        }
        return await self._make_request(params)
