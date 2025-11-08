import uuid
from models import User
from repositories import UserRepository
from datetime import datetime

from registry import register_command

@register_command("login")
def login(username: str, password: str):
    user = UserRepository.login(username=username, password=password)
    if not user:
        return None
    return {
        "command" : "login",
        "user_id" : user.user_id
    }