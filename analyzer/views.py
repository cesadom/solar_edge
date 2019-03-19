from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail

import sys
from .models import SolarSystem, SolarModule, SolarMeasurement, SolarMeasurement_power, ThreadConfig, GeneralConfig
from weatherforecast.models import WeatherForecast, WeatherForecastDayHour
from weatherforecast.views import sunnydays, sunPerDay, logWeatherForecast
from smartdevice.views import createSmartDevice, luftibus_on, luftibus_off
import solaredge
import requests
import time
from datetime import date, datetime, timedelta
import dateutil.parser
import threading
from threading import Thread
from solaredge_API import solaredge

# Load Background Job Interval from Configuration. Else --> set to 3min
bkgInterval = getattr(settings, 'BKG_INTERVAL', (3*60))

# Load SolarEdge API Key and API Site ID from Configuration. Else --> set to None
APIKEY = getattr(settings, 'SEDGE_APIKEY', None)
APIID = getattr(settings, 'SEDGE_SITEID', None)

# Load SolarEdge API 
solE = solaredge.Solaredge(APIKEY)


# TODO: Change weather API to OpenWeather API
# Load worldweatheronline.com API Key and Configuration
weatherAPIKEY = "cdb9121d690f43aca7a110709191801"
weatherAPILocation = "Meilen"
weatherAPIForecastDays = str(7)
weatherAPIURL = "http://api.worldweatheronline.com/premium/v1/weather.ashx?key=" + weatherAPIKEY + "&q=" + weatherAPILocation + "&format=json&num_of_days=" + weatherAPIForecastDays

# returns Solar Edge Overview
def getSolEdgeOverview():
    try:
        api_adr_site_overview = 'https://monitoringapi.solaredge.com/site/' + APIID + '/overview?api_key=' + APIKEY
        api_res_site_overview = requests.get(api_adr_site_overview).json()
    except:
        print('ERROR in API request!')
        pass
    
    return api_res_site_overview

# returns Solar Edge current Power Flow
def getSolEdgeCurrentPowerFlow():
    api_res_site_currentPowerFlow = None
    try:
        api_res_site_currentPowerFlow = solE.get_current_power_flow(APIID)
    except:
        print('ERROR in API request get_current_power_flow!')
        pass
    
    return api_res_site_currentPowerFlow

# returns Solar Edge Overcapacity, may also be negative due to supply from grid
def getSolEdgeCurrentOvercapacity():
    currentPowerFlow = getSolEdgeCurrentPowerFlow()
    # print(currentPowerFlow)
    if not currentPowerFlow:
        return False
    else:
        return float(currentPowerFlow['siteCurrentPowerFlow']['PV']['currentPower']) - float(currentPowerFlow['siteCurrentPowerFlow']['LOAD']['currentPower'])

