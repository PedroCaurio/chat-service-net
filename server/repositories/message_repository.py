from typing import List, Dict, Any
from tinydb import Query
from server.database.database_instance import db, locked_db
import uuid


TABLE_NAME = "messages"


class MessageRepository:
    """Repositório para mensagens privadas usando TinyDB.

    Estrutura por documento:
      { "conversation_id": "priv:...", "messages": [ {message}, ... ] }
    """

    @staticmethod
    def append_message(conversation_id: str, message: Dict[str, Any]) -> str:
        if "message_id" not in message or not message.get("message_id"):
            message["message_id"] = str(uuid.uuid4())
        with locked_db():
            t = db.table(TABLE_NAME)
            q = Query()
            conv = t.get(q.conversation_id == conversation_id)
            if conv:
                msgs = conv.get("messages", [])
                msgs.append(message)
                t.update({"messages": msgs}, q.conversation_id == conversation_id)
            else:
                t.insert({"conversation_id": conversation_id, "messages": [message]})
        return message["message_id"]

    @staticmethod
    def get_messages(conversation_id: str) -> List[Dict[str, Any]]:
        with locked_db():
            t = db.table(TABLE_NAME)
            q = Query()
            conv = t.get(q.conversation_id == conversation_id)
        if conv:
            return conv.get("messages", [])
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
