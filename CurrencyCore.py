'''
Core Subsystem
Group 2,
Devin Spiker
Richard Hailey
David Lambert
CMSC 495 6381
'''
import os
import datetime
import tkinter as tk
from tkinter import ttk
import json

import io
from dataclasses import dataclass
from database import Database
from api import Api

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
    def __init__(self, logging: bool = False,
                  cache_age: datetime.timedelta = datetime.timedelta(days=1)):
        self.cache_age = cache_age
        self.logging: bool = logging
        if self.logging:
            self.write_log(f"Init: cache age set to {str(cache_age)}")

        self.config = self.load_config()  # Load the configuration file
        self.api_key = self.config.get("API_KEY")
        if self.api_key is None:
            print("API_KEY not found in the configuration file.")
            self.write_log("API_KEY not found in the configuration file.")
        self.api = Api(self.api_key)
        currency_list = self.api.get_currency_list()
        if currency_list is None:
            print("Failed to reach api endpoint, check API_Key or network connections")
            self.write_log("Failed to reach api endpoint, check API_Key or network connections")
        self.database = Database()
        self.gui = CurrencyConverter(currency_list, self.run)

    def run(self):
        '''Redefining the run function for our programs purposes'''
        self.write_log("Start")
        conversion = self.get_input()
        if conversion is None:
            self.update_gui("Error: Numeric input only in 'Input Quantity' Field")
            self.write_log("End")
        currency = self.get_currency(conversion)
        if currency is None:
            # TODO: return better error message to user
            self.update_gui("ERROR")
            self.write_log("End")
            return
        conversion.rate = currency.conversion_rates[conversion.new]
        if conversion.rate is None:
            # TODO: return better error message to user
            self.update_gui("ERROR")
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

class CurrencyConverter(tk.Tk):
    '''Currency Converter Class GUI '''
    # pylint: disable=too-many-instance-attributes
    def __init__(self, currency_list: list[list], submit_function):
        '''Redefine init'''
        super().__init__()
        self.title('Currency Converter')
        self.geometry('700x700')
        self.config(background='black')

        self.label = ttk.Label(
            self, text='Currency Converter', background='black', foreground='gold'
            )
        self.label.pack()

        codes = [x[0] for x in currency_list]

        frame_input = ttk.Frame(self, padding=10)
        frame_input.pack(side="top", padx=50, pady=20)

        frame_convert = ttk.Frame(self, padding=10)
        frame_convert.pack(side="top", padx=50, pady=20)

        self.label_input_quantity = ttk.Label(
            frame_input,
             text='Input Quantity',
              background='black',
               foreground='gold')
        self.label_input_quantity.pack(side="left", padx=5, pady=5)

        self.input_quantity = tk.Text(
            frame_input,
             height=1,
              width=20,
               font=("Arial", 14),
                bg='red',
                 fg='gold')
        self.input_quantity.pack(side="left", padx=5, pady=5)

        self.label_convert_from = ttk.Label(
            frame_convert,
             text='Convert From',
              background='black',
               foreground='gold')
        self.label_convert_from.pack(side="left", padx=5, pady=5)

        self.selected_from = ttk.Combobox(frame_convert,state="readonly", values=codes)
        self.selected_from.set("USD")
        self.selected_from.pack(side="left", padx=5, pady=5)

        self.label_convert_to = ttk.Label(
            frame_convert,
             text='Convert To',
              background='black',
               foreground='gold')
        self.label_convert_to.pack(side="left", padx=5, pady=5)

        self.selected_to = ttk.Combobox(frame_convert,state="readonly", values=codes)
        self.selected_to.set("EUR")
        self.selected_to.pack(side="left", padx=5, pady=5)

        self.button = tk.Button(
            self,
             text='Submit',
              width=25,
               font=("Arial", 14),
                command=submit_function, bg='red', fg='gold')
        self.button.pack(side="bottom", padx=50, pady=20)

        self.output_box = tk.Text(
            self,
             height=1,
              width=40,
               font=("Arial", 14),
                bg='red',
                 fg='gold',
                  state="disabled"
            )
        self.output_box.pack(side="bottom", padx=50, pady=20)

    def getinput_quantity(self) -> float | None:
        '''Function for obtaining the input quantity from the GUI'''
        input_quantity = self.input_quantity.get(1.0, "end-1c")
        try:
            input_quantity = float(input_quantity)
        except ValueError:
            return None
        return input_quantity

    def output(self, user_input):
        '''function to display outout to GUI/user'''
        self.output_box.config(state='normal')
        self.output_box.delete(1.0, "end")
        self.output_box.insert(tk.END, user_input)
        self.output_box.config(state='disabled')

if __name__ == "__main__":
    #app = Core()
    #app.gui.mainloop()

    app = Core(logging=True)
    app.gui.mainloop()
    