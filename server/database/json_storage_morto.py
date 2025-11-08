import json
import os
import threading
import uuid # é pra gerar ids unicos para usuarios, grupos, mensagens etc
            # é pra evitar colisao de ids, mesmo que dois usuarios criem usuario ao mesmo tempo com o mesmo nome
            # ou passar um diciconario de user que não tem user_id
            # não acho que vai acontecer né XDD mas é legal ter isso no trab
            # att 2 ah ja tem os ids unicos no GroupRepository e UserRepository
            # depois tem que atualizar o group_repository.py e user_repository.py pra usar esse 
            # json_storage.py
from .lock_manager import lock_collections
# .centralizei os locks no lock_manager.py

BASE_DIR = os.path.join(os.path.dirname(__file__), "data")
# base_dir = diretorio onde os arquivos json vão ser salvos, ah não ser que queiram mudar o
# lugar de onde guardar os arquivos json

def ensure_dir(path): # garante que o diretório existe
    os.makedirs(path, exist=True)

def file_path(name): # retorna o path completo do arquivo json para a coleção "name"
    ensure_dir(BASE_DIR)
    return os.path.join(BASE_DIR, f"{name}.json")


def read_json(path, default): # lê o json do path, ou retorna default se não existir
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        # arquivo corrompido, retorna default
        return default


def write_json(path, data): # salva o json, o json.dump serve pra converter objeto python em json
    
    tmp = f"{path}.tmp" # abre em modo rascunho
    with open(tmp, "w", encoding="utf-8") as f: # f é o objeto arquivo
        json.dump(data, f, ensure_ascii=False, indent=2) # escreve o json formatado no arquivo e joga ele pro disco
        # o data aqui é a lista users, groups, messages etc
        # eu não sei se alguem quer mudar o nome parametro data, já que tem pelo menos uns 3 data diferente nesse trab
        # ident = 2 é pra deixar 2 espaços de recuo
    os.replace(tmp, path)


def load_collection(name, default_create=list):
    """Carrega uma coleção do arquivo JSON. Por padrão retornará lista vazia.

    name: nome lógico da coleção (ex: 'users', 'groups', 'messages')
    default_create: função para o valor padrão quando o arquivo não existe
    """
    path = file_path(name)
    # lock por-coleção para permitir concorrência entre coleções diferentes
    with lock_collections([name]):
        return read_json(path, default_create())
        # é uma função que le o json do path, ou cria o default (lista vazia por padrão) caso não exista 


def save_collection(name, data):
    """Salva uma coleção objeto JSON."""
    path = file_path(name)
    with lock_collections([name]):
        write_json(path, data) # chama a função que salva o json no path


def ensure_collections():
    # cria arquivos padrão se não existirem
    load_collection("users", default_create=list)
    load_collection("groups", default_create=list)
    load_collection("messages", default_create=dict)


def add_user(user):
    """Adiciona um usuário. O usuário recebido pode passar 'user_id' vazio. Retorna o user_id criado."""
    if "user_id" not in user or not user["user_id"]: 
        user["user_id"] = str(uuid.uuid4()) # o id unico

    users = load_collection("users", default_create=list) 
    users.append(user)
    save_collection("users", users) # atualiza a coleção de usuarios
    return user["user_id"]


def get_user_by_id(user_id):
    users = load_collection("users", default_create=list)
    for user in users:
        if user.get("user_id") == user_id:
            return user
    return None


def get_all_users():
    return load_collection("users", default_create=list)


def add_group(group):
    if "group_id" not in group or not group["group_id"]:
        group["group_id"] = str(uuid.uuid4()) # id unico para cada grupo

    groups = load_collection("groups", default_create=list)
    groups.append(group) 
    save_collection("groups", groups)
    return group["group_id"]


def get_group_by_id(group_id): # retorna o grupo com o group_id 
    groups = load_collection("groups", default_create=list)
    for group in groups:
        if group.get("group_id") == group_id:
            return group
    return None


def all_groups():
    return load_collection("groups", default_create=list)

# É só um lembrete pra perguntar dps ou pra quem ler 
# um all_groups_by_id() para todos os ids dos grupos? o all groups tem 
# todas ids dos grupos juntos com os grupos.
# também, é necessário fazer um all_groups_by_id(user_id) que retorna todos os grupos que o user_id faz parte?

def append_message(conversation_id, message):
    """Adiciona uma mensagem a uma conversa."""
    messages = load_collection("messages", default_create=dict)
    if conversation_id not in messages:
        messages[conversation_id] = []
        
    # garantir id da mensagem
    if "message_id" not in message or not message["message_id"]:
        message["message_id"] = str(uuid.uuid4()) # id unico para cada mensagem
    messages[conversation_id].append(message)
    save_collection("messages", messages)


def get_messages(conversation_id):
    messages = load_collection("messages", default_create=dict) # dict é {conversation_id: [messages]}
    return messages.get(conversation_id, []) # retorna a lista de mensagens da conversa


def list_collections():
    (BASE_DIR)
    files = [f[:-5] for f in os.listdir(BASE_DIR) if f.endswith('.json')]
    # ele le os arquivos json no diretorio base e retorna a lista de coleções sem .json
    return files


if __name__ == "__main__":
    ensure_collections()
    print("Collections disponíveis:", list_collections())