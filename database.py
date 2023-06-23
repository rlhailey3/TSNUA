import pymongo

class Database:
    def __init__(self, host: str = "localhost", port: int = 27017,
                 db_name: str = "currencies", collection_name: str = "rates"):

        self.client = pymongo.MongoClient(host=host, port=port)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def close(self):
        """Close the underlying pymongo MongoClient

        call when finished with the database
        """
        self.client.close()

    def getCurrency(self, base: str) -> dict | None:
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

        find_filter = {"base": base}
        return self.collection.find_one(find_filter)


    def updateCurrency(self, entry: dict) -> bool:
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

        update_filter = {"base": entry["base"]}
        record = {"$set": entry}
        
        update = self.collection.update_one(update_filter, record, upsert=True)
        return update.acknowledged
