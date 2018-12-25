from django.contrib import admin
from .models import SolarSystem, SolarModule, SolarMeasurement, SolarLiveData

admin.site.register(SolarSystem)
admin.site.register(SolarModule)
admin.site.register(SolarMeasurement)
admin.site.register(SolarLiveData)
