import uuid
from models import User, Group
from repositories import UserRepository, GroupRepository
from datetime import datetime

def create_user(username: str, password: str):
    return UserRepository.add_user(
        User(username=username, password=password, user_id=str(uuid.uuid4()))
    )
    
def create_group(admin: str, name: str, users: list[str]) -> bool:
    return GroupRepository.add_group(
        Group(
            name=name,
            admin=admin,
            users=users,
            created_at=datetime.now().timestamp(),
            group_id=str(uuid.uuid4())
        )
    )

def get_all_users() -> list[User]:
    return UserRepository.get_all_users()