@login_required
def home(request):
    
    # Initialize variable to check if form has been submited 
    form_submitted = False

    # Load API Key and API Site ID from submitted form. Else --> preset from Config or set to None
    if 'APIKEY_input' in request.GET:
        solarEdgeAPIKey = request.GET['APIKEY_input']
        form_submitted = True
    else:
        solarEdgeAPIKey = APIKEY

    if 'APIID_input' in request.GET:
       solarEdgeID = request.GET['APIID_input']
    else:
       solarEdgeID = APIID
    
    # Try to load data from API
    api_request_success = True
    request.session['weather_api_res']=None
    try:
        # SolarEdge API requests
        api_adr_site_details ='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/details?api_key=' + solarEdgeAPIKey
        request.session['api_res_site_details']=requests.get(api_adr_site_details).json()
        api_adr_site_overview ='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/overview?api_key=' + solarEdgeAPIKey
        request.session['api_res_site_overview']=requests.get(api_adr_site_overview).json()
        api_adr_site_dataPeriod='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/dataPeriod?api_key=' + solarEdgeAPIKey
        request.session['api_res_site_dataPeriod']=requests.get(api_adr_site_dataPeriod).json()
        api_adr_site_energy='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/energy?timeUnit=DAY&startDate=' + (datetime.now() - timedelta(10)).strftime("%Y-%m-%d") + '&endDate=' + datetime.now().strftime("%Y-%m-%d") + '&api_key=' + solarEdgeAPIKey
        request.session['api_res_site_energy']=requests.get(api_adr_site_energy).json()
        api_adr_site_energyDetails_DAY='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/energyDetails?meters=PRODUCTION,CONSUMPTION&timeUnit=DAY&startTime=' + (datetime.now() - timedelta(2)).strftime("%Y-%m-%d") + '%2000:00:00&endTime=' + datetime.now().strftime("%Y-%m-%d") + '%2023:59:59&api_key=' + solarEdgeAPIKey
        request.session['api_res_site_energyDetails_DAY']=requests.get(api_adr_site_energyDetails_DAY).json()
        # Weather API requests
        request.session['weather_api_res']=requests.get(weatherAPIURL).json()
        # print(request.session['weather_api_res'])
    except:
        api_request_success = False
        pass
    
    # Parse API 'energyDetails' for Consumption & Production meter values
    solarEnergyDetails = request.session['api_res_site_energyDetails_DAY']['energyDetails']
    print('api_request_success:')
    print(api_request_success)
    for meterTelemetry in solarEnergyDetails['meters']:
        if meterTelemetry['type'] == 'Consumption':
            meterTelemetryConsumption = meterTelemetry['values']
            # print('meterTelemetryConsumption:')
            # print(meterTelemetryConsumption)
            
            ## Delete the last item of the list == today, as it is not yet the final value
            del meterTelemetryConsumption[-1]
            # print('--- meterTelemetryConsumption W/O today:')
            # print(meterTelemetryConsumption)
        elif meterTelemetry['type'] == 'Production':
            meterTelemetryProduction = meterTelemetry['values']
            # print('meterTelemetryProduction:')
            # print(meterTelemetryProduction)

            ## Delete the last item of the list == today, as it is not yet the final value
            del meterTelemetryProduction[-1]
            # print('--- meterTelemetryProduction W/O today:')
            # print(meterTelemetryProduction)
            

    # Parse Consumption & Production meter values and write data into SolarMeasurement Model
    model_write_success = True
    meterTelemetry_added = False
    try:
        for consumptionValue in meterTelemetryConsumption:
            if 'value' in consumptionValue:
                sMeasurement, created = SolarMeasurement.objects.get_or_create(time=dateutil.parser.parse(consumptionValue['date']), defaults={'timeUnit': solarEnergyDetails['timeUnit'], 'unit': solarEnergyDetails['unit'], 'energyConsumtion': consumptionValue['value']})
                sMeasurement.save()
                # print('consumptionValue:')
                # print(consumptionValue)
                # print('---- sMeasurement:')
                # print(sMeasurement)
                # print('created:')
                # print(created)
        for productionValue in meterTelemetryProduction:
            if 'value' in productionValue:
                # print('---- productionValue:')
                # print(productionValue)
                sMeasurement = SolarMeasurement.objects.filter(time=dateutil.parser.parse(productionValue['date']))
                # print('---- BEFORE sMeasurement:')
                # print(sMeasurement)
                if not sMeasurement:
                    print('---- ERROR: MISSING ENTRY IN PRODUCTION LIST ----')
                    # raise ValueError('Unexpacted missing value for given time: ' + productionValue['time'])
                
                # SKIP UPDATE IF VALUE ALREADY UPDATED
                # print(sMeasurement.values('energyProduction')[0]['energyProduction'])
                if not sMeasurement.values('energyProduction')[0]['energyProduction']:
                    sMeasurement.update(energyProduction = productionValue['value'])
                    meterTelemetry_added = True
                    # print('---- AFTER sMeasurement:')
                    # print(sMeasurement)
                # else:
                    # print('---- NO UPDATE sMeasurement:')
                   
    except Exception as e:
        pass
        model_write_success = False
        print (e, type(e))
    
    print('model_write_success:')
    print(model_write_success)
    print('meterTelemetry_added:')
    print(meterTelemetry_added)
    
    """
    time = models.DateTimeField(default=timezone.now)
    timeUnit = models.CharField(max_length=10)
    unit = models.CharField(max_length=10)
    energyProduction = models.PositiveIntegerField(default=0)
    energyConsumtion 
    """
    
    # Parse Weather API result
    try:
        weather_api_weatherForecast = request.session['weather_api_res']['data']['weather']
        weather_api_forecastedSunHours = dict()
        for forecastedDate in weather_api_weatherForecast:
            # sMeasurement, created = SolarMeasurement.objects.get_or_create(time=dateutil.parser.parse(consumptionValue['date']), defaults={'timeUnit': solarEnergyDetails['timeUnit'], 'unit': solarEnergyDetails['unit'], 'energyConsumtion': consumptionValue['value']})
            # sMeasurement.save()
            # sMeasurement = SolarMeasurement.objects.filter(time=dateutil.parser.parse(productionValue['date']))
            # sMeasurement.update(energyProduction = productionValue['value'])
            print(forecastedDate['date'])
            weatherForecast_obj, created = WeatherForecast.objects.get_or_create(forecastDate=datetime.today().strftime('%Y-%m-%d'), date=forecastedDate['date'], defaults={'sunHours': forecastedDate['sunHour']})
            weatherForecast_obj.save()
            # print(forecastedDate['sunHour'])
            value=forecastedDate['date']
            weather_api_forecastedSunHours[value]={'sunHour': forecastedDate['sunHour']}
            weather_api_forecastedSunHours[value]['chanceofsunshineAtDayHour'] = {}
            for forecastedHours in forecastedDate['hourly']:
                forecastedHoursTime_str=str(forecastedHours['time'])
                # print(forecastedHoursTime_str)
                forecastedHoursChanceofsunshine_str=str(forecastedHours['chanceofsunshine'])
                # print(forecastedHoursChanceofsunshine_str)
                weather_api_forecastedSunHours[value]['chanceofsunshineAtDayHour'][forecastedHoursTime_str] = forecastedHoursChanceofsunshine_str
                weatherForecastDayHour_obj, created = WeatherForecastDayHour.objects.get_or_create(time=forecastedHours['time'], weatherForecast=weatherForecast_obj, chanceofsunshine=forecastedHours['chanceofsunshine'])
            
        print(weather_api_forecastedSunHours)
        # print(weather_api_forecastedSunHours)
    except:
        pass
        print("ERROR weather_api_forecastedSunHours")
        weather_api_forecastedSunHours = None

    # Create SmartDevice
    smartDevice1 = {
        'name': 'Luftentfeuchter',
        'description ': 'entzieht Feuchtigkeit aus der Luft. Verfügt über Hydrostat Sensor.',
        'smartFunctions': [],
    }
    
    smartDevice2 = {
        'name': 'smart Steckdose D-Link',
        'description ': 'Smart Steckdose für Luftibus',
        'smartFunctions': [
            {
                'code': 'f10100',
                'name': 'ferngesteuerte Ein- und Ausschaltfunktion',
                'description': 'Der Stromfluss kann ferngesteuert ein oder ausgeschaltet werden',
                'config': [
                    {
                        'code': 'c10100',
                        'description': 'dafault state',
                        'value': 'OFF',
                    }
                ]
            },
            {
                'code': 'f10200',
                'name': 'Stromflussmessung',
                'description': 'Der Stromfluss wird gemessen und kann abgefragt werden',
                'config': [
                    {
                        'code': 'c20100',
                        'description': 'interval for energy measurements in seconds',
                        'value': '30',
                    }
                ]
            }
        ],
    }
    
    # smartDevice1_obj = createSmartDevice(smartDevice1)
    # print("smartDevice1_obj")
    # print(smartDevice1_obj)
    # smartDevice2_obj = createSmartDevice(smartDevice2)
    # print("smartDevice2_obj")
    # print(smartDevice2_obj)
    
    
    # load data into context
    api_res_site_details = request.session['api_res_site_details']
    api_res_site_overview = request.session['api_res_site_overview']
    api_res_site_dataPeriod = request.session['api_res_site_dataPeriod']
    api_res_site_energy = request.session['api_res_site_energy']
    api_res_site_energyDetails = request.session['api_res_site_energyDetails_DAY']

    context = {
        'title': 'Home',
        'API_results': {
            'api_res_site_details': api_res_site_details,
            'api_res_site_overview': api_res_site_overview,
            'api_res_site_dataPeriod': api_res_site_dataPeriod,
            'api_res_site_energy': api_res_site_energy,
            'api_res_site_energyDetails': api_res_site_energyDetails,
            'weather_api_res_all': weather_api_forecastedSunHours,
            # 'smartDevice1_obj': smartDevice1_obj,
            # 'smartDevice2_obj': smartDevice2_obj
        },
    }
    return render(request, 'analyzer/home.html', context)

