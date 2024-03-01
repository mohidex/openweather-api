import aiohttp
import asyncio
from typing import Optional, Any, Never
from .items import WeatherReport

from .exceptions import UnauthorizedError, NotFoundError, TooManyRequestError, UnexpectedError


class OpenWeatherAPIClient:
    """Asynchronous client for the OpenWeatherMap API.

    Attributes:
        api_key (str): The API key for accessing the OpenWeatherMap API.
        unit (str): The unit system for temperature values (default is 'metric').
        version (str): The API version to use (default is '2.5').
        endpoint (str): The base endpoint URL for weather data.
    """

    BASE_URL = 'https://api.openweathermap.org/data'

    def __init__(
            self,
            api_key: str,
            unit: Optional[str] = 'metric',
            version: Optional[str] = '2.5'
    ):
        """Initialize the OpenWeatherAPIClient."""
        self.api_key = api_key
        self.unit = unit
        self.version = version
        self.endpoint = f'{self.BASE_URL}/{self.version}/weather'

    @staticmethod
    async def _raise_for_failed_requests(response: aiohttp.ClientResponse) -> Never:
        """Raise expected error for failed api calls"""
        match response.status:
            case 401:
                raise UnauthorizedError('Please provide a valid access token')
            case 404:
                raise NotFoundError('No report found for your queries')
            case 429:
                raise TooManyRequestError('You are making too many requests, please try again later')
            case _:
                raise UnexpectedError('Something unexpected happens, please contact the source')

    async def _make_request(self, params: dict[str: Any]) -> WeatherReport:
        """Make an asynchronous request to the OpenWeatherMap API."""

        params.update({
            'units': self.unit,
            'appid': self.api_key,
        })
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.endpoint, params=params) as response:
                    if response.status == 200:
                        response_json = await response.json()
                        return WeatherReport.from_json_response(response_json)
            except (asyncio.TimeoutError, aiohttp.ClientConnectionError):
                raise UnexpectedError('Something unexpected happens, please check your network')

    async def get_weather_by_city(self, city_name: str, lang: Optional[str] = 'en') -> WeatherReport:
        """Get weather data for a city by making an asynchronous API request."""

        params = {'q': city_name, 'lang': lang}
        return await self._make_request(params)

    async def get_weather_by_lat_lon(self, lat: float, lon: float) -> WeatherReport:
        """Get weather data for a location by latitude and longitude."""

        params = {'lat': lat, 'lon': lon}
        return await self._make_request(params)

    async def get_weather(self, **kwargs) -> WeatherReport:
        """Get weather data by any query parameter."""

        return await self._make_request(kwargs)
