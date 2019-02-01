from django.contrib import admin

from .models import SmartDevice, SmartFunction, SmartFunctionUnstructuredData, SmartFunctionParameter, SmartFunctionConfig

admin.site.register(SmartDevice)
admin.site.register(SmartFunction)
admin.site.register(SmartFunctionUnstructuredData)
admin.site.register(SmartFunctionParameter)
admin.site.register(SmartFunctionConfig)