def get_data(request, *args, **kwargs):
    form_submitted = False
    if 'APIKEY_input' in request.GET:
        solarEdgeAPIKey = request.GET['APIKEY_input']
        form_submitted = True
    else:
        solarEdgeAPIKey = APIKEY

    if 'APIID_input' in request.GET:
       solarEdgeID = request.GET['APIID_input']
    else:
       solarEdgeID = APIID
       
    api_request_success = True
    try:
        api_adr_site_details ='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/details?api_key=' + solarEdgeAPIKey
        request.session['api_res_site_details']=requests.get(api_adr_site_details).json()
        api_adr_site_overview ='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/overview?api_key=' + solarEdgeAPIKey
        request.session['api_res_site_overview']=requests.get(api_adr_site_overview).json()
        api_adr_site_dataPeriod='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/dataPeriod?api_key=' + solarEdgeAPIKey
        request.session['api_res_site_dataPeriod']=requests.get(api_adr_site_dataPeriod).json()
        api_adr_site_energy='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/energy?timeUnit=DAY&startDate=' + (datetime.now() - timedelta(10)).strftime("%Y-%m-%d") + '&endDate=' + datetime.now().strftime("%Y-%m-%d") + '&api_key=' + solarEdgeAPIKey
        request.session['api_res_site_energy']=requests.get(api_adr_site_energy).json()
        api_adr_site_energyDetails='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/energyDetails?meters=PRODUCTION,CONSUMPTION&timeUnit=DAY&startTime=' + (datetime.now() - timedelta(10)).strftime("%Y-%m-%d") + '%2000:00:00&endTime=' + datetime.now().strftime("%Y-%m-%d") + '%2023:59:59&api_key=' + solarEdgeAPIKey
        request.session['api_res_site_energyDetails']=requests.get(api_adr_site_energyDetails).json()
    except:
        api_request_success = False
        pass
    

    api_res_site_details = request.session['api_res_site_details']
    api_res_site_overview = request.session['api_res_site_overview']
    api_res_site_dataPeriod = request.session['api_res_site_dataPeriod']
    api_res_site_energy = request.session['api_res_site_energy']
    api_res_site_energyDetails = request.session['api_res_site_energyDetails']

    context = {
        'API_results': {
            'api_res_site_details': api_res_site_details,
            'api_res_site_overview': api_res_site_overview,
            'api_res_site_dataPeriod': api_res_site_dataPeriod,
            'api_res_site_energy': api_res_site_energy,
            'api_res_site_energyDetails': api_res_site_energyDetails,
        },
    }
    return JsonResponse(context) # http response

