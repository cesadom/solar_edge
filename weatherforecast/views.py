from django.shortcuts import render
from datetime import date, datetime, timedelta

# calculate the most sunny days between the given dates and return a sorted list from the most sunny to the less sunny day
# TODO: finalize the function by adding weatherforecast
def sunnydays(date_from, date_to):
	return [
		{'date': str(date.today() + timedelta(5)), 'sunhours': 6},
		{'date': str(date.today() + timedelta(2)), 'sunhours': 5},
		{'date': str(date.today()), 'sunhours': 4.5}
	]
