import uuid
from models import User, Group
from repositories import UserRepository, GroupRepository
from datetime import datetime

from registry import register_command

@register_command("action", "create_user")
def create_user(username: str, password: str):
    return UserRepository.add_user(
        User(username=username, password=password, user_id=str(uuid.uuid4()))
    )


@register_command("action", "get_all_users")
def get_all_users() -> list[User]:
    return UserRepository.get_all_users()


@register_command("action", "create_group") 
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