from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='analyzer-home'),
    path('about/', views.about, name='analyzer-about'),
    path('cron/', views.cron, name='analyzer-cron'),
]