@login_required
def chart(request):
    return render(request, 'analyzer/chart.html', {'title': 'Chart'})

@login_required
def api_plain(request):
    form_submitted = False
    if 'APIKEY_input' in request.GET:
        solarEdgeAPIKey = request.GET['APIKEY_input']
        form_submitted = True
    else:
        solarEdgeAPIKey = APIKEY

    if 'APIID_input' in request.GET:
       solarEdgeID = request.GET['APIID_input']
    else:
       solarEdgeID = APIID

    # CACHE EXAMPLE FROM https://simpleisbetterthancomplex.com/tutorial/2018/02/03/how-to-use-restful-apis-with-django.html ##
    is_cached = ('api_res_site_overview' in request.session)
    print('is_cached:')
    print(is_cached)
    # cashed_since = 100

    if is_cached and (solarEdgeAPIKey != None) and ('cache_ts' in request.session):
        cashed_since = time.time() - request.session['cache_ts'] 
    else:
        cashed_since = 0

    try:
        print('cashed_since:')
        print(cashed_since)
        print('request.session[api_res_site_overview]:')
        print(request.session['api_res_site_overview'])
    except:
        pass
    
    # if (not is_cached) or (cashed_since >= 20) or request.session['api_res_site_overview'] == None:
    if True:
        request.session['cache_ts'] = time.time()
        request.session['api_res_site_list'] = None
        request.session['api_res_site_details'] = None
        request.session['api_res_site_overview'] = None
        request.session['api_res_site_dataPeriod'] = None
        request.session['api_res_site_energy'] = None
        request.session['api_res_site_energyDetails'] = None
        request.session['api_res_site_timeFrameEnergy'] = None
        request.session['api_res_site_power'] = None
        request.session['api_res_site_powerDetails'] = None
        request.session['api_res_site_currentPowerFlow'] = None
        request.session['api_res_site_envBenefits'] = None
        request.session['api_res_site_inventory'] = None
        request.session['api_res_equip_list'] = None

        try:
            api_adr_site_list='https://monitoringapi.solaredge.com/sites/list?api_key=' + solarEdgeAPIKey
            request.session['api_res_site_list']=requests.get(api_adr_site_list).json()
            api_adr_site_details='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/details?api_key=' + solarEdgeAPIKey
            request.session['api_res_site_details']=requests.get(api_adr_site_details).json()
            api_adr_site_overview='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/overview?api_key=' + solarEdgeAPIKey
            request.session['api_res_site_overview']=requests.get(api_adr_site_overview).json()
            api_adr_site_dataPeriod='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/dataPeriod?api_key=' + solarEdgeAPIKey
            request.session['api_res_site_dataPeriod']=requests.get(api_adr_site_dataPeriod).json()
            api_adr_site_energy='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/energy?timeUnit=DAY&endDate=2018-12-31&startDate=2018-12-01&api_key=' + solarEdgeAPIKey
            request.session['api_res_site_energy']=requests.get(api_adr_site_energy).json()
            api_adr_site_energyDetails='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/energyDetails?meters=PRODUCTION,CONSUMPTION&timeUnit=DAY&startTime=2018-12-01%2000:00:00&endTime=2018-12-07%2023:59:59&api_key=' + solarEdgeAPIKey
            request.session['api_res_site_energyDetails']=requests.get(api_adr_site_energyDetails).json()
            api_adr_site_energyDetails_QUART_HOUR='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/energyDetails?meters=PRODUCTION,CONSUMPTION&timeUnit=QUARTER_OF_AN_HOUR&startTime=' + (datetime.now() - timedelta(2)).strftime("%Y-%m-%d") + '%2000:00:00&endTime=' + datetime.now().strftime("%Y-%m-%d") + '%2023:59:59&api_key=' + solarEdgeAPIKey
            request.session['api_res_site_energyDetails_QUART_HOUR']=requests.get(api_adr_site_energyDetails_QUART_HOUR).json()
            api_adr_site_timeFrameEnergy='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/timeFrameEnergy?timeUnit=DAY&endDate=2018-12-31&startDate=2018-12-01&api_key=' + solarEdgeAPIKey
            request.session['api_res_site_timeFrameEnergy']=requests.get(api_adr_site_timeFrameEnergy).json()
            api_adr_site_power='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/power?startTime=2018-12-07%2007:00:00&endTime=2018-12-07%2019:00:00&api_key=' + solarEdgeAPIKey
            request.session['api_res_site_power']=requests.get(api_adr_site_power).json()
            api_adr_site_powerDetails='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/powerDetails?meters=PRODUCTION,CONSUMPTION&startTime=2018-12-07%2000:00:00&endTime=2018-12-07%2023:59:59&api_key=' + solarEdgeAPIKey
            request.session['api_res_site_powerDetails']=requests.get(api_adr_site_powerDetails).json()
            api_adr_site_currentPowerFlow='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/currentPowerFlow?api_key=' + solarEdgeAPIKey
            request.session['api_res_site_currentPowerFlow']=requests.get(api_adr_site_currentPowerFlow).json()
            api_adr_site_envBenefits='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/envBenefits?systemUnits=Imperial&api_key=' + solarEdgeAPIKey
            request.session['api_res_site_envBenefits']=requests.get(api_adr_site_envBenefits).json()
            api_adr_site_inventory='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/inventory?api_key=' + solarEdgeAPIKey
            request.session['api_res_site_inventory']=requests.get(api_adr_site_inventory).json()
            api_adr_equip_list='https://monitoringapi.solaredge.com/equipment/' + solarEdgeID + '/list?api_key=' + solarEdgeAPIKey
            request.session['api_res_equip_list']=requests.get(api_adr_equip_list).json()
        except:
            pass

    api_res_site_list = request.session['api_res_site_list']
    api_res_site_details = request.session['api_res_site_details']
    api_res_site_overview = request.session['api_res_site_overview']
    api_res_site_dataPeriod = request.session['api_res_site_dataPeriod']
    api_res_site_energy = request.session['api_res_site_energy']
    api_res_site_energyDetails = request.session['api_res_site_energyDetails']
    api_res_site_energyDetails_QUART_HOUR = request.session['api_res_site_energyDetails_QUART_HOUR']
    api_res_site_timeFrameEnergy = request.session['api_res_site_timeFrameEnergy']
    api_res_site_power = request.session['api_res_site_power']
    api_res_site_powerDetails = request.session['api_res_site_powerDetails']
    api_res_site_currentPowerFlow = request.session['api_res_site_currentPowerFlow']
    api_res_site_envBenefits = request.session['api_res_site_envBenefits']
    api_res_site_inventory = request.session['api_res_site_inventory']
    api_res_equip_list = request.session['api_res_equip_list']
   


    context = {
        'title': 'Plain API',
        'form_submitted': form_submitted,
        'API_results': {
            'is_cached': is_cached,
            'cashed_since': cashed_since,
            'api_res_site_list': api_res_site_list,
            'api_res_site_details': api_res_site_details,
            'api_res_site_overview': api_res_site_overview,
            'api_res_site_dataPeriod': api_res_site_dataPeriod,
            'api_res_site_energy': api_res_site_energy,
            'api_res_site_energyDetails': api_res_site_energyDetails,
            'api_res_site_energyDetails_QUART_HOUR': api_res_site_energyDetails_QUART_HOUR,
            'api_res_site_timeFrameEnergy': api_res_site_timeFrameEnergy,
            'api_res_site_power': api_res_site_power,
            'api_res_site_powerDetails': api_res_site_powerDetails,
            'api_res_site_currentPowerFlow': api_res_site_currentPowerFlow,
            'api_res_site_envBenefits': api_res_site_envBenefits,
            'api_res_site_inventory': api_res_site_inventory,
            'api_res_equip_list': api_res_equip_list
        },
        'APIKEY': solarEdgeAPIKey,
        'APIID': solarEdgeID        
    }
    return render(request, 'analyzer/api_plain.html', context)

