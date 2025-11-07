import uuid
from server.models import User, Group
from server.repositories import UserRepository, GroupRepository
from datetime import datetime

from registry import register_command

# User Actions

@register_command("action", "create_user")
def create_user(username: str, password: str):
    return UserRepository.add_user(
        User(username=username, password=password, user_id=str(uuid.uuid4()))
    )

@register_command("action", "get_user")
def get_user(user_id: str) -> User | None:
    return UserRepository.get_user_by_id(user_id)

@register_command("action", "update_user")
def update_user(new_user: dict) -> bool:
    return UserRepository.update_user(User.from_dict(new_user))

@register_command("action", "delete_user")
def delete_user(user_id: str) -> bool:
    return UserRepository.delete_user_by_id(user_id)

def send_private_message(sender_id: str, receiver_id: str, message: str) -> bool:
    ... # Placeholder for sending private message logic
    return True

# User - Group Actions

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

@register_command("action", "get_group")
def get_group(group_id: str) -> Group | None:
    return GroupRepository.get_group_by_id(group_id)

@register_command("action", "update_group_name")
def update_group_name(group: dict) -> bool:
    return GroupRepository.update_group_name(Group.from_dict(group))

@register_command("action", "delete_group")
def delete_group(group_id: str) -> bool:
    return GroupRepository.delete_group_by_id(group_id)

@register_command("action", "add_member")
def add_member(group_id: str, user_id: str) -> bool:
    return GroupRepository.add_user_to_group(group_id, user_id)

@register_command("action", "kick_member")
def kick_member(group_id: str, user_id: str) -> bool:
    return GroupRepository.remove_user_from_group(group_id, user_id)

def send_group_message(sender_id: str, group_id: str, message: str) -> bool:
    ... # Placeholder for sending group message logic
    return True

# Misc/Test Actions


@register_command("action", "get_all_users")
def get_all_users() -> list[User]:
    return UserRepository.get_all_users()


def sync():
    ... # Placeholder for sync logic