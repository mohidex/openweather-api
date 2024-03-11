import asyncio
from django.core.management.base import BaseCommand
from weatherapp.models import City

from loader.city_loader import CityLoader


class Command(BaseCommand):
    help = 'Populate the database with cities from an Excel file'
    url = 'https://openweathermap.org/storage/app/media/cities_list.xlsx'
    override = False
    loader = CityLoader(url, override=override)

    def add_arguments(self, parser):
        parser.add_argument('--override', action='store_true', help='Override the existing data in the database')

    async def load_cities(self) -> None:
        async for city in self.loader.get_cities():
            city_name = city.name.lower()
            try:
                city = await City.objects.aget(name=city_name)
                if self.loader.override:
                    city.country = city.country
                    city.latitude = city.lat
                    city.longitude = city.lon
                    await city.asave()
            except City.DoesNotExist:
                await City.objects.acreate(
                    name=city_name,
                    country=city.country,
                    latitude=city.lat,
                    longitude=city.lon,
                )

    def handle(self, *args, **options):
        self.override = options['override']
        asyncio.run(self.load_cities())
        self.stdout.write(self.style.SUCCESS('Successfully populated the database with cities'))
