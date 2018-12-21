from django.db import models

class SolarSystem(models.Model):
    id=None
    apiSiteIdList=None
    name=None
    address=None

class SolarModule(models.Model):
    id=None
    solModuleType=None
    description=None

class SolarMeasurement(models.Model):
    id=None
    solModuleId=None
    time=None
