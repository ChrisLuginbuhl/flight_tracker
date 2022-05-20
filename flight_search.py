import logging
import requests
from credentials import TEQUILA_FLIGHTSEARCH_API_KEY
import ssl
import json
from pprint import pprint

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

class FlightSearch:
    def check_tls(self):
        """Method for checking that TLS is at least v1.2 as required by API. Search method returns list of
            dicts as results"""
        logger.debug(f"SSL Version: {ssl.OPENSSL_VERSION}")
        s = requests.Session()
        logger.debug(f"TLS Version: {s.get('https://www.howsmyssl.com/a/check').json()['tls_version']}")

    def search_for_flight(self, origin_city_code, dest_city_code, from_date, to_date, min_nights, max_nights,
                           round_trip, max_stops, currency) -> list:
        """Asks tequila for flights, returns a list of dicts (if there are any matching flights)"""
        tequila_flight_search_endpoint = "https://tequila-api.kiwi.com/v2/search"
        teq_search_params = {
            'fly_from': f'city:{origin_city_code}',
            'fly_to': dest_city_code,
            'date_from': from_date,
            'date_to': to_date,
            'nights_in_dst_from': min_nights,
            'nights_in_dst_to': max_nights,
            'flight_type': round_trip,
            'max_stopovers': max_stops,
            'curr': currency,
        }
        teq_search_header = {
            "apikey": TEQUILA_FLIGHTSEARCH_API_KEY,
            "Content-Type": "application/json",
            # "Accept-Encoding": "gzip"
        }

        response = requests.get(url=tequila_flight_search_endpoint, params=teq_search_params, headers=teq_search_header)
        try:
            response.raise_for_status()
        except requests.HTTPError:
            logger.debug(f"Status: {response.json()['status']}")
            logger.debug(f"Error text: {response.json()['error']}")
        else:
            logger.error('Another error occurred during Tequila flight search')
        flights = response.json()
        with open("flight_search_results.json", 'a') as log_file:
            json.dump(flights, log_file, indent=4, sort_keys=True)
        #     logger.debug(f"Here is the complete JSON: {flights}")
        return flights['data']
