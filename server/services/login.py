import uuid
from server.models import User
from server.repositories import UserRepository
from datetime import datetime

from server.registry import register_command

@register_command("login")
def login(username: str, password: str):
    user = UserRepository.login(username=username, password=password)
    if not user:
        return None
    return {
        "command" : "login",
        "user_id" : user.user_id
    }