from django.shortcuts import render
from django.http import HttpResponse

from django.conf import settings
import solaredge
import requests


APIKEY = getattr(settings, "solarEdgeAPIKey", None)
APIID = getattr(settings, "solarEdgeID", None)
# APIKEY = settings.solarEdgeAPIKey
# APIID = settings.solarEdgeID


def home(request):
    api_address='http://api.openweathermap.org/data/2.5/weather?appid=0c42f7f6b53b244c78a418f4f181282a&q='
    url = api_address + city
    json_data = requests.get(url).json()
    format_add = json_data['base']
    print(format_add)


    # http = urllib3.PoolManager()
    # req = http.request('GET', 'https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/overview?api_key=' + solarEdgeAPIKey)
    # print(req)

    # with urlopen("https://monitoringapi.solaredge.com/site/" + solarEdgeID + "/overview?api_key=" + solarEdgeAPIKey) as response:
    #   source = response.read()
    # print(source)

    # r = requests.get("https://monitoringapi.solaredge.com/site/" + solarEdgeID + "/overview?api_key=" + solarEdgeAPIKey)
    # r.json()

    # print('APIKEY: ' + APIKEY)

    # details = s.get_details(APIID)

    context = {
        'settings': settings,
        'APIKEY': APIKEY,
        'APIID': APIID        
    }
    return render(request, 'analyzer/home.html', context)


def about(request):
    return render(request, 'analyzer/about.html', {'title': 'About'})
