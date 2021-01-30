from common.database import Database
import uuid


class Store(object):
    def __init__(self, location, number, _id=None):
        self.location = location
        self.number = number
        self._id = uuid.uuid4().hex if _id is None else _id

    def save_to_mongo(self):
        Database.insert(collection='stores', data=self.json())

    def json(self):
        return{
            "_id": self._id,
            "location": self.location,
            "number": self.number
        }

    @classmethod
    def find_stores(cls):
        stores = Database.find(collection='stores', query={})
        return [cls(**elem) for elem in stores]

    @classmethod
    def find_by_date(cls, date):
        found_trans = Database.find(collection="reports", query={"date": date})
        return [cls(**elem) for elem in found_trans]