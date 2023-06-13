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
    conversion_rates: dict[str: float]
    timestamp: datetime.datetime
    valid: bool


class Core:
    def __init__(self):

        api_key = None

        with open("api.key", "r") as file:
            api_key = file.read()

        if api_key is None:
            pass
            # TODO: No API Key, fail

        self.api = Api(api_key)
        """
        self.gui = GUI()
        self.database = Database("Values")
        """


    def run(self):
        while True:
            currency = Currency | None
            conversion = self.gui.getInput()
            if conversion is None:
                pass
                # TODO Error

            currency = self.database.getCurrency(conversion)
            if currency is None:
                currency = self.api.getCurrency(conversion)
                if currency is None:
                    pass
                    # TODO Handle lots of api errors
                
                self.datbase.updateCurrency(currency)

            conversion.rate = currency.conversion_rates[conversion.new]

            self.convert(conversion)

            self.updateGui(conversion)
                
    def convert(self, conversion):
        conversion.result = conversion.base_value * conversion.rate

    def updateGui(self, conversion):
        self.gui.setOutput(conversion.result)

    def getInput(self) -> Conversion | None:
        conversion = Conversion(
            self.gui.getBase(),
            self.gui.getNew(),
            self.gui.getBaseValue()
        )

        return conversion
