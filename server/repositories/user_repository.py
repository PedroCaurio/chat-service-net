'''
Camada de Abstração para facilitar o desenvolvimento. Sendo responsável apenas
por se comunicar com os dados dos usuários no TinyDB.
'''

from tinydb import Query
from server.models.user import User
from server.database.database_instance import db, locked_db

user_db = db.table("users")

def id_query(user_id: str): return Query().user_id == user_id

class UserRepository:

    # CRUD Operations

    @staticmethod
    def add_user(user: User) -> bool:   # CREATE
        if UserRepository.user_exists(user.username):
            return False
        with locked_db():
            user_db = db.table("users")
            user_db.insert(user.to_dict())
        return True

    @staticmethod
    def get_user_by_id(user_id: str) -> User | None:   # READ
        with locked_db():
            user_db = db.table("users")
            result = user_db.get(id_query(user_id))
        if result:
            return User.from_dict(result)
        return None

    @staticmethod
    def delete_user_by_id(user_id: str) -> bool:   # DELETE
        with locked_db():
            user_db = db.table("users")
            removed = user_db.remove(id_query(user_id))
        return len(removed) > 0

    @staticmethod
    def update_user(user: User) -> bool:   # UPDATE
        with locked_db():
            user_db = db.table("users")
            # existe o user_id?
            if not user_db.contains(id_query(user.user_id)):
                return False
            # username duplicado em outro id?
            dup = user_db.search((Query().username == user.username) & (Query().user_id != user.user_id))
            if dup:
                return False
            user_db.update(user.to_dict(), cond=id_query(user.user_id))
        return True


    # Utils

    @staticmethod
    def get_all_users() -> list[User]:
        with locked_db():
            user_db = db.table("users")
            results = user_db.all()
        return [User.from_dict(data) for data in results]

    @staticmethod
    def user_exists(username: str) -> bool:
        with locked_db():
            user_db = db.table("users")
            result = user_db.get(Query().username == username)
        return result is not None
    
    @staticmethod
    def get_user_by_username(username: str) -> User | None:
        """Retorna o objeto User para o username informado ou None se não existir."""
        with locked_db():
            user_db = db.table("users")
            result = user_db.get(Query().username == username)
        if result:
            return User.from_dict(result)
        return None