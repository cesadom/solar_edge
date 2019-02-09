from django.shortcuts import render
from .models import SmartFunction, SmartDevice, SmartFunctionUnstructuredData
from datetime import datetime, timedelta
import requests

def createSmartDevice_view(request):
  # TODO: Implement django.forms
  if 'data' in POST:
    createSmartDevice(POST['data'])
    context = {}
    return render(request, 'analyzer/createSmartDevice_success.html', context)
  else:
    context = {}
    return render(request, 'analyzer/createSmartDevice.html', context)

# Create new SmartDevice object and return it, return existing object if SmartDevice already exists. 
def createSmartDevice(smartDeviceData):
  smartDevice, smartDeviceCreated = smartDevice.objects.get_or_create(name=smartDeviceData['name'], defaults={'description': smartDeviceData['description']})
  smartDevice.save()
  for smartF in smartDeviceData['smartFunctions']:
     smartF_obj, smartDeviceFunctionCreated = smartFunction.objects.get_or_create(code=smartF['code'], defaults={'name': smartF['name'], 'description': smartF['description']})
     smartDevice.smartFunction.add(smartF_obj)
  print(smartDeviceCreated)
  return smartDevice

# switches luftibus on via IFTTT trigger
# TODO: save status and history in model and check before switching on
def luftibus_on():
    code = "d90100"
    # get object with code
    luftibus_obj = SmartDevice.objects.get(code=code)
    print("LUFTIBUS: " + str(luftibus_obj))
    luftibusConfig_obj = SmartFunctionUnstructuredData.objects.filter(smartDevice_id=luftibus_obj.id)
    print("LUFTIBUS Config: " + str(luftibusConfig_obj))
    luftibusLastON = luftibusConfig_obj.get(smartDeviceDataKey='last_ON')
    luftibusLastOFF = luftibusConfig_obj.get(smartDeviceDataKey='last_OFF')
    luftibusTimeON = luftibusConfig_obj.get(smartDeviceDataKey='time_ON')
    luftibusTotTimeON = luftibusConfig_obj.get(smartDeviceDataKey='totTime_ON')
    luftibusTotTimeONDate = luftibusConfig_obj.get(smartDeviceDataKey='totTime_ON_Date')

    luftibusLastON.smartDeviceDataValue = datetime.now()
    luftibusTimeON.smartDeviceDataValue = 3
    luftibusLastON.save()
    luftibusTimeON.save()

    # luftibus_obj, created = SmartDevice.objects.get_or_create(code=code, defaults={'name': name, ...})
    # TODO: evaluate if ON is possible based on Data
    # TODO: finalize check to switch on or not based on Confic tot
    event="luftibus_on"
    requests.post("https://maker.ifttt.com/trigger/"+event+"/with/key/guXHOYmQVhhA06ScMESPWht0tyY1SjKRAexZpdJcUVY")
    print('luftibus eingeschaltet!')
    return "on"

# switches luftibus off via IFTTT trigger
def luftibus_off():
    code = "d90100"
    luftibus_obj = SmartDevice.objects.get(code=code)
    print("LUFTIBUS: " + str(luftibus_obj))
    luftibusConfig_obj = SmartFunctionUnstructuredData.objects.filter(smartDevice_id=luftibus_obj.id)
    print("LUFTIBUS Config: " + str(luftibusConfig_obj))
    luftibusLastON = luftibusConfig_obj.get(smartDeviceDataKey='last_ON')
    luftibusLastOFF = luftibusConfig_obj.get(smartDeviceDataKey='last_OFF')
    luftibusTimeON = luftibusConfig_obj.get(smartDeviceDataKey='time_ON')
    luftibusTotTimeON = luftibusConfig_obj.get(smartDeviceDataKey='totTime_ON')
    
    
    timeDiff = datetime.now() - datetime.strptime(luftibusLastON.smartDeviceDataValue, "%Y-%m-%d %H:%M:%S.%f")
    timeDiff = round(timeDiff.total_seconds())
    print("time delta")
    print(timeDiff)

    luftibusTimeON.smartDeviceDataValue = timeDiff
    luftibusTimeON.save()
    
    # TODO: finalize check to switch off or not
    if timeDiff > (60*15):
      event="luftibus_off"
      requests.post("https://maker.ifttt.com/trigger/"+event+"/with/key/guXHOYmQVhhA06ScMESPWht0tyY1SjKRAexZpdJcUVY")
      print('luftibus ausgeschaltet!')
      luftibusLastOFF.smartDeviceDataValue = datetime.now()
      luftibusLastOFF.save()
      return "off"
    else:
      print('luftibus bleibt noch angeschaltet!')
