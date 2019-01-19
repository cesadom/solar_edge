from django.db import models

class SmartFunction(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()

class SmartDevice(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    wattHours = models.PositiveIntegerField(default=None, blank=True, null=True)
    functions = models.ForeignKey(SmartFunction, on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self):
        return self.name + " - " + self.description + ", " + str(self.wattHours) + "wh"
