from django.db import models
from django.utils import timezone

class SolarSystem(models.Model):
    apiSiteId = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class SolarModule(models.Model):
    solSystem = models.ForeignKey(SolarSystem, on_delete=models.CASCADE)
    solModuleType = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class SolarMeasurement(models.Model):
    solModule = models.ForeignKey(SolarModule, on_delete=models.CASCADE, blank=True, null=True)
    time = models.DateTimeField(default=timezone.now)
    timeUnit = models.CharField(max_length=10)
    unit = models.CharField(max_length=10)
    energyProduction = models.PositiveIntegerField(default=None, blank=True, null=True)
    energyConsumtion = models.PositiveIntegerField(default=None, blank=True, null=True)
    
    def __str__(self):
        return str(self.time) + " - energy production: " + str(self.energyProduction) + " " + self.unit + " per " + self.timeUnit + ", energy consumtion: " + str(self.energyConsumtion) + " " + self.unit + " per " + self.timeUnit

class SolarMeasurement_power(models.Model):
    solModule = models.ForeignKey(SolarModule, on_delete=models.CASCADE, blank=True, null=True)
    time = models.DateTimeField(default=timezone.now)
    timeUnit = models.CharField(max_length=10)
    unit = models.CharField(max_length=10)
    powerProduction = models.FloatField(default=None, blank=True, null=True)
    powerConsumtion = models.FloatField(default=None, blank=True, null=True)
    
    def __str__(self):
        return str(self.time) + " - energy production: " + str(self.powerProduction) + " " + self.unit + " per " + self.timeUnit + ", energy consumtion: " + str(self.powerConsumtion) + " " + self.unit + " per " + self.timeUnit

class ThreadConfig(models.Model):
    threadConfig = models.CharField(max_length=20)
    threadValue = models.IntegerField(default=None, blank=True, null=True)
    
    def __str__(self):
        return "ThreadConfig: " + str(self.threadConfig) + " = " + str(self.threadValue)
