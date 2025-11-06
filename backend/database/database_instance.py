from tinydb import TinyDB

DB_FILE_PATH = "./db.json"

def open_database() -> TinyDB:
    return TinyDB(DB_FILE_PATH)

db = open_database()