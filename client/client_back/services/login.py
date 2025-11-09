import json
from registry import register_command

''' Função para formatar a entrada do usuário '''
def login(username: str, password: str):
    msg = {
        "type": "request",
        "payload": {
            "command": "login",
            "username": username,
            "password": password
        }
    }

    return msg

''' Comando para realizaar o login e retornar o json formatado'''
@register_command("login")
def do_login():
    username = input("digite seu usuario: ")
    password = input("digite sua senha: ")

    if username and password:
        return login(username, password)
    return None