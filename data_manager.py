# import gzip
import requests
import logging
import json
from credentials import KIWI_API_KEY, SHEETY_TOKEN
from collections import defaultdict
from pprint import pprint

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

SHEETY_ENDPOINT = "https://api.sheety.co/d9c16105ada6ba4a8dfde1c1d0a1ed09/flightDeals100DaysOfCode/prices"


class DataManager:
    # This class is responsible for talking to the Google Sheet.

    def __init__(self):
        self.cities = []
        self.iata_codes = []
        self.price_thresholds = []
        self.num_cities = None
        self.spreadsheet = None
        self.joined_spreadsheet = None
        self.sheety_endpoint = SHEETY_ENDPOINT


    def get_from_sheety(self) -> dict:
        """returns data from sheety as dict of three lists. Includes iata codes so you can skip looking them up
        one at a time on Tequila with get_iata_codes()"""

        sheety_header = {
            "Content-Type": "application/json",
            "Authorization": SHEETY_TOKEN,
        }
        response = requests.get(url=self.sheety_endpoint, headers=sheety_header)
        response.raise_for_status()
        self.spreadsheet = response.json()
        # logger.debug(f"Spredsheet data: {self.spreadsheet}")
        # pprint(self.spreadsheet)
        self.num_cities = len(self.spreadsheet['prices'])
        logger.debug(f"num cities in sheety: {self.num_cities}")
        self.cities = [self.spreadsheet['prices'][i]['city'] for i in range(self.num_cities)]
        self.iata_codes = [self.spreadsheet['prices'][i]['iataCode'] for i in range(self.num_cities)]
        self.price_thresholds = [self.spreadsheet['prices'][i]['notificationThreshold'] for i in range(self.num_cities)]
        return {
               'city_names': self.cities,
               'iata_codes': self.iata_codes,
               'price_thresholds': self.price_thresholds
            }

    def get_iata_codes(self, city_name: str) -> str:
        tequila_endpoint = "https://tequila-api.kiwi.com/locations/query"
        tequila_params = {
            "term": city_name,
            "location_types": "city",
            "limit": 1
        }
        tequila_header = {
            "apikey": KIWI_API_KEY,
            "Accept-Encoding": "gzip"
        }
        # response is byte string. Looks like:  b'{"locations":[{"id":"toronto_on_ca","active":tru...
        response = requests.get(url=tequila_endpoint, params=tequila_params, headers=tequila_header)
        response.raise_for_status()
        logger.debug(f"response content: {response.content.decode('UTF-8')}, "
                     f"type: {type(response.content.decode('UTF-8'))}")
        data = json.loads(response.content.decode('UTF-8'))
        if data['locations'] == []:
            logger.warning(f"Could not find city code for {city_name}. Setting IATA code as 'N/A'")
            city_code = 'N/A'
        else:
            city_code = data['locations'][0]['code']
        logger.debug(f"City code from Tequila: {city_code}")
        return city_code

        # If response is gzipped (as Tequila offers to do):
        # gzipFile = gzip.GzipFile(fileobj=response.content)
        # result = gzipFile.read()
        # # result = gzip.decompress(response.read())
        # logger.debug(result)

    def join_data(self, c_names, i_codes):
        joined_data = {c_names[i]: i_codes[i] for i in range(self.num_cities)}
        self.joined_spreadsheet = self.spreadsheet.copy()
        for i in range(self.num_cities):
            self.joined_spreadsheet['prices'][i]['iataCode'] = joined_data[self.joined_spreadsheet['prices'][i]['city']]
        logger.debug(f"Joined spreadsheet: {self.joined_spreadsheet}")

    def write_city_codes(self):
        for i in range(self.num_cities):
            obj_id = str(self.joined_spreadsheet['prices'][i]['id'])
            sheety_put_endpoint = f"{self.sheety_endpoint}/{obj_id}" # obj_id for each city comes from spreadsheet json
            logger.debug(f"endpoint for PUT: {sheety_put_endpoint}")
            sheety_header = {
                "Content-Type": "application/json",
                "Authorization": SHEETY_TOKEN,
            }
            sheety_data = {  # note camel case (no spaces for spreadsheet column names)
                'price': {
                    'iataCode': self.joined_spreadsheet['prices'][i]['iataCode']
                }
            }
            response = requests.put(url=sheety_put_endpoint, json=sheety_data, headers=sheety_header)
            response.raise_for_status()
            logger.debug(response.text)

    def update_iata_codes(self):
        city_names = self.get_from_sheety()['city_names']  # from Sheety/google sheets
        iata_codes = [self.get_iata_codes(city) for city in city_names]  # get from Tequila search API
        # logger.debug(iata_codes)
        self.join_data(city_names, iata_codes)  # make a new dict in datamanager with city name and corresponding citycode
        self.write_city_codes()  # Put the city codes in the spreadsheet using Sheety
        return iata_codes

