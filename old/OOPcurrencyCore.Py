import requests

# Suppose the Currency class is in a module named currency_module.py
from currency_module import Currency

class CurrencyExchange:
    API_URL = "https://api.exchangerate-api.com/v4/latest/{}"

    def __init__(self, from_currency: Currency, to_currency: Currency, api_key=None):
        self.from_currency = from_currency
        self.to_currency = to_currency
        self.api_key = api_key if api_key else "your_default_api_key"

    def get_exchange_rate(self):
        response = requests.get(self.API_URL.format(self.from_currency.name) + f"?access_key={self.api_key}")
        data = response.json()
        exchange_rate = data['rates'][str(self.to_currency.name)]
        return exchange_rate


class Application:
    def __init__(self, database, currency_exchange):
        self.database = database
        self.currency_exchange = currency_exchange
        self.currencies = ['USD', 'EUR', 'JPY', 'GBP', 'AUD', 'CAD', 'CHF', 'CNY', 'SEK', 'NZD']

    def search(self, from_currency, to_currency):
        # First, check if the exchange rate is already in the database
        currency_data = self.database.find_currency(from_currency, to_currency)
        if currency_data:
            return currency_data['exchange_rate']

        # If the exchange rate isn't in the database, use the API to fetch it
        exchange_rate = self.currency_exchange.get_exchange_rate()

        # Save the new exchange rate to the database
        self.database.insert_currency(from_currency, to_currency, exchange_rate)

        return exchange_rate


if __name__ == "__main__":
    from db_module import CurrencyDatabase

    # Initialize the necessary objects
    db = CurrencyDatabase()

    user_api_key = "the_api_key_user_entered"  # You will get this from the GUI
    currency_exchange = CurrencyExchange(Currency('USD'), Currency('EUR'), user_api_key)

    app = Application(db, currency_exchange)

    # Call the search method
    exchange_rate = app.search(Currency('USD'), Currency('EUR'))

    print(f"The exchange rate from USD to EUR is {exchange_rate}")
