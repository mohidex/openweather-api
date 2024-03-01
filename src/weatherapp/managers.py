from django.db import models
from asgiref.sync import sync_to_async


class WeatherDataManager(models.Manager):
    def get_latest(self, city):
        return self.filter(city=city).alatest('timestamp')

    def all_by_city(self, city):
        return self.filter(city=city).order_by('-timestamp')

    async def aget_latest(self, city):
        return await sync_to_async(self.get_latest)(city=city)

    async def aall_by_city(self, city):
        return await sync_to_async(self.all_by_city)(city=city)
