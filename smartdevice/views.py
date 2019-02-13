from django.shortcuts import render
from .models import SmartFunction, SmartDevice, SmartFunctionUnstructuredData
from datetime import date, datetime, timedelta
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

    if datetime.strptime(str(luftibusLastON.smartDeviceDataValue), "%Y-%m-%d %H:%M:%S.%f") <= datetime.strptime(str(luftibusLastOFF.smartDeviceDataValue), "%Y-%m-%d %H:%M:%S.%f"):
      luftibusLastON.smartDeviceDataValue = datetime.now()
      luftibusLastON.save()

    timeDiff = datetime.now() - datetime.strptime(str(luftibusLastON.smartDeviceDataValue), "%Y-%m-%d %H:%M:%S.%f")
    timeDiff = round(timeDiff.total_seconds())
    print("time delta")
    print(timeDiff)

    luftibusTimeON.smartDeviceDataValue = timeDiff
    luftibusTimeON.save()

    luftibusTotTimeONDate_date = datetime.strptime(str(luftibusTotTimeONDate.smartDeviceDataValue), "%Y-%m-%d").date()

    if luftibusTotTimeONDate_date == date.today():
      if datetime.strptime(str(luftibusLastON.smartDeviceDataValue), "%Y-%m-%d %H:%M:%S.%f") <= datetime.strptime(str(luftibusLastOFF.smartDeviceDataValue), "%Y-%m-%d %H:%M:%S.%f"):
        print("add diff")
        luftibusTotTimeON.smartDeviceDataValue = int(luftibusTotTimeON.smartDeviceDataValue) + int(timeDiff)
      else:
        # TODO: fix current Hack with fix coded addition of 20 min interval
        luftibusTotTimeON.smartDeviceDataValue = int(luftibusTotTimeON.smartDeviceDataValue) + (60*20)        
        print("add 20min")
    elif luftibusTotTimeONDate_date < date.today():
      # this will not take into account all possible corner cases around midnight, but at midnight no sun is epexted to shine..
      luftibusTotTimeON.smartDeviceDataValue = timeDiff
      luftibusTotTimeONDate.smartDeviceDataValue = date.today()
    else:
      luftibusTotTimeONDate.smartDeviceDataValue = date.today()
    
    luftibusTotTimeONDate.save()
    luftibusTotTimeON.save()


    # decide wether to switch on or off depending on the total time on
    if int(luftibusTotTimeON.smartDeviceDataValue) > (60*60*8):
      print('luftibus soll trotzdem ausgehen!')
      event="luftibus_off"
      requests.post("https://maker.ifttt.com/trigger/"+event+"/with/key/guXHOYmQVhhA06ScMESPWht0tyY1SjKRAexZpdJcUVY")
      return "trotzdem off, da luftibus heute bereits " + str(luftibusTotTimeON.smartDeviceDataValue) + " sec gelaufen ist!"
    else:
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
    
    
    timeDiff = datetime.now() - datetime.strptime(str(luftibusLastON.smartDeviceDataValue), "%Y-%m-%d %H:%M:%S.%f")
    timeDiff = round(timeDiff.total_seconds())
    print("time delta")
    print(timeDiff)

    luftibusTimeON.smartDeviceDataValue = timeDiff
    luftibusTimeON.save()
    
    # decide wether to switch off or not depending on the time on
    if timeDiff <= (60*15):
      print('luftibus bleibt noch angeschaltet!')
      # TODO: something goeas wrong with the output of the message if it jumps to on and eventhough switches off, maybe better to hard code switch on also here..
      luftibus_on()
      return "trotzdem on, da luftibus erst seit " + str(timeDiff) + " sec läuft!"
    elif datetime.now().hour >= 20 and int(luftibusTotTimeON.smartDeviceDataValue) <= (60*60*3):
      print('luftibus geht trotzdem an!')
      # TODO: something goes wrong with the output of the message if it jumps to on and eventhough switches off, maybe better to hard code switch on also here..
      luftibus_on()
      return "trotzdem on, da luftibus noch keine 3h gelaufen ist!"
    else:
      event="luftibus_off"
      requests.post("https://maker.ifttt.com/trigger/"+event+"/with/key/guXHOYmQVhhA06ScMESPWht0tyY1SjKRAexZpdJcUVY")
      print('luftibus ausgeschaltet!')
      luftibusLastOFF.smartDeviceDataValue = datetime.now()
      luftibusLastOFF.save()
      return "off"
