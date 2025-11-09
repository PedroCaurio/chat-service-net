from server.services.chat_groups import send_group_message, get_group_messages

# Este arquivo delega a lógica de persistência/validação de mensagens
# para `services.chat_groups` para evitar duplicação de código.

__all__ = ["send_group_message", "get_group_messages"]