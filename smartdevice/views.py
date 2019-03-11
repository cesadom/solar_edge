from django.shortcuts import render
from .models import SmartFunction, SmartDevice, SmartFunctionUnstructuredData
from datetime import date, datetime, timedelta
import requests

from weatherforecast.views import sunnydays, sunPerDay, logWeatherForecast

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
def luftibus_on(reason=None):
    code = "d90100"
    # get object with code
    luftibus_obj = SmartDevice.objects.get(code=code)
    print("LUFTIBUS: " + str(luftibus_obj))
    luftibusConfig_obj = SmartFunctionUnstructuredData.objects.filter(smartDevice_id=luftibus_obj.id)
    print("LUFTIBUS Config: " + str(luftibusConfig_obj))
    luftibusLastON = luftibusConfig_obj.get(smartDeviceDataKey='last_ON')
    luftibusLastON_date = datetime.strptime(str(luftibusLastON.smartDeviceDataValue), "%Y-%m-%d %H:%M:%S.%f")
    luftibusLastOFF = luftibusConfig_obj.get(smartDeviceDataKey='last_OFF')
    luftibusLastOFF_date = datetime.strptime(str(luftibusLastOFF.smartDeviceDataValue), "%Y-%m-%d %H:%M:%S.%f")
    luftibusTimeON = luftibusConfig_obj.get(smartDeviceDataKey='time_ON')
    luftibusTotTimeON = luftibusConfig_obj.get(smartDeviceDataKey='totTime_ON')
    luftibusTotTimeON_int = int(luftibusTotTimeON.smartDeviceDataValue)
    luftibusTotTimeONDate = luftibusConfig_obj.get(smartDeviceDataKey='totTime_ON_Date')
    luftibusTotTimeONDate_date = datetime.strptime(str(luftibusTotTimeONDate.smartDeviceDataValue), "%Y-%m-%d").date()

    # decide wether to switch on or off depending on the total time on
    if int(luftibusTotTimeON.smartDeviceDataValue) > (60*60*8):
      print('luftibus soll trotzdem ausgehen!')
      # switch off due to max time exceeded
      luftibus_off("maxTimeExceeded")
      return "trotzdem off, da luftibus heute bereits " + str(luftibusTotTimeON.smartDeviceDataValue) + " sec gelaufen ist!"
    else:
      event="luftibus_on"
      requests.post("https://maker.ifttt.com/trigger/"+event+"/with/key/guXHOYmQVhhA06ScMESPWht0tyY1SjKRAexZpdJcUVY")
      print('luftibus eingeschaltet!')
      
      timeDiff = datetime.now() - luftibusLastON_date
      timeDiff = round(timeDiff.total_seconds())
      print("time diff: " + str(timeDiff))
      luftibusTimeON.smartDeviceDataValue = timeDiff
      luftibusTimeON.save()
      luftibusLastON.smartDeviceDataValue = datetime.now()
      luftibusLastON.save()
      
      # if luftibus has switched from off to on, then no time has to be added to the TotTimeONDate, return already here
      if luftibusLastON_date < luftibusLastOFF_date:
        print("just switched on")
        return "on"

      # check if the date the TotTimeONDate has been calculated, if it is from today add the diff to it...
      if luftibusTotTimeONDate_date == date.today():
        print("add diff to TotTimeON")
        luftibusTotTimeON.smartDeviceDataValue = int(luftibusTotTimeON.smartDeviceDataValue) + int(timeDiff)
      # ... if it is from yasterday reset the value with the diff value and set the date to today
      elif luftibusTotTimeONDate_date < date.today():
        # this will not take into account all possible corner cases around midnight, but at midnight no sun is expected to shine..
        print("set TotTimeON to diff")
        luftibusTotTimeON.smartDeviceDataValue = timeDiff
        luftibusTotTimeONDate.smartDeviceDataValue = date.today()
      # ... if the date is not set or in any other case set the date to today 
      else:
        luftibusTotTimeONDate.smartDeviceDataValue = date.today()
      luftibusTotTimeONDate.save()
      luftibusTotTimeON.save()
      
      return "on"
 
# switches luftibus off via IFTTT trigger
def luftibus_off(reason=None):
    code = "d90100"
    luftibus_obj = SmartDevice.objects.get(code=code)
    print("LUFTIBUS: " + str(luftibus_obj))
    luftibusConfig_obj = SmartFunctionUnstructuredData.objects.filter(smartDevice_id=luftibus_obj.id)
    print("LUFTIBUS Config: " + str(luftibusConfig_obj))
    luftibusLastON = luftibusConfig_obj.get(smartDeviceDataKey='last_ON')
    luftibusLastON_date = datetime.strptime(str(luftibusLastON.smartDeviceDataValue), "%Y-%m-%d %H:%M:%S.%f")
    luftibusLastOFF = luftibusConfig_obj.get(smartDeviceDataKey='last_OFF')
    luftibusLastOFF_date = datetime.strptime(str(luftibusLastOFF.smartDeviceDataValue), "%Y-%m-%d %H:%M:%S.%f")
    luftibusTimeON = luftibusConfig_obj.get(smartDeviceDataKey='time_ON')
    luftibusTotTimeON = luftibusConfig_obj.get(smartDeviceDataKey='totTime_ON')
    luftibusTotTimeON_int = int(luftibusTotTimeON.smartDeviceDataValue)
    luftibusTotTimeONDate = luftibusConfig_obj.get(smartDeviceDataKey='totTime_ON_Date')
    luftibusTotTimeONDate_date = datetime.strptime(str(luftibusTotTimeONDate.smartDeviceDataValue), "%Y-%m-%d").date()
    
    
    timeDiff = datetime.now() - luftibusLastON_date
    timeDiff = round(timeDiff.total_seconds())
    print("time diff: " + str(timeDiff))

    luftibusTimeON.smartDeviceDataValue = timeDiff
    luftibusTimeON.save()
    
    # decide wether to switch off or not depending on the time on
    if timeDiff <= (60*15):
      print('luftibus bleibt noch angeschaltet!')
      # TODO: something goes wrong with the output of the message if it jumps to on and eventhough switches off, implement decorators.
      luftibus_on("off_to_on_minTimeON")
      return "trotzdem on, da luftibus erst seit " + str(timeDiff) + " sec läuft!"
#    elif datetime.now().hour >= 20 and luftibusTotTimeON_int <= (60*60*3) and sunPerDay(date.today() + timedelta(1)) < 4:
    elif datetime.now().hour >= 20 and luftibusTotTimeON_int <= (60*60*3):
      print('luftibus geht trotzdem an!')
      # TODO: something goes wrong with the output of the message if it jumps to on and eventhough switches off, implement decorators.
      luftibus_on("off_to_on_maxTimeNotReached")
      return "trotzdem on, da luftibus noch keine 3h gelaufen ist!"
    else:
      event="luftibus_off"
      requests.post("https://maker.ifttt.com/trigger/"+event+"/with/key/guXHOYmQVhhA06ScMESPWht0tyY1SjKRAexZpdJcUVY")
      print('luftibus ausgeschaltet!')
      luftibusLastOFF.smartDeviceDataValue = datetime.now()
      luftibusLastOFF.save()
      return "off"
