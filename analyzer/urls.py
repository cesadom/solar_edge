from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.home, name='analyzer-home'),
    url(r'^api/data/$', views.get_data, name='api-data'),
    path('chart/', views.chart, name='analyzer-chart'),
    path('api_plain/', views.api_plain, name='analyzer-api_plain'),
    path('about/', views.about, name='analyzer-about'),
    path('cron/', views.cron, name='analyzer-cron'),
]