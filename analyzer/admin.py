from django.contrib import admin
from .models import SolarSystem, SolarModule, SolarMeasurement, SolarMeasurement_power, ThreadConfig

admin.site.register(SolarSystem)
admin.site.register(SolarModule)
admin.site.register(SolarMeasurement)
admin.site.register(SolarMeasurement_power)
admin.site.register(ThreadConfig)