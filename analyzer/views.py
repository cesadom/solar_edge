from django.shortcuts import render
from django.http import HttpResponse

from django.conf import settings
import solaredge
import requests


APIKEY = getattr(settings, 'SEDGE_APIKEY', None)
APIID = getattr(settings, 'SEDGE_SITEID', None)
# APIKEY = settings.solarEdgeAPIKey
# APIID = settings.solarEdgeID


def home(request):
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

     

    ## TRY TO CACHE LIKE IN THIS EXAMPLE FROM https://simpleisbetterthancomplex.com/tutorial/2018/02/03/how-to-use-restful-apis-with-django.html ##
    # is_cached = ('geodata' in request.session)

    # if not is_cached:
    #     ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '')
    #     response = requests.get('http://freegeoip.net/json/%s' % ip_address)
    #     request.session['geodata'] = response.json()

    # geodata = request.session['geodata']

    # return render(request, 'core/home.html', {
    #     'ip': geodata['ip'],
    #     'country': geodata['country_name'],
    #     'latitude': geodata['latitude'],
    #     'longitude': geodata['longitude'],
    #     'api_key': 'AIzaSyC1UpCQp9zHokhNOBK07AvZTiO09icwD8I',  # Don't do this! This is just an example. Secure your keys properly.
    #     'is_cached': is_cached
    # }


    # api_address='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/overview?api_key=' + solarEdgeAPIKey
    # api_res_site_list = None
    
    # try:
    #     api_res_site_list = requests.get(api_address).json()
    # except:
    #     pass
    
    
    api_res_site_list = None
    api_res_site_details = None
    api_res_site_overview = None
    api_res_site_dataPeriod = None
    api_res_site_energy = None
    api_res_site_energyDetails = None
    api_res_site_timeFrameEnergy = None
    api_res_site_power = None
    api_res_site_powerDetails = None
    api_res_site_currentPowerFlow = None
    api_res_site_envBenefits = None
    api_res_site_inventory = None
    api_res_equip_list = None
    
    try:
        api_adr_site_list='https://monitoringapi.solaredge.com/sites/list?api_key=' + solarEdgeAPIKey
        api_res_site_list=requests.get(api_adr_site_list).json()
        api_adr_site_details='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/details?api_key=' + solarEdgeAPIKey
        api_res_site_details=requests.get(api_adr_site_details).json()
        api_adr_site_overview='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/overview?api_key=' + solarEdgeAPIKey
        api_res_site_overview=requests.get(api_adr_site_overview).json()
        api_adr_site_dataPeriod='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/dataPeriod?api_key=' + solarEdgeAPIKey
        api_res_site_dataPeriod=requests.get(api_adr_site_dataPeriod).json()
        api_adr_site_energy='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/energy?timeUnit=DAY&endDate=2018-12-31&startDate=2018-12-01&api_key=' + solarEdgeAPIKey
        api_res_site_energy=requests.get(api_adr_site_energy).json()
        api_adr_site_energyDetails='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/energyDetails?meters=PRODUCTION,CONSUMPTION&timeUnit=DAY&startTime=2018-12-01%2000:00:00&endTime=2018-12-07%2023:59:59&api_key=' + solarEdgeAPIKey
        api_res_site_energyDetails=requests.get(api_adr_site_energyDetails).json()
        api_adr_site_timeFrameEnergy='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/timeFrameEnergy?timeUnit=DAY&endDate=2018-12-31&startDate=2018-12-01&api_key=' + solarEdgeAPIKey
        api_res_site_timeFrameEnergy=requests.get(api_adr_site_timeFrameEnergy).json()
        api_adr_site_power='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/power?startTime=2018-12-07%2007:00:00&endTime=2018-12-07%2019:00:00&api_key=' + solarEdgeAPIKey
        api_res_site_power=requests.get(api_adr_site_power).json()
        api_adr_site_powerDetails='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/powerDetails?meters=PRODUCTION,CONSUMPTION&startTime=2018-12-07%2000:00:00&endTime=2018-12-07%2023:59:59&api_key=' + solarEdgeAPIKey
        api_res_site_powerDetails=requests.get(api_adr_site_powerDetails).json()
        api_adr_site_currentPowerFlow='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/currentPowerFlow?api_key=' + solarEdgeAPIKey
        api_res_site_currentPowerFlow=requests.get(api_adr_site_currentPowerFlow).json()
        api_adr_site_envBenefits='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/envBenefits?systemUnits=Imperial&api_key=' + solarEdgeAPIKey
        api_res_site_envBenefits=requests.get(api_adr_site_envBenefits).json()
        api_adr_site_inventory='https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/inventory?api_key=' + solarEdgeAPIKey
        api_res_site_inventory=requests.get(api_adr_site_inventory).json()
        api_adr_equip_list='https://monitoringapi.solaredge.com/equipment/' + solarEdgeID + '/list?api_key=' + solarEdgeAPIKey
        api_res_equip_list=requests.get(api_adr_equip_list).json()
    except:
        pass

    context = {
        'form_submitted': form_submitted,
        'API_results': {
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
    return render(request, 'analyzer/home.html', context)


def about(request):
    return render(request, 'analyzer/about.html', {'title': 'About'})
