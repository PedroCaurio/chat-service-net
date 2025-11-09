"""Script para criar usuários no TinyDB via UserRepository.

Uso:
  # criando interativamente
  python -m server.scripts.create_user --username alice --password 1234

  # fornecendo user_id explicitamente
  python -m server.scripts.create_user --username bob --password 1234 --user-id bob-id-1

Observação: execute a partir da raiz do projeto. Se tiver problema de imports, rode:
  $env:PYTHONPATH = '.'; python -m server.scripts.create_user --username alice --password 1234

"""
import argparse
import uuid
from ..models.user import User
from ..repositories.user_repository import UserRepository

## Eu pedi por meio de auxiliares fazerem um script pra criar um usuarios só 
# pra testar rapidamente 
#Para gerar um user_id custom:
#$env:PYTHONPATH = '.'; python -m server.scripts.create_user --username user --password 1234 --user-id user-id-1
#Saída esperada:
#Usuário criado: username=user, user_id=user-id-1

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--user-id", dest="user_id", default=None)
    args = parser.parse_args()

    user_id = args.user_id or str(uuid.uuid4())
    user = User(username=args.username, password=args.password, user_id=user_id)

    ok = UserRepository.add_user(user)
    if ok:
        print(f"Usuário criado: username={user.username}, user_id={user.user_id}")
    else:
        print("Falha: usuário já existe (username duplicado).")


if __name__ == '__main__':
    main()
