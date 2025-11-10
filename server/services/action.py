'''
Camada para os comandos, sendo responsável pela lógica dos comandos que o servidor
pode executar.
'''

import uuid
from models.user import User
from models.group import Group
from repositories import UserRepository, GroupRepository
from datetime import datetime

from registry import register_command
import services.chat_private as chat_private


# User Actions


@register_command("register")
def register(username: str, password: str):
    return UserRepository.add_user(
        User(username=username, password=password, user_id=str(uuid.uuid4()))
    )

@register_command("login")
def login(username: str, password: str):
    user = UserRepository.authenticate_user(username=username, password=password)
    if not user:
        return None
    return {
        "command" : "login",
        "user_id" : user.user_id
    }


@register_command("get_user")
def get_user(user_id: str) -> User | None:
    return UserRepository.get_user_by_id(user_id)


@register_command("update_user")
def update_user(new_user: dict) -> bool:
    return UserRepository.update_user(User.from_dict(new_user))


@register_command("delete_user")
def delete_user(user_id: str) -> bool:
    return UserRepository.delete_user_by_id(user_id)


def send_private_message(sender_id: str, receiver_id: str, message: str) -> bool:
    return chat_private.send_private_message(sender_id, receiver_id, message)


# User - Group Actions


@register_command("create_group")
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


@register_command("get_group")
def get_group(group_id: str) -> Group | None:
    return GroupRepository.get_group_by_id(group_id)


@register_command("update_group_name")
def update_group_name(group: dict) -> bool:
    return GroupRepository.update_group_name(Group.from_dict(group))


@register_command("delete_group")
def delete_group(group_id: str) -> bool:
    return GroupRepository.delete_group_by_id(group_id)


@register_command("add_member")
def add_member(group_id: str, user_id: str) -> bool:
    return GroupRepository.add_user_to_group(group_id, user_id)


@register_command("kick_member")
def kick_member(group_id: str, user_id: str) -> bool:
    return GroupRepository.remove_user_from_group(group_id, user_id)


@register_command("send_group_message")
def send_group_message(sender_id: str, group_id: str, message: str) -> bool:
    return chat_private.send_group_message(sender_id, group_id, message)


# Misc/Test Actions


@register_command("get_all_users")
def get_all_users() -> list[User]:
    return UserRepository.get_all_users()


def sync():
    ... # Placeholder for sync logic
