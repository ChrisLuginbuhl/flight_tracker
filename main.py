# This program implements the Day 39 problem in 100 Days of Code. Reads a list of cities from a google spreadsheet,
# looks up IATA codes for those cities if any are missing, and searches for flights according to serach parameters
# in constants below. Results for most recent search saved in log file.  If any results that are below the price
# threshold, a notification is sent via SMS (Twilio)
# Chris Luginbuhl May 2022.

# Note that one_for_city as a Tequila search parameter no longer works (as used in Udemy solution).

from data_manager import DataManager
from flight_search import FlightSearch
from flight_data import FlightData
import logging
from notification_manager import NotificationManager
from datetime import datetime, timedelta

MIN_NIGHTS = 7  # Doesn't seem to matter if you pass an int or a string here. API docs say int.
MAX_NIGHTS = 28
CITY_FROM = 'YVR'
MAX_DAYS_AHEAD = 30  # How many days in the future can the departure be?
MIN_DAYS_AHEAD = 1
ROUND_TRIP = 'round'  # either 'round' or 'oneway'
MAX_STOPS = 0
CURRENCY = 'CAD'

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

data_mgr = DataManager()
flight_search = FlightSearch()
notification_mgr = NotificationManager()

# get IATA codes from Tequila or Sheety
sheety_data = data_mgr.get_from_sheety()
iata_code_list = sheety_data['iata_codes']
if '' in iata_code_list:
    logger.info('Updating iata code list...')
    iata_code_list = data_mgr.update_iata_codes()  # gets iata codes from Tequila API and updates Google sheet/sheety
    logger.info('Updating iata codes complete')
logger.debug(f"iata code list: {iata_code_list}")
price_thresholds = sheety_data['price_thresholds']

# Search for flights, find best price
from_date = (datetime.today() + timedelta(days=MIN_DAYS_AHEAD)).strftime('%d/%m/%Y')
to_date = (datetime.today() + timedelta(days=MAX_DAYS_AHEAD)).strftime('%d/%m/%Y')

# Clear old log file
log_file = open("flight_search_results.json", 'w')
log_file.write('\n')
log_file.close()

cheap_flights = []
for dest_city_code in iata_code_list:
    if dest_city_code != 'N/A':
        flight_data_result = flight_search.search_for_flight(CITY_FROM, dest_city_code, from_date, to_date, MIN_NIGHTS,
                                                               MAX_NIGHTS, ROUND_TRIP, MAX_STOPS, CURRENCY)
        if flight_data_result != []:
            best_flight = FlightData(flight_data_result).find_cheapest()
            print(f"Best flight from {best_flight['cityFrom']} to {best_flight['cityTo']} is {best_flight['price']}")
            index = iata_code_list.index(dest_city_code)
            if int(best_flight['price']) <= price_thresholds[index]:
                print("This is below the price threshold")
                cheap_flights.append(best_flight)
        else:
            print("Found no flights to this city")
    else:
        index = iata_code_list.index(dest_city_code)
        print(f"Skipping {sheety_data['city_names'][index]} because we are missing the IATA code for that city.")

notification_mgr.notify(cheap_flights)



