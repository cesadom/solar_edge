from django.contrib import admin
from .models import WeatherForecast, WeatherForecastDayHour, WeatherActualMeasurement

admin.site.register(WeatherForecast)
admin.site.register(WeatherForecastDayHour)
admin.site.register(WeatherActualMeasurement)
