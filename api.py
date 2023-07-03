'''
API subsystem
Group 2,
Devin Spiker
Richard Hailey
David Lambert
CMSC 495 6381
'''
import requests

class Api:
    """class encapsulaing exchangerate-api request functionality"""

    # Class attributes that don't change between instances
    # codes_url is the api endpoint to get the list of currency codes
    # conversion_url is the api endpoint to conversions for the provided base
    # use the .format(*args) function to format the urls with your
    # api key at {0} and the base currency at {1}
    codes_url: str = "https://v6.exchangerate-api.com/v6/{0}/codes"
    conversion_url: str = "https://v6.exchangerate-api.com/v6/{0}/latest/{1}"

    def __init__(self, api_key: str):
        """Create an api class for exchangerate-api

        Keyword arguments:
        api_key -- users api key for exchangerate-api
        """
        self.api_key = api_key

    def get_currency_list(self) -> list[list] | None:
        """Query the api for all supported currencies

        return list[list] (or none on failure) of the available currencies
        the lists in the returned list contain the currency code in index 0 and
        the currency long form name in index 1
        """
        endpoint = Api.codes_url.format(self.api_key)
        data = self.get(endpoint)
        if data is not None:
            return data["supported_codes"]

    def get_currency(self, base: str) -> dict | None:
        """Retrieve the conversion rates for a specific currency

        Keyword arguments:
        base -- the starting currency to conver

        return dict (or none on failure) with conversion rates found at the
        "conversion_rates" key
        """
        endpoint = Api.conversion_url.format(self.api_key, base)
        return self.get(endpoint)

    def get(self, endpoint: str) -> dict | None:
        """helper funciton for reducing code duplication of get functionality

        Keyword arguments:
        endpoint -- the formatted api endpoint
        """
        response = requests.get(endpoint,timeout=10)
        if response.ok:
            return response.json()
