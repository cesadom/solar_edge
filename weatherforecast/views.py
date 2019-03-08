from django.shortcuts import render
from datetime import date, datetime, timedelta
import requests
from weatherforecast.models import WeatherForecast, WeatherForecastDayHour

# Load worldweatheronline.com API Key and Configuration
weatherAPIKEY = "cdb9121d690f43aca7a110709191801"
weatherAPILocation = "Meilen"
weatherAPIForecastDays = str(7)
weatherAPIURL = "http://api.worldweatheronline.com/premium/v1/weather.ashx?key=" + weatherAPIKEY + "&q=" + weatherAPILocation + "&format=json&num_of_days=" + weatherAPIForecastDays

# calculate the most sunny days between the given dates and return a sorted list from the most sunny to the less sunny day
# TODO: finalize the function by adding weatherforecast
def sunnydays(date_from, date_to):
	return [
		{'date': str(date.today() + timedelta(5)), 'sunhours': 6},
		{'date': str(date.today() + timedelta(2)), 'sunhours': 5},
		{'date': str(date.today()), 'sunhours': 4.5}
	]

def sunPerDay(day=date.today()):
	print("sunPerDay for: " + str(day))
	try:
		# look for latest weatherForecast_obj.forecastDate of the forecast for 'date'
		weatherForecast_obj = WeatherForecast.objects.filter(date=day.strftime('%Y-%m-%d')).latest('forecastDate')
		print(weatherForecast_obj) 
		
		# take weatherForecast_obj.sunHours
		return weatherForecast_obj.sunHours
	except:
		print("ERROR on reading WeatherForecast!")
		return False

def logWeatherForecast():
    # Try to load data from API
	api_request_success = True
	weather_api_res=None
	try:
		# Weather API requests
		weather_api_res=requests.get(weatherAPIURL).json()
		# print(weather_api_res)
	except:
		api_request_success = False
		pass

	try:
		weather_api_weatherForecast = weather_api_res['data']['weather']
		weather_api_forecastedSunHours = dict()
		for forecastedDate in weather_api_weatherForecast:
			# sMeasurement, created = SolarMeasurement.objects.get_or_create(time=dateutil.parser.parse(consumptionValue['date']), defaults={'timeUnit': solarEnergyDetails['timeUnit'], 'unit': solarEnergyDetails['unit'], 'energyConsumtion': consumptionValue['value']})
			# sMeasurement.save()
			# sMeasurement = SolarMeasurement.objects.filter(time=dateutil.parser.parse(productionValue['date']))
			# sMeasurement.update(energyProduction = productionValue['value'])
			# print(forecastedDate['date'])
			weatherForecast_obj, created = WeatherForecast.objects.get_or_create(forecastDate=datetime.today().strftime('%Y-%m-%d'), date=forecastedDate['date'], defaults={'sunHours': forecastedDate['sunHour']})
			weatherForecast_obj.save()
			# print(forecastedDate['sunHour'])
			value=forecastedDate['date']
			weather_api_forecastedSunHours[value]={'sunHour': forecastedDate['sunHour']}
			weather_api_forecastedSunHours[value]['chanceofsunshineAtDayHour'] = {}
			for forecastedHours in forecastedDate['hourly']:
				forecastedHoursTime_str=str(forecastedHours['time'])
				# print("forecastedHoursTime_str: " + forecastedHoursTime_str)
				forecastedHoursChanceofsunshine_str=str(forecastedHours['chanceofsunshine'])
				print(forecastedDate['date'] + ":" + forecastedHoursTime_str + " -> " + forecastedHoursChanceofsunshine_str + " %")
				weather_api_forecastedSunHours[value]['chanceofsunshineAtDayHour'][forecastedHoursTime_str] = forecastedHoursChanceofsunshine_str
				weatherForecastDayHour_obj, created = WeatherForecastDayHour.objects.get_or_create(time=forecastedHours['time'], weatherForecast=weatherForecast_obj, chanceofsunshine=forecastedHours['chanceofsunshine'])
		# print(weather_api_forecastedSunHours)
	except:
		pass
		weather_api_forecastedSunHours = None

	return True