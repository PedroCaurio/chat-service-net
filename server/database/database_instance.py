'''
Criar uma instância única e compartilhada do banco de dados
Utiliza o tinydb que armazena tudo em um db.json
'''

from contextlib import contextmanager
from tinydb import TinyDB
from .lock_manager import lock_collections

DB_FILE_PATH = "./db.json"

def open_database() -> TinyDB:
    return TinyDB(DB_FILE_PATH)

db = open_database()


@contextmanager
def locked_db():
    """Context manager que adquire o lock global do DB.
    Uso:
        with locked_db():
            # operar sobre `db`
    """
    # a chave "db" é usada para o lock global do banco
    with lock_collections(["db"]):
        yield db # yield é usado para retornar o db 