def about(request):
    return render(request, 'analyzer/about.html', {'title': 'About'})

def cron(request):
    luftibus_status = switchLuftibus()

    if not luftibus_status:
        return HttpResponse('ERROR in getSolEdgeCurrentOvercapacity call')
    else:
        return HttpResponse('all done! luftibus: ' + luftibus_status)

def switchLuftibus():
    # mostsunnydays = sunnydays(datetime.now, datetime.now() + timedelta(10))
    # print(getSolEdgeCurrentOvercapacity())

    currentOvercapacity = getSolEdgeCurrentOvercapacity()
    luftibus_status = "not executed!"

    if not currentOvercapacity:
        return False
    elif float(currentOvercapacity) > 0.5:
        luftibus_status = luftibus_on()
    else:
        luftibus_status = luftibus_off()
    return luftibus_status


def checkThreadRun():
    ThreadConfig_obj = ThreadConfig.objects.get(threadConfig="ThreadRun")
    ThreadRun = ThreadConfig_obj.threadValue
    if ThreadRun > 0:
        return True
    else:
        return False

def logPowerFlow():
    sole_currPowerFlow = getSolEdgeCurrentPowerFlow()
    if not sole_currPowerFlow:
        return False
    unit = sole_currPowerFlow['siteCurrentPowerFlow']['unit']
    
    # Check if power flows from Grid (1) or into Grid (-1)
    if sole_currPowerFlow['siteCurrentPowerFlow']['connections'][0]['from'] == "GRID":
        powerFromGrid = 1
    else:
        powerFromGrid = -1

    GRIDCurrentPower = sole_currPowerFlow['siteCurrentPowerFlow']['GRID']['currentPower'] * powerFromGrid
    LOADCurrentPower = sole_currPowerFlow['siteCurrentPowerFlow']['LOAD']['currentPower']
    PVCurrentPower = sole_currPowerFlow['siteCurrentPowerFlow']['PV']['currentPower']
    print("Solarstrom: " + str(PVCurrentPower) + " " + unit)
    print("Verbrauch:  " + str(LOADCurrentPower) + " " + unit)
    print("Netzstrom:  " + str(GRIDCurrentPower) + " " + unit)

    # TODO: insert time considering timezone
    try:
        sMeasurement_power_nearReal, created = SolarMeasurement_power.objects.get_or_create(time=datetime.now(), defaults={'timeUnit': "NEARREAL", 'unit': unit, 'powerProduction': PVCurrentPower, 'powerConsumtion': LOADCurrentPower, 'powerGrid': GRIDCurrentPower})
        sMeasurement_power_nearReal.save()
        print("model SolarMeasurement_power successfully written!")
        return True
    except:
        print("ERROR on writing model SolarMeasurement_power!")
        return False

