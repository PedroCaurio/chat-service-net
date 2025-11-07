import uuid
from models import User
from repositories import UserRepository
from datetime import datetime

from registry import register_command

@register_command("login", "login")
def login(username: str, password: str):
    user = UserRepository.login(username=username, password=password)
    if not user:
        return None
    return user.user_id