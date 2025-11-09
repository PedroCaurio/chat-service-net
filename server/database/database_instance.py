'''
Criar uma instância única e compartilhada do banco de dados
Utiliza o tinydb que armazena tudo em um db.json
'''

from tinydb import TinyDB

DB_FILE_PATH = "./db.json"

def open_database() -> TinyDB:
    return TinyDB(DB_FILE_PATH)

db = open_database()