import logging
logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


class FlightData:
    """Takes a list of dicts of flight search results (response.json()['data']). Has method for returning dict
    of cheapest flight"""
    def __init__(self, fl_data: list):
        self.data = fl_data

    def find_cheapest(self):
        # Doesn't work - can't figure out why. Works on min_test.py data.
        # minPricedItem = min(self.data, key=lambda x: int(x['price']))
        # logger.debug(minPricedItem)
        # return minPricedItem

        # Try this instead. And don't forget prices in data are strings!
        prices = [int(flight['price']) for flight in self.data]
        logger.debug(f"FlightData.findcheapest() says: Prices are: {prices}")
        lowest_price = min(prices)
        position = prices.index(lowest_price)
        return self.data[position]
