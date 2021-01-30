from common.database import Database
import uuid


class User(object):
    def __init__(self, email, password, _id=None):
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    def save_to_mongo(self):
        Database.insert(collection='users', data=self.json())

    def json(self):
        return{
            "_id": self._id,
            "email": self.email,
            "password": self.password
        }

    @classmethod
    def find_user(cls, email):
        users = Database.find(collection='users', query={"email": email})
        return [cls(**elem) for elem in users]


    @classmethod
    def password_valid(cls, email, password):
        user = cls.find_user(email)
        if user[0].password == password:
            return True
        else:
            return False

