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
    energyProduction = models.PositiveIntegerField(default=0, blank=True, null=True)
    energyConsumtion = models.PositiveIntegerField(default=0, blank=True, null=True)
    
    def __str__(self):
        return str(self.time) + ": " + str(self.energyProduction) + ", " + str(self.energyConsumtion)

class SolarLiveData(models.Model):
    solModule = models.ForeignKey(SolarModule, on_delete=models.CASCADE, blank=True, null=True)
    time = models.DateTimeField(default=timezone.now)
    timeUnit = models.CharField(max_length=10)
    unit = models.CharField(max_length=10)
    energyProduction = models.PositiveIntegerField(default=0)
    energyConsumtion = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.time + ": " + self.energyProduction + ", " + self.energyConsumtion
