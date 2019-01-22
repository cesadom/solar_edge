from django.shortcuts import render
from .models import SmartFunction, SmartDevice

def createSmartDevice_view(request):
  if post:
    createSmartDevice(POST['data'])
    context = {}
    return render(request, 'analyzer/createSmartDevice_success.html', context)
  elif:
    context = {}
    return render(request, 'analyzer/createSmartDevice.html', context)

# Create new SmartDevice object and return it, return existing object if SmartDevice already exists. 
def createSmartDevice(smartDeviceData):
  smartDevice, smartDeviceCreated = smartDevice.objects.get_or_create(name=smartDeviceData['name'], defaults={'description': smartDeviceData['description ']})
  smartDevice.save()
  print(smartDeviceCreated)
  return smartDevice
