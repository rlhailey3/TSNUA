import os
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.messagebox import showinfo
import pymongo
import json
from api import Api


class Conversion:
    def __init__(self, base: str, new: str, base_value: float):
        self.base = base
        self.new = new
        self.base_value = base_value
        self.rate = None
        self.results = None


class Currency:
    def __init__(self, base: str, conversion_rates: dict, timestamp: datetime.datetime, valid: bool):
        self.base = base
        self.conversion_rates = conversion_rates
        self.timestamp = timestamp
        self.valid = valid


class Database:
    def __init__(self, host: str = "localhost", port: int = 27017,
                 db_name: str = "currencies", collection_name: str = "rates"):
        self.client = pymongo.MongoClient(host=host, port=port)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def close(self):
        self.client.close()

    def getCurrency(self, base: str) -> dict or None:
        find_filter = {"base_code": base}
        return self.collection.find_one(find_filter)

    def updateCurrency(self, entry: dict) -> bool:
        update_filter = {"base_code": entry["base_code"]}
        record = {"$set": entry}
        update = self.collection.update_one(update_filter, record, upsert=True)
        return update.acknowledged


class Core:
    def __init__(self, gui):
        self.config = self.loadConfig()  # Load the configuration file
        self.api_key = self.config.get("API_KEY")
        if self.api_key is None:
            raise Exception("API_KEY not found in the configuration file.")
        self.api = Api(self.api_key)
        self.database = Database()
        self.gui = gui

    def run(self):
        conversion = self.getInput()
        currency = self.getCurrency(conversion)
        if currency is None:
            self.updateGui("ERROR")
            return
        conversion.rate = currency.conversion_rates.get(conversion.new, None)
        if conversion.rate is None:
            self.updateGui("ERROR")
            return
        conversion.results = self.convert(conversion)
        self.updateGui(f'Conversion: {conversion.base} {conversion.base_value} = {conversion.new} {conversion.results}')

    def getInput(self):
        base = self.gui.selected_from.get()
        new = self.gui.selected_to.get()
        value = float(self.gui.getinputQuantity())
        return Conversion(base, new, value)

    def getCurrency(self, conversion):
        currency_data = self.database.getCurrency(conversion.base)
        if currency_data is None:
            currency_data = self.api.getCurrency(conversion.base)
            if currency_data is not None:
                timestamp_str = currency_data.get("timestamp", "")
                timestamp = datetime.datetime.fromisoformat(timestamp_str) if timestamp_str else None
                currency = Currency(
                    base=currency_data["base_code"],
                    conversion_rates=currency_data["conversion_rates"],
                    timestamp=timestamp,
                    valid=True
                )
                self.database.updateCurrency({
                    "base_code": currency.base,
                    "conversion_rates": currency.conversion_rates,
                    "timestamp": currency.timestamp,
                    "valid": currency.valid
                })
        return currency

    def convert(self, conversion):
        return conversion.rate * conversion.base_value

    def updateGui(self, message):
        self.gui.output(message)

    def loadConfig(self):
        with open("config.json") as f:
            return json.load(f)


class CurrencyConverter(tk.Tk):
    def __init__(self):
        super().__init__()

        self.core = Core(self)
        self.title('Currency Converter')
        self.geometry('700x700')
        self.config(background='black')

        self.label = ttk.Label(self, text='Currency Converter', background='black', foreground='gold')
        self.label.pack()

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

        self.selected_from = ttk.Combobox(frame_convert, values=["USD", "EURO", "BHD", "OMR", "KWD", "JOD", "GBP", "KYD", "GIP", "CHF"])
        self.selected_from.set("USD")
        self.selected_from.pack(side=LEFT, padx=5, pady=5)

        self.labelConvertTo = ttk.Label(frame_convert, text='Convert To', background='black', foreground='gold')
        self.labelConvertTo.pack(side=LEFT, padx=5, pady=5)

        self.selected_to = ttk.Combobox(frame_convert, values=["USD", "EURO", "BHD", "OMR", "KWD", "JOD", "GBP", "KYD", "GIP", "CHF"])
        self.selected_to.set("EURO")
        self.selected_to.pack(side=LEFT, padx=5, pady=5)

        self.button = tk.Button(self, text='Submit', width=25, font=("Arial", 14), command=self.core.run, bg='red', fg='gold')
        self.button.pack(side=BOTTOM, padx=50, pady=20)

        self.outputBox = tk.Text(self, height=1, width=40, font=("Arial", 14), bg='red', fg='gold')
        self.outputBox.pack(side=BOTTOM, padx=50, pady=20)

    def getinputQuantity(self):
        return self.inputQuantity.get(1.0, "end-1c")

    def output(self, input):
        self.outputBox.delete(1.0, "end")
        self.outputBox.insert(tk.END, input)


if __name__ == "__main__":
    app = CurrencyConverter()
    app.mainloop()











