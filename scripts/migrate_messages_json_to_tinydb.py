import json
import os
from tinydb import Query

root = os.path.dirname(os.path.dirname(__file__))
src = os.path.join(root, "server", "database", "data", "messages.json")

if not os.path.exists(src):
    print("Nenhum arquivo messages.json encontrado em:", src)
    raise SystemExit(0)

with open(src, "r", encoding="utf-8") as f:
    data = json.load(f)  # espera dict {conversation_id: [messages]}

from server.database.database_instance import db
from server.database.lock_manager import lock_collections

# migrar
from tinydb import Query

with lock_collections(["db", "messages"]):
    t = db.table("messages")
    for conv_id, msgs in data.items():
        existing = t.get(Query().conversation_id == conv_id)
        if existing:
            existing_msgs = existing.get("messages", [])
            existing_msgs.extend(msgs)
            t.update({"messages": existing_msgs}, Query().conversation_id == conv_id)
        else:
            t.insert({"conversation_id": conv_id, "messages": msgs})

print("Migração completa. Verifique TinyDB (tabela 'messages').")
