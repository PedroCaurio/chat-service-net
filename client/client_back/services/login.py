import json
from client_back.registry import register_command

''' Função para formatar a entrada do usuário '''
def format_login(username: str, password: str):
    msg = {
        "type": "login",
        "payload": {
            "username": username,
            "password": password
        }
    }

    return msg

''' Comando para realizaar o login e retornar o json formatado'''
@register_command("login")
def login(username, password):
    #username = input("digite seu usuario: ")
    #password = input("digite sua senha: ")

    if username and password:
        return format_login(username, password)
    return None

@register_command("receive_login")
def receive_login(user_id):
    if user_id:
        return True
    return False