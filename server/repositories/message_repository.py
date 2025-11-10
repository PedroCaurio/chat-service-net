from typing import List, Dict, Any
from tinydb import Query
from database.database_instance import db, locked_db
from models.message import Message
import uuid


TABLE_NAME = "messages"


class MessageRepository:
    """Repositório para mensagens privadas usando TinyDB.

    Estrutura por documento:
      { "conversation_id": "priv:...", "messages": [ {message}, ... ] }
    """
    ## CRUD Operations
    
    ## Att Arthur: botei o model Message mas 
    ## O TinyDB armazena como dict, então converti na hora de salvar e recuperar
    ## Se acharem que não faz sentido fazer essa mudança, podem desfazer
    @staticmethod
    def append_message(conversation_id: str, message: Message) -> str:
        """Adiciona uma Message (objeto) à conversa indicada e retorna message_id."""
        # garante message_id
        if not getattr(message, "message_id", None):
            message.message_id = str(uuid.uuid4())

        # converte para dict antes de salvar (TinyDB armazena JSON/dict)
        msg_dict = message.to_dict()

        with locked_db():
            t = db.table(TABLE_NAME)
            q = Query()
            conv = t.get(q.conversation_id == conversation_id)
            if conv:
                msgs = conv.get("messages", [])
                msgs.append(msg_dict)
                t.update({"messages": msgs}, q.conversation_id == conversation_id)
            else:
                t.insert({"conversation_id": conversation_id, "messages": [msg_dict]})
        return message.message_id

    @staticmethod
    def get_messages(conversation_id: str) -> List[Message]:
        with locked_db():
            t = db.table(TABLE_NAME)
            q = Query()
            conv = t.get(q.conversation_id == conversation_id)
        if conv:
            # converte cada dict salvo de volta para Message
            return [Message.from_dict(msg_dict) for msg_dict in conv.get("messages", [])]
        return []

    @staticmethod
    def get_all_conversations() -> List[Dict[str, Any]]:
        with locked_db():
            t = db.table(TABLE_NAME)
            return t.all()

    @staticmethod
    def delete_conversation(conversation_id: str) -> None:
        with locked_db():
            t = db.table(TABLE_NAME)
            q = Query()
            t.remove(q.conversation_id == conversation_id)
