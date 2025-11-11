'''
Cria a forma dos dados do usuário que será armazenado no banco de dados.
'''


from dataclasses import asdict, dataclass


''' Cria a estrutura com um decorador de dataclass, que facilita
a escrita pois implementa automaticamente alguns métodos como __init__ e __repr__.
Essa classe também possuí métodos para tradução com o banco de dados, já que ele armazena
JSON/Dicts.
'''
@dataclass
class User:
    username: str
    password: str

    @staticmethod
    def from_dict(data: dict) -> 'User':
        return User(
            username=data['username'],
            password=data['password']
        )

    def to_dict(self) -> dict:
        return asdict(self)