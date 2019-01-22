from django.db import models
from datetime import date, datetime

class WeatherForecast(models.Model):
    date = models.CharField(max_length=10)
    forecastDate = models.DateField(auto_now=False, auto_now_add=False, default=datetime.today().strftime('%Y-%m-%d'))
    sunHours = models.DecimalField(max_digits=3, decimal_places=1)
    autoForecastRate = models.PositiveIntegerField(default=None, blank=True, null=True)
    manualForecastRate = models.PositiveIntegerField(default=None, blank=True, null=True)
    
    def __str__(self):
        return self.date + " - sun hours: " + str(self.sunHours) + "h, forecasted at " + str(self.forecastDate)

class WeatherForecastDayHour(models.Model):
    time = models.PositiveIntegerField(default=None, blank=True, null=True)
    weatherForecast = models.ForeignKey(WeatherForecast, on_delete=models.CASCADE, blank=True, null=True)
    chanceofsunshine = models.PositiveIntegerField(default=None, blank=True, null=True)
    autoForecastRate = models.PositiveIntegerField(default=None, blank=True, null=True)
    manualForecastRate = models.PositiveIntegerField(default=None, blank=True, null=True)
    
    def __str__(self):
        return self.weatherForecast.date + " - " + str(self.time) + ": " + str(self.chanceofsunshine) + "%"

class WeatherActualMeasurement(models.Model):
    date = models.CharField(max_length=10)
    time = models.PositiveIntegerField(default=None, blank=True, null=True)
    weatherCondition = models.CharField(max_length=40)

    def __str__(self):
        return self.date + " - " +self.date + ": " + self.weatherCondition
