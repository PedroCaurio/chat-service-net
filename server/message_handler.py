import json
from typing import Optional

from repositories import UserRepository, GroupRepository
from services.chat_private import send_private_message, get_private_messages
from services.chat_general import send_general_message, get_general_messages
from services.groups import send_group_message, get_group_messages
from models.message import Message
import client_registry


def handle_message(user_id: str, envelope: dict, conn) -> Optional[dict]:
    """Processa envelopes JSON recebidos do cliente.

    Esta função contém a lógica de roteamento/validação de mensagens e
    chama os serviços de domínio (chat_general/chat_private/chat_groups).
    Retorna um dict de resposta ou None.
    """
    print(envelope)
    try:
        msg_type = envelope.get("type", "general")
        if msg_type == "general":
            text = envelope.get("message")
            if text:
                msg = send_general_message(user_id, text)
                if msg:
                    payload = json.dumps(msg.to_dict(), ensure_ascii=False).encode("utf-8")
                    for uid in client_registry.list_online():
                        if uid != user_id:
                            try:
                                client_registry.send_to_user(uid, payload)
                            except Exception:
                                pass
                    return {"status": "success", "payload": msg.to_dict()}
                else:
                    return {"status": "error", "message": "Falha ao persistir mensagem"}

        elif msg_type == "private":
            receiver = envelope.get("target_user_id") or envelope.get("to")
            text = envelope.get("message") or envelope.get("text") or ""
            if receiver and text:
                target_obj = UserRepository.get_user_by_id(receiver)
                if target_obj is None:
                    target_obj = UserRepository.get_user_by_username(receiver)
                if target_obj is None:
                    return {"status": "error", "message": "Usuário não encontrado"}

                receiver_id = target_obj.user_id
                ok = send_private_message(user_id, receiver_id, text)
                if ok:
                    msg = Message(from_=user_id, to=receiver_id, text=text)
                    payload = json.dumps(msg.to_dict(), ensure_ascii=False).encode("utf-8")
                    client_registry.send_to_user(receiver_id, payload)
                    return {"status": "success", "message": f"Mensagem enviada para {receiver}", "payload": msg.to_dict()}
                else:
                    return {"status": "error", "message": "Falha ao persistir/enviar mensagem"}


        elif msg_type == "group":
            group_id = envelope.get("group_id")
            text = envelope.get("message") or envelope.get("text") or ""
            if group_id and text:
                group = GroupRepository.get_group_by_id(group_id)
                if group and user_id in getattr(group, "users", []):
                    ok = send_group_message(user_id, group_id, text)
                    if ok:
                        msg = Message(from_=user_id, to=group_id, text=text)
                        payload = json.dumps(msg.to_dict(), ensure_ascii=False).encode("utf-8")
                        client_registry.send_to_group(group_id, payload, exclude_id=user_id)
                        return {"status": "success", "message": f"Mensagem enviada para o grupo {getattr(group, 'name', group_id)}", "payload": msg.to_dict()}
                    else:
                        return {"status": "error", "message": "Falha ao enviar para o grupo"}
                else:
                    return {"status": "error", "message": "Grupo não encontrado ou você não é membro"}
            else:
                return {"status": "error", "message": "Campos insuficientes para mensagem de grupo"}

        elif msg_type == "get_private_messages":
            other = envelope.get("other_user_id") or envelope.get("with")
            if other:
                messages = get_private_messages(user_id, other)
                return {
                    "status": "success",
                    "type": "private_history",
                    "messages": [msg.to_dict() for msg in messages]
                }
            else:
                return {"status": "error", "message": "Usuário do histórico privado não especificado"}

        elif msg_type == "get_group_messages":
            group_id = envelope.get("group_id")
            if group_id:
                messages = get_group_messages(group_id)
                return {
                    "status": "success",
                    "type": "group_history",
                    "group_id": group_id,
                    "messages": [msg.to_dict() for msg in messages]
                }
            else:
                return {"status": "error", "message": "ID do grupo não especificado"}

        elif msg_type == "get_user_groups":
            groups = GroupRepository.get_user_groups(user_id)
            groups_data = [{"group_id": g.group_id, "name": g.name} for g in groups]
            return {"status": "success", "type": "user_groups", "groups": groups_data}

        elif msg_type == "get_general_messages":
            messages = get_general_messages()
            return {
                "status": "success",
                "type": "general_history",
                "messages": [msg.to_dict() for msg in messages]
            }

        elif msg_type == "get_online_users":
            online_users = client_registry.list_online()
            return {"status": "success", "type": "online_users", "users": online_users}

        else:
            return {"status": "error", "message": "Tipo de mensagem não suportado"}

    except Exception as e:
        return {"status": "error", "message": f"Erro interno: {str(e)}"}
