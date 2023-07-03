'''
Database subsystem
Group 2,
Devin Spiker
Richard Hailey
David Lambert
CMSC 495 6381
'''
import pymongo

class Database:
    '''class for database initialization and handling'''
    def __init__(self, host: str = "localhost", port: int = 27017,
                 db_name: str = "currencies", collection_name: str = "rates"):

        self.client = pymongo.MongoClient(host=host, port=port)
        self.database = self.client[db_name]
        self.collection = self.database[collection_name]

    def close(self):
        """Close the underlying pymongo MongoClient

        call when finished with the database
        """
        self.client.close()

    def get_currency(self, base: str) -> dict | None:
        """Given a base currency, return the conversion rates or None on failure

        Keyword arguments
        base -- 3 letter ISO 4217 currency code

        return dict with the following keys
            {
                "base_code": str,
                "conversion_rates": {
                    "USD": int,
                    "AUD": int,
                    ...
                },
                "timestamp": iso format str
            }
        """
        find_filter = {"base_code": base}
        return self.collection.find_one(find_filter)

    def update_currency(self, entry: dict) -> bool:
        """Update, or insert if not found, a currencies conversion rates
        
        Keyword arguments:
        entry -- dict containing the conversion information
            {
                "base_code": str,
                "conversion_rates": {
                    "USD": int,
                    "AUD": int,
                    ...
                },
                "timestamp": iso format str
            }
        """
        update_filter = {"base_code": entry["base_code"]}
        record = {"$set": entry}
        update = self.collection.update_one(update_filter, record, upsert=True)
        return update.acknowledged