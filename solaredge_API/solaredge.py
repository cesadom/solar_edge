import requests
import functools
import pytz
import dateutil.parser
import datetime as dt
from dateutil import rrule
from .misc import urljoin, pairwise

__title__ = "solaredge"
__version__ = "0.0.2"
__author__ = "Bert Outtier, EnergieID"
__license__ = "MIT"

BASEURL = 'https://monitoringapi.solaredge.com'


class Solaredge:
    """
    Object containing SolarEdge's site API-methods, and some functions that return Pandas DataFrames
    See https://www.solaredge.com/sites/default/files/se_monitoring_api.pdf
    """
    def __init__(self, site_token):
        """
        To communicate, you need to set a site token.
        Get it from your account.

        Parameters
        ----------
        site_token : str
        """
        self.token = site_token

    @functools.lru_cache(maxsize=128, typed=False)
    def get_list(self, size=100, start_index=0, search_text="", sort_property="",
                 sort_order='ASC', status='Active,Pending'):
        """
        Request all sites

        Returns
        -------
        dict
        """

        url = urljoin(BASEURL, "sites", "list")

        params = {
            'api_key': self.token,
            'size': size,
            'startIndex': start_index,
            'sortOrder': sort_order,
            'status': status
        }

        if search_text:
            params['searchText'] = search_text

        if sort_property:
            params['sortProperty'] = sort_property

        r = requests.get(url, params)
        r.raise_for_status()
        return r.json()

    @functools.lru_cache(maxsize=128, typed=False)
    def get_details(self, site_id):
        """
        Request details about a certain site

        Parameters
        ----------
        site_id : int

        Returns
        -------
        dict
        """
        url = urljoin(BASEURL, "site", site_id, "details")
        params = {
            'api_key': self.token
        }
        r = requests.get(url, params)
        r.raise_for_status()
        return r.json()

    @functools.lru_cache(maxsize=128, typed=False)
    def get_data_period(self, site_id):
        """
        Request the data period for a certain site.
        This returns the start and end dates for which there
        is data available.

        Use `get_data_period_parsed` to get the dates as datetime objects

        Parameters
        ----------
        site_id : int

        Returns
        -------
        dict
        """
        url = urljoin(BASEURL, "site", site_id, "dataPeriod")
        params = {
            'api_key': self.token
        }
        r = requests.get(url, params)
        r.raise_for_status()
        j = r.json()
        return j

    def get_data_period_parsed(self, site_id):
        """
        Request the data period for a certain site.
        This returns the start and end dates for which there
        is data available, as datetime objects

        Parameters
        ----------
        site_id : int

        Returns
        -------
        (pd.Timestamp, pd.Timestamp)
        """
        import pandas as pd
        j = self.get_data_period(site_id=site_id)
        tz = self.get_timezone(site_id=site_id)
        start, end = [pd.Timestamp(j['dataPeriod'][param]) for param in ['startDate', 'endDate']]
        start, end = start.tz_localize(tz), end.tz_localize(tz)
        return start, end

    def get_energy(self, site_id, start_date, end_date, time_unit='DAY'):
        url = urljoin(BASEURL, "site", site_id, "energy")
        params = {
            'api_key': self.token,
            'startDate': start_date,
            'endDate': end_date,
            'timeUnit': time_unit
        }
        r = requests.get(url, params)
        r.raise_for_status()
        return r.json()

    def get_time_frame_energy(self, site_id, start_date, end_date, time_unit='DAY'):
        url = urljoin(BASEURL, "site", site_id, "timeFrameEnergy")
        params = {
            'api_key': self.token,
            'startDate': start_date,
            'endDate': end_date,
            'timeUnit': time_unit
        }
        r = requests.get(url, params)
        r.raise_for_status()
        return r.json()

    def get_power(self, site_id, start_time, end_time):
        url = urljoin(BASEURL, "site", site_id, "power")
        params = {
            'api_key': self.token,
            'startTime': start_time,
            'endTime': end_time
        }
        r = requests.get(url, params)
        r.raise_for_status()
        return r.json()

    def get_overview(self, site_id):
        url = urljoin(BASEURL, "site", site_id, "overview")
        params = {
            'api_key': self.token
        }
        r = requests.get(url, params)
        r.raise_for_status()
        return r.json()

    def get_power_details(self, site_id, start_time, end_time, meters=None):
        url = urljoin(BASEURL, "site", site_id, "powerDetails")
        params = {
            'api_key': self.token,
            'startTime': start_time,
            'endTime': end_time
        }

        if meters:
            params['meters'] = meters

        r = requests.get(url, params)
        r.raise_for_status()
        return r.json()

    def get_energy_details(self, site_id, start_time, end_time, meters=None, time_unit="DAY"):
        """
        Request Energy Details for a specific site and timeframe

        Use `get_energy_details_dataframe` to get the result as a Pandas DataFrame

        Parameters
        ----------
        site_id : int
        start_time : str
            needs to have the format '%Y-%m-%d %H:%M:%S' ("2018-02-15 10:00:00")
        end_time : str
            see `start_time
        meters : str
            default None
            options: any combination of PRODUCTION, CONSUMPTION, SELFCONSUMPTION, FEEDIN, PURCHASED
                separated by a comma. eg: "PRODUCTION,CONSUMPTION"
        time_unit : str
            default DAY
            options: QUARTER_OF_AN_HOUR, HOUR, DAY, WEEK, MONTH, YEAR
            Note that QUARTER_OF_AN_HOUR and HOUR are restricted to one month of data,
            DAY is restricted to one year of data, the others are unrestricted

        Returns
        -------
        dict
        """
        url = urljoin(BASEURL, "site", site_id, "energyDetails")
        params = {
            'api_key': self.token,
            'startTime': start_time,
            'endTime': end_time,
            'timeUnit': time_unit
        }

        if meters:
            params['meters'] = meters

        r = requests.get(url, params)
        r.raise_for_status()

        j = r.json()
        return j

    def get_energy_details_dataframe(self, site_id, start_time, end_time, meters=None, time_unit="DAY"):
        """
        Request Energy Details for a certain site and timeframe as a Pandas DataFrame

        Parameters
        ----------
        site_id : int
        start_time : str | dt.date | dt.datetime
            Can be any date or datetime object (also pandas.Timestamp)
            Timezone-naive objects will be treated as local time at the site
        end_time : str | dt.date | dt.datetime
            See `start_time`
        meters : [str]
            default None
            list with any combination of these terms: PRODUCTION, CONSUMPTION, SELFCONSUMPTION, FEEDIN, PURCHASED
        time_unit : str
            default DAY
            options: QUARTER_OF_AN_HOUR, HOUR, DAY, WEEK, MONTH, YEAR
            Note that this method works around the usage restrictions by requesting chunks of data

        Returns
        -------
        pandas.DataFrame
        """
        from .parsers import parse_energydetails
        import pandas as pd

        tz = self.get_timezone(site_id=site_id)
        if meters:
            meters = ','.join(meters)

        # use a generator to do some lazy loading and to (hopefully) save some memory when requesting large periods of time
        def generate_frames():
            # work around the usage restrictions by creating intervals to request data in
            for start, end in self.intervalize(time_unit=time_unit, start=start_time, end=end_time):
                # format start and end in the correct string notation
                start, end = [self._fmt_date(date_obj=time, fmt='%Y-%m-%d %H:%M:%S', tz=tz) for time in [start, end]]
                j = self.get_energy_details(site_id=site_id, start_time=start, end_time=end, meters=meters, time_unit=time_unit)
                frame = parse_energydetails(j)
                yield frame

        frames = generate_frames()
        df = pd.concat(frames)
        df = df.drop_duplicates()
        df = df.tz_localize(tz)
        return df

    def get_current_power_flow(self, site_id):
        url = urljoin(BASEURL, "site", site_id, "currentPowerFlow")
        params = {
            'api_key': self.token
        }

        r = requests.get(url, params)
        r.raise_for_status()
        return r.json()

    def get_storage_data(self, site_id, start_time, end_time, serials=None):
        url = urljoin(BASEURL, "site", site_id, "storageData")
        params = {
            'api_key': self.token,
            'startTime': start_time,
            'endTime': end_time
        }

        if serials:
            params['serials'] = serials.join(',')

        r = requests.get(url, params)
        r.raise_for_status()
        return r.json()

    def get_inventory(self, site_id):
        url = urljoin(BASEURL, "site", site_id, "inventory")
        params = {
            'api_key': self.token
        }
        r = requests.get(url, params)
        r.raise_for_status()
        return r.json()

    def get_timezone(self, site_id):
        """
        Get the timezone of a certain site (eg. 'Europe/Brussels')

        Parameters
        ----------
        site_id : int

        Returns
        -------
        str
        """
        details = self.get_details(site_id=site_id)
        tz = details['details']['location']['timeZone']
        return tz

    @staticmethod
    def _fmt_date(date_obj, fmt, tz=None):
        """
        Convert any input to a valid datestring of format
        If you pass a localized datetime, it is converted to tz first

        Parameters
        ----------
        date_obj : str | dt.date | dt.datetime

        Returns
        -------
        str
        """
        if isinstance(date_obj, str):
            try:
                dt.datetime.strptime(date_obj, fmt)
            except ValueError:
                date_obj = dateutil.parser.parse(date_obj)
            else:
                return date_obj
        if hasattr(date_obj, 'tzinfo') and date_obj.tzinfo is not None:
            if tz is None:
                raise ValueError('Please supply a target timezone')
            _tz = pytz.timezone(tz)
            date_obj = date_obj.astimezone(_tz)

        return date_obj.strftime(fmt)

    @staticmethod
    def intervalize(time_unit, start, end):
        """
        Create pairs of start and end with regular intervals, to deal with usage restrictions on the API
        e.g. requests with `time_unit="DAY"` are limited to 1 year, so when `start` and `end` are more
        than 1 year apart, pairs of timestamps will be generated that respect this limit.

        Parameters
        ----------
        time_unit : str
            options: QUARTER_OF_AN_HOUR, HOUR, DAY, WEEK, MONTH, YEAR
        start : dt.datetime | pd.Timestamp
        end : dt.datetime | pd.Timestamp

        Returns
        -------
        ((pd.Timestamp, pd.Timestamp))
        """
        import pandas as pd

        if time_unit in {"WEEK", "MONTH", "YEAR"}:
            # no restrictions, so just return start and end
            return [(start, end)]
        elif time_unit == "DAY":
            rule = rrule.YEARLY
        elif time_unit in {"QUARTER_OF_AN_HOUR", "HOUR"}:
            rule = rrule.MONTHLY
        else:
            raise ValueError('Unknown interval: {}. Choose from QUARTER_OF_AN_HOUR, HOUR, DAY, WEEK, MONTH, YEAR')

        res = []
        for day in rrule.rrule(rule, dtstart=start, until=end):
            res.append(pd.Timestamp(day))
        res.append(end)
        res = sorted(set(res))
        res = pairwise(res)
        return res
