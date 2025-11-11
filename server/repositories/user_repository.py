'''
Camada de Abstração para facilitar o desenvolvimento. Sendo responsável apenas
por se comunicar com os dados dos usuários no TinyDB.
'''

from tinydb import Query
from models.user import User
from database.database_instance import db, locked_db

def id_query(user_id: str): return Query().user_id == user_id

class UserRepository:

    # CRUD Operations

    @staticmethod
    def _user_db():
        return db.table("users")

    @staticmethod
    def add_user(user: User) -> bool:   # CREATE
        if UserRepository.user_exists(user.username):
            return False
        with locked_db():
            UserRepository._user_db().insert(user.to_dict())
        return True

    @staticmethod
    def get_user_by_id(user_id: str) -> User | None:   # READ
        with locked_db():
            result = UserRepository._user_db().get(id_query(user_id))
        if result:
            return User.from_dict(result)
        return None

    @staticmethod
    def delete_user_by_id(user_id: str) -> bool:   # DELETE
        with locked_db():
            removed = UserRepository._user_db().remove(id_query(user_id))
        return len(removed) > 0

    @staticmethod
    def update_user(user: User) -> bool:   # UPDATE
        with locked_db():
            # existe o user_id?
            user_db = UserRepository._user_db()
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
            results = UserRepository._user_db().all()
        ret = {}
        print(results)
        for data in results:
            ret[data["username"]] = "clique para conversar" # Depois temos que trocar esse clique para conversar pela ultima msg
            
        return ret

    @staticmethod
    def user_exists(username: str) -> bool:
        with locked_db():
            result = UserRepository._user_db().get(Query().username.test(lambda u: u.lower() == username.lower()))
        return result is not None
    
    @staticmethod
    def get_user_by_username(username: str) -> User | None:
        with locked_db():
            result = UserRepository._user_db().get(Query().username.test(lambda u: u.lower() == username.lower()))
        if result:
            return User.from_dict(result)
        return None
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> User | None:
        UserQ = Query()
        with locked_db():
            result = UserRepository._user_db().get(
                (UserQ.username.test(lambda u: u.lower() == username.lower())) &
                (UserQ.password == password)
            )
        if result:
            print("autenticação do usuário")
            return User.from_dict(result)
        return None