def start_thread(request):
    if not bgTask_thread.isAlive():
        bgTask_thread.start()
        print("####### NEW THREAD STARTED #######")
        return HttpResponse('Thread startet')
    else:
        print("####### !!THREAD IS ALREADY RUNNING!! #######")
        return HttpResponse('Thread läuft bereits!!!!')
    # thread.join()

def checkLastSentEmail(recipList):
    truncRecipList = (recipList[:145] + '..') if len(recipList) > 145 else recipList
    truncRecipList = "LastSentEmail" + str(truncRecipList)
    generalConfig_obj = GeneralConfig.objects.filter(generalConfigKey=truncRecipList)
    # If it is the first e-mail sent to this recipient list, no object will be returned --> send e-mail
    if not generalConfig_obj:
        return True

    # If an e-mail has already been sent to this recipient list, an object will be returned
    lastSentEmailDate = datetime.strptime(generalConfig_obj[0].generalConfigValue, '%Y-%m-%d %H:%M:%S.%f')
    timeDelta = datetime.now()-lastSentEmailDate

    # If the last e-mail has been sent within the last 4 hours --> don't send e-mail, else send e-mail
    if timeDelta.total_seconds() <= (4*60*60):
        print("es sind erst " + str(round(timeDelta.total_seconds()/60/60,3)) + " Stunden vergangen seit dem letzten E-Mail Versand!")
        return False
    else:
        return True

