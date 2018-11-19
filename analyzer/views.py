from django.shortcuts import render
from django.http import HttpResponse
# import json
# # from urllib.request import urlopen
# #import analyzer_settings as settings
# # import requests
# import urllib3
from django.conf import settings
import solaredge

APIKEY = getattr(settings, "solarEdgeAPIKey", None)
APIID = getattr(settings, "solarEdgeID", None)

# http = urllib3.PoolManager()
# req = http.request('GET', 'https://monitoringapi.solaredge.com/site/' + solarEdgeID + '/overview?api_key=' + solarEdgeAPIKey)
# print(req)

# with urlopen("https://monitoringapi.solaredge.com/site/" + solarEdgeID + "/overview?api_key=" + solarEdgeAPIKey) as response:
# 	source = response.read()
# print(source)

# r = requests.get("https://monitoringapi.solaredge.com/site/" + solarEdgeID + "/overview?api_key=" + solarEdgeAPIKey)
# r.json()

# print('APIKEY: ' + APIKEY)
s = solaredge.Solaredge(APIKEY)

# details = s.get_details(APIID)


posts = [
    {
        'author': 'CoreyMS',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'August 27, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'August 28, 2018'
    }
]


def home(request):
    context = {
        'posts': posts
    }
    return render(request, 'analyzer/home.html', context)


def about(request):
    return render(request, 'analyzer/about.html', {'title': 'About'})