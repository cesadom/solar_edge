from django.shortcuts import render
from datetime import datetime, timedelta

# calculate the most sunny days between the given dates and return a sorted list from the most sunny to the less sunny day
# TODO: finalize the function by adding weatherforecast
def sunnydays(date_from, date_to):
	return [
		{'date': datetime.now() + timedelta(5), 'sunhours': 6},
		{'date': datetime.now() + timedelta(2), 'sunhours': 5},
		{'date': datetime.now, 'sunhours': 4.5}
	]
