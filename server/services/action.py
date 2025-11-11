'''
Camada para os comandos, sendo responsável pela lógica dos comandos que o servidor
pode executar.
'''

import uuid
from models.user import User
from models.group import Group
from models import Message
from repositories import UserRepository, GroupRepository
from datetime import datetime

from registry import register_command
import services.chat_private as chat_private
from services.chat_general import send_general_message
import client_registry 
import json

# ---- COMANDOS IMPLEMENTADOS -----

@register_command("login")
def login(username: str, password: str, conn):
    user = UserRepository.authenticate_user(username=username, password=password)
    client_registry.register_client(user.user_id, conn)
    if not user:
        return None
    return {
        "type" : "login",
        "payload": {
            "user_id" : user.user_id,
            "username": user.username,
            "users": get_all_users()
        }
    }


@register_command("message")
def message(origin, destiny, message):
    print("messagee")
    receiver = destiny
    text = message
    if receiver and text:
        target_obj = UserRepository.get_user_by_id(receiver)
        if target_obj is None:
            target_obj = UserRepository.get_user_by_username(receiver)
        if target_obj is None:
            return {"status": "error", "message": "Usuário não encontrado"}
        origin_obj = UserRepository.get_user_by_username(origin)
        receiver_id = target_obj.user_id
        origin_id = origin_obj.user_id
        print("origem:", origin_id, "destino: ", receiver_id)
        ok = send_private_message(origin_id, receiver_id, text)
        if ok:
            msg = Message(from_=origin_id, to=receiver_id, text=text)
            payload = json.dumps({"type": "private_message", "payload": {"origin": origin, "destiny": destiny, "message": msg.to_dict()}}, ensure_ascii=False).encode("utf-8")
            print("enviou?", client_registry.send_to_user(receiver_id, payload))
            return {"type": "private_message", "payload": {"origin": origin, "destiny": destiny, "message": msg.to_dict()}}
        else:
            return {"status": "error", "message": "Falha ao persistir/enviar mensagem"}
   


@register_command("get_all_users")
def get_all_users() -> list[User]:
    return UserRepository.get_all_users()
def send_private_message(sender_id: str, receiver_id: str, message: str) -> bool:
    return chat_private.send_private_message(sender_id, receiver_id, message)



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



@register_command("group")
def group(group_name, new_user, user_id):
    group = GroupRepository.get_group_by_name(group_name)
    if not group:
        new_group = Group(admin=user_id, users=[user_id], name=group_name, group_id=group_name)
        GroupRepository.add_group(new_group)
    GroupRepository.add_user_to_group(group_name, new_user)

@register_command("general_message")
def general_message(origin, message):
    user_id = UserRepository.get_user_by_username(origin).user_id
    text = message
    if text:
        msg = send_general_message(user_id, text)
        if msg:
            payload = json.dumps({"type": "general_message", "payload": {"origin": origin, "message": msg.to_dict()}}, ensure_ascii=False).encode("utf-8")
            for uid in client_registry.list_online():
                if uid != user_id:
                    try:
                        client_registry.send_to_user(uid, payload)
                    except Exception:
                        pass
            return {"type": "general_message", "payload": {"origin": origin, "message": msg.to_dict()}}
        else:
            return {"status": "error", "message": "Falha ao persistir mensagem"}




# ----- COMANDOS NÃO IMPLEMENTADOS (BUA BUA) -----

def sync():
    ... 




@register_command("get_user")
def get_user(user_id: str) -> User | None:
    return UserRepository.get_user_by_id(user_id)


@register_command("update_user")
def update_user(new_user: dict) -> bool:
    return UserRepository.update_user(User.from_dict(new_user))


@register_command("delete_user")
def delete_user(user_id: str) -> bool:
    return UserRepository.delete_user_by_id(user_id)

@register_command("register")
def register(username: str, password: str):
    return UserRepository.add_user(
        User(username=username, password=password, user_id=str(uuid.uuid4()))
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