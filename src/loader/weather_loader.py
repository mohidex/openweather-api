import asyncio
from typing import Optional
from weatherapp.models import City, WeatherData
from openweather.client import OpenWeatherAPIClient
from openweather.exceptions import (
    UnauthorizedError,
    TooManyRequestError,
    UnexpectedError,
    InvalidResponse,
    NotFoundError
)
from openweather.items import WeatherReport


class WeatherLoader:
    """
    Asynchronous loader for weather data from the OpenWeather API.
    attributes:
        openweather_client (OpenWeatherAPIClient): The client to use for the requests.
        cities (list[str]): A list of active cities to fetch weather data for.
        request_queue (asyncio.Queue): A queue to hold the requests for weather data.
        db_writer_queue (asyncio.Queue): A queue to hold the weather data to write to the database.
        is_circuit_breaker_open (bool): A flag to indicate if the circuit breaker is open.
    """

    def __init__(self, client: OpenWeatherAPIClient) -> None:
        self.openweather_client = client
        self.request_queue = asyncio.Queue()
        self.db_writer_queue = asyncio.Queue()
        self.is_circuit_breaker_open = False

    async def get_weather_by_city(self, city: str) -> Optional[WeatherReport]:
        """Asynchronously fetch weather data for a given city."""

        if self.is_circuit_breaker_open:
            return None
        try:
            return await self.openweather_client.get_weather_by_city(city)
        except TooManyRequestError:
            # retry again after 60 seconds
            await asyncio.sleep(60)
            return await self.get_weather_by_city(city)
        except (UnauthorizedError, UnexpectedError):
            self.is_circuit_breaker_open = True
            return None
        except (InvalidResponse, NotFoundError):
            return None

    async def load_weather_data(self) -> None:
        """Asynchronously load weather data for all active cities."""
        async for city in City.objects.filter(active=True):
            await self.request_queue.put(city.name)

    async def process_requests(self) -> None:
        """Asynchronously process requests from the queue."""
        while True:
            city = await self.request_queue.get()
            if city is None:
                break
            print(f'process_requests {city}')
            weather_report = await self.get_weather_by_city(city)
            if weather_report:
                await self.db_writer_queue.put(weather_report)
            self.request_queue.task_done()

    async def write_to_db(self) -> None:
        """Asynchronously write weather data to the database."""
        while True:
            weather_report = await self.db_writer_queue.get()
            if weather_report is None:
                break
            print(f'write_to_db {weather_report}')
            weather_data = WeatherData.from_weather_report(weather_report)
            await weather_data.asave()
            self.db_writer_queue.task_done()

    async def run(self) -> None:
        """Asynchronously run the weather loader."""
        await self.load_weather_data()

        api_tasks = []
        for _ in range(3):
            api_tasks.append(asyncio.create_task(self.process_requests()))
        await self.request_queue.join()

        db_tasks = []
        for _ in range(5):
            db_tasks.append(asyncio.create_task(self.write_to_db()))
        await self.db_writer_queue.join()

        for task in api_tasks:
            task.cancel()
        await asyncio.gather(*api_tasks, return_exceptions=True)

        for task in db_tasks:
            task.cancel()
        await asyncio.gather(*db_tasks, return_exceptions=True)

