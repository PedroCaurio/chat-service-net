from enum import Enum
from PyQt6.QtCore import pyqtSlot
from os.path import isfile
from json import dumps, loads

def create_file():
    tables = {"chats": {}, "user": {}}
    with open("./data.json", "w", encoding="utf-8") as file:
        file.write(dumps(tables))
        file.close()

class MessageType(Enum):
    received = 0
    sent = 1

class DataHelper:
    
    def __init__(self):
        self._load_data()


    def _load_data(self):
        if (not isfile("./data.json")):
            create_file()
            self.chats = {}
            self.user = {}
            return
        
        with open("data.json", "r", encoding="utf-8") as file:
            data = loads(file.read())
            file.close()
        self.chats = data["chats"]
        self.user = data["user"]

    def to_dict(self):
        return {
            "chats": self.chats,
            "user": self.user
        }

    def save_data(self):
        with open("data.json", "w", encoding="utf-8") as file:
            file.write(dumps(self.to_dict()))
            file.close()


    def store_message(self, message: str, sent: MessageType, sender: str, target_id: str, timestamp: str):
        if (not self.chats.get(target_id)):
            self.chats[target_id] = []
        history: list = self.chats[target_id]
        history.append({"message": message, "sent": sent.value, "timestamp": timestamp, "sender": sender})

data_helper = DataHelper()