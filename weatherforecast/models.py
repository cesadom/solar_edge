from django.db import models

class WeatherForecast(models.Model):
    date = models.CharField(max_length=10)
    sunHours = models.DecimalField(max_digits=3, decimal_places=1)
    
    def __str__(self):
        return self.date + " - sun hours: " + self.sunHours + "h"

class WeatherForecastDayHour(models.Model):
    time = models.PositiveIntegerField(default=None, blank=True, null=True)
    chanceofsunshine = models.PositiveIntegerField(default=None, blank=True, null=True)
    weatherForecast = models.ForeignKey(WeatherForecast, on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self):
        return self.time + " - " + self.description + ", " + str(self.wattHours) + "wh"
