'''
Cria a forma dos dados de grupo que será armazenado no banco de dados.
'''

from dataclasses import asdict, dataclass


''' Cria a estrutura com um decorador de dataclass, que facilita
a escrita pois implementa automaticamente alguns métodos como __init__ e __repr__.
Essa classe também possuí métodos para tradução com o banco de dados, já que ele armazena
JSON/Dicts.
'''
@dataclass
class Group:
    admin: str
    users: list[str]
    name: str
    created_at: int
    group_id: str

    @staticmethod
    def from_dict(data: dict) -> 'Group':
        return Group(
            admin=data["admin"],
            users=data["users"],
            group_id=data['group_id'],
            name=data['name'],
            created_at=data['created_at']
        )
    
    def to_dict(self) -> dict:
        return asdict(self)