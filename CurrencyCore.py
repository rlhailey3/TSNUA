import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.messagebox import showinfo

import json
from api import Api
from database import Database


import io
import datetime
from dataclasses import dataclass


@dataclass
class Conversion:
    base: str
    new: str
    base_value: float
    rate: float | None = None
    results: float | None = None


@dataclass
class Currency:
    base: str
    conversion_rates: dict[str, float]
    timestamp: datetime.datetime


class Core:
    def __init__(self, logging: bool = False, cacheAge: datetime.timedelta = datetime.timedelta(days=1)):
        self.config = self.loadConfig()  # Load the configuration file
        self.api_key = self.config.get("API_KEY")
        if self.api_key is None:
            raise Exception("API_KEY not found in the configuration file.")
        self.api = Api(self.api_key)
        currency_list = self.api.getCurrencyList()
        if currency_list is None:
            raise Exception("Failed to reach api endpoint, check API_Key or network connections")
        self.database = Database()
        self.gui = CurrencyConverter(currency_list, self.run)

        self.cacheAge = cacheAge
        self.logfile: None | io.TextIOWrapper = None

        if logging:
            self.logfile = open("./logfile.txt", "w")
            self.writeLog("Init: cache age set to {0}".format(str(cacheAge)))

            

    def run(self):
        self.writeLog("Start")
        conversion = self.getInput()
        if conversion is None:
            self.updateGui("Error: Numeric input only in 'Input Quantity' Field")
            self.writeLog("End")
            return

        currency = self.getCurrency(conversion)
        if currency is None:
            # TODO: return better error message to user
            self.updateGui("ERROR")
            self.writeLog("End")
            return
        
        conversion.rate = currency.conversion_rates[conversion.new]
        if conversion.rate is None:
            # TODO: return better error message to user
            self.updateGui("ERROR")
            return

        conversion.results = self.convert(conversion)
        self.writeLog(f'Conversion: {conversion.base} {conversion.base_value} = {conversion.new} {conversion.results}')
        self.writeLog("End")
        self.updateGui(f'Conversion: {conversion.base} {conversion.base_value} = {conversion.new} {conversion.results}')

    def writeLog(self, log: str) -> None:
        if self.logfile is not None:
            timestamp = str(datetime.datetime.now())
            entry = "{0} - {1}\n".format(timestamp, log)
            self.logfile.write(entry)


    def getInput(self) -> Conversion | None:
        self.writeLog("start getInput()")
        base = self.gui.selected_from.get()
        new = self.gui.selected_to.get()
        value = self.gui.getinputQuantity()

        if value is None:
            self.writeLog("Invalid base_value input")
            self.writeLog("end getInput()")
            return None

        self.writeLog("base currency: {0}".format(base))
        self.writeLog("new currency: {0}".format(new))
        self.writeLog("base_value: {0}".format(str(value)))
        
        self.writeLog("end getInput()")
        return Conversion(base, new, value)

    def getCurrency(self, conversion) -> Currency | None:
        self.writeLog("start getCurrency()")
        currency_data = self.database.getCurrency(conversion.base)
        self.writeLog("cache database queried")
        update = False

        if currency_data is not None:
            self.writeLog("cache entry found")
            old_time = datetime.datetime.fromisoformat(currency_data["timestamp"])
            now_time = datetime.datetime.now()
            delta = now_time - old_time
            if delta > self.cacheAge:
                self.writeLog("cache entry expired")
                update = True

        if currency_data is None or update:
            self.writeLog("query API")
            currency_data = self.api.getCurrency(conversion.base)
            update = True
            
        if update and currency_data is not None:
            self.writeLog("updating cache entry")
            self.database.updateCurrency(
                {
                    "base_code": currency_data["base_code"],
                    "conversion_rates": currency_data["conversion_rates"],
                    "timestamp": str(datetime.datetime.now())
                }
            )

        if currency_data is None:
            self.writeLog("no currency data found")
            self.writeLog("End getCurrency()")
            return None
        
        currency = Currency(
            base=currency_data["base_code"],
            conversion_rates=currency_data["conversion_rates"],
            timestamp=datetime.datetime.now())

        self.writeLog("End getCurrency()")
        return currency

    def convert(self, conversion):
        return conversion.rate * conversion.base_value

    def updateGui(self, message):
        self.gui.output(message)

    def loadConfig(self):
        with open("config.json") as f:
            return json.load(f)


class CurrencyConverter(tk.Tk):
    def __init__(self, currency_list: list[list], submit_function):
        super().__init__()

        self.title('Currency Converter')
        self.geometry('700x700')
        self.config(background='black')

        self.label = ttk.Label(self, text='Currency Converter', background='black', foreground='gold')
        self.label.pack()

        codes = [x[0] for x in currency_list]

        frame_input = ttk.Frame(self, padding=10)
        frame_input.pack(side=TOP, padx=50, pady=20)

        frame_convert = ttk.Frame(self, padding=10)
        frame_convert.pack(side=TOP, padx=50, pady=20)

        self.labelInputQuantity = ttk.Label(frame_input, text='Input Quantity', background='black', foreground='gold')
        self.labelInputQuantity.pack(side=LEFT, padx=5, pady=5)

        self.inputQuantity = tk.Text(frame_input, height=1, width=20, font=("Arial", 14), bg='red', fg='gold')
        self.inputQuantity.pack(side=LEFT, padx=5, pady=5)

        self.labelConvertFrom = ttk.Label(frame_convert, text='Convert From', background='black', foreground='gold')
        self.labelConvertFrom.pack(side=LEFT, padx=5, pady=5)

        self.selected_from = ttk.Combobox(frame_convert,state="readonly", values=codes)
        self.selected_from.set("USD")
        self.selected_from.pack(side=LEFT, padx=5, pady=5)

        self.labelConvertTo = ttk.Label(frame_convert, text='Convert To', background='black', foreground='gold')
        self.labelConvertTo.pack(side=LEFT, padx=5, pady=5)

        self.selected_to = ttk.Combobox(frame_convert,state="readonly", values=codes)
        self.selected_to.set("EUR")
        self.selected_to.pack(side=LEFT, padx=5, pady=5)

        self.button = tk.Button(self, text='Submit', width=25, font=("Arial", 14), command=submit_function, bg='red', fg='gold')
        self.button.pack(side=BOTTOM, padx=50, pady=20)

        self.outputBox = tk.Text(self, height=1, width=40, font=("Arial", 14), bg='red', fg='gold')
        self.outputBox.pack(side=BOTTOM, padx=50, pady=20)

    def getinputQuantity(self) -> float | None:
       
        input = self.inputQuantity.get(1.0, "end-1c")

        try:
            input = float(input)
        except:
            return None
    
        return input

    def output(self, input):
        self.outputBox.delete(1.0, "end")
        self.outputBox.insert(tk.END, input)


if __name__ == "__main__":
    #app = Core()
    #app.gui.mainloop()

    app = Core(logging=True)
    app.gui.mainloop()

