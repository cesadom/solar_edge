from django.contrib import admin
from .models import WeatherForecast, WeatherForecastDayHour

admin.site.register(WeatherForecast)
admin.site.register(WeatherForecastDayHour)
