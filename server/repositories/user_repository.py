from tinydb import Query
from models import User
from database import db

user_db = db.table("users")

class UserRepository:
    
    @staticmethod
    def add_user(user: User) -> bool:
        if (UserRepository.user_exists(user.username)): return False
        user_db.insert(user.to_dict())
        return True
    
    @staticmethod
    def get_user_by_id(user_id: str) -> User | None:
        result = user_db.get(doc_id=user_id)
        result["id"] = user_id
        if result:
            return User.from_dict(result)
        return None
    
    @staticmethod
    def get_all_users() -> list[User]:
        results = user_db.all()
        return [User.from_dict(data) for data in results]
    
    @staticmethod
    def user_exists(username: str) -> bool:
        result = user_db.get(Query().username == username)
        return result is not None

    @staticmethod
    def delete_user_by_id(user_id: str) -> None:
        user_db.remove(doc_ids=[user_id])