from django.contrib import admin

from .models import SmartDevice, SmartFunction

admin.site.register(SmartDevice)
admin.site.register(SmartFunction)