def sendMailToRecipList(emailSubject, emailMessage, recipList = ['domenico.cesare@gmail.com']):
    if checkLastSentEmail(recipList):
        print(emailSubject)
        print(emailMessage)
        print(recipList)
        # try:
        send_mail(
            subject=emailSubject,
            from_email=getattr(settings, 'EMAIL_HOST_USER', None),
            recipient_list=recipList,
            message=emailMessage,
            fail_silently=False,
        )
        truncRecipList = (recipList[:145] + '..') if len(recipList) > 145 else recipList
        truncRecipList = "LastSentEmail" + str(truncRecipList)
        lastSentEmailDate, created = GeneralConfig.objects.get_or_create(generalConfigKey=truncRecipList, defaults={'generalConfigValue': datetime.now()})
        lastSentEmailDate.generalConfigValue=datetime.now()
        lastSentEmailDate.save()

        print('E-Mail sent to ' + str(recipList))
        return True
        # except:
        #     print('ERROR during sending E-Mail!')
        #     return False
    else:
        return True



def notifyOvercapacity(overcapacityThreshold = getattr(settings, 'OVERCAP_NOTIF_THRESHOLD', 3.5)):
    currentOvercapacity = getSolEdgeCurrentOvercapacity()
    print('currentOvercapacity: ' + str(currentOvercapacity))
    if not currentOvercapacity:
        print('ERROR in getSolEdgeCurrentOvercapacity call!')
        return False
    elif float(currentOvercapacity) > float(overcapacityThreshold):
        emailSbj = 'Luftibus App meldet ' + str(round(currentOvercapacity,2)) + ' kW Überkapazität'
        emailMsg = 'Wir haben ' + str(round(currentOvercapacity,2)) + ' kW Überkapazität. Jetzt wäre es Zeit einen grossen Verbraucher anzuschalten!'
        emailRcp = getattr(settings, 'NOTIF_THRESHOLD_RECIP', "domenico.cesare@gmail.com").split(';')
        # emailRcp = ['domenico.cesare@gmail.com']
        emailSuccess = sendMailToRecipList(emailSbj, emailMsg, emailRcp)
        return emailSuccess
    else:
        return True

