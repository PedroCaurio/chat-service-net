'''
Camada de Abstração para facilitar o desenvolvimento. Sendo responsável apenas
por se comunicar com os dados dos usuários no TinyDB.
'''

from tinydb import Query
from models import User
from database import db

user_db = db.table("users")

def id_query(user_id: str): return Query().user_id == user_id

class UserRepository:
    
    # CRUD Operations

    @staticmethod
    def add_user(user: User) -> bool:   # CREATE
        if (UserRepository.user_exists(user.username)): return False
        user_db.insert(user.to_dict())
        return True
    
    @staticmethod
    def get_user_by_id(user_id: str) -> User | None:   # READ
        result = user_db.get(id_query(user_id))
        if result:
            return User.from_dict(result)
        return None
    
    @staticmethod
    def delete_user_by_id(user_id: str) -> bool:   # DELETE
        return len(user_db.remove(id_query(user_id))) > 0

    @staticmethod
    def update_user(user: User) -> bool:   # UPDATE
        User = Query()
        if not user_db.contains(id_query(user.user_id)) or user_db.contains(User.username == user.username and User.user_id != user.user_id):
            return False
        user_db.update(user.to_dict(), cond=id_query(user.user_id))
        return True



    # Utils
    
    @staticmethod
    def get_all_users() -> list[User]:
        results = user_db.all()
        return [User.from_dict(data) for data in results]
    
    @staticmethod
    def user_exists(username: str) -> bool:
        result = user_db.get(Query().username == username)
        return result is not None
    
    @staticmethod
    def login(username: str, password: str) -> User | None:
        UserQ = Query()
        result = user_db.get(UserQ.username == username)

        if result and result["password"] == password:
            return User.from_dict(result)
        return None
