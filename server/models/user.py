'''
Cria a forma dos dados do usuário que será armazenado no banco de dados.
'''


from dataclasses import dataclass


''' Cria a estrutura com um decorador de dataclass, que facilita
a escrita pois implementa automaticamente alguns métodos como __init__ e __repr__.
Essa classe também possuí métodos para tradução com o banco de dados, já que ele armazena
JSON/Dicts.
'''
@dataclass
@dataclass
class User:
    username: str
    password: str
    user_id: str

    @staticmethod
    def from_dict(data: dict) -> 'User':
        return User(
            user_id=data['user_id'],
            username=data['username'],
            password=data['password']
        )

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "password": self.password
        }