def routineThread(times):
    # for i in range(times):
    i=0

    while True:
        if (not checkThreadRun()):
            break
        
        # Write Current Power Flow into DB log
        logPowerFlowWritten = logPowerFlow()
        print('Power Flow Log written = ' + str(logPowerFlowWritten))
        sys.stdout.flush()

        # Check current overcapacity and notify via e-mail if exceeding 1kW
        notifyOvercapacitySuccess = notifyOvercapacity()
        print('Notify if overcapacity is to high successful = ' + str(notifyOvercapacitySuccess))
        sys.stdout.flush()

        # Write Weatherforecast in DB
        logWeatherFCSuccess = logWeatherForecast()
        print('Log Weatherforecast into DB successful = ' + str(logWeatherFCSuccess))
        sys.stdout.flush()
        
        # Switch luftibus
        # switchLuftibusSuccess = switchLuftibus()
        # print('Switch luftibus successful = ' + str(switchLuftibusSuccess))
        # sys.stdout.flush()


        print(' -------- Thread running with Interval of ' + str(bkgInterval) + ' seconds. Iteration: ' + str(i) + ' completed! -------- ')
        sys.stdout.flush()

        time.sleep(int(bkgInterval))
        i+=1
        
    print('Thread finished!')

# initiate global thread for background task
bgTask_thread = Thread(target = routineThread, args = (10, ))



