from django.db import models

# predefined available function values
class SmartFunction(models.Model):
    code = models.CharField(max_length=6)
    name = models.CharField(max_length=30)
    description = models.TextField()
    
    def __str__(self):
        return self.name

class SmartDevice(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    url = models.CharField(max_length=255, default=None, blank=True, null=True)
    wattHours = models.PositiveIntegerField(default=None, blank=True, null=True)
    functions = models.ManyToManyField(SmartFunction)
    
    def __str__(self):
        return self.name + " - " + self.description + ", " + str(self.wattHours) + "wh"

# predefined available functionParameter values
class SmartFunctionParameter(models.Model):
    smartFunctionParamCode = models.CharField(max_length=6)
    smartFunctionParamDescription = models.CharField(max_length=100)
    smartFunctionParamMeta = models.CharField(max_length=200)
    
    def __str__(self):
        return self.smartFunctionParam

class SmartFunctionConfig(models.Model):
    smartFunction = models.ForeignKey(SmartFunction, on_delete=models.CASCADE)
    smartFunctionParameter = models.ForeignKey(SmartFunctionParameter, on_delete=models.CASCADE, default=None, blank=True, null=True)
    configValue = models.CharField(max_length=100)
    
    def __str__(self):
        return self.smartFunction + ": " + self.smartFunctionParameter + " = " + self.configValue
