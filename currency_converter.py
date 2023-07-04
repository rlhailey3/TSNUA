'''
Core Subsystem
Group 2,
Devin Spiker
Richard Hailey
David Lambert
CMSC 495 6381
'''
import datetime
import json
from dataclasses import dataclass
from include.database import Database
from include.api import Api
from include.gui import Gui

@dataclass
class Conversion:
    '''Conversion class for Conversion objects'''
    base: str
    new: str
    base_value: float
    rate: float | None = None
    results: float | None = None

@dataclass
class Currency:
    '''Class for Currency objects'''
    base: str
    conversion_rates: dict[str, float]
    timestamp: datetime.datetime

class Core:
    '''Core class which houses primary software components'''
    def __init__(self):
        config = self.load_config()
        api_key = config["API_KEY"]
        mongo_host: str = config["mongo"]["host"]
        mongo_port: int = config["mongo"]["port"]
        d_days = config["cache"]["days"]
        d_hours = config["cache"]["hours"]
        d_minutes = config["cache"]["minutes"]
        d_seconds = config["cache"]["seconds"]
        self.cache_age = datetime.timedelta(
                days=d_days,
                hours=d_hours,
                minutes=d_minutes,
                seconds=d_seconds)
        self.logging: bool = config["logging"]
        self.write_log(f"Init: cache age set to {str(self.cache_age)}")
        if api_key is None:
            print("API_KEY not found in the configuration file.")
            self.write_log("API_KEY not found in the configuration file.")
            exit(1)
        self.api = Api(api_key)
        currency_list = self.api.get_currency_list()
        if currency_list is None:
            print("Failed to reach api endpoint, check API_Key or network connections")
            self.write_log("Failed to reach api endpoint, check API_Key or network connections")
            exit(1)
        self.database = Database(host=mongo_host, port=mongo_port)
        self.gui = Gui(currency_list, self.run)

    def run(self):
        '''Redefining the run function for our programs purposes'''
        self.write_log("Start")
        conversion = self.get_input()
        if conversion is None:
            self.update_gui("Error: Numeric input only in 'Input Quantity' Field")
            self.write_log("End")
            return
        currency = self.get_currency(conversion)
        if currency is None:
            # TODO: return better error message to user
            self.update_gui("Check remaining API request credits")
            self.write_log("API currency query failure")
            return
        conversion.rate = currency.conversion_rates[conversion.new]
        if conversion.rate is None:
            self.update_gui("Unable to find conversion between selected currencies")
            return
        conversion.results = self.convert(conversion)
        self.write_log(f'Conversion: {conversion.base} {conversion.base_value}'
            + f'= {conversion.new} {conversion.results}')#line too long
        self.write_log("End")
        self.update_gui(f'Conversion: {conversion.base} {conversion.base_value}'
            + f'= {conversion.new} {conversion.results}')

    def write_log(self, log: str) -> None:
        '''Function that enables logging'''
        if self.logging:
            with open("./logfile.txt", "a+", encoding="utf8") as logfile:
                timestamp = str(datetime.datetime.now())
                entry = f"{timestamp} - {log}\n"
                logfile.write(entry)

    def get_input(self) -> Conversion | None:
        '''function for obtaining input from user'''
        self.write_log("start get_input()")
        base = self.gui.selected_from.get()
        new = self.gui.selected_to.get()
        value = self.gui.getinput_quantity()
        if value is None:
            self.write_log("Invalid base_value input")
            self.write_log("end get_input()")
            return None
        self.write_log(f"base currency: {base}")
        self.write_log(f"new currency: {new}")
        self.write_log(f"base_value: {str(value)}")
        self.write_log("end get_input()")
        return Conversion(base, new, value)

    def get_currency(self, conversion) -> Currency | None:
        '''Function for conducting currency conversion'''
        self.write_log("start get_currency()")
        currency_data = self.database.get_currency(conversion.base)
        self.write_log("cache database queried")
        update = False
        if currency_data is not None:
            self.write_log("cache entry found")
            old_time = datetime.datetime.fromisoformat(currency_data["timestamp"])
            now_time = datetime.datetime.now()
            delta = now_time - old_time
            if delta > self.cache_age:
                self.write_log("cache entry expired")
                update = True
        if currency_data is None or update:
            self.write_log("query API")
            currency_data = self.api.get_currency(conversion.base)
            update = True
        if update and currency_data is not None:
            self.write_log("updating cache entry")
            self.database.update_currency(
                {
                    "base_code": currency_data["base_code"],
                    "conversion_rates": currency_data["conversion_rates"],
                    "timestamp": str(datetime.datetime.now())
                }
            )
        if currency_data is None:
            self.write_log("no currency data found")
            self.write_log("End get_currency()")
            return None
        currency = Currency(
            base=currency_data["base_code"],
            conversion_rates=currency_data["conversion_rates"],
            timestamp=datetime.datetime.now())
        self.write_log("End get_currency()")
        return currency

    def convert(self, conversion):
        '''Function for running conversion'''
        return conversion.rate * conversion.base_value

    def update_gui(self, message):
        '''Function for updating GUI'''
        self.gui.output(message)

    def load_config(self):
        '''Loads json file'''
        with open("config.json",encoding="utf8") as config_file:
            return json.load(config_file)

if __name__ == "__main__":
    app = Core()
    app.gui.mainloop()
#end of class
