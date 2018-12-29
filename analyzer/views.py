from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import SolarSystem, SolarModule, SolarMeasurement, SolarLiveData
from django.utils import timezone

from django.conf import settings
import solaredge
import requests
import time
from datetime import datetime, timedelta
import dateutil.parser


# Load API Key and API Site ID from Configuration. Else --> set to None
APIKEY = getattr(settings, 'SEDGE_APIKEY', None)
APIID = getattr(settings, 'SEDGE_SITEID', None)

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
    try:
        api_adr_site_details ='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/details?api_key=' + solarEdgeAPIKey
        request.session['api_res_site_details']=requests.get(api_adr_site_details).json()
        api_adr_site_overview ='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/overview?api_key=' + solarEdgeAPIKey
        request.session['api_res_site_overview']=requests.get(api_adr_site_overview).json()
        api_adr_site_dataPeriod='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/dataPeriod?api_key=' + solarEdgeAPIKey
        request.session['api_res_site_dataPeriod']=requests.get(api_adr_site_dataPeriod).json()
        api_adr_site_energy='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/energy?timeUnit=DAY&startDate=' + (datetime.now() - timedelta(10)).strftime("%Y-%m-%d") + '&endDate=' + datetime.now().strftime("%Y-%m-%d") + '&api_key=' + solarEdgeAPIKey
        request.session['api_res_site_energy']=requests.get(api_adr_site_energy).json()
        api_adr_site_energyDetails='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/energyDetails?meters=PRODUCTION,CONSUMPTION&timeUnit=DAY&startTime=' + (datetime.now() - timedelta(350)).strftime("%Y-%m-%d") + '%2000:00:00&endTime=' + datetime.now().strftime("%Y-%m-%d") + '%2023:59:59&api_key=' + solarEdgeAPIKey
        request.session['api_res_site_energyDetails']=requests.get(api_adr_site_energyDetails).json()
    except:
        api_request_success = False
        pass
    
    # Parse API 'energyDetails' for Consumption & Production meter values
    solarEnergyDetails = request.session['api_res_site_energyDetails']['energyDetails']
    print('api_request_success:')
    print(api_request_success)
    for meterTelemetry in solarEnergyDetails['meters']:
        if meterTelemetry['type'] == 'Consumption':
            meterTelemetryConsumption = meterTelemetry['values']
            print('meterTelemetryConsumption:')
            print(meterTelemetryConsumption)
        elif meterTelemetry['type'] == 'Production':
            meterTelemetryProduction = meterTelemetry['values']
            print('meterTelemetryProduction:')
            print(meterTelemetryProduction)

    # Parse Consumption & Production meter values and write data into SolarMeasurement Model
    model_write_success = True
    try:
        for consumptionValue in meterTelemetryConsumption:
            if 'value' in consumptionValue:
                sMeasurement, created = SolarMeasurement.objects.get_or_create(time=dateutil.parser.parse(consumptionValue['date']), defaults={'timeUnit': solarEnergyDetails['timeUnit'], 'unit': solarEnergyDetails['unit'], 'energyConsumtion': consumptionValue['value']})
                sMeasurement.save()
                print('consumptionValue:')
                print(consumptionValue)
                print('---- sMeasurement:')
                print(sMeasurement)
                print('created:')
                print(created)
        for productionValue in meterTelemetryProduction:
            if 'value' in productionValue:
                print('---- productionValue:')
                print(productionValue)
                sMeasurement = SolarMeasurement.objects.filter(time=dateutil.parser.parse(productionValue['date']))
                print('---- BEFORE sMeasurement:')
                print(sMeasurement)
                if not sMeasurement:
                    print('---- ERROR: MISSING ENTRY IN PRODUCTION LIST ----')
                    # raise ValueError('Unexpacted missing value for given time: ' + productionValue['time'])
                # NOTE: CONTINUE HERE AND TRY TO SKIP UPDATE IF VALUE ALREADY UPDATED
                
                print(sMeasurement.values('value').first())
                # if not sMeasurement.values('value').first():
                #     sMeasurement.update(energyProduction = productionValue['value'])
                #     print('---- AFTER sMeasurement:')
                #     print(sMeasurement)
                # else:
                #     print('---- NO UPDATE sMeasurement:')
                   
    except:
        pass
        model_write_success = False

    print('model_write_success:')
    print(model_write_success)
    
    """
    time = models.DateTimeField(default=timezone.now)
    timeUnit = models.CharField(max_length=10)
    unit = models.CharField(max_length=10)
    energyProduction = models.PositiveIntegerField(default=0)
    energyConsumtion 
    """

    api_res_site_details = request.session['api_res_site_details']
    api_res_site_overview = request.session['api_res_site_overview']
    api_res_site_dataPeriod = request.session['api_res_site_dataPeriod']
    api_res_site_energy = request.session['api_res_site_energy']
    api_res_site_energyDetails = request.session['api_res_site_energyDetails']

    context = {
        'title': 'Home',
        'API_results': {
            'api_res_site_details': api_res_site_details,
            'api_res_site_overview': api_res_site_overview,
            'api_res_site_dataPeriod': api_res_site_dataPeriod,
            'api_res_site_energy': api_res_site_energy,
            'api_res_site_energyDetails': api_res_site_energyDetails,
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
    cashed_since = 10000000000

    if is_cached and (solarEdgeAPIKey != None) and ('cache_ts' in request.session):
        cashed_since = time.time() - request.session['cache_ts'] 

    
    if (not is_cached) or (cashed_since >= 7200) or request.session['api_res_site_overview'] == None:
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

@login_required
def cron(request):
    return HttpResponse('all done!')
