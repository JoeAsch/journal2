from common.database import Database
from datetime import datetime, timedelta
import uuid


class Transaction(object):
    def __init__(self, sales, traffic, pieces, drive, store_id, tran_date=datetime.date, _id=None):
        self.sales = int(sales)
        self.traffic = int(traffic)
        self.pieces = int(pieces)
        self.drive = drive
        self.store_id = store_id
        self.tran_date = datetime.utcnow() if tran_date is None else tran_date
        self._id = uuid.uuid4().hex if _id is None else _id

    def save_to_mongo(self):
        Database.insert(collection='reports', data=self.json())

    @classmethod
    def find_trans(cls):
        trans = Database.find(collection="reports", query={})
        return [cls(**elem) for elem in trans]

    @classmethod
    def find_by_date(cls, tran_date):
        found_trans = Database.find(collection="reports", query={"tran_date": datetime.strptime(tran_date,'%Y-%m-%d')})
        return [cls(**elem) for elem in found_trans]

    @classmethod
    def find_by_range(cls, tran_date):
        found_trans = Database.find(collection="reports", query={"tran_date": {"$gte": tran_date}}).limit(7)
        return[cls(**elem) for elem in found_trans]

    @classmethod
    def find_by_week(cls, tran_date):
        found_trans = Database.find(collection="reports", query={"$and": [{"tran_date": {"$lte": datetime.strptime(tran_date, '%Y-%m-%d')+timedelta(7)}},
                                    {"tran_date": {"$gte": datetime.strptime(tran_date,'%Y-%m-%d')}}]})
        return [cls(**elem) for elem in found_trans]

    def json(self):
        return{
            "_id": self._id,
            "sales": self.sales,
            "traffic": self.traffic,
            "pieces": self.pieces,
            "drive": self.drive,
            "tran_date": self.tran_date,
            "store_id": self.store_id

        }
