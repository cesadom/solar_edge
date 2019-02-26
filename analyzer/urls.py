from django.urls import path
from django.conf.urls import url
from . import views
from smartdevice.views import createSmartDevice_view

urlpatterns = [
    path('', views.home, name='analyzer-home'),
    url(r'^api/data/$', views.get_data, name='api-data'),
    path('chart/', views.chart, name='analyzer-chart'),
    path('api_plain/', views.api_plain, name='analyzer-api_plain'),
    path('about/', views.about, name='analyzer-about'),
    path('cron/', views.cron, name='analyzer-cron'),
    path('start_thread/', views.start_thread, name='analyzer-start_thread'),
    path('createSmartDevice/', createSmartDevice_view, name='createSmartDevice'),
]