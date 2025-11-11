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
def register(username: str, password: str, **kwargs):
    return UserRepository.add_user(
        User(username=username, password=password)
    )

@register_command("auth")
def auth(username: str, password: str):
    user = UserRepository.authenticate_user(username=username, password=password)
    if not user:
        return False
    return True


@register_command("get_user")
def get_user(username: str) -> User | None:
    return UserRepository.get_user_by_id(username)


@register_command("update_user")
def update_user(new_user: dict) -> bool:
    return UserRepository.update_user(User.from_dict(new_user))


@register_command("delete_user")
def delete_user(username: str) -> bool:
    return UserRepository.delete_user_by_id(username)


def send_private_message(sender_username: str, receiver_username: str, message: str) -> bool:
    return chat_private.send_private_message(sender_username, receiver_username, message)


# User - Group Actions


@register_command("create_group")
def create_group(admin: str, name: str, users: list[str]) -> bool:
    return GroupRepository.add_group(
        Group(
            name=name,
            admin=admin,
            users=users,
            created_at=datetime.now().timestamp(),
        )
    )


@register_command("get_group")
def get_group(group_name: str) -> Group | None:
    return GroupRepository.get_group_by_name(group_name)


@register_command("update_group_name")
def update_group_name(group: dict) -> bool:
    return GroupRepository.update_group_name(Group.from_dict(group))


@register_command("delete_group")
def delete_group(group_name: str) -> bool:
    return GroupRepository.delete_group_by_name(group_name)


@register_command("add_member")
def add_member(group_name: str, username: str) -> bool:
    return GroupRepository.add_user_to_group(group_name, username)


@register_command("kick_member")
def kick_member(group_name: str, username: str) -> bool:
    return GroupRepository.remove_user_from_group(group_name, username)


@register_command("send_group_message")
def send_group_message(sender_username: str, group_name: str, message: str) -> bool:
    return chat_private.send_group_message(sender_username, group_name, message)


# Misc/Test Actions


@register_command("get_all_users")
def get_all_users() -> list[User]:
    return UserRepository.get_all_users()


def sync():
    ... # Placeholder for